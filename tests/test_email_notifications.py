import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.email_notifications import is_email_configured, send_low_stock_alert, send_welcome_email


class TestEmailNotifications(unittest.TestCase):
    
    def test_is_email_configured(self):
        """Test checking if email is configured"""
        result = is_email_configured()
        self.assertIsInstance(result, bool)
    
    def test_send_low_stock_alert(self):
        """Test low stock alert function exists"""
        self.assertTrue(callable(send_low_stock_alert))
    
    def test_send_welcome_email(self):
        """Test welcome email function exists"""
        self.assertTrue(callable(send_welcome_email))


if __name__ == '__main__':
    unittest.main()
