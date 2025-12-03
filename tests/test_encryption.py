import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.encryption import hash_password, verify_password


class TestEncryption(unittest.TestCase):
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        self.assertIsNotNone(hashed)
        self.assertNotEqual(hashed, password)
        self.assertGreater(len(hashed), 0)
    
    def test_hash_different_passwords_produce_different_hashes(self):
        """Test that different passwords produce different hashes"""
        password1 = "password1"
        password2 = "password2"
        
        hash1 = hash_password(password1)
        hash2 = hash_password(password2)
        
        self.assertNotEqual(hash1, hash2)
    
    def test_same_password_different_salts(self):
        """Test that same password produces different hashes (due to random salt)"""
        password = "samepassword"
        
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        self.assertNotEqual(hash1, hash2)
    
    def test_verify_correct_password(self):
        """Test verifying a correct password"""
        password = "mypassword123"
        hashed = hash_password(password)
        
        self.assertTrue(verify_password(password, hashed))
    
    def test_verify_incorrect_password(self):
        """Test verifying an incorrect password"""
        password = "mypassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        
        self.assertFalse(verify_password(wrong_password, hashed))
    
    def test_verify_empty_password(self):
        """Test verifying empty password"""
        password = ""
        hashed = hash_password(password)
        
        self.assertTrue(verify_password("", hashed))
        self.assertFalse(verify_password("notempty", hashed))


if __name__ == '__main__':
    unittest.main()
