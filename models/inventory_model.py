from database.db_connection import get_connection

def add_item(payload: dict) -> int:
    conn = get_connection(); cur = conn.cursor()
    cur.execute(
        "INSERT INTO items (name, sku, quantity, price, min_stock_level, reorder_point, barcode) VALUES (?,?,?,?,?,?,?)",
        (payload.get("name"), payload.get("sku"), int(payload.get("quantity", 0)), 
         float(payload.get("price", 0.0)), int(payload.get("min_stock_level", 10)), 
         int(payload.get("reorder_point", 20)), payload.get("barcode"))
    )
    conn.commit()
    iid = cur.lastrowid
    conn.close()
    return iid

def update_item(item_id: int, payload: dict) -> bool:
    fields, vals = [], []
    for k in ("name", "sku", "quantity", "price", "min_stock_level", "reorder_point", "barcode"):
        if k in payload and payload[k] is not None:
            fields.append(f"{k}=?")
            vals.append(payload[k])
    if not fields:
        return False
    vals.append(item_id)
    conn = get_connection(); cur = conn.cursor()
    cur.execute(f"UPDATE items SET {', '.join(fields)} WHERE id = ?", vals)
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def delete_item(item_id: int) -> bool:
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

def get_items(limit: int = 200):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id, name, sku, quantity, price, min_stock_level, reorder_point, barcode FROM items ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def search_items(q: str, limit: int = 200):
    q = (q or "").strip()
    if not q:
        return get_items(limit)
    like = f"%{q}%"
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT id, name, sku, quantity, price, min_stock_level, reorder_point, barcode
        FROM items
        WHERE name LIKE ? OR sku LIKE ? OR barcode LIKE ?
        ORDER BY id DESC LIMIT ?
    """, (like, like, like, limit))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_item(item_id: int):
    """Get a single item by ID"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, sku, quantity, price, min_stock_level, reorder_point, barcode FROM items WHERE id = ?", (item_id,))
        row = cur.fetchone()
        if row:
            return {
                "success": True,
                "item": {
                    "id": row[0],
                    "name": row[1],
                    "sku": row[2],
                    "quantity": row[3],
                    "price": row[4],
                    "min_stock_level": row[5],
                    "reorder_point": row[6],
                    "barcode": row[7]
                }
            }
        return {"success": False, "message": "Item not found"}
    except Exception as e:
        return {"success": False, "message": f"Error fetching item: {e}"}
    finally:
        conn.close()

def update_item_quantity(item_id: int, new_quantity: int):
    """Update item quantity"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE items SET quantity = ? WHERE id = ?", (new_quantity, item_id))
        conn.commit()
        if cur.rowcount == 0:
            return {"success": False, "message": "Item not found"}
        return {"success": True, "message": "Quantity updated successfully"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error updating quantity: {e}"}
    finally:
        conn.close()
