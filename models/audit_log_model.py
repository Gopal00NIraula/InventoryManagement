"""
Audit Log Model for tracking user actions and system events
"""
from datetime import datetime
from database.db_connection import get_connection


def log_action(user_id, username, action, resource_type, resource_id=None, details=None, ip_address=None):
    """
    Log a user action to the audit_logs table
    
    Args:
        user_id (int): ID of the user performing the action
        username (str): Username of the user
        action (str): Action performed (CREATE, UPDATE, DELETE, VIEW, LOGIN, LOGOUT, etc.)
        resource_type (str): Type of resource (ITEM, SUPPLIER, CUSTOMER, PURCHASE_ORDER, SALES_ORDER, USER, etc.)
        resource_id (int, optional): ID of the specific resource affected
        details (str, optional): Additional details about the action in JSON format or plain text
        ip_address (str, optional): IP address of the user
    
    Returns:
        int: ID of the created audit log entry
    """
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO audit_logs (user_id, username, action, resource_type, resource_id, details, ip_address, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, username, action, resource_type, resource_id, details, ip_address, datetime.now().isoformat()))
    
    conn.commit()
    return cur.lastrowid


def get_all_logs(limit=100, offset=0):
    """
    Get all audit logs with pagination
    
    Args:
        limit (int): Maximum number of logs to return
        offset (int): Number of logs to skip
    
    Returns:
        list: List of audit log dictionaries
    """
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, user_id, username, action, resource_type, resource_id, details, ip_address, timestamp
        FROM audit_logs
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    
    rows = cur.fetchall()
    return [
        {
            'id': row[0],
            'user_id': row[1],
            'username': row[2],
            'action': row[3],
            'resource_type': row[4],
            'resource_id': row[5],
            'details': row[6],
            'ip_address': row[7],
            'timestamp': row[8]
        }
        for row in rows
    ]


def get_user_logs(user_id, limit=100):
    """
    Get audit logs for a specific user
    
    Args:
        user_id (int): ID of the user
        limit (int): Maximum number of logs to return
    
    Returns:
        list: List of audit log dictionaries
    """
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, user_id, username, action, resource_type, resource_id, details, ip_address, timestamp
        FROM audit_logs
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (user_id, limit))
    
    rows = cur.fetchall()
    return [
        {
            'id': row[0],
            'user_id': row[1],
            'username': row[2],
            'action': row[3],
            'resource_type': row[4],
            'resource_id': row[5],
            'details': row[6],
            'ip_address': row[7],
            'timestamp': row[8]
        }
        for row in rows
    ]


def get_resource_logs(resource_type, resource_id, limit=50):
    """
    Get audit logs for a specific resource
    
    Args:
        resource_type (str): Type of resource (ITEM, SUPPLIER, etc.)
        resource_id (int): ID of the resource
        limit (int): Maximum number of logs to return
    
    Returns:
        list: List of audit log dictionaries
    """
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, user_id, username, action, resource_type, resource_id, details, ip_address, timestamp
        FROM audit_logs
        WHERE resource_type = ? AND resource_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (resource_type, resource_id, limit))
    
    rows = cur.fetchall()
    return [
        {
            'id': row[0],
            'user_id': row[1],
            'username': row[2],
            'action': row[3],
            'resource_type': row[4],
            'resource_id': row[5],
            'details': row[6],
            'ip_address': row[7],
            'timestamp': row[8]
        }
        for row in rows
    ]


def filter_logs(user_id=None, username=None, action=None, resource_type=None, 
                start_date=None, end_date=None, limit=100, offset=0):
    """
    Filter audit logs based on multiple criteria
    
    Args:
        user_id (int, optional): Filter by user ID
        username (str, optional): Filter by username (partial match)
        action (str, optional): Filter by action type
        resource_type (str, optional): Filter by resource type
        start_date (str, optional): Filter logs after this date (ISO format)
        end_date (str, optional): Filter logs before this date (ISO format)
        limit (int): Maximum number of logs to return
        offset (int): Number of logs to skip
    
    Returns:
        list: List of audit log dictionaries matching the filters
    """
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT id, user_id, username, action, resource_type, resource_id, details, ip_address, timestamp
        FROM audit_logs
        WHERE 1=1
    """
    params = []
    
    if user_id is not None:
        query += " AND user_id = ?"
        params.append(user_id)
    
    if username:
        query += " AND username LIKE ?"
        params.append(f"%{username}%")
    
    if action:
        query += " AND action = ?"
        params.append(action)
    
    if resource_type:
        query += " AND resource_type = ?"
        params.append(resource_type)
    
    if start_date:
        query += " AND timestamp >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND timestamp <= ?"
        params.append(end_date)
    
    query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cur.execute(query, params)
    rows = cur.fetchall()
    
    return [
        {
            'id': row[0],
            'user_id': row[1],
            'username': row[2],
            'action': row[3],
            'resource_type': row[4],
            'resource_id': row[5],
            'details': row[6],
            'ip_address': row[7],
            'timestamp': row[8]
        }
        for row in rows
    ]


def get_log_count():
    """
    Get total count of audit logs
    
    Returns:
        int: Total number of audit log entries
    """
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM audit_logs")
    return cur.fetchone()[0]


def get_filtered_count(user_id=None, username=None, action=None, resource_type=None, 
                       start_date=None, end_date=None):
    """
    Get count of audit logs matching filter criteria
    
    Args:
        user_id (int, optional): Filter by user ID
        username (str, optional): Filter by username (partial match)
        action (str, optional): Filter by action type
        resource_type (str, optional): Filter by resource type
        start_date (str, optional): Filter logs after this date (ISO format)
        end_date (str, optional): Filter logs before this date (ISO format)
    
    Returns:
        int: Count of matching audit log entries
    """
    conn = get_connection()
    cur = conn.cursor()
    
    query = "SELECT COUNT(*) FROM audit_logs WHERE 1=1"
    params = []
    
    if user_id is not None:
        query += " AND user_id = ?"
        params.append(user_id)
    
    if username:
        query += " AND username LIKE ?"
        params.append(f"%{username}%")
    
    if action:
        query += " AND action = ?"
        params.append(action)
    
    if resource_type:
        query += " AND resource_type = ?"
        params.append(resource_type)
    
    if start_date:
        query += " AND timestamp >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND timestamp <= ?"
        params.append(end_date)
    
    cur.execute(query, params)
    return cur.fetchone()[0]


def delete_old_logs(days=90):
    """
    Delete audit logs older than specified number of days
    
    Args:
        days (int): Number of days to retain logs
    
    Returns:
        int: Number of deleted log entries
    """
    conn = get_connection()
    cur = conn.cursor()
    
    cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
    
    cur.execute("""
        DELETE FROM audit_logs
        WHERE timestamp < ?
    """, (cutoff_date.isoformat(),))
    
    conn.commit()
    return cur.rowcount
