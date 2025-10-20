from database.db_connection import get_connection

def add_item(name, sku, category, quantity, price, threshold=5):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO inventory (item_name, sku, category, quantity, price, threshold)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, sku, category, quantity, price, threshold))
    conn.commit()
    conn.close()

def get_all_items():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, item_name, sku, category, quantity, price FROM inventory")
    rows = cur.fetchall()
    conn.close()
    return rows

def search_items(query):
    conn = get_connection()
    cur = conn.cursor()
    q = f"%{query.lower()}%"
    cur.execute("""
        SELECT id, item_name, sku, category, quantity, price
        FROM inventory
        WHERE LOWER(item_name) LIKE ? OR LOWER(sku) LIKE ? OR LOWER(category) LIKE ?
    """, (q, q, q))
    rows = cur.fetchall()
    conn.close()
    return rows

def update_item(item_id, name, category, quantity, price):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE inventory
        SET item_name = ?, category = ?, quantity = ?, price = ?
        WHERE id = ?
    """, (name, category, quantity, price, item_id))
    conn.commit()
    conn.close()


def delete_item(item_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
