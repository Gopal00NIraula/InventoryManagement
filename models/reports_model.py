"""
Reports Model for generating analytics and insights
"""
from database.db_connection import get_connection
from datetime import datetime, timedelta


def get_inventory_summary():
    """
    Get summary statistics for inventory
    
    Returns:
        dict: Summary with total items, total quantity, total value, low stock count, out of stock count
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # Total items
    cur.execute("SELECT COUNT(*) FROM items")
    total_items = cur.fetchone()[0]
    
    # Total quantity across all items
    cur.execute("SELECT SUM(quantity) FROM items")
    total_quantity = cur.fetchone()[0] or 0
    
    # Total inventory value (quantity * price)
    cur.execute("SELECT SUM(quantity * price) FROM items")
    total_value = cur.fetchone()[0] or 0.0
    
    # Out of stock items
    cur.execute("SELECT COUNT(*) FROM items WHERE quantity = 0")
    out_of_stock = cur.fetchone()[0]
    
    # Low stock items (quantity <= min_stock_level or <= 10 if not set)
    cur.execute("SELECT COUNT(*) FROM items WHERE quantity > 0 AND quantity <= COALESCE(min_stock_level, 10)")
    low_stock = cur.fetchone()[0]
    
    # Average price
    cur.execute("SELECT AVG(price) FROM items WHERE price > 0")
    avg_price = cur.fetchone()[0] or 0.0
    
    conn.close()
    
    return {
        'total_items': total_items,
        'total_quantity': total_quantity,
        'total_value': round(total_value, 2),
        'out_of_stock_count': out_of_stock,
        'low_stock_count': low_stock,
        'average_price': round(avg_price, 2)
    }


def get_sales_report(start_date=None, end_date=None):
    """
    Get sales report for specified date range
    
    Args:
        start_date (str, optional): Start date in ISO format
        end_date (str, optional): End date in ISO format
    
    Returns:
        dict: Sales statistics and details
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # Build query with date filters
    query = """
        SELECT 
            COUNT(*) as total_orders,
            SUM(quantity) as total_quantity_sold,
            SUM(quantity * unit_price) as total_revenue,
            AVG(quantity * unit_price) as avg_order_value
        FROM sales_orders
        WHERE status = 'COMPLETED'
    """
    params = []
    
    if start_date:
        query += " AND order_date >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND order_date <= ?"
        params.append(end_date)
    
    cur.execute(query, params)
    row = cur.fetchone()
    
    total_orders = row[0] or 0
    total_quantity = row[1] or 0
    total_revenue = row[2] or 0.0
    avg_order_value = row[3] or 0.0
    
    # Top selling items
    top_items_query = """
        SELECT 
            i.name,
            i.sku,
            SUM(so.quantity) as total_sold,
            SUM(so.quantity * so.unit_price) as revenue
        FROM sales_orders so
        JOIN items i ON so.item_id = i.id
        WHERE so.status = 'COMPLETED'
    """
    top_params = []
    
    if start_date:
        top_items_query += " AND so.order_date >= ?"
        top_params.append(start_date)
    
    if end_date:
        top_items_query += " AND so.order_date <= ?"
        top_params.append(end_date)
    
    top_items_query += """
        GROUP BY i.id, i.name, i.sku
        ORDER BY total_sold DESC
        LIMIT 10
    """
    
    cur.execute(top_items_query, top_params)
    top_items = [
        {
            'name': row[0],
            'sku': row[1],
            'total_sold': row[2],
            'revenue': round(row[3], 2)
        }
        for row in cur.fetchall()
    ]
    
    # Sales by customer
    customer_query = """
        SELECT 
            c.name,
            COUNT(so.id) as order_count,
            SUM(so.quantity * so.unit_price) as total_spent
        FROM sales_orders so
        JOIN customers c ON so.customer_id = c.id
        WHERE so.status = 'COMPLETED'
    """
    customer_params = []
    
    if start_date:
        customer_query += " AND so.order_date >= ?"
        customer_params.append(start_date)
    
    if end_date:
        customer_query += " AND so.order_date <= ?"
        customer_params.append(end_date)
    
    customer_query += """
        GROUP BY c.id, c.name
        ORDER BY total_spent DESC
        LIMIT 10
    """
    
    cur.execute(customer_query, customer_params)
    top_customers = [
        {
            'name': row[0],
            'order_count': row[1],
            'total_spent': round(row[2], 2)
        }
        for row in cur.fetchall()
    ]
    
    conn.close()
    
    return {
        'total_orders': total_orders,
        'total_quantity_sold': total_quantity,
        'total_revenue': round(total_revenue, 2),
        'average_order_value': round(avg_order_value, 2),
        'top_selling_items': top_items,
        'top_customers': top_customers
    }


