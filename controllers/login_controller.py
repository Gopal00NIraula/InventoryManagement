# controllers/login_controller.py

from models.user_model import authenticate_user

def login(username: str, password: str):
    """Validate login credentials"""
    role = authenticate_user(username, password)
    if role:
        print(f"[LOGIN SUCCESS] Welcome {username} ({role})")
        return True, role
    else:
        print("[LOGIN FAILED] Invalid credentials")
        return False, None
