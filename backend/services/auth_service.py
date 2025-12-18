import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_manager import CSVDatabase
from database.user_db import UserDB
from backend.models.user import User
from backend.utils.validators import validate_username, validate_password, validate_name
from backend.utils.security import generate_session_token
from typing import Optional, Dict

class AuthService:
    """Authentication service"""
    
    def __init__(self, db: CSVDatabase):
        self.user_db = UserDB(db)
        self.sessions = {}  # Simple in-memory session storage {token: user_id}
    
    def register(self, tai_khoan: str, mat_khau: str, ho_ten: str) -> Dict:
        """
        Đăng ký user mới
        
        Args:
            tai_khoan: Username
            mat_khau: Password
            ho_ten: Full name
        
        Returns:
            Dictionary with success status and data/error
        """
        # Validate inputs
        valid, error = validate_username(tai_khoan)
        if not valid:
            return {'success': False, 'error': error}
        
        valid, error = validate_password(mat_khau)
        if not valid:
            return {'success': False, 'error': error}
        
        valid, error = validate_name(ho_ten)
        if not valid:
            return {'success': False, 'error': error}
        
        # Check if username exists
        if self.user_db.get_user_by_username(tai_khoan):
            return {'success': False, 'error': 'Username đã tồn tại'}
        
        try:
            # Create user
            user = self.user_db.create_user(tai_khoan, mat_khau, ho_ten)
            
            return {
                'success': True,
                'user': user.to_dict()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def login(self, tai_khoan: str, mat_khau: str) -> Dict:
        """
        Đăng nhập
        
        Args:
            tai_khoan: Username
            mat_khau: Password
        
        Returns:
            Dictionary with success status and data/error
        """
        # Verify credentials
        user = self.user_db.verify_login(tai_khoan, mat_khau)
        
        if not user:
            return {'success': False, 'error': 'Username hoặc password không đúng'}
        
        # Generate session token
        token = generate_session_token()
        self.sessions[token] = user.UserID
        
        return {
            'success': True,
            'token': token,
            'user': user.to_dict()
        }
    
    def logout(self, token: str) -> Dict:
        """
        Đăng xuất
        
        Args:
            token: Session token
        
        Returns:
            Dictionary with success status
        """
        if token in self.sessions:
            del self.sessions[token]
        
        return {'success': True}
    
    def verify_session(self, token: str) -> Optional[User]:
        """
        Verify session token và trả về user
        
        Args:
            token: Session token
        
        Returns:
            User object if valid, None if invalid
        """
        user_id = self.sessions.get(token)
        if user_id:
            return self.user_db.get_user_by_id(user_id)
        return None
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        """Alias for verify_session"""
        return self.verify_session(token)
