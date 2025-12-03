"""
Role-based permission system for Inventory Management

Roles:
- ADMIN: Full access to all features, can manage users, view audit logs
- STAFF: Can manage inventory (CRUD operations), create purchase/sales orders
- VIEWER: Read-only access to inventory and reports
"""

def has_permission(user: dict, permission: str) -> bool:
    """
    Check if user has a specific permission.
    
    Args:
        user: User dict with 'role' key
        permission: Permission name (e.g., 'manage_inventory', 'manage_users')
    
    Returns:
        bool: True if user has permission
    """
    if not user or 'role' not in user:
        return False
    
    role = user['role']
    
    # ADMIN has all permissions
    if role == 'ADMIN':
        return True
    
    # Define permission matrix
    permissions = {
        'STAFF': [
            'view_inventory',
            'create_item',
            'edit_item',
            'delete_item',
            'create_purchase',
            'create_sale',
            'view_reports',
            'manage_team',  # Can manage users under them
            'view_suppliers',
            'manage_suppliers',
            'view_customers',
            'manage_customers',
        ],
        'VIEWER': [
            'view_inventory',
            'view_reports',
            'view_suppliers',
            'view_customers',
        ]
    }
    
    return permission in permissions.get(role, [])

def require_permission(user: dict, permission: str):
    """
    Raise PermissionError if user doesn't have permission.
    Use as a guard in controller functions.
    """
    if not has_permission(user, permission):
        role = user.get('role', 'Unknown') if user else 'None'
        raise PermissionError(f"Role '{role}' does not have permission: {permission}")

def can_manage_inventory(user: dict) -> bool:
    """Quick check if user can add/edit/delete inventory items"""
    return has_permission(user, 'create_item')

def can_manage_users(user: dict) -> bool:
    """Quick check if user can manage other users"""
    return user.get('role') == 'ADMIN'

def can_view_audit_logs(user: dict) -> bool:
    """Quick check if user can view audit logs"""
    return user.get('role') == 'ADMIN'

def is_admin(user: dict) -> bool:
    """Check if user is ADMIN"""
    return user.get('role') == 'ADMIN'

def is_staff(user: dict) -> bool:
    """Check if user is STAFF"""
    return user.get('role') == 'STAFF'

def is_viewer(user: dict) -> bool:
    """Check if user is VIEWER"""
    return user.get('role') == 'VIEWER'
