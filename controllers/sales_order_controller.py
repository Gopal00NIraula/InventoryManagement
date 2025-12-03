from models.sales_order_model import (
    create_sales_order as model_create_so,
    get_sales_order as model_get_so,
    list_all_sales_orders as model_list_so,
    update_sales_order_status as model_update_so_status,
    delete_sales_order as model_delete_so
)
from models.inventory_model import get_item, update_item_quantity
from models.audit_log_model import log_action
from utils.permissions import require_permission
import json

def create_sales_order(user, form_data):
    """Create a new sales order (requires create_sale permission)"""
    require_permission(user, "create_sale")
    
    try:
        customer_id = int(form_data.get("customer_id"))
        item_id = int(form_data.get("item_id"))
        quantity = int(form_data.get("quantity"))
        unit_price = float(form_data.get("unit_price"))
        notes = form_data.get("notes", "").strip() or None
        
        if quantity <= 0:
            return {"success": False, "message": "Quantity must be positive"}
        if unit_price < 0:
            return {"success": False, "message": "Unit price cannot be negative"}
        
        # Check if enough inventory available
        item_result = get_item(item_id)
        if not item_result.get("success"):
            return {"success": False, "message": "Item not found"}
        
        current_qty = item_result["item"]["quantity"]
        if current_qty < quantity:
            return {"success": False, "message": f"Insufficient inventory. Available: {current_qty}, Requested: {quantity}"}
        
        result = model_create_so(customer_id, item_id, quantity, unit_price, user["id"], notes)
        
        if result.get("success"):
            # Log sales order creation
            log_action(
                user_id=user['id'],
                username=user['username'],
                action='CREATE',
                resource_type='SALES_ORDER',
                resource_id=result.get('order_id'),
                details=json.dumps({
                    'customer_id': customer_id,
                    'item_id': item_id,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_amount': quantity * unit_price
                })
            )
        
        return result
    except (ValueError, KeyError) as e:
        return {"success": False, "message": f"Invalid form data: {e}"}

def list_sales_orders(user, status=None):
    """List all sales orders (requires view_inventory permission)"""
    require_permission(user, "view_inventory")
    return model_list_so(status)

def get_sales_order(user, order_id):
    """Get sales order details (requires view_inventory permission)"""
    require_permission(user, "view_inventory")
    return model_get_so(order_id)

def complete_sales_order(user, order_id):
    """
    Complete a sales order and update inventory.
    Decreases item quantity by order quantity.
    """
    require_permission(user, "create_sale")
    
    # Get order details
    result = model_get_so(order_id)
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
    
    # Verify sufficient quantity
    if current_qty < order["quantity"]:
        return {"success": False, "message": f"Insufficient inventory. Available: {current_qty}, Required: {order['quantity']}"}
    
    new_qty = current_qty - order["quantity"]
    
    # Update item quantity
    update_result = update_item_quantity(order["item_id"], new_qty)
    if not update_result.get("success"):
        return update_result
    
    # Update order status
    status_result = model_update_so_status(order_id, "COMPLETED")
    if status_result.get("success"):
        status_result["message"] = f"Sales order completed. Item quantity decreased by {order['quantity']} (from {current_qty} to {new_qty})"
        
        # Log sales order completion
        log_action(
            user_id=user['id'],
            username=user['username'],
            action='COMPLETE',
            resource_type='SALES_ORDER',
            resource_id=order_id,
            details=json.dumps({
                'item_id': order["item_id"],
                'quantity_sold': order["quantity"],
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
                    'sales',
                    order_id,
                    1  # Number of items (single item per order in this system)
                )
        except Exception as e:
            print(f"Email notification error: {e}")
    
    return status_result

def cancel_sales_order(user, order_id):
    """Cancel a sales order (requires create_sale permission)"""
    require_permission(user, "create_sale")
    result = model_update_so_status(order_id, "CANCELLED")
    
    if result.get("success"):
        # Log sales order cancellation
        log_action(
            user_id=user['id'],
            username=user['username'],
            action='CANCEL',
            resource_type='SALES_ORDER',
            resource_id=order_id,
            details="Sales order cancelled"
        )
    
    return result

def delete_sales_order(user, order_id):
    """Delete a pending sales order (requires create_sale permission)"""
    require_permission(user, "create_sale")
    result = model_delete_so(order_id)
    
    if result.get("success"):
        # Log sales order deletion
        log_action(
            user_id=user['id'],
            username=user['username'],
            action='DELETE',
            resource_type='SALES_ORDER',
            resource_id=order_id,
            details="Sales order deleted"
        )
    
    return result
