import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.customer_model import create_customer, get_customer, update_customer, delete_customer, search_customers
from database.db_setup import setup_database
from database.db_connection import get_connection


class TestCustomerModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test database once for all tests"""
        setup_database()
    
    def setUp(self):
        """Clear customers table before each test"""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM customers WHERE name LIKE 'Test Customer%'")
        conn.commit()
    
    def test_create_customer(self):
        """Test creating a new customer"""
        result = create_customer(
            name="Test Customer 1",
            email="customer1@test.com",
            phone="555-1001",
            address="456 Customer Ave"
        )
        self.assertTrue(result["success"])
        self.assertGreater(result["id"], 0)
    
    def test_get_customer(self):
        """Test retrieving a customer by ID"""
        result = create_customer(
            name="Test Customer 2",
            email="customer2@test.com"
        )
        
        response = get_customer(result["id"])
        self.assertTrue(response["success"])
        customer = response["customer"]
        self.assertEqual(customer["name"], "Test Customer 2")
        self.assertEqual(customer["email"], "customer2@test.com")
    
    def test_update_customer(self):
        """Test updating customer information"""
        result = create_customer(name="Test Customer 3", phone="555-1003")
        
        update_result = update_customer(
            result["id"],
            email="updated@test.com",
            phone="555-9999"
        )
        self.assertTrue(update_result["success"])
        
        response = get_customer(result["id"])
        updated = response["customer"]
        self.assertEqual(updated["email"], "updated@test.com")
        self.assertEqual(updated["phone"], "555-9999")
    
    def test_delete_customer(self):
        """Test deleting a customer"""
        result = create_customer(name="Test Customer 4")
        
        delete_result = delete_customer(result["id"])
        self.assertTrue(delete_result["success"])
        
        deleted = get_customer(result["id"])
        self.assertFalse(deleted.get("success", False) if deleted else False)
    
    def test_search_customers(self):
        """Test searching customers"""
        create_customer(name="Test Customer Alpha", email="alpha@test.com")
        create_customer(name="Test Customer Beta", email="beta@test.com")
        
        response = search_customers("Alpha")
        self.assertTrue(response["success"])
        results = response["customers"]
        self.assertGreaterEqual(len(results), 1)
        self.assertTrue(any("Alpha" in c["name"] for c in results))


if __name__ == '__main__':
    unittest.main()