def get_purchase_report(start_date=None, end_date=None):
    """
    Get purchase report for specified date range
    
    Args:
        start_date (str, optional): Start date in ISO format
        end_date (str, optional): End date in ISO format
    
    Returns:
        dict: Purchase statistics and details
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # Build query with date filters
    query = """
        SELECT 
            COUNT(*) as total_orders,
            SUM(quantity) as total_quantity_purchased,
            SUM(quantity * unit_price) as total_cost,
            AVG(quantity * unit_price) as avg_order_cost
        FROM purchase_orders
        WHERE status = 'COMPLETED'
    """
    params = []
    
    if start_date:
        query += " AND order_date >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND order_date <= ?"
        params.append(end_date)
    
    cur.execute(query, params)
    row = cur.fetchone()
    
    total_orders = row[0] or 0
    total_quantity = row[1] or 0
    total_cost = row[2] or 0.0
    avg_order_cost = row[3] or 0.0
    
    # Most purchased items
    top_items_query = """
        SELECT 
            i.name,
            i.sku,
            SUM(po.quantity) as total_purchased,
            SUM(po.quantity * po.unit_price) as total_cost
        FROM purchase_orders po
        JOIN items i ON po.item_id = i.id
        WHERE po.status = 'COMPLETED'
    """
    top_params = []
    
    if start_date:
        top_items_query += " AND po.order_date >= ?"
        top_params.append(start_date)
    
    if end_date:
        top_items_query += " AND po.order_date <= ?"
        top_params.append(end_date)
    
    top_items_query += """
        GROUP BY i.id, i.name, i.sku
        ORDER BY total_purchased DESC
        LIMIT 10
    """
    
    cur.execute(top_items_query, top_params)
    top_items = [
        {
            'name': row[0],
            'sku': row[1],
            'total_purchased': row[2],
            'total_cost': round(row[3], 2)
        }
        for row in cur.fetchall()
    ]
    
    # Purchases by supplier
    supplier_query = """
        SELECT 
            s.name,
            COUNT(po.id) as order_count,
            SUM(po.quantity * po.unit_price) as total_cost
        FROM purchase_orders po
        JOIN suppliers s ON po.supplier_id = s.id
        WHERE po.status = 'COMPLETED'
    """
    supplier_params = []
    
    if start_date:
        supplier_query += " AND po.order_date >= ?"
        supplier_params.append(start_date)
    
    if end_date:
        supplier_query += " AND po.order_date <= ?"
        supplier_params.append(end_date)
    
    supplier_query += """
        GROUP BY s.id, s.name
        ORDER BY total_cost DESC
        LIMIT 10
    """
    
    cur.execute(supplier_query, supplier_params)
    top_suppliers = [
        {
            'name': row[0],
            'order_count': row[1],
            'total_cost': round(row[2], 2)
        }
        for row in cur.fetchall()
    ]
    
    conn.close()
    
    return {
        'total_orders': total_orders,
        'total_quantity_purchased': total_quantity,
        'total_cost': round(total_cost, 2),
        'average_order_cost': round(avg_order_cost, 2),
        'most_purchased_items': top_items,
        'top_suppliers': top_suppliers
    }


def get_stock_movement_report(start_date=None, end_date=None):
    """
    Get stock movement report showing items with most activity
    
    Args:
        start_date (str, optional): Start date in ISO format
        end_date (str, optional): End date in ISO format
    
    Returns:
        list: Items with their stock movements
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # Get items with purchase and sales activity
    query = """
        SELECT 
            i.id,
            i.name,
            i.sku,
            i.quantity as current_stock,
            COALESCE(purchases.total_in, 0) as total_purchased,
            COALESCE(sales.total_out, 0) as total_sold,
            COALESCE(purchases.total_in, 0) - COALESCE(sales.total_out, 0) as net_change
        FROM items i
        LEFT JOIN (
            SELECT item_id, SUM(quantity) as total_in
            FROM purchase_orders
            WHERE status = 'COMPLETED'
    """
    
    purchase_conditions = []
    if start_date:
        purchase_conditions.append(f" AND order_date >= '{start_date}'")
    if end_date:
        purchase_conditions.append(f" AND order_date <= '{end_date}'")
    
    query += ''.join(purchase_conditions)
    query += """
            GROUP BY item_id
        ) purchases ON i.id = purchases.item_id
        LEFT JOIN (
            SELECT item_id, SUM(quantity) as total_out
            FROM sales_orders
            WHERE status = 'COMPLETED'
    """
    
    sales_conditions = []
    if start_date:
        sales_conditions.append(f" AND order_date >= '{start_date}'")
    if end_date:
        sales_conditions.append(f" AND order_date <= '{end_date}'")
    
    query += ''.join(sales_conditions)
    query += """
            GROUP BY item_id
        ) sales ON i.id = sales.item_id
        WHERE COALESCE(purchases.total_in, 0) > 0 OR COALESCE(sales.total_out, 0) > 0
        ORDER BY (COALESCE(purchases.total_in, 0) + COALESCE(sales.total_out, 0)) DESC
        LIMIT 50
    """
    
    cur.execute(query)
    
    movements = [
        {
            'id': row[0],
            'name': row[1],
            'sku': row[2],
            'current_stock': row[3],
            'total_purchased': row[4],
            'total_sold': row[5],
            'net_change': row[6]
        }
        for row in cur.fetchall()
    ]
    
    conn.close()
    return movements


