import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controllers.login_controller import login, create_admin_account
from database.db_setup import setup_database
from database.db_connection import get_connection


class TestLoginController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test database once for all tests"""
        setup_database()
    
    def setUp(self):
        """Clear test users before each test"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM users WHERE email LIKE '%@testlogin.com'")
            conn.commit()
        finally:
            conn.close()
    
    def test_login_success(self):
        """Test successful login"""
        user_result = create_admin_account({
            "first_name": "Test",
            "last_name": "Admin",
            "password": "testpass123",
            "email": "admin@testlogin.com"
        })
        
        username = user_result["username"]
        success, user = login(username, "testpass123")
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user.get("username"), username)
    
    def test_login_failure(self):
        """Test failed login with wrong password"""
        user_result = create_admin_account({
            "first_name": "Test",
            "last_name": "User",
            "password": "correctpass",
            "email": "user@testlogin.com"
        })
        
        success, user = login(user_result["username"], "wrongpass")
        self.assertFalse(success)
        self.assertIsNone(user)
    
    def test_create_admin_account(self):
        """Test creating admin account"""
        result = create_admin_account({
            "username": "newadmin",
            "password": "adminpass",
            "email": "newadmin@testlogin.com"
        })
        
        self.assertIsNotNone(result)
        self.assertIn("id", result)


if __name__ == '__main__':
    unittest.main()
