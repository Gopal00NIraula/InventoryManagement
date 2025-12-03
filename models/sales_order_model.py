from database.db_connection import get_connection
from datetime import datetime

def generate_order_number(prefix="SO"):
    """Generate unique order number with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{timestamp}"

def create_sales_order(customer_id, item_id, quantity, unit_price, created_by, notes=None):
    """Create a new sales order"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        order_number = generate_order_number("SO")
        total_price = quantity * unit_price
        
        cur.execute("""
            INSERT INTO sales_orders 
            (order_number, customer_id, item_id, quantity, unit_price, total_price, notes, created_by, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
        """, (order_number, customer_id, item_id, quantity, unit_price, total_price, notes, created_by))
        conn.commit()
        
        order_id = cur.lastrowid
        return {"success": True, "id": order_id, "order_number": order_number, "message": "Sales order created successfully"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error creating sales order: {e}"}
    finally:
        conn.close()

def get_sales_order(order_id):
    """Get sales order by ID with related data"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT so.*, c.name as customer_name, i.name as item_name, i.sku,
                   u.username as created_by_name
            FROM sales_orders so
            JOIN customers c ON so.customer_id = c.id
            JOIN items i ON so.item_id = i.id
            JOIN users u ON so.created_by = u.id
            WHERE so.id = ?
        """, (order_id,))
        row = cur.fetchone()
        
        if row:
            return {
                "success": True,
                "order": {
                    "id": row[0],
                    "order_number": row[1],
                    "customer_id": row[2],
                    "item_id": row[3],
                    "quantity": row[4],
                    "unit_price": row[5],
                    "total_price": row[6],
                    "status": row[7],
                    "notes": row[8],
                    "created_by": row[9],
                    "created_at": row[10],
                    "completed_at": row[11],
                    "customer_name": row[12],
                    "item_name": row[13],
                    "sku": row[14],
                    "created_by_name": row[15]
                }
            }
        return {"success": False, "message": "Sales order not found"}
    except Exception as e:
        return {"success": False, "message": f"Error fetching sales order: {e}"}
    finally:
        conn.close()

def list_all_sales_orders(status=None):
    """Get all sales orders, optionally filtered by status"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        if status:
            query = """
                SELECT so.*, c.name as customer_name, i.name as item_name, i.sku,
                       u.username as created_by_name
                FROM sales_orders so
                JOIN customers c ON so.customer_id = c.id
                JOIN items i ON so.item_id = i.id
                JOIN users u ON so.created_by = u.id
                WHERE so.status = ?
                ORDER BY so.created_at DESC
            """
            cur.execute(query, (status,))
        else:
            query = """
                SELECT so.*, c.name as customer_name, i.name as item_name, i.sku,
                       u.username as created_by_name
                FROM sales_orders so
                JOIN customers c ON so.customer_id = c.id
                JOIN items i ON so.item_id = i.id
                JOIN users u ON so.created_by = u.id
                ORDER BY so.created_at DESC
            """
            cur.execute(query)
        
        rows = cur.fetchall()
        orders = []
        for row in rows:
            orders.append({
                "id": row[0],
                "order_number": row[1],
                "customer_id": row[2],
                "item_id": row[3],
                "quantity": row[4],
                "unit_price": row[5],
                "total_price": row[6],
                "status": row[7],
                "notes": row[8],
                "created_by": row[9],
                "created_at": row[10],
                "completed_at": row[11],
                "customer_name": row[12],
                "item_name": row[13],
                "sku": row[14],
                "created_by_name": row[15]
            })
        return {"success": True, "orders": orders}
    except Exception as e:
        return {"success": False, "message": f"Error listing sales orders: {e}"}
    finally:
        conn.close()

def update_sales_order_status(order_id, status, completed_at=None):
    """Update sales order status"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        if status not in ('PENDING', 'COMPLETED', 'CANCELLED'):
            return {"success": False, "message": "Invalid status"}
        
        if status == 'COMPLETED' and not completed_at:
            completed_at = datetime.now().isoformat()
        
        cur.execute("""
            UPDATE sales_orders 
            SET status = ?, completed_at = ?
            WHERE id = ?
        """, (status, completed_at, order_id))
        conn.commit()
        
        if cur.rowcount == 0:
            return {"success": False, "message": "Sales order not found"}
        
        return {"success": True, "message": f"Sales order status updated to {status}"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error updating sales order: {e}"}
    finally:
        conn.close()

def delete_sales_order(order_id):
    """Delete a sales order (only if PENDING)"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Check status first
        cur.execute("SELECT status FROM sales_orders WHERE id = ?", (order_id,))
        row = cur.fetchone()
        if not row:
            return {"success": False, "message": "Sales order not found"}
        
        if row[0] != 'PENDING':
            return {"success": False, "message": "Cannot delete non-pending sales order"}
        
        cur.execute("DELETE FROM sales_orders WHERE id = ?", (order_id,))
        conn.commit()
        return {"success": True, "message": "Sales order deleted successfully"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error deleting sales order: {e}"}
    finally:
        conn.close()
