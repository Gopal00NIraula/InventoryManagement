from database.db_connection import get_connection
from datetime import datetime

def check_and_create_alerts():
    """
    Check all items for low stock conditions and create alerts.
    Returns list of new alerts created.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Get all items with their current stock levels
        cur.execute("""
            SELECT id, name, sku, quantity, min_stock_level, reorder_point
            FROM items
        """)
        items = cur.fetchall()
        
        new_alerts = []
        
        for item in items:
            item_id, name, sku, quantity, min_stock, reorder_point = item
            
            # Determine alert type
            alert_type = None
            message = None
            
            if quantity == 0:
                alert_type = "OUT_OF_STOCK"
                message = f"Item '{name}' (SKU: {sku}) is OUT OF STOCK"
            elif quantity <= min_stock:
                alert_type = "LOW_STOCK"
                message = f"Item '{name}' (SKU: {sku}) is LOW on stock. Current: {quantity}, Min: {min_stock}"
            elif quantity <= reorder_point:
                alert_type = "REORDER"
                message = f"Item '{name}' (SKU: {sku}) has reached reorder point. Current: {quantity}, Reorder at: {reorder_point}"
            
            if alert_type:
                # Check if there's already an unresolved alert for this item and type
                cur.execute("""
                    SELECT id FROM stock_alerts
                    WHERE item_id = ? AND alert_type = ? AND is_resolved = 0
                    ORDER BY created_at DESC LIMIT 1
                """, (item_id, alert_type))
                
                existing_alert = cur.fetchone()
                
                if not existing_alert:
                    # Create new alert
                    cur.execute("""
                        INSERT INTO stock_alerts (item_id, alert_type, message, quantity_at_alert)
                        VALUES (?, ?, ?, ?)
                    """, (item_id, alert_type, message, quantity))
                    conn.commit()
                    
                    new_alerts.append({
                        "id": cur.lastrowid,
                        "item_id": item_id,
                        "item_name": name,
                        "sku": sku,
                        "alert_type": alert_type,
                        "message": message,
                        "quantity": quantity
                    })
        
        return {"success": True, "alerts": new_alerts, "count": len(new_alerts)}
    except Exception as e:
        return {"success": False, "message": f"Error checking stock alerts: {e}"}
    finally:
        conn.close()

def get_active_alerts():
    """Get all unresolved alerts"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT sa.*, i.name as item_name, i.sku, i.quantity as current_quantity
            FROM stock_alerts sa
            JOIN items i ON sa.item_id = i.id
            WHERE sa.is_resolved = 0
            ORDER BY 
                CASE sa.alert_type
                    WHEN 'OUT_OF_STOCK' THEN 1
                    WHEN 'LOW_STOCK' THEN 2
                    WHEN 'REORDER' THEN 3
                END,
                sa.created_at DESC
        """)
        rows = cur.fetchall()
        
        alerts = []
        for row in rows:
            alerts.append({
                "id": row[0],
                "item_id": row[1],
                "alert_type": row[2],
                "message": row[3],
                "quantity_at_alert": row[4],
                "is_resolved": row[5],
                "created_at": row[6],
                "resolved_at": row[7],
                "item_name": row[8],
                "sku": row[9],
                "current_quantity": row[10]
            })
        
        return {"success": True, "alerts": alerts}
    except Exception as e:
        return {"success": False, "message": f"Error fetching alerts: {e}"}
    finally:
        conn.close()

def get_alert_summary():
    """Get summary count of alerts by type"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT alert_type, COUNT(*) as count
            FROM stock_alerts
            WHERE is_resolved = 0
            GROUP BY alert_type
        """)
        rows = cur.fetchall()
        
        summary = {
            "OUT_OF_STOCK": 0,
            "LOW_STOCK": 0,
            "REORDER": 0,
            "TOTAL": 0
        }
        
        for row in rows:
            summary[row[0]] = row[1]
            summary["TOTAL"] += row[1]
        
        return {"success": True, "summary": summary}
    except Exception as e:
        return {"success": False, "message": f"Error fetching alert summary: {e}"}
    finally:
        conn.close()

def resolve_alert(alert_id):
    """Mark an alert as resolved"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE stock_alerts
            SET is_resolved = 1, resolved_at = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), alert_id))
        conn.commit()
        
        if cur.rowcount == 0:
            return {"success": False, "message": "Alert not found"}
        
        return {"success": True, "message": "Alert resolved"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error resolving alert: {e}"}
    finally:
        conn.close()

def resolve_alerts_for_item(item_id):
    """Resolve all alerts for a specific item (useful when stock is replenished)"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE stock_alerts
            SET is_resolved = 1, resolved_at = ?
            WHERE item_id = ? AND is_resolved = 0
        """, (datetime.now().isoformat(), item_id))
        conn.commit()
        
        count = cur.rowcount
        return {"success": True, "message": f"Resolved {count} alert(s)", "count": count}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error resolving alerts: {e}"}
    finally:
        conn.close()

def get_low_stock_items():
    """Get list of items currently below min stock level"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, name, sku, quantity, min_stock_level, reorder_point, price
            FROM items
            WHERE quantity <= min_stock_level
            ORDER BY quantity ASC
        """)
        rows = cur.fetchall()
        
        items = []
        for row in rows:
            items.append({
                "id": row[0],
                "name": row[1],
                "sku": row[2],
                "quantity": row[3],
                "min_stock_level": row[4],
                "reorder_point": row[5],
                "price": row[6],
                "status": "OUT_OF_STOCK" if row[3] == 0 else "LOW_STOCK"
            })
        
        return {"success": True, "items": items}
    except Exception as e:
        return {"success": False, "message": f"Error fetching low stock items: {e}"}
    finally:
        conn.close()


def send_low_stock_email_alerts():
    """
    Send email notifications for low stock items to all admin users
    Returns dict with success status and message
    """
    try:
        from utils.email_notifications import send_low_stock_alert, is_email_configured
        from models.user_model import list_all_users
        
        # Check if email is configured
        if not is_email_configured():
            return {"success": False, "message": "Email notifications not configured"}
        
        # Get low stock items
        result = get_low_stock_items()
        if not result.get("success") or not result.get("items"):
            return {"success": False, "message": "No low stock items to notify"}
        
        items = result.get("items")
        
        # Get all admin users
        users_result = list_all_users()
        if not users_result.get("success"):
            return {"success": False, "message": "Failed to get user list"}
        
        admin_users = [u for u in users_result.get("users", []) if u.get("role") == "ADMIN"]
        
        if not admin_users:
            return {"success": False, "message": "No admin users to notify"}
        
        # Send email to each admin with a valid email
        sent_count = 0
        for user in admin_users:
            if user.get("email"):
                result = send_low_stock_alert(user["email"], items)
                if result.get("success"):
                    sent_count += 1
        
        return {
            "success": True,
            "message": f"Sent low stock alerts to {sent_count} admin(s)",
            "items_count": len(items),
            "recipients": sent_count
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error sending email alerts: {e}"}
