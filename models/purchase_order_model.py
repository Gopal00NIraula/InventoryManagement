from database.db_connection import get_connection
from datetime import datetime

def generate_order_number(prefix="PO"):
    """Generate unique order number with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{timestamp}"

def create_purchase_order(supplier_id, item_id, quantity, unit_price, created_by, notes=None):
    """Create a new purchase order"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        order_number = generate_order_number("PO")
        total_price = quantity * unit_price
        
        cur.execute("""
            INSERT INTO purchase_orders 
            (order_number, supplier_id, item_id, quantity, unit_price, total_price, notes, created_by, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
        """, (order_number, supplier_id, item_id, quantity, unit_price, total_price, notes, created_by))
        conn.commit()
        
        order_id = cur.lastrowid
        return {"success": True, "id": order_id, "order_number": order_number, "message": "Purchase order created successfully"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error creating purchase order: {e}"}
    finally:
        conn.close()

def get_purchase_order(order_id):
    """Get purchase order by ID with related data"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT po.*, s.name as supplier_name, i.name as item_name, i.sku,
                   u.username as created_by_name
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.id
            JOIN items i ON po.item_id = i.id
            JOIN users u ON po.created_by = u.id
            WHERE po.id = ?
        """, (order_id,))
        row = cur.fetchone()
        
        if row:
            return {
                "success": True,
                "order": {
                    "id": row[0],
                    "order_number": row[1],
                    "supplier_id": row[2],
                    "item_id": row[3],
                    "quantity": row[4],
                    "unit_price": row[5],
                    "total_price": row[6],
                    "status": row[7],
                    "notes": row[8],
                    "created_by": row[9],
                    "created_at": row[10],
                    "completed_at": row[11],
                    "supplier_name": row[12],
                    "item_name": row[13],
                    "sku": row[14],
                    "created_by_name": row[15]
                }
            }
        return {"success": False, "message": "Purchase order not found"}
    except Exception as e:
        return {"success": False, "message": f"Error fetching purchase order: {e}"}
    finally:
        conn.close()

def list_all_purchase_orders(status=None):
    """Get all purchase orders, optionally filtered by status"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        if status:
            query = """
                SELECT po.*, s.name as supplier_name, i.name as item_name, i.sku,
                       u.username as created_by_name
                FROM purchase_orders po
                JOIN suppliers s ON po.supplier_id = s.id
                JOIN items i ON po.item_id = i.id
                JOIN users u ON po.created_by = u.id
                WHERE po.status = ?
                ORDER BY po.created_at DESC
            """
            cur.execute(query, (status,))
        else:
            query = """
                SELECT po.*, s.name as supplier_name, i.name as item_name, i.sku,
                       u.username as created_by_name
                FROM purchase_orders po
                JOIN suppliers s ON po.supplier_id = s.id
                JOIN items i ON po.item_id = i.id
                JOIN users u ON po.created_by = u.id
                ORDER BY po.created_at DESC
            """
            cur.execute(query)
        
        rows = cur.fetchall()
        orders = []
        for row in rows:
            orders.append({
                "id": row[0],
                "order_number": row[1],
                "supplier_id": row[2],
                "item_id": row[3],
                "quantity": row[4],
                "unit_price": row[5],
                "total_price": row[6],
                "status": row[7],
                "notes": row[8],
                "created_by": row[9],
                "created_at": row[10],
                "completed_at": row[11],
                "supplier_name": row[12],
                "item_name": row[13],
                "sku": row[14],
                "created_by_name": row[15]
            })
        return {"success": True, "orders": orders}
    except Exception as e:
        return {"success": False, "message": f"Error listing purchase orders: {e}"}
    finally:
        conn.close()

def update_purchase_order_status(order_id, status, completed_at=None):
    """Update purchase order status"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        if status not in ('PENDING', 'COMPLETED', 'CANCELLED'):
            return {"success": False, "message": "Invalid status"}
        
        if status == 'COMPLETED' and not completed_at:
            completed_at = datetime.now().isoformat()
        
        cur.execute("""
            UPDATE purchase_orders 
            SET status = ?, completed_at = ?
            WHERE id = ?
        """, (status, completed_at, order_id))
        conn.commit()
        
        if cur.rowcount == 0:
            return {"success": False, "message": "Purchase order not found"}
        
        return {"success": True, "message": f"Purchase order status updated to {status}"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error updating purchase order: {e}"}
    finally:
        conn.close()

def delete_purchase_order(order_id):
    """Delete a purchase order (only if PENDING)"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Check status first
        cur.execute("SELECT status FROM purchase_orders WHERE id = ?", (order_id,))
        row = cur.fetchone()
        if not row:
            return {"success": False, "message": "Purchase order not found"}
        
        if row[0] != 'PENDING':
            return {"success": False, "message": "Cannot delete non-pending purchase order"}
        
        cur.execute("DELETE FROM purchase_orders WHERE id = ?", (order_id,))
        conn.commit()
        return {"success": True, "message": "Purchase order deleted successfully"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error deleting purchase order: {e}"}
    finally:
        conn.close()
