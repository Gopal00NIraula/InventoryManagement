import unittest
import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.user_model import create_user, authenticate
from database.db_setup import setup_database
from database.db_connection import get_connection


class TestUserModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test database once for all tests"""
        setup_database()
    
    def setUp(self):
        """Clear users table before each test"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM users WHERE email LIKE '%@testuser.com'")
            conn.commit()
        finally:
            conn.close()
        time.sleep(0.1)
    
    def test_create_user(self):
        """Test creating a new user"""
        result = create_user(password="password123", role="ADMIN", first_name="Test", last_name="User1", email="test1@testuser.com")
        self.assertIsNotNone(result)
        self.assertIn("id", result)
        self.assertIn("username", result)
    
    def test_authenticate_valid_credentials(self):
        """Test authentication with valid credentials"""
        result = create_user(password="password123", role="ADMIN", first_name="Auth", last_name="Test", email="auth@testuser.com")
        username = result["username"]
        
        auth_result = authenticate(username, "password123")
        self.assertIsNotNone(auth_result)
        self.assertEqual(auth_result["username"], username)
        self.assertEqual(auth_result["role"], "ADMIN")
    
    def test_authenticate_invalid_password(self):
        """Test authentication with invalid password"""
        result = create_user(password="password123", role="ADMIN", first_name="Invalid", last_name="Test", email="invalid@testuser.com")
        username = result["username"]
        
        auth_result = authenticate(username, "wrongpassword")
        self.assertIsNone(auth_result)
    
    def test_authenticate_nonexistent_user(self):
        """Test authentication with non-existent username"""
        auth_result = authenticate("nonexistent_user_xyz", "password123")
        self.assertIsNone(auth_result)


if __name__ == '__main__':
    unittest.main()
