from models.supplier_model import (
    create_supplier as model_create_supplier,
    get_supplier as model_get_supplier,
    list_all_suppliers as model_list_suppliers,
    update_supplier as model_update_supplier,
    delete_supplier as model_delete_supplier,
    search_suppliers as model_search_suppliers
)
from models.audit_log_model import log_action
from utils.permissions import require_permission
import json

def create_supplier(user, form_data):
    """Create a new supplier (requires manage_suppliers permission)"""
    require_permission(user, "manage_suppliers")
    
    name = form_data.get("name", "").strip()
    if not name:
        return {"success": False, "message": "Supplier name is required"}
    
    contact_person = form_data.get("contact_person", "").strip() or None
    email = form_data.get("email", "").strip() or None
    phone = form_data.get("phone", "").strip() or None
    address = form_data.get("address", "").strip() or None
    
    result = model_create_supplier(name, contact_person, email, phone, address)
    
    if result.get("success"):
        # Log supplier creation
        log_action(
            user_id=user['id'],
            username=user['username'],
            action='CREATE',
            resource_type='SUPPLIER',
            resource_id=result.get('supplier_id'),
            details=json.dumps({'name': name, 'email': email, 'phone': phone})
        )
    
    return result

def get_supplier(user, supplier_id):
    """Get supplier details (requires view_suppliers permission)"""
    require_permission(user, "view_suppliers")
    return model_get_supplier(supplier_id)

def list_suppliers(user):
    """List all suppliers (requires view_suppliers permission)"""
    require_permission(user, "view_suppliers")
    return model_list_suppliers()

def update_supplier(user, supplier_id, form_data):
    """Update supplier (requires manage_suppliers permission)"""
    require_permission(user, "manage_suppliers")
    
    name = form_data.get("name", "").strip() or None
    contact_person = form_data.get("contact_person", "").strip() or None
    email = form_data.get("email", "").strip() or None
    phone = form_data.get("phone", "").strip() or None
    address = form_data.get("address", "").strip() or None
    
    result = model_update_supplier(supplier_id, name, contact_person, email, phone, address)
    
    if result.get("success"):
        # Log supplier update
        log_action(
            user_id=user['id'],
            username=user['username'],
            action='UPDATE',
            resource_type='SUPPLIER',
            resource_id=supplier_id,
            details=json.dumps({'updated_fields': [k for k, v in form_data.items() if v]})
        )
    
    return result

def delete_supplier(user, supplier_id):
    """Delete supplier (requires manage_suppliers permission)"""
    require_permission(user, "manage_suppliers")
    result = model_delete_supplier(supplier_id)
    
    if result.get("success"):
        # Log supplier deletion
        log_action(
            user_id=user['id'],
            username=user['username'],
            action='DELETE',
            resource_type='SUPPLIER',
            resource_id=supplier_id,
            details=f"Supplier {supplier_id} deleted"
        )
    
    return result

def search_suppliers(user, query):
    """Search suppliers (requires view_suppliers permission)"""
    require_permission(user, "view_suppliers")
    return model_search_suppliers(query)
