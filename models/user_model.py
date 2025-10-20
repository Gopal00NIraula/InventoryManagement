# models/user_model.py

from database.db_connection import get_connection
from utils.encryption import hash_password, verify_password

def create_user(username: str, password: str, role: str = "staff"):
    conn = get_connection()
    cur = conn.cursor()
    hashed_pw = hash_password(password)
    try:
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username, hashed_pw, role))
        conn.commit()
        print(f"[DB] User '{username}' created successfully.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()

def authenticate_user(username: str, password: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT password, role FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()

    if not user:
        return None

    hashed_pw, role = user
    if verify_password(password, hashed_pw):
        return role
    return None
