import hashlib
import secrets

def hash_password(password):
    salt = secrets.token_bytes(16)
    iterations = 100000
    hash_val = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations).hexdigest()
    return f"pbkdf2_sha256${iterations}${salt.hex()}${hash_val}"