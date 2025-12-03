import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.dashboard_stats import get_dashboard_stats, get_recent_activity
from database.db_setup import setup_database


class TestDashboardStats(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test database once for all tests"""
        setup_database()
    
    def test_get_dashboard_stats(self):
        """Test getting dashboard statistics"""
        result = get_dashboard_stats()
        self.assertTrue(result.get("success", False))
        stats = result.get("stats", {})
        self.assertIsInstance(stats, dict)
        self.assertIn("total_items", stats)
        self.assertGreaterEqual(stats["total_items"], 0)
    
    def test_get_recent_activity(self):
        """Test getting recent activity"""
        result = get_recent_activity(limit=5)
        self.assertTrue(result.get("success", False))
        activity = result.get("activity", [])
        self.assertIsInstance(activity, list)


if __name__ == '__main__':
    unittest.main()
