import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.supplier_model import create_supplier, get_supplier, update_supplier, delete_supplier, search_suppliers
from database.db_setup import setup_database
from database.db_connection import get_connection


class TestSupplierModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test database once for all tests"""
        setup_database()
    
    def setUp(self):
        """Clear suppliers table before each test"""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM suppliers WHERE name LIKE 'Test Supplier%'")
        conn.commit()
    
    def test_create_supplier(self):
        """Test creating a new supplier"""
        result = create_supplier(
            name="Test Supplier 1",
            contact_person="John Doe",
            email="john@testsupplier.com",
            phone="555-0001",
            address="123 Test St"
        )
        self.assertTrue(result["success"])
        self.assertGreater(result["id"], 0)
    
    def test_get_supplier(self):
        """Test retrieving a supplier by ID"""
        result = create_supplier(
            name="Test Supplier 2",
            email="info@testsupplier2.com"
        )
        
        response = get_supplier(result["id"])
        self.assertTrue(response["success"])
        supplier = response["supplier"]
        self.assertEqual(supplier["name"], "Test Supplier 2")
        self.assertEqual(supplier["email"], "info@testsupplier2.com")
    
    def test_update_supplier(self):
        """Test updating supplier information"""
        result = create_supplier(name="Test Supplier 3", phone="555-0003")
        
        update_result = update_supplier(
            result["id"],
            contact_person="Jane Smith",
            phone="555-9999"
        )
        self.assertTrue(update_result["success"])
        
        response = get_supplier(result["id"])
        updated = response["supplier"]
        self.assertEqual(updated["contact_person"], "Jane Smith")
        self.assertEqual(updated["phone"], "555-9999")
    
    def test_delete_supplier(self):
        """Test deleting a supplier"""
        result = create_supplier(name="Test Supplier 4")
        
        delete_result = delete_supplier(result["id"])
        self.assertTrue(delete_result["success"])
        
        deleted = get_supplier(result["id"])
        self.assertFalse(deleted.get("success", False) if deleted else False)
    
    def test_search_suppliers(self):
        """Test searching suppliers"""
        create_supplier(name="Test Supplier ABC", email="abc@test.com")
        create_supplier(name="Test Supplier XYZ", email="xyz@test.com")
        
        response = search_suppliers("ABC")
        self.assertTrue(response["success"])
        results = response["suppliers"]
        self.assertGreaterEqual(len(results), 1)
        self.assertTrue(any("ABC" in s["name"] for s in results))


if __name__ == '__main__':
    unittest.main()
