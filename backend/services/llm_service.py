import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.utils.config import Config
from database.db_manager import CSVDatabase
from database.action_db import ActionDB, ThirdPartyAPIDB
from typing import Dict, Optional
import json
from dotenv import load_dotenv

load_dotenv()

try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("Warning: litellm not installed. LLM features will not work.")

class LLMService:
    """LLM service using LiteLLM"""
    
    def __init__(self, db: CSVDatabase):
        self.action_db = ActionDB(db)
        self.api_db = ThirdPartyAPIDB(db)
        self.model = Config.LITELLM_MODEL
        self.api_key = Config.LITELLM_API_KEY
        
        # Get API config from database
        self.api_config = self.api_db.get_api_by_type('LLM')
        if not self.api_config:
            print("Warning: LLM API config not found in database")
    
    def chat_completion(self, messages: list, conversation_history: list = None) -> Dict:
        """
        Get chat completion from LLM
        
        Args:
            messages: Current message (format: [{"role": "user", "content": "text"}])
            conversation_history: Previous messages for context
        
        Returns:
            Dictionary with response and action_id
        """
        if not LITELLM_AVAILABLE:
            return {
                'success': False,
                'error': 'LiteLLM not installed'
            }
        
        
        try:
            all_messages = []
            
            all_messages.append({
                "role": "system",
                "content": "You are a helpful English conversation teacher. Help the user practice English conversation naturally and provide corrections when needed."
            })
            
            if conversation_history:
                all_messages.extend(conversation_history)
            
            all_messages.extend(messages)
            
            request_data = {
                'model': self.model,
                'messages': all_messages
            }
            
            action = self.action_db.create_action(
                api_id=self.api_config.APIID if self.api_config else 1,
                request=request_data
            )
            
            response = litellm.completion(
                model=self.model,
                messages=all_messages,
                api_key=self.api_key
            )
            
            response_text = response.choices[0].message.content
            
            usage_info = {}
            if hasattr(response, 'usage') and response.usage:
                try:
                    usage_info = {
                        'prompt_tokens': getattr(response.usage, 'prompt_tokens', 0),
                        'completion_tokens': getattr(response.usage, 'completion_tokens', 0),
                        'total_tokens': getattr(response.usage, 'total_tokens', 0)
                    }
                except Exception as e:
                    print(f"Warning: Could not extract usage info: {e}")
            
            response_data = {
                'response': response_text,
                'model': getattr(response, 'model', self.model),
                'usage': usage_info
            }
            
            self.action_db.update_action_response(action.ActionID, response_data)
            
            return {
                'success': True,
                'response': response_text,
                'action_id': action.ActionID
            }
            
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def simple_chat(self, user_message: str) -> Dict:
        messages = [{"role": "user", "content": user_message}]
        return self.chat_completion(messages)
