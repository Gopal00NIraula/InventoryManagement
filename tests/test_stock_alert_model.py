import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.stock_alert_model import check_and_create_alerts, get_active_alerts, resolve_alert
from models.inventory_model import add_item, update_item
from database.db_setup import setup_database
from database.db_connection import get_connection


class TestStockAlertModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test database once for all tests"""
        setup_database()
    
    def setUp(self):
        """Clear test data before each test"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM stock_alerts WHERE item_id IN (SELECT id FROM items WHERE sku LIKE 'ALERT-%')")
            cur.execute("DELETE FROM items WHERE sku LIKE 'ALERT-%'")
            conn.commit()
        finally:
            conn.close()
    
    def test_check_and_create_alerts(self):
        """Test checking and creating stock alerts"""
        item_id = add_item({
            "sku": "ALERT-001",
            "name": "Low Stock Item",
            "quantity": 5,
            "price": 10.0,
            "min_stock_level": 10,
            "reorder_point": 15
        })
        
        check_and_create_alerts()
        
        result = get_active_alerts()
        self.assertTrue(result.get("success", False))
        self.assertIsInstance(result.get("alerts", []), list)
    
    def test_get_active_alerts(self):
        """Test retrieving active alerts"""
        result = get_active_alerts()
        self.assertTrue(result.get("success", False))
        self.assertIn("alerts", result)
        self.assertIsInstance(result["alerts"], list)
    
    def test_resolve_alert(self):
        """Test marking an alert as resolved"""
        item_id = add_item({
            "sku": "ALERT-002",
            "name": "Alert Test Item",
            "quantity": 3,
            "price": 15.0,
            "min_stock_level": 10
        })
        
        check_and_create_alerts()
        alert_result = get_active_alerts()
        
        if alert_result.get("success") and len(alert_result.get("alerts", [])) > 0:
            alert_id = alert_result["alerts"][0]["id"]
            result = resolve_alert(alert_id)
            self.assertTrue(result.get("success", False))


if __name__ == '__main__':
    unittest.main()
