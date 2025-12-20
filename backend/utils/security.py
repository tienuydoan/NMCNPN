import bcrypt
import secrets
import hashlib

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    try:
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False

def generate_session_token() -> str:
    return secrets.token_urlsafe(32)

def generate_file_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
