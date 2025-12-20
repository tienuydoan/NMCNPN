import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_manager import CSVDatabase
from backend.models.conversation import Conversation, UserMessage, AIMessage
from typing import List, Optional
from datetime import datetime

class ConversationDB:
    def __init__(self, db: CSVDatabase):
        self.db = db
        self.filename = "hoi_thoai.csv"
        self.fieldnames = ['ConversationID', 'UserID', 'Mode', 'Datetime']
    
    def create_conversation(self, user_id: int, mode: str = "text") -> Conversation:
        conversation_id = self.db.get_next_id(self.filename, 'ConversationID')
        
        conversation = Conversation(
            ConversationID=conversation_id,
            UserID=user_id,
            Mode=mode,
            Datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        self.db.append(self.filename, conversation.to_csv_dict(), self.fieldnames)
        return conversation
    
    def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        data = self.db.find_by_field(self.filename, 'ConversationID', str(conversation_id))
        if data:
            return Conversation.from_csv_dict(data)
        return None
    
    def get_user_conversations(self, user_id: int) -> List[Conversation]:
        data = self.db.find_all_by_field(self.filename, 'UserID', str(user_id))
        conversations = [Conversation.from_csv_dict(row) for row in data]
        conversations.sort(key=lambda x: x.Datetime, reverse=True)
        return conversations
    
    def delete_conversation(self, conversation_id: int) -> bool:
        return self.db.delete_by_field(
            self.filename,
            'ConversationID',
            str(conversation_id),
            self.fieldnames
        )

class MessageDB:
    def __init__(self, db: CSVDatabase):
        self.db = db
        self.user_msg_filename = "user_message.csv"
        self.ai_msg_filename = "ai_message.csv"
        self.user_msg_fieldnames = ['MessageID', 'ConversationID', 'Message', 'Createtime']
        self.ai_msg_fieldnames = ['MessageID', 'ConversationID', 'Message', 'Createtime', 'ActionID']
    
    def create_user_message(self, conversation_id: int, message: str) -> UserMessage:
        message_id = self.db.get_next_id(self.user_msg_filename, 'MessageID')
        
        user_msg = UserMessage(
            MessageID=message_id,
            ConversationID=conversation_id,
            Message=message,
            Createtime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        self.db.append(self.user_msg_filename, user_msg.to_csv_dict(), self.user_msg_fieldnames)
        return user_msg
    
    def create_ai_message(self, conversation_id: int, message: str, 
                         action_id: Optional[int] = None) -> AIMessage:
        message_id = self.db.get_next_id(self.ai_msg_filename, 'MessageID')
        
        ai_msg = AIMessage(
            MessageID=message_id,
            ConversationID=conversation_id,
            Message=message,
            Createtime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            ActionID=action_id
        )
        
        self.db.append(self.ai_msg_filename, ai_msg.to_csv_dict(), self.ai_msg_fieldnames)
        return ai_msg
    
    def get_conversation_messages(self, conversation_id: int) -> List[dict]:
        user_messages = self.db.find_all_by_field(
            self.user_msg_filename, 'ConversationID', str(conversation_id)
        )
        ai_messages = self.db.find_all_by_field(
            self.ai_msg_filename, 'ConversationID', str(conversation_id)
        )
        
        messages = []
        
        for msg_data in user_messages:
            msg = UserMessage.from_csv_dict(msg_data)
            messages.append({
                'type': 'user',
                'message': msg,
                'time': msg.Createtime
            })
        
        for msg_data in ai_messages:
            msg = AIMessage.from_csv_dict(msg_data)
            messages.append({
                'type': 'ai',
                'message': msg,
                'time': msg.Createtime
            })
        
        # Sort by time
        messages.sort(key=lambda x: x['time'])
        return messages
    
    def get_ai_message(self, message_id: int) -> Optional[AIMessage]:
        data = self.db.find_by_field(self.ai_msg_filename, 'MessageID', str(message_id))
        if data:
            return AIMessage.from_csv_dict(data)
        return None
    
    def get_user_message(self, message_id: int) -> Optional[UserMessage]:
        data = self.db.find_by_field(self.user_msg_filename, 'MessageID', str(message_id))
        if data:
            return UserMessage.from_csv_dict(data)
        return None
