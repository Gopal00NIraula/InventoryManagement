# utils/encryption.py

import hashlib

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify a plain password against the stored hash"""
    return hash_password(password) == hashed
