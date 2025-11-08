# utils/encryption.py
import os, base64, hashlib, hmac

# Use PBKDF2-HMAC-SHA256 with random salt
_ITER = 120_000

def hash_password(password: str) -> str:
    if not isinstance(password, str):
        raise TypeError("password must be str")
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITER)
    return f"pbkdf2$sha256${_ITER}${base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"

def verify_password(password: str, hashed: str) -> bool:
    try:
        scheme, algo, iters, b64_salt, b64_dk = hashed.split("$", 4)
        if scheme != "pbkdf2" or algo != "sha256":
            return False
        iters = int(iters)
        salt = base64.b64decode(b64_salt)
        dk_expected = base64.b64decode(b64_dk)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iters)
        return hmac.compare_digest(dk, dk_expected)
    except Exception:
        return False
