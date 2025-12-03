import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.inventory_model import add_item, get_items, update_item, delete_item, search_items
from database.db_setup import setup_database
from database.db_connection import get_connection


class TestInventoryModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test database once for all tests"""
        setup_database()
    
    def setUp(self):
        """Clear items table before each test"""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM items WHERE sku LIKE 'TEST-%'")
        conn.commit()
    
    def test_add_item(self):
        """Test adding a new inventory item"""
        payload = {
            "sku": "TEST-001",
            "name": "Test Product",
            "quantity": 100,
            "price": 29.99,
            "min_stock_level": 10,
            "reorder_point": 20
        }
        item_id = add_item(payload)
        self.assertIsNotNone(item_id)
        self.assertGreater(item_id, 0)
    
    def test_add_item_with_barcode(self):
        """Test adding item with barcode"""
        payload = {
            "sku": "TEST-002",
            "name": "Test Product 2",
            "quantity": 50,
            "price": 19.99,
            "barcode": "1234567890123"
        }
        item_id = add_item(payload)
        self.assertIsNotNone(item_id)
        
        items = search_items("TEST-002")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["barcode"], "1234567890123")
    
    def test_get_items(self):
        """Test retrieving all items"""
        add_item({"sku": "TEST-003", "name": "Item 1", "quantity": 10, "price": 9.99})
        add_item({"sku": "TEST-004", "name": "Item 2", "quantity": 20, "price": 19.99})
        
        items = get_items(limit=100)
        test_items = [item for item in items if item["sku"].startswith("TEST-")]
        self.assertGreaterEqual(len(test_items), 2)
    
    def test_update_item(self):
        """Test updating an item"""
        payload = {"sku": "TEST-005", "name": "Original Name", "quantity": 100, "price": 29.99}
        item_id = add_item(payload)
        
        update_payload = {"name": "Updated Name", "quantity": 150, "price": 34.99}
        success = update_item(item_id, update_payload)
        self.assertTrue(success)
        
        items = search_items("TEST-005")
        self.assertEqual(items[0]["name"], "Updated Name")
        self.assertEqual(items[0]["quantity"], 150)
        self.assertEqual(items[0]["price"], 34.99)
    
    def test_delete_item(self):
        """Test deleting an item"""
        payload = {"sku": "TEST-006", "name": "To Delete", "quantity": 10, "price": 9.99}
        item_id = add_item(payload)
        
        success = delete_item(item_id)
        self.assertTrue(success)
        
        items = search_items("TEST-006")
        self.assertEqual(len(items), 0)
    
    def test_search_items_by_name(self):
        """Test searching items by name"""
        add_item({"sku": "TEST-007", "name": "Laptop Computer", "quantity": 5, "price": 999.99})
        add_item({"sku": "TEST-008", "name": "Desktop Computer", "quantity": 3, "price": 799.99})
        
        results = search_items("Computer")
        test_results = [item for item in results if item["sku"].startswith("TEST-")]
        self.assertGreaterEqual(len(test_results), 2)
    
    def test_search_items_by_sku(self):
        """Test searching items by SKU"""
        add_item({"sku": "TEST-009", "name": "Test Item", "quantity": 10, "price": 9.99})
        
        results = search_items("TEST-009")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["sku"], "TEST-009")


if __name__ == '__main__':
    unittest.main()
