import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.utils.config import Config
from database.db_manager import CSVDatabase
from database.action_db import ActionDB, ThirdPartyAPIDB
from database.vocab_db import VocabularyDB
from backend.utils.validators import validate_vocab_word
from typing import Dict
import requests

class VocabService:
    """Vocabulary lookup service using Dictionary API"""
    
    def __init__(self, db: CSVDatabase):
        self.action_db = ActionDB(db)
        self.api_db = ThirdPartyAPIDB(db)
        self.vocab_db = VocabularyDB(db)
        self.api_url = Config.DICTIONARY_API_URL
        
        # Get API config from database
        self.api_config = self.api_db.get_api_by_type('dictionary')
    
    def lookup_word(self, word: str, user_id: int) -> Dict:
        """
        Tra cứu từ vựng
        
        Args:
            word: English word to lookup
            user_id: User ID
        
        Returns:
            Dictionary with word info (meaning, pronunciation, audio)
        """
        # Validate word
        valid, error = validate_vocab_word(word)
        if not valid:
            return {
                'success': False,
                'error': error
            }
        
        word = word.strip().lower()
        
        # Check if already looked up
        existing = self.vocab_db.check_word_exists(user_id, word)
        if existing:
            return {
                'success': True,
                'word': word,
                'meaning': existing.Meaning,
                'pronunciation': existing.Pronunciation,
                'audio': existing.Audio,
                'from_history': True
            }
        
        try:
            # Log request
            request_data = {
                'word': word
            }
            
            action = self.action_db.create_action(
                api_id=self.api_config.APIID if self.api_config else 4,
                request=request_data
            )
            
            # Call Dictionary API
            url = f"{self.api_url}/{word}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': 'Không tìm thấy từ trong từ điển'
                }
            
            data = response.json()
            
            if not data or len(data) == 0:
                return {
                    'success': False,
                    'error': 'Không có dữ liệu từ điển'
                }
            
            # Extract information
            word_data = data[0]
            
            # Get pronunciation
            pronunciation = ""
            if 'phonetic' in word_data:
                pronunciation = word_data['phonetic']
            elif 'phonetics' in word_data and len(word_data['phonetics']) > 0:
                pronunciation = word_data['phonetics'][0].get('text', '')
            
            # Get audio
            audio_url = ""
            if 'phonetics' in word_data:
                for phonetic in word_data['phonetics']:
                    if 'audio' in phonetic and phonetic['audio']:
                        audio_url = phonetic['audio']
                        break
            
            # Get meanings (simplified - just get first definition)
            meaning = ""
            if 'meanings' in word_data and len(word_data['meanings']) > 0:
                first_meaning = word_data['meanings'][0]
                if 'definitions' in first_meaning and len(first_meaning['definitions']) > 0:
                    meaning = first_meaning['definitions'][0].get('definition', '')
                    
                    # Try to get example
                    example = first_meaning['definitions'][0].get('example', '')
                    if example:
                        meaning += f"\nExample: {example}"
            
            # Note: This API returns English definitions, not Vietnamese
            # For Vietnamese translations, you would need a different API
            # For now, we'll just use the English definition
            
            # Log response
            response_data = {
                'word': word,
                'pronunciation': pronunciation,
                'meaning': meaning,
                'audio': audio_url
            }
            
            self.action_db.update_action_response(action.ActionID, response_data)
            
            # Save to vocabulary history
            vocab = self.vocab_db.create_vocabulary(
                user_id=user_id,
                vocab=word,
                meaning=meaning,
                pronunciation=pronunciation,
                audio=audio_url,
                action_id=action.ActionID
            )
            
            return {
                'success': True,
                'word': word,
                'meaning': meaning,
                'pronunciation': pronunciation,
                'audio': audio_url,
                'vocab_id': vocab.VocabID,
                'from_history': False
            }
            
        except requests.RequestException as e:
            print(f"Error calling Dictionary API: {e}")
            return {
                'success': False,
                'error': 'Lỗi kết nối đến Dictionary API'
            }
        except Exception as e:
            print(f"Error in lookup_word: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_vocabulary_history(self, user_id: int) -> Dict:
        """
        Lấy lịch sử từ vựng của user
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with vocabulary list
        """
        try:
            vocabs = self.vocab_db.get_user_vocabulary(user_id)
            
            vocab_list = []
            for v in vocabs:
                vocab_list.append({
                    'vocab_id': v.VocabID,
                    'word': v.Vocab,
                    'meaning': v.Meaning,
                    'pronunciation': v.Pronunciation,
                    'audio': v.Audio,
                    'time': v.Time
                })
            
            return {
                'success': True,
                'vocabulary': vocab_list
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
