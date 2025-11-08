# models/inventory_model.py
from database.db_connection import get_connection

def add_item(payload: dict) -> int:
    conn = get_connection(); cur = conn.cursor()
    cur.execute(
        "INSERT INTO items (name, sku, quantity, location) VALUES (?,?,?,?)",
        (payload.get("name"), payload.get("sku"), int(payload.get("quantity", 0)), payload.get("location"))
    )
    conn.commit()
    iid = cur.lastrowid
    conn.close()
    return iid

def update_item(item_id: int, payload: dict) -> bool:
    fields, vals = [], []
    for k in ("name", "sku", "quantity", "location"):
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
    cur.execute("SELECT id, name, sku, quantity, location FROM items ORDER BY id DESC LIMIT ?", (limit,))
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
        SELECT id, name, sku, quantity, location
        FROM items
        WHERE name LIKE ? OR sku LIKE ? OR COALESCE(location,'') LIKE ?
        ORDER BY id DESC LIMIT ?
    """, (like, like, like, limit))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
