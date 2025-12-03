import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.barcode_utils import generate_barcode_number


class TestBarcodeUtils(unittest.TestCase):
    
    def test_generate_barcode_number(self):
        """Test generating a barcode number"""
        barcode = generate_barcode_number(1, "TEST-SKU")
        
        self.assertIsNotNone(barcode)
        self.assertGreater(len(barcode), 0)
    
    def test_generate_unique_barcodes(self):
        """Test that generated barcodes are unique"""
        barcodes = set()
        for i in range(100):
            barcode = generate_barcode_number(i, f"SKU-{i}")
            barcodes.add(barcode)
        
        self.assertGreater(len(barcodes), 90)


if __name__ == '__main__':
    unittest.main()
