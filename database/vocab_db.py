import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_manager import CSVDatabase
from backend.models.vocab import Vocabulary
from typing import List, Optional
from datetime import datetime

class VocabularyDB:
    """Vocabulary database operations"""
    
    def __init__(self, db: CSVDatabase):
        self.db = db
        self.filename = "vocabulary.csv"
        self.fieldnames = ['VocabID', 'ActionID', 'UserID', 'Vocab', 'Meaning', 
                          'Pronunciation', 'Audio', 'Time']
    
    def create_vocabulary(self, user_id: int, vocab: str, meaning: str, 
                         pronunciation: str, audio: str, 
                         action_id: Optional[int] = None) -> Vocabulary:
        """
        Tạo vocabulary record mới
        
        Args:
            user_id: User ID
            vocab: English word
            meaning: Vietnamese meaning
            pronunciation: Phonetic pronunciation
            audio: Audio file path or URL
            action_id: Action ID (dictionary API call)
        
        Returns:
            Vocabulary object
        """
        vocab_id = self.db.get_next_id(self.filename, 'VocabID')
        
        vocabulary = Vocabulary(
            VocabID=vocab_id,
            ActionID=action_id,
            UserID=user_id,
            Vocab=vocab,
            Meaning=meaning,
            Pronunciation=pronunciation,
            Audio=audio,
            Time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        self.db.append(self.filename, vocabulary.to_csv_dict(), self.fieldnames)
        return vocabulary
    
    def get_user_vocabulary(self, user_id: int) -> List[Vocabulary]:
        """Lấy tất cả vocabulary của user"""
        data = self.db.find_all_by_field(self.filename, 'UserID', str(user_id))
        vocabs = [Vocabulary.from_csv_dict(row) for row in data]
        # Sort by time descending (newest first)
        vocabs.sort(key=lambda x: x.Time, reverse=True)
        return vocabs
    
    def search_user_vocabulary(self, user_id: int, search_term: str) -> List[Vocabulary]:
        """Tìm kiếm vocabulary của user"""
        vocabs = self.get_user_vocabulary(user_id)
        search_lower = search_term.lower()
        return [v for v in vocabs if search_lower in v.Vocab.lower()]
    
    def get_vocabulary_by_id(self, vocab_id: int) -> Optional[Vocabulary]:
        """Lấy vocabulary theo ID"""
        data = self.db.find_by_field(self.filename, 'VocabID', str(vocab_id))
        if data:
            return Vocabulary.from_csv_dict(data)
        return None
    
    def check_word_exists(self, user_id: int, vocab: str) -> Optional[Vocabulary]:
        """Kiểm tra xem user đã tra từ này chưa"""
        vocabs = self.get_user_vocabulary(user_id)
        for v in vocabs:
            if v.Vocab.lower() == vocab.lower():
                return v
        return None
