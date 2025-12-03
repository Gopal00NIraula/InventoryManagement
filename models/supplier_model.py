from database.db_connection import get_connection

def create_supplier(name, contact_person=None, email=None, phone=None, address=None):
    """Create a new supplier"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO suppliers (name, contact_person, email, phone, address)
            VALUES (?, ?, ?, ?, ?)
        """, (name, contact_person, email, phone, address))
        conn.commit()
        supplier_id = cur.lastrowid
        return {"success": True, "id": supplier_id, "message": "Supplier created successfully"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error creating supplier: {e}"}
    finally:
        conn.close()

def get_supplier(supplier_id):
    """Get supplier by ID"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        row = cur.fetchone()
        if row:
            return {
                "success": True,
                "supplier": {
                    "id": row[0],
                    "name": row[1],
                    "contact_person": row[2],
                    "email": row[3],
                    "phone": row[4],
                    "address": row[5],
                    "created_at": row[6]
                }
            }
        return {"success": False, "message": "Supplier not found"}
    except Exception as e:
        return {"success": False, "message": f"Error fetching supplier: {e}"}
    finally:
        conn.close()

def list_all_suppliers():
    """Get all suppliers"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM suppliers ORDER BY name")
        rows = cur.fetchall()
        suppliers = []
        for row in rows:
            suppliers.append({
                "id": row[0],
                "name": row[1],
                "contact_person": row[2],
                "email": row[3],
                "phone": row[4],
                "address": row[5],
                "created_at": row[6]
            })
        return {"success": True, "suppliers": suppliers}
    except Exception as e:
        return {"success": False, "message": f"Error listing suppliers: {e}"}
    finally:
        conn.close()

def update_supplier(supplier_id, name=None, contact_person=None, email=None, phone=None, address=None):
    """Update supplier information"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Build dynamic update query
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if contact_person is not None:
            updates.append("contact_person = ?")
            params.append(contact_person)
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        if phone is not None:
            updates.append("phone = ?")
            params.append(phone)
        if address is not None:
            updates.append("address = ?")
            params.append(address)
        
        if not updates:
            return {"success": False, "message": "No fields to update"}
        
        params.append(supplier_id)
        query = f"UPDATE suppliers SET {', '.join(updates)} WHERE id = ?"
        
        cur.execute(query, params)
        conn.commit()
        
        if cur.rowcount == 0:
            return {"success": False, "message": "Supplier not found"}
        
        return {"success": True, "message": "Supplier updated successfully"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error updating supplier: {e}"}
    finally:
        conn.close()

def delete_supplier(supplier_id):
    """Delete a supplier"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
        conn.commit()
        
        if cur.rowcount == 0:
            return {"success": False, "message": "Supplier not found"}
        
        return {"success": True, "message": "Supplier deleted successfully"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error deleting supplier: {e}"}
    finally:
        conn.close()

def search_suppliers(query):
    """Search suppliers by name, contact person, or email"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        search_pattern = f"%{query}%"
        cur.execute("""
            SELECT * FROM suppliers 
            WHERE name LIKE ? OR contact_person LIKE ? OR email LIKE ?
            ORDER BY name
        """, (search_pattern, search_pattern, search_pattern))
        
        rows = cur.fetchall()
        suppliers = []
        for row in rows:
            suppliers.append({
                "id": row[0],
                "name": row[1],
                "contact_person": row[2],
                "email": row[3],
                "phone": row[4],
                "address": row[5],
                "created_at": row[6]
            })
        return {"success": True, "suppliers": suppliers}
    except Exception as e:
        return {"success": False, "message": f"Error searching suppliers: {e}"}
    finally:
        conn.close()
