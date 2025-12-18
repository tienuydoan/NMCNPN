import re
from typing import Optional, Tuple

def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate username
    
    Args:
        username: Username to validate
    
    Returns:
        (is_valid, error_message)
    """
    if not username:
        return False, "Username không được để trống"
    
    if len(username) < 3:
        return False, "Username phải có ít nhất 3 ký tự"
    
    if len(username) > 50:
        return False, "Username không được dài quá 50 ký tự"
    
    # Only allow alphanumeric and underscore
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username chỉ được chứa chữ cái, số và dấu gạch dưới"
    
    return True, None

def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password
    
    Args:
        password: Password to validate
    
    Returns:
        (is_valid, error_message)
    """
    if not password:
        return False, "Password không được để trống"
    
    if len(password) < 6:
        return False, "Password phải có ít nhất 6 ký tự"
    
    if len(password) > 100:
        return False, "Password không được dài quá 100 ký tự"
    
    return True, None

def validate_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate full name
    
    Args:
        name: Full name to validate
    
    Returns:
        (is_valid, error_message)
    """
    if not name:
        return False, "Họ tên không được để trống"
    
    if len(name) < 2:
        return False, "Họ tên phải có ít nhất 2 ký tự"
    
    if len(name) > 100:
        return False, "Họ tên không được dài quá 100 ký tự"
    
    return True, None

def validate_message(message: str) -> Tuple[bool, Optional[str]]:
    """
    Validate chat message
    
    Args:
        message: Message to validate
    
    Returns:
        (is_valid, error_message)
    """
    if not message or not message.strip():
        return False, "Tin nhắn không được để trống"
    
    if len(message) > 5000:
        return False, "Tin nhắn không được dài quá 5000 ký tự"
    
    return True, None

def validate_vocab_word(word: str) -> Tuple[bool, Optional[str]]:
    """
    Validate vocabulary word
    
    Args:
        word: Word to validate
    
    Returns:
        (is_valid, error_message)
    """
    if not word or not word.strip():
        return False, "Từ vựng không được để trống"
    
    if len(word) > 100:
        return False, "Từ vựng không được dài quá 100 ký tự"
    
    # Only allow letters, spaces, hyphens
    if not re.match(r'^[a-zA-Z\s\-]+$', word):
        return False, "Từ vựng chỉ được chứa chữ cái, khoảng trắng và dấu gạch ngang"
    
    return True, None
