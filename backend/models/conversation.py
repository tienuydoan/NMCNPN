from typing import Dict, Optional
from datetime import datetime

class Conversation:
    """Conversation model class"""
    
    def __init__(self, ConversationID: int, UserID: int, Mode: str, Datetime: str):
        self.ConversationID = int(ConversationID)
        self.UserID = int(UserID)
        self.Mode = Mode  # "text" or "continuous"
        self.Datetime = Datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'ConversationID': self.ConversationID,
            'UserID': self.UserID,
            'Mode': self.Mode,
            'Datetime': self.Datetime
        }
    
    def to_csv_dict(self) -> Dict:
        """Convert to dictionary for CSV storage"""
        return {
            'ConversationID': str(self.ConversationID),
            'UserID': str(self.UserID),
            'Mode': self.Mode,
            'Datetime': self.Datetime
        }
    
    @staticmethod
    def from_csv_dict(data: Dict) -> 'Conversation':
        """Create Conversation object from CSV dictionary"""
        return Conversation(
            ConversationID=data['ConversationID'],
            UserID=data['UserID'],
            Mode=data['Mode'],
            Datetime=data['Datetime']
        )

class UserMessage:
    """User message model class"""
    
    def __init__(self, MessageID: int, ConversationID: int, Message: str, Createtime: str):
        self.MessageID = int(MessageID)
        self.ConversationID = int(ConversationID)
        self.Message = Message
        self.Createtime = Createtime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'MessageID': self.MessageID,
            'ConversationID': self.ConversationID,
            'Message': self.Message,
            'Createtime': self.Createtime
        }
    
    def to_csv_dict(self) -> Dict:
        """Convert to dictionary for CSV storage"""
        return {
            'MessageID': str(self.MessageID),
            'ConversationID': str(self.ConversationID),
            'Message': self.Message,
            'Createtime': self.Createtime
        }
    
    @staticmethod
    def from_csv_dict(data: Dict) -> 'UserMessage':
        """Create UserMessage object from CSV dictionary"""
        return UserMessage(
            MessageID=data['MessageID'],
            ConversationID=data['ConversationID'],
            Message=data['Message'],
            Createtime=data['Createtime']
        )

class AIMessage:
    """AI message model class"""
    
    def __init__(self, MessageID: int, ConversationID: int, Message: str, 
                 Createtime: str, ActionID: Optional[int] = None):
        self.MessageID = int(MessageID)
        self.ConversationID = int(ConversationID)
        self.Message = Message
        self.Createtime = Createtime
        self.ActionID = int(ActionID) if ActionID else None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'MessageID': self.MessageID,
            'ConversationID': self.ConversationID,
            'Message': self.Message,
            'Createtime': self.Createtime,
            'ActionID': self.ActionID
        }
    
    def to_csv_dict(self) -> Dict:
        """Convert to dictionary for CSV storage"""
        return {
            'MessageID': str(self.MessageID),
            'ConversationID': str(self.ConversationID),
            'Message': self.Message,
            'Createtime': self.Createtime,
            'ActionID': str(self.ActionID) if self.ActionID else ''
        }
    
    @staticmethod
    def from_csv_dict(data: Dict) -> 'AIMessage':
        """Create AIMessage object from CSV dictionary"""
        return AIMessage(
            MessageID=data['MessageID'],
            ConversationID=data['ConversationID'],
            Message=data['Message'],
            Createtime=data['Createtime'],
            ActionID=data.get('ActionID') if data.get('ActionID') else None
        )
