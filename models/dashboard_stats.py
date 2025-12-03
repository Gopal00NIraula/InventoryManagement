"""
Dashboard Statistics and Metrics
"""
from database.db_connection import get_connection
from datetime import datetime, timedelta


def get_dashboard_stats():
    """
    Get comprehensive dashboard statistics
    
    Returns:
        dict: Dashboard metrics including inventory, orders, alerts
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        stats = {}
        
        # Total items count
        cur.execute("SELECT COUNT(*) FROM items")
        stats['total_items'] = cur.fetchone()[0]
        
        # Total inventory value
        cur.execute("SELECT SUM(quantity * price) FROM items")
        total_value = cur.fetchone()[0]
        stats['total_inventory_value'] = total_value if total_value else 0.0
        
        # Low stock items count
        cur.execute("""
            SELECT COUNT(*) FROM items 
            WHERE quantity <= min_stock_level
        """)
        stats['low_stock_count'] = cur.fetchone()[0]
        
        # Out of stock items count
        cur.execute("SELECT COUNT(*) FROM items WHERE quantity = 0")
        stats['out_of_stock_count'] = cur.fetchone()[0]
        
        # Total suppliers
        cur.execute("SELECT COUNT(*) FROM suppliers")
        stats['total_suppliers'] = cur.fetchone()[0]
        
        # Total customers
        cur.execute("SELECT COUNT(*) FROM customers")
        stats['total_customers'] = cur.fetchone()[0]
        
        # Pending purchase orders
        cur.execute("SELECT COUNT(*) FROM purchase_orders WHERE status = 'PENDING'")
        stats['pending_purchase_orders'] = cur.fetchone()[0]
        
        # Pending sales orders
        cur.execute("SELECT COUNT(*) FROM sales_orders WHERE status = 'PENDING'")
        stats['pending_sales_orders'] = cur.fetchone()[0]
        
        # Today's activity (last 24 hours)
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        
        cur.execute("""
            SELECT COUNT(*) FROM purchase_orders 
            WHERE created_at >= ?
        """, (yesterday,))
        stats['todays_purchases'] = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(*) FROM sales_orders 
            WHERE created_at >= ?
        """, (yesterday,))
        stats['todays_sales'] = cur.fetchone()[0]
        
        # This week's activity (last 7 days)
        last_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        
        cur.execute("""
            SELECT COUNT(*) FROM purchase_orders 
            WHERE status = 'COMPLETED' AND created_at >= ?
        """, (last_week,))
        stats['week_completed_purchases'] = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(*) FROM sales_orders 
            WHERE status = 'COMPLETED' AND created_at >= ?
        """, (last_week,))
        stats['week_completed_sales'] = cur.fetchone()[0]
        
        # Active alerts count
        cur.execute("SELECT COUNT(*) FROM stock_alerts WHERE is_resolved = 0")
        stats['active_alerts'] = cur.fetchone()[0]
        
        # Average item price
        cur.execute("SELECT AVG(price) FROM items WHERE price > 0")
        avg_price = cur.fetchone()[0]
        stats['average_item_price'] = avg_price if avg_price else 0.0
        
        # Total users
        cur.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        stats['active_users'] = cur.fetchone()[0]
        
        return {"success": True, "stats": stats}
        
    except Exception as e:
        return {"success": False, "message": f"Error fetching dashboard stats: {e}"}
    finally:
        conn.close()


def get_recent_activity(limit=10):
    """
    Get recent activity from audit logs
    
    Args:
        limit (int): Number of recent activities to fetch
        
    Returns:
        dict: List of recent activities
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT action, resource_type, username, timestamp, details
            FROM audit_logs
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cur.fetchall()
        activities = []
        
        for row in rows:
            activities.append({
                "action": row[0],
                "resource_type": row[1],
                "username": row[2],
                "timestamp": row[3],
                "details": row[4]
            })
        
        return {"success": True, "activities": activities}
        
    except Exception as e:
        return {"success": False, "message": f"Error fetching recent activity: {e}"}
    finally:
        conn.close()


def get_top_items_by_value(limit=5):
    """
    Get top items by total inventory value (quantity * price)
    
    Args:
        limit (int): Number of top items to return
        
    Returns:
        dict: List of top items
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT name, sku, quantity, price, (quantity * price) as total_value
            FROM items
            WHERE quantity > 0
            ORDER BY total_value DESC
            LIMIT ?
        """, (limit,))
        
        rows = cur.fetchall()
        items = []
        
        for row in rows:
            items.append({
                "name": row[0],
                "sku": row[1],
                "quantity": row[2],
                "price": row[3],
                "total_value": row[4]
            })
        
        return {"success": True, "items": items}
        
    except Exception as e:
        return {"success": False, "message": f"Error fetching top items: {e}"}
    finally:
        conn.close()


def get_items_needing_attention():
    """
    Get items that need immediate attention (out of stock or low stock)
    
    Returns:
        dict: Categorized items needing attention
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Out of stock
        cur.execute("""
            SELECT name, sku, quantity, min_stock_level
            FROM items
            WHERE quantity = 0
            ORDER BY name
            LIMIT 5
        """)
        
        out_of_stock = []
        for row in cur.fetchall():
            out_of_stock.append({
                "name": row[0],
                "sku": row[1],
                "quantity": row[2],
                "min_stock_level": row[3]
            })
        
        # Low stock
        cur.execute("""
            SELECT name, sku, quantity, min_stock_level
            FROM items
            WHERE quantity > 0 AND quantity <= min_stock_level
            ORDER BY quantity ASC
            LIMIT 5
        """)
        
        low_stock = []
        for row in cur.fetchall():
            low_stock.append({
                "name": row[0],
                "sku": row[1],
                "quantity": row[2],
                "min_stock_level": row[3]
            })
        
        return {
            "success": True,
            "out_of_stock": out_of_stock,
            "low_stock": low_stock
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error fetching items needing attention: {e}"}
    finally:
        conn.close()
