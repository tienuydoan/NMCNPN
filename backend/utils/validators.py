import re
from typing import Optional, Tuple

def validate_username(username: str) -> Tuple[bool, Optional[str]]:
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
    if not password:
        return False,
    
    if len(password) < 6:
        return False,
    
    if len(password) > 100:
        return False,
    
    return True, None

def validate_name(name: str) -> Tuple[bool, Optional[str]]:
    if not name:
        return False,
    
    if len(name) < 2:
        return False,
    
    if len(name) > 100:
        return False,
    
    return True, None

def validate_message(message: str) -> Tuple[bool, Optional[str]]:
    if not message or not message.strip():
        return False,
    
    if len(message) > 5000:
        return False,
    
    return True, None

def validate_vocab_word(word: str) -> Tuple[bool, Optional[str]]:
    if not word or not word.strip():
        return False,
    
    if len(word) > 100:
        return False,
    
    # Only allow letters, spaces, hyphens
    if not re.match(r'^[a-zA-Z\s\-]+$', word):
        return False,
    
    return True, None
