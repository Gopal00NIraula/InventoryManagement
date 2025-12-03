from models.customer_model import (
    create_customer as model_create_customer,
    get_customer as model_get_customer,
    list_all_customers as model_list_customers,
    update_customer as model_update_customer,
    delete_customer as model_delete_customer,
    search_customers as model_search_customers
)
from models.audit_log_model import log_action
from utils.permissions import require_permission
import json

def create_customer(user, form_data):
    """Create a new customer (requires manage_customers permission)"""
    require_permission(user, "manage_customers")
    
    name = form_data.get("name", "").strip()
    if not name:
        return {"success": False, "message": "Customer name is required"}
    
    email = form_data.get("email", "").strip() or None
    phone = form_data.get("phone", "").strip() or None
    address = form_data.get("address", "").strip() or None
    
    result = model_create_customer(name, email, phone, address)
    
    if result.get("success"):
        # Log customer creation
        log_action(
            user_id=user['id'],
            username=user['username'],
            action='CREATE',
            resource_type='CUSTOMER',
            resource_id=result.get('customer_id'),
            details=json.dumps({'name': name, 'email': email, 'phone': phone})
        )
    
    return result

def get_customer(user, customer_id):
    """Get customer details (requires view_customers permission)"""
    require_permission(user, "view_customers")
    return model_get_customer(customer_id)

def list_customers(user):
    """List all customers (requires view_customers permission)"""
    require_permission(user, "view_customers")
    return model_list_customers()

def update_customer(user, customer_id, form_data):
    """Update customer (requires manage_customers permission)"""
    require_permission(user, "manage_customers")
    
    name = form_data.get("name", "").strip() or None
    email = form_data.get("email", "").strip() or None
    phone = form_data.get("phone", "").strip() or None
    address = form_data.get("address", "").strip() or None
    
    result = model_update_customer(customer_id, name, email, phone, address)
    
    if result.get("success"):
        # Log customer update
        log_action(
            user_id=user['id'],
            username=user['username'],
            action='UPDATE',
            resource_type='CUSTOMER',
            resource_id=customer_id,
            details=json.dumps({'updated_fields': [k for k, v in form_data.items() if v]})
        )
    
    return result

def delete_customer(user, customer_id):
    """Delete customer (requires manage_customers permission)"""
    require_permission(user, "manage_customers")
    result = model_delete_customer(customer_id)
    
    if result.get("success"):
        # Log customer deletion
        log_action(
            user_id=user['id'],
            username=user['username'],
            action='DELETE',
            resource_type='CUSTOMER',
            resource_id=customer_id,
            details=f"Customer {customer_id} deleted"
        )
    
    return result

def search_customers(user, query):
    """Search customers (requires view_customers permission)"""
    require_permission(user, "view_customers")
    return model_search_customers(query)
