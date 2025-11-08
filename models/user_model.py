# models/user_model.py
from database.db_connection import get_connection
from utils.encryption import hash_password, verify_password
import random

# ---------- username generation ----------
def _initials(first_name: str | None, last_name: str | None) -> str:
    f = (first_name or "").strip()
    l = (last_name or "").strip()
    if f and l:
        return (f[0] + l[0]).lower()
    if f:
        return (f[0] + "x").lower()
    if l:
        return ("x" + l[0]).lower()
    return "xx"

def _random_digits(n: int = 4) -> str:
    return f"{random.randint(0, 10**n - 1):0{n}d}"

def generate_username(first_name: str | None, last_name: str | None) -> str:
    """Make unique username like ak0182."""
    prefix = _initials(first_name, last_name)
    conn = get_connection(); cur = conn.cursor()
    try:
        for _ in range(10000):
            candidate = prefix + _random_digits(4)
            cur.execute("SELECT 1 FROM users WHERE username = ?", (candidate,))
            if not cur.fetchone():
                return candidate
        raise RuntimeError("Unable to generate a unique username.")
    finally:
        conn.close()

# ---------- auth ----------
def authenticate(identifier: str, password: str):
    """identifier can be username OR email."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT id, username, email, password, role, first_name, last_name, phone, business_name
        FROM users
        WHERE username = ? OR email = ?
        LIMIT 1
    """, (identifier, identifier))
    row = cur.fetchone()
    conn.close()
    if not row or not verify_password(password, row["password"]):
        return None
    return {
        "id": row["id"],
        "username": row["username"],
        "email": row["email"],
        "role": row["role"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "phone": row["phone"],
        "business_name": row["business_name"]
    }

# ---------- user CRUD ----------
def create_user(
    *,
    password: str,
    role: str = "employee",
    manager_id: int | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    business_name: str | None = None,
    username: str | None = None  # if None, auto-generate from names
):
    if role not in ("manager", "employee"):
        raise ValueError("Invalid role")
    uname = username or generate_username(first_name, last_name)
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (username, email, password, role, manager_id, first_name, last_name, phone, business_name)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (uname, email, hash_password(password), role, manager_id, first_name, last_name, phone, business_name))
    conn.commit()
    uid = cur.lastrowid
    conn.close()
    return {"id": uid, "username": uname}

def delete_user(user_id: int, requesting_user: dict) -> bool:
    """Managers can delete employees in their own team."""
    if requesting_user.get("role") != "manager":
        raise PermissionError("Only managers can delete users.")
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id, role, manager_id FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        conn.close(); return False
    if row["role"] != "employee":
        conn.close(); raise PermissionError("Managers can only delete employees.")
    if row["manager_id"] != requesting_user["id"]:
        conn.close(); raise PermissionError("Employee not under this manager.")
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def list_team_employees(manager_id: int):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE role='employee' AND manager_id = ?", (manager_id,))
    rows = cur.fetchall()
    conn.close()
    return [{"id": r["id"], "username": r["username"]} for r in rows]
