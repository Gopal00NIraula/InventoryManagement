# controllers/login_controller.py
from models.user_model import authenticate, create_user

def login(identifier: str, password: str):
    user = authenticate(identifier, password)
    return (True, user) if user else (False, None)

def create_manager_account(form: dict):
    """
    form keys expected:
    first_name, last_name, phone, email, business_name, password
    """
    p = (form.get("password") or "").strip()
    if not p:
        raise ValueError("Password is required.")
    res = create_user(
        password=p,
        role="manager",
        manager_id=None,
        first_name=(form.get("first_name") or "").strip() or None,
        last_name=(form.get("last_name") or "").strip() or None,
        phone=(form.get("phone") or "").strip() or None,
        email=(form.get("email") or "").strip() or None,
        business_name=(form.get("business_name") or "").strip() or None,
        username=None,  # auto-generate
    )
    return res  # {"id": ..., "username": "..."}
