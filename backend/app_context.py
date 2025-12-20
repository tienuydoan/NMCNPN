"""
Shared application context
Provides singleton instances of services to be shared across blueprints
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.db_manager import CSVDatabase
from backend.services.auth_service import AuthService
from backend.services.llm_service import LLMService
from backend.services.stt_service import STTService
from backend.services.tts_service import TTSService
from backend.services.vocab_service import VocabService

db = CSVDatabase()

auth_service = AuthService(db)
llm_service = LLMService(db)
stt_service = STTService(db)
tts_service = TTSService(db)
vocab_service = VocabService(db)
