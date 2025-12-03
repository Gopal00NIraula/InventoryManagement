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
        SELECT id, username, email, password, role, first_name, last_name, phone, business_name, is_active
        FROM users
        WHERE (username = ? OR email = ?) AND is_active = 1
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
        "business_name": row["business_name"],
        "is_active": row["is_active"]
    }

# ---------- user CRUD ----------
def create_user(
    *,
    password: str,
    role: str = "STAFF",
    manager_id: int | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    business_name: str | None = None,
    username: str | None = None,  # if None, auto-generate from names
    is_active: int = 1
):
    if role not in ("ADMIN", "STAFF", "VIEWER"):
        raise ValueError(f"Invalid role: {role}. Must be ADMIN, STAFF, or VIEWER")
    uname = username or generate_username(first_name, last_name)
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (username, email, password, role, manager_id, first_name, last_name, phone, business_name, is_active)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (uname, email, hash_password(password), role, manager_id, first_name, last_name, phone, business_name, is_active))
    conn.commit()
    uid = cur.lastrowid
    conn.close()
    
    # Send welcome email if email is configured
    if email:
        try:
            from utils.email_notifications import send_welcome_email, is_email_configured
            if is_email_configured():
                send_welcome_email(email, uname, temporary_password=password)
        except Exception as e:
            print(f"Welcome email error: {e}")
    
    return {"id": uid, "username": uname}

def delete_user(user_id: int, requesting_user: dict) -> bool:
    """ADMIN can delete any user. STAFF can deactivate (not delete) users under them."""
    if requesting_user.get("role") not in ("ADMIN", "STAFF"):
        raise PermissionError("Only ADMIN or STAFF can manage users.")
    
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id, role, manager_id FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        conn.close(); return False
    
    # ADMIN can delete anyone except themselves
    if requesting_user.get("role") == "ADMIN":
        if row["id"] == requesting_user["id"]:
            conn.close(); raise PermissionError("Cannot delete your own account.")
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    else:
        # STAFF can only deactivate users under them
        if row["role"] not in ("STAFF", "VIEWER"):
            conn.close(); raise PermissionError("STAFF can only manage STAFF/VIEWER users.")
        if row["manager_id"] != requesting_user["id"]:
            conn.close(); raise PermissionError("User not under your management.")
        cur.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
    
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def list_team_employees(manager_id: int):
    """List users under this manager (for STAFF). ADMIN sees all."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT id, username, first_name, last_name, email, phone, role, is_active 
        FROM users 
        WHERE manager_id = ? AND is_active = 1
        ORDER BY username
    """, (manager_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def list_all_users(requesting_user: dict):
    """ADMIN can see all users."""
    if requesting_user.get("role") != "ADMIN":
        raise PermissionError("Only ADMIN can list all users.")
    
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT id, username, first_name, last_name, email, phone, role, is_active, created_at
        FROM users
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_user(user_id: int, requesting_user: dict, **updates):
    """Update user information. ADMIN can update anyone. Users can update themselves."""
    if requesting_user.get("role") != "ADMIN" and requesting_user.get("id") != user_id:
        raise PermissionError("You can only update your own profile unless you are ADMIN.")
    
    allowed_fields = ["first_name", "last_name", "email", "phone", "business_name", "role", "is_active"]
    fields_to_update = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if not fields_to_update:
        return False
    
    # Only ADMIN can change roles and is_active
    if requesting_user.get("role") != "ADMIN":
        fields_to_update.pop("role", None)
        fields_to_update.pop("is_active", None)
    
    set_clause = ", ".join([f"{k} = ?" for k in fields_to_update.keys()])
    values = list(fields_to_update.values()) + [user_id]
    
    conn = get_connection(); cur = conn.cursor()
    cur.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok
