from typing import Optional, Dict

class User:
    """User model class"""
    
    def __init__(self, UserID: int, tai_khoan: str, mat_khau: str, 
                 RoleID: int, active: bool, ho_ten: str):
        self.UserID = int(UserID)
        self.tai_khoan = tai_khoan
        self.mat_khau = mat_khau  # Hashed password
        self.RoleID = int(RoleID)
        self.active = active if isinstance(active, bool) else active.lower() == 'true'
        self.ho_ten = ho_ten
    
    def to_dict(self, include_password=False) -> Dict:
        """
        Convert user object to dictionary
        
        Args:
            include_password: Include hashed password in dict (default False for security)
        
        Returns:
            Dictionary representation of user
        """
        data = {
            'UserID': self.UserID,
            'tai_khoan': self.tai_khoan,
            'RoleID': self.RoleID,
            'active': self.active,
            'ho_ten': self.ho_ten
        }
        
        if include_password:
            data['mat_khau'] = self.mat_khau
        
        return data
    
    def to_csv_dict(self) -> Dict:
        """Convert to dictionary for CSV storage"""
        return {
            'UserID': str(self.UserID),
            'tai_khoan': self.tai_khoan,
            'mat_khau': self.mat_khau,
            'RoleID': str(self.RoleID),
            'active': 'true' if self.active else 'false',
            'ho_ten': self.ho_ten
        }
    
    @staticmethod
    def from_csv_dict(data: Dict) -> 'User':
        """Create User object from CSV dictionary"""
        return User(
            UserID=data['UserID'],
            tai_khoan=data['tai_khoan'],
            mat_khau=data['mat_khau'],
            RoleID=data['RoleID'],
            active=data['active'],
            ho_ten=data['ho_ten']
        )
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.RoleID == 1
    
    def is_active(self) -> bool:
        """Check if user account is active"""
        return self.active
