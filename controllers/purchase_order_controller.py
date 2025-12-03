from models.purchase_order_model import (
    create_purchase_order as model_create_po,
    get_purchase_order as model_get_po,
    list_all_purchase_orders as model_list_po,
    update_purchase_order_status as model_update_po_status,
    delete_purchase_order as model_delete_po
)
from models.inventory_model import get_item, update_item_quantity
from models.audit_log_model import log_action
from utils.permissions import require_permission
import json

def create_purchase_order(user, form_data):
    """Create a new purchase order (requires create_purchase permission)"""
    require_permission(user, "create_purchase")
    
    try:
        supplier_id = int(form_data.get("supplier_id"))
        item_id = int(form_data.get("item_id"))
        quantity = int(form_data.get("quantity"))
        unit_price = float(form_data.get("unit_price"))
        notes = form_data.get("notes", "").strip() or None
        
        if quantity <= 0:
            return {"success": False, "message": "Quantity must be positive"}
        if unit_price < 0:
            return {"success": False, "message": "Unit price cannot be negative"}
        
        result = model_create_po(supplier_id, item_id, quantity, unit_price, user["id"], notes)
        
        if result.get("success"):
            # Log purchase order creation
            log_action(
                user_id=user['id'],
                username=user['username'],
                action='CREATE',
                resource_type='PURCHASE_ORDER',
                resource_id=result.get('order_id'),
                details=json.dumps({
                    'supplier_id': supplier_id,
                    'item_id': item_id,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_amount': quantity * unit_price
                })
            )
        
        return result
    except (ValueError, KeyError) as e:
        return {"success": False, "message": f"Invalid form data: {e}"}

def list_purchase_orders(user, status=None):
    """List all purchase orders (requires view_inventory permission)"""
    require_permission(user, "view_inventory")
    return model_list_po(status)

def get_purchase_order(user, order_id):
    """Get purchase order details (requires view_inventory permission)"""
    require_permission(user, "view_inventory")
    return model_get_po(order_id)

def complete_purchase_order(user, order_id):
    """
    Complete a purchase order and update inventory.
    Increases item quantity by order quantity.
    """
    require_permission(user, "create_purchase")
    
    # Get order details
    result = model_get_po(order_id)
    if not result.get("success"):
        return result
    
    order = result["order"]
    
    if order["status"] != "PENDING":
        return {"success": False, "message": f"Cannot complete order with status: {order['status']}"}
    
    # Get current item quantity
    item_result = get_item(order["item_id"])
    if not item_result.get("success"):
        return {"success": False, "message": "Item not found"}
    
    current_qty = item_result["item"]["quantity"]
    new_qty = current_qty + order["quantity"]
    
    # Update item quantity
    update_result = update_item_quantity(order["item_id"], new_qty)
    if not update_result.get("success"):
        return update_result
    
    # Update order status
    status_result = model_update_po_status(order_id, "COMPLETED")
    if status_result.get("success"):
        status_result["message"] = f"Purchase order completed. Item quantity increased by {order['quantity']} (from {current_qty} to {new_qty})"
        
        # Log purchase order completion
        log_action(
            user_id=user['id'],
            username=user['username'],
            action='COMPLETE',
            resource_type='PURCHASE_ORDER',
            resource_id=order_id,
            details=json.dumps({
                'item_id': order["item_id"],
                'quantity_added': order["quantity"],
                'old_quantity': current_qty,
                'new_quantity': new_qty
            })
        )
        
        # Send email notification if configured
        try:
            from utils.email_notifications import send_order_completion_notification, is_email_configured
            if is_email_configured() and user.get('email'):
                send_order_completion_notification(
                    user['email'],
                    'purchase',
                    order_id,
                    1  # Number of items (single item per order in this system)
                )
        except Exception as e:
            print(f"Email notification error: {e}")
    
    return status_result

def cancel_purchase_order(user, order_id):
    """Cancel a purchase order (requires create_purchase permission)"""
    require_permission(user, "create_purchase")
    result = model_update_po_status(order_id, "CANCELLED")
    
    if result.get("success"):
        # Log purchase order cancellation
        log_action(
            user_id=user['id'],
            username=user['username'],
            action='CANCEL',
            resource_type='PURCHASE_ORDER',
            resource_id=order_id,
            details="Purchase order cancelled"
        )
    
    return result

def delete_purchase_order(user, order_id):
    """Delete a pending purchase order (requires create_purchase permission)"""
    require_permission(user, "create_purchase")
    result = model_delete_po(order_id)
    
    if result.get("success"):
        # Log purchase order deletion
        log_action(
            user_id=user['id'],
            username=user['username'],
            action='DELETE',
            resource_type='PURCHASE_ORDER',
            resource_id=order_id,
            details="Purchase order deleted"
        )
    
    return result
