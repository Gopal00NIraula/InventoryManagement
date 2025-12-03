from models.inventory_model import get_items, add_item, update_item, delete_item, search_items
from models.audit_log_model import log_action
from utils.permissions import require_permission
from utils.barcode_utils import generate_barcode_number, update_item_barcode
import json

def list_items():
    """Anyone can view items"""
    return get_items()

def find_items(query: str):
    """Anyone can search items"""
    return search_items(query)

def create_item(current_user: dict, payload: dict):
    """ADMIN and STAFF can create items"""
    require_permission(current_user, 'create_item')
    
    # Generate barcode if not provided
    if not payload.get('barcode'):
        # Create item first to get ID
        item_id = add_item(payload)
        # Generate and update barcode
        barcode_num = generate_barcode_number(item_id, payload.get('sku', ''))
        update_item_barcode(item_id, barcode_num)
    else:
        item_id = add_item(payload)
    
    # Log item creation
    log_action(
        user_id=current_user['id'],
        username=current_user['username'],
        action='CREATE',
        resource_type='ITEM',
        resource_id=item_id,
        details=json.dumps({
            'name': payload.get('name'),
            'quantity': payload.get('quantity'),
            'price': payload.get('price')
        })
    )
    
    return item_id

def edit_item(current_user: dict, item_id: int, payload: dict):
    """ADMIN and STAFF can edit items"""
    require_permission(current_user, 'edit_item')
    result = update_item(item_id, payload)
    
    # Log item update
    log_action(
        user_id=current_user['id'],
        username=current_user['username'],
        action='UPDATE',
        resource_type='ITEM',
        resource_id=item_id,
        details=json.dumps({
            'updated_fields': list(payload.keys()),
            'new_values': payload
        })
    )
    
    return result

def remove_item(current_user: dict, item_id: int):
    """ADMIN and STAFF can delete items"""
    require_permission(current_user, 'delete_item')
    result = delete_item(item_id)
    
    # Log item deletion
    log_action(
        user_id=current_user['id'],
        username=current_user['username'],
        action='DELETE',
        resource_type='ITEM',
        resource_id=item_id,
        details=f"Item {item_id} deleted"
    )
    
    return result