def get_low_stock_report():
    """
    Get report of items with low or zero stock
    
    Returns:
        dict: Items categorized by stock status
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # Out of stock items
    cur.execute("""
        SELECT id, name, sku, quantity, price, COALESCE(min_stock_level, 10) as min_level
        FROM items
        WHERE quantity = 0
        ORDER BY name
    """)
    
    out_of_stock = [
        {
            'id': row[0],
            'name': row[1],
            'sku': row[2],
            'quantity': row[3],
            'price': row[4],
            'min_stock_level': row[5]
        }
        for row in cur.fetchall()
    ]
    
    # Low stock items (quantity > 0 but <= min_stock_level)
    cur.execute("""
        SELECT id, name, sku, quantity, price, COALESCE(min_stock_level, 10) as min_level
        FROM items
        WHERE quantity > 0 AND quantity <= COALESCE(min_stock_level, 10)
        ORDER BY quantity ASC, name
    """)
    
    low_stock = [
        {
            'id': row[0],
            'name': row[1],
            'sku': row[2],
            'quantity': row[3],
            'price': row[4],
            'min_stock_level': row[5]
        }
        for row in cur.fetchall()
    ]
    
    # Items needing reorder (quantity <= reorder_point)
    cur.execute("""
        SELECT id, name, sku, quantity, price, COALESCE(reorder_point, 20) as reorder_pt
        FROM items
        WHERE quantity > COALESCE(min_stock_level, 10) 
        AND quantity <= COALESCE(reorder_point, 20)
        ORDER BY quantity ASC, name
    """)
    
    reorder_needed = [
        {
            'id': row[0],
            'name': row[1],
            'sku': row[2],
            'quantity': row[3],
            'price': row[4],
            'reorder_point': row[5]
        }
        for row in cur.fetchall()
    ]
    
    conn.close()
    
    return {
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'reorder_needed': reorder_needed,
        'total_critical': len(out_of_stock) + len(low_stock)
    }


def get_profit_analysis(start_date=None, end_date=None):
    """
    Calculate profit/loss by comparing purchase costs and sales revenue
    
    Args:
        start_date (str, optional): Start date in ISO format
        end_date (str, optional): End date in ISO format
    
    Returns:
        dict: Profit analysis metrics
    """
    sales_report = get_sales_report(start_date, end_date)
    purchase_report = get_purchase_report(start_date, end_date)
    
    total_revenue = sales_report['total_revenue']
    total_cost = purchase_report['total_cost']
    gross_profit = total_revenue - total_cost
    profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return {
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'gross_profit': round(gross_profit, 2),
        'profit_margin_percent': round(profit_margin, 2),
        'total_sales_orders': sales_report['total_orders'],
        'total_purchase_orders': purchase_report['total_orders']
    }
