import bcrypt
import secrets
import hashlib

def hash_password(password: str) -> str:
    """
    Hash password sử dụng bcrypt
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password string
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify password với hashed password
    
    Args:
        password: Plain text password
        hashed_password: Hashed password từ database
    
    Returns:
        True nếu password đúng, False nếu sai
    """
    try:
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False

def generate_session_token() -> str:
    """
    Tạo session token ngẫu nhiên
    
    Returns:
        Random session token string
    """
    return secrets.token_urlsafe(32)

def generate_file_hash(content: bytes) -> str:
    """
    Tạo hash cho file content (để tạo unique filename)
    
    Args:
        content: File content as bytes
    
    Returns:
        SHA256 hash string
    """
    return hashlib.sha256(content).hexdigest()
