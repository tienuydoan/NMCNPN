import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_manager import CSVDatabase
from backend.models.user import User
from backend.utils.security import hash_password, verify_password
from typing import Optional

class UserDB:
    def __init__(self, db: CSVDatabase):
        self.db = db
        self.filename = "nguoi_dung.csv"
        self.fieldnames = ['UserID', 'tai_khoan', 'mat_khau', 'RoleID', 'active', 'ho_ten']
    
    def create_user(self, tai_khoan: str, mat_khau: str, ho_ten: str, 
                   role_id: int = 0) -> User:
        if self.get_user_by_username(tai_khoan):
            raise ValueError(f"Username '{tai_khoan}' đã tồn tại")
        
        user_id = self.db.get_next_id(self.filename, 'UserID')
        
        user = User(
            UserID=user_id,
            tai_khoan=tai_khoan,
            mat_khau=hash_password(mat_khau),
            RoleID=role_id,
            active=True,
            ho_ten=ho_ten
        )
        
        self.db.append(self.filename, user.to_csv_dict(), self.fieldnames)
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        data = self.db.find_by_field(self.filename, 'UserID', str(user_id))
        if data:
            return User.from_csv_dict(data)
        return None
    
    def get_user_by_username(self, tai_khoan: str) -> Optional[User]:
        data = self.db.find_by_field(self.filename, 'tai_khoan', tai_khoan)
        if data:
            return User.from_csv_dict(data)
        return None
    
    def verify_login(self, tai_khoan: str, mat_khau: str) -> Optional[User]:
        user = self.get_user_by_username(tai_khoan)
        
        if not user:
            return None
        
        if not user.is_active():
            return None
        
        if verify_password(mat_khau, user.mat_khau):
            return user
        
        return None
    
    def update_user(self, user: User) -> bool:
        return self.db.update_by_field(
            self.filename, 
            'UserID', 
            str(user.UserID),
            user.to_csv_dict(),
            self.fieldnames
        )
    
    def deactivate_user(self, user_id: int) -> bool:
        user = self.get_user_by_id(user_id)
        if user:
            user.active = False
            return self.update_user(user)
        return False
    
    def get_all_users(self):
        data = self.db.read(self.filename)
        return [User.from_csv_dict(row) for row in data]
