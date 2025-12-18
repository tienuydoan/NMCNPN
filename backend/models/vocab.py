from typing import Dict, Optional

class Vocabulary:
    """Vocabulary model class"""
    
    def __init__(self, VocabID: int, ActionID: Optional[int], UserID: int, 
                 Vocab: str, Meaning: str, Pronunciation: str, 
                 Audio: str, Time: str):
        self.VocabID = int(VocabID)
        self.ActionID = int(ActionID) if ActionID else None
        self.UserID = int(UserID)
        self.Vocab = Vocab
        self.Meaning = Meaning
        self.Pronunciation = Pronunciation
        self.Audio = Audio
        self.Time = Time
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'VocabID': self.VocabID,
            'ActionID': self.ActionID,
            'UserID': self.UserID,
            'Vocab': self.Vocab,
            'Meaning': self.Meaning,
            'Pronunciation': self.Pronunciation,
            'Audio': self.Audio,
            'Time': self.Time
        }
    
    def to_csv_dict(self) -> Dict:
        """Convert to dictionary for CSV storage"""
        return {
            'VocabID': str(self.VocabID),
            'ActionID': str(self.ActionID) if self.ActionID else '',
            'UserID': str(self.UserID),
            'Vocab': self.Vocab,
            'Meaning': self.Meaning,
            'Pronunciation': self.Pronunciation,
            'Audio': self.Audio,
            'Time': self.Time
        }
    
    @staticmethod
    def from_csv_dict(data: Dict) -> 'Vocabulary':
        """Create Vocabulary object from CSV dictionary"""
        return Vocabulary(
            VocabID=data['VocabID'],
            ActionID=data.get('ActionID') if data.get('ActionID') else None,
            UserID=data['UserID'],
            Vocab=data['Vocab'],
            Meaning=data['Meaning'],
            Pronunciation=data['Pronunciation'],
            Audio=data['Audio'],
            Time=data['Time']
        )
