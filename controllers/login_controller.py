from models.user_model import authenticate, create_user
from models.audit_log_model import log_action

def login(identifier: str, password: str):
    user = authenticate(identifier, password)
    if user:
        # Log successful login
        log_action(
            user_id=user['id'],
            username=user['username'],
            action='LOGIN',
            resource_type='AUTH',
            details=f"User {user['username']} logged in successfully"
        )
        return (True, user)
    return (False, None)

def create_admin_account(form: dict):
    """
    Create an ADMIN account (used for initial setup or by existing ADMIN)
    form keys expected: first_name, last_name, phone, email, business_name, password
    """
    p = (form.get("password") or "").strip()
    if not p:
        raise ValueError("Password is required.")
    res = create_user(
        password=p,
        role="ADMIN",
        manager_id=None,
        first_name=(form.get("first_name") or "").strip() or None,
        last_name=(form.get("last_name") or "").strip() or None,
        phone=(form.get("phone") or "").strip() or None,
        email=(form.get("email") or "").strip() or None,
        business_name=(form.get("business_name") or "").strip() or None,
        username=None,  # auto-generate
    )
    
    # Log admin account creation (system-level action)
    log_action(
        user_id=res['id'],
        username=res['username'],
        action='CREATE',
        resource_type='USER',
        resource_id=res['id'],
        details=f"ADMIN account created: {res['username']}"
    )
    
    return res

create_manager_account = create_admin_account
