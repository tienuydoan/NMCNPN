import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.utils.config import Config
from database.db_manager import CSVDatabase
from database.action_db import ActionDB, ThirdPartyAPIDB
from typing import Dict, Optional
from io import BytesIO

try:
    from elevenlabs.client import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    print("Warning: elevenlabs not installed. STT features will not work.")

class STTService:
    """Speech-to-Text service using ElevenLabs API"""
    
    def __init__(self, db: CSVDatabase):
        self.action_db = ActionDB(db)
        self.api_db = ThirdPartyAPIDB(db)
        self.api_key = Config.ELEVENLABS_API_KEY
        self.language = Config.ELEVENLABS_LANGUAGE
        self.model_id = Config.ELEVENLABS_STT_MODEL
        
        # Get API config from database
        self.api_config = self.api_db.get_api_by_type('speech-to-text')
        
        # Initialize client if available
        if ELEVENLABS_AVAILABLE and self.api_key:
            try:
                self.client = ElevenLabs(api_key=self.api_key)
            except Exception as e:
                print(f"Error initializing ElevenLabs client: {e}")
                self.client = None
        else:
            self.client = None
    
    def transcribe_audio(self, audio_content: bytes, audio_format: str = 'wav') -> Dict:
        """
        Transcribe audio to text using ElevenLabs
        
        Args:
            audio_content: Audio file content as bytes
            audio_format: Audio format ('wav', 'mp3', etc.)
        
        Returns:
            Dictionary with transcript and action_id
        """
        if not ELEVENLABS_AVAILABLE:
            return {
                'success': False,
                'error': 'ElevenLabs not installed. Run: pip install elevenlabs'
            }
        
        if not self.client:
            return {
                'success': False,
                'error': 'ElevenLabs not configured properly. Check ELEVENLABS_API_KEY in .env'
            }
        
        try:
            # Log request
            request_data = {
                'audio_format': audio_format,
                'language': self.language,
                'audio_size': len(audio_content),
                'model': self.model_id
            }
            
            action = self.action_db.create_action(
                api_id=self.api_config.APIID if self.api_config else 2,
                request=request_data
            )
            
            # Prepare audio as BytesIO
            audio_data = BytesIO(audio_content)
            audio_data.name = f"audio.{audio_format}"  # Set filename for format detection
            
            # Call ElevenLabs API
            transcription = self.client.speech_to_text.convert(
                file=audio_data,
                model_id=self.model_id,
                language_code=self.language,
                tag_audio_events=True,
                diarize=False  # Single speaker for now
            )
            
            # Extract transcript text
            transcript = transcription.text if hasattr(transcription, 'text') else str(transcription)
            
            # Log response
            response_data = {
                'transcript': transcript,
                'model': self.model_id
            }
            
            self.action_db.update_action_response(action.ActionID, response_data)
            
            return {
                'success': True,
                'transcript': transcript,
                'action_id': action.ActionID
            }
            
        except Exception as e:
            print(f"Error calling ElevenLabs Speech-to-Text API: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def transcribe_audio_file(self, audio_path: str) -> Dict:
        """
        Transcribe audio from file path
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Dictionary with transcript
        """
        try:
            with open(audio_path, 'rb') as f:
                audio_content = f.read()
            
            # Detect format from extension
            audio_format = os.path.splitext(audio_path)[1][1:]  # Remove dot
            
            return self.transcribe_audio(audio_content, audio_format)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error reading audio file: {str(e)}'
            }
