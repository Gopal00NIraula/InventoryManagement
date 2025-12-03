from database.db_connection import get_connection

def create_customer(name, email=None, phone=None, address=None):
    """Create a new customer"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO customers (name, email, phone, address)
            VALUES (?, ?, ?, ?)
        """, (name, email, phone, address))
        conn.commit()
        customer_id = cur.lastrowid
        return {"success": True, "id": customer_id, "message": "Customer created successfully"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error creating customer: {e}"}
    finally:
        conn.close()

def get_customer(customer_id):
    """Get customer by ID"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cur.fetchone()
        if row:
            return {
                "success": True,
                "customer": {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "address": row[4],
                    "created_at": row[5]
                }
            }
        return {"success": False, "message": "Customer not found"}
    except Exception as e:
        return {"success": False, "message": f"Error fetching customer: {e}"}
    finally:
        conn.close()

def list_all_customers():
    """Get all customers"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM customers ORDER BY name")
        rows = cur.fetchall()
        customers = []
        for row in rows:
            customers.append({
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "phone": row[3],
                "address": row[4],
                "created_at": row[5]
            })
        return {"success": True, "customers": customers}
    except Exception as e:
        return {"success": False, "message": f"Error listing customers: {e}"}
    finally:
        conn.close()

def update_customer(customer_id, name=None, email=None, phone=None, address=None):
    """Update customer information"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Build dynamic update query
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
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
        
        params.append(customer_id)
        query = f"UPDATE customers SET {', '.join(updates)} WHERE id = ?"
        
        cur.execute(query, params)
        conn.commit()
        
        if cur.rowcount == 0:
            return {"success": False, "message": "Customer not found"}
        
        return {"success": True, "message": "Customer updated successfully"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error updating customer: {e}"}
    finally:
        conn.close()

def delete_customer(customer_id):
    """Delete a customer"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        conn.commit()
        
        if cur.rowcount == 0:
            return {"success": False, "message": "Customer not found"}
        
        return {"success": True, "message": "Customer deleted successfully"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error deleting customer: {e}"}
    finally:
        conn.close()

def search_customers(query):
    """Search customers by name or email"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        search_pattern = f"%{query}%"
        cur.execute("""
            SELECT * FROM customers 
            WHERE name LIKE ? OR email LIKE ?
            ORDER BY name
        """, (search_pattern, search_pattern))
        
        rows = cur.fetchall()
        customers = []
        for row in rows:
            customers.append({
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "phone": row[3],
                "address": row[4],
                "created_at": row[5]
            })
        return {"success": True, "customers": customers}
    except Exception as e:
        return {"success": False, "message": f"Error searching customers: {e}"}
    finally:
        conn.close()
