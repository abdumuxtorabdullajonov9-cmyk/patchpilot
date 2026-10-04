import hashlib
import os

def hash_password(password):
    salt = os.urandom(16)
    hashed = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1, dklen=32).hexdigest()
    return salt.hex() + ':' + hashed