import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.utils.config import Config
from database.db_manager import CSVDatabase
from database.action_db import ActionDB, ThirdPartyAPIDB
from typing import Dict, Optional
import hashlib
from datetime import datetime

try:
    from elevenlabs.client import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    print("Warning: elevenlabs not installed. TTS features will not work.")

class TTSService:
    """Text-to-Speech service using ElevenLabs API"""
    
    def __init__(self, db: CSVDatabase):
        self.action_db = ActionDB(db)
        self.api_db = ThirdPartyAPIDB(db)
        self.api_key = Config.ELEVENLABS_API_KEY
        self.voice_id = Config.ELEVENLABS_VOICE_ID
        self.model_id = Config.ELEVENLABS_MODEL_ID
        self.audio_dir = Config.AUDIO_DIR
        
        # Ensure audio directory exists
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
        
        # Get API config from database
        self.api_config = self.api_db.get_api_by_type('text-to-speech')
        
        # Initialize client if available
        if ELEVENLABS_AVAILABLE and self.api_key:
            try:
                self.client = ElevenLabs(api_key=self.api_key)
            except Exception as e:
                print(f"Error initializing ElevenLabs TTS client: {e}")
                self.client = None
        else:
            self.client = None
    
    def synthesize_speech(self, text: str, output_format: str = 'mp3') -> Dict:
        """
        Convert text to speech using ElevenLabs
        
        Args:
            text: Text to convert
            output_format: Audio format ('mp3' or 'wav')
        
        Returns:
            Dictionary with audio file path and action_id
        """
        if not ELEVENLABS_AVAILABLE:
            return {
                'success': False,
                'error': 'ElevenLabs not installed. Run: pip install elevenlabs'
            }
        
        if not self.client:
            return {
                'success': False,
                'error': 'ElevenLabs TTS not configured properly. Check ELEVENLABS_API_KEY in .env'
            }
        
        try:
            # Log request
            request_data = {
                'text': text,
                'voice_id': self.voice_id,
                'model_id': self.model_id,
                'format': output_format
            }
            
            action = self.action_db.create_action(
                api_id=self.api_config.APIID if self.api_config else 3,
                request=request_data
            )
            
            # Map output format to ElevenLabs format
            format_map = {
                'mp3': 'mp3_44100_128',
                'wav': 'pcm_44100'
            }
            elevenlabs_format = format_map.get(output_format.lower(), 'mp3_44100_128')
            
            # Call ElevenLabs API
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id=self.model_id,
                output_format=elevenlabs_format
            )
            
            # Collect audio bytes from generator
            audio_content = b""
            for chunk in audio_generator:
                audio_content += chunk
            
            # Save audio file
            filename = self._generate_filename(text, output_format)
            audio_path = os.path.join(self.audio_dir, filename)
            
            with open(audio_path, 'wb') as out:
                out.write(audio_content)
            
            # Log response
            response_data = {
                'audio_path': audio_path,
                'audio_size': len(audio_content),
                'voice_id': self.voice_id,
                'model_id': self.model_id
            }
            
            self.action_db.update_action_response(action.ActionID, response_data)
            
            return {
                'success': True,
                'audio_path': audio_path,
                'action_id': action.ActionID
            }
            
        except Exception as e:
            print(f"Error calling ElevenLabs Text-to-Speech API: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_filename(self, text: str, format: str) -> str:
        """Generate unique filename for audio file"""
        # Create hash of text + timestamp
        content = f"{text}_{datetime.now().isoformat()}"
        hash_val = hashlib.md5(content.encode()).hexdigest()
        return f"tts_{hash_val}.{format}"
    
    def get_audio_content(self, audio_path: str) -> Optional[bytes]:
        """Read audio file and return content"""
        try:
            if os.path.exists(audio_path):
                with open(audio_path, 'rb') as f:
                    return f.read()
        except Exception as e:
            print(f"Error reading audio file: {e}")
        return None
