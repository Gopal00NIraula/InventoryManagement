import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.audit_log_model import log_action, get_all_logs, get_user_logs
from database.db_setup import setup_database
from database.db_connection import get_connection


class TestAuditLogModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test database once for all tests"""
        setup_database()
    
    def setUp(self):
        """Clear audit logs before each test"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM audit_logs WHERE action LIKE 'TEST_%'")
            conn.commit()
        finally:
            conn.close()
    
    def test_log_action(self):
        """Test logging an action"""
        result = log_action(
            user_id=1,
            username="testuser",
            action="TEST_CREATE",
            resource_type="items",
            resource_id=123,
            details="Created test item"
        )
        self.assertTrue(result)
    
    def test_get_audit_logs(self):
        """Test retrieving audit logs"""
        log_action(1, "testuser", "TEST_UPDATE", "items", 456, "Updated item")
        log_action(2, "testuser2", "TEST_DELETE", "customers", 789, "Deleted customer")
        
        logs = get_all_logs(limit=10)
        test_logs = [log for log in logs if log.get("action", "").startswith("TEST_")]
        self.assertGreaterEqual(len(test_logs), 2)
    
    def test_get_audit_logs_by_user(self):
        """Test retrieving audit logs for specific user"""
        log_action(100, "testuser100", "TEST_USER_ACTION", "suppliers", 111, "User specific action")
        
        logs = get_user_logs(100, limit=10)
        self.assertGreaterEqual(len(logs), 1)


if __name__ == '__main__':
    unittest.main()
