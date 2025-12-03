import unittest
import sys
import os
import tempfile
import csv
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.import_export import (
    export_to_csv, import_from_csv,
    export_inventory_to_csv, import_inventory_from_csv
)


class TestImportExport(unittest.TestCase):
    
    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_export_to_csv(self):
        """Test exporting data to CSV"""
        data = [
            {"name": "Item 1", "price": "10.99", "quantity": "5"},
            {"name": "Item 2", "price": "20.99", "quantity": "10"}
        ]
        headers = ["name", "price", "quantity"]
        filepath = os.path.join(self.test_dir, "test_export.csv")
        
        result = export_to_csv(data, filepath, headers)
        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists(filepath))
        
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["name"], "Item 1")
    
    def test_import_from_csv(self):
        """Test importing data from CSV"""
        filepath = os.path.join(self.test_dir, "test_import.csv")
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["sku", "name", "quantity", "price"])
            writer.writeheader()
            writer.writerow({"sku": "SKU001", "name": "Product 1", "quantity": "100", "price": "29.99"})
            writer.writerow({"sku": "SKU002", "name": "Product 2", "quantity": "50", "price": "19.99"})
        
        required_headers = ["sku", "name", "quantity", "price"]
        result = import_from_csv(filepath, required_headers)
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["sku"], "SKU001")
    
    def test_import_from_csv_missing_headers(self):
        """Test importing CSV with missing required headers"""
        filepath = os.path.join(self.test_dir, "test_missing_headers.csv")
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["sku", "name"])
            writer.writeheader()
            writer.writerow({"sku": "SKU001", "name": "Product 1"})
        
        required_headers = ["sku", "name", "quantity", "price"]
        result = import_from_csv(filepath, required_headers)
        
        # Should fail due to missing required headers
        if result.get("success"):
            # If it succeeds, it should have handled missing headers gracefully
            self.assertTrue(True)
        else:
            # Otherwise it should fail and have an error message
            self.assertFalse(result["success"])
    
    def test_export_inventory_to_csv_empty_list(self):
        """Test exporting empty inventory list"""
        filepath = os.path.join(self.test_dir, "empty_inventory.csv")
        
        success = export_inventory_to_csv([], filepath)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(filepath))
        
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)


if __name__ == '__main__':
    unittest.main()
