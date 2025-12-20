import os
from dotenv import load_dotenv

# Load environment variables từ .env file
load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '127.0.0.1')
    
    # LLM API settings
    LITELLM_API_KEY = os.getenv('LITELLM_API_KEY', '')
    LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gpt-3.5-turbo')
    
    # ElevenLabs API settings
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', '')
    ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', 'JBFqnCBsd6RMkjVDRZzb')
    ELEVENLABS_MODEL_ID = os.getenv('ELEVENLABS_MODEL_ID', 'eleven_multilingual_v2')
    ELEVENLABS_STT_MODEL = os.getenv('ELEVENLABS_STT_MODEL', 'scribe_v1')
    ELEVENLABS_LANGUAGE = os.getenv('ELEVENLABS_LANGUAGE', 'eng')
    
    # Dictionary API settings
    DICTIONARY_API_URL = os.getenv('DICTIONARY_API_URL', 
                                    'https://api.dictionaryapi.dev/api/v2/entries/en')
    
    # Database settings
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    AUDIO_DIR = os.path.join(DATA_DIR, 'audio')
    
    # API Configuration
    API_CONFIGS = {
        'LLM': {
            'provider': 'openai',
            'api_key': LITELLM_API_KEY,
            'model': LITELLM_MODEL
        },
        'speech-to-text': {
            'provider': 'elevenlabs',
            'api_key': ELEVENLABS_API_KEY,
            'language': ELEVENLABS_LANGUAGE,
            'model': ELEVENLABS_STT_MODEL
        },
        'text-to-speech': {
            'provider': 'elevenlabs',
            'api_key': ELEVENLABS_API_KEY,
            'voice_id': ELEVENLABS_VOICE_ID,
            'model': ELEVENLABS_MODEL_ID
        },
        'dictionary': {
            'provider': 'free',
            'url': DICTIONARY_API_URL
        }
    }
    
    @classmethod
    def validate(cls):
        warnings = []
        
        if not cls.LITELLM_API_KEY:
            warnings.append("LITELLM_API_KEY not set - LLM features will not work")
        
        if not cls.ELEVENLABS_API_KEY:
            warnings.append("ELEVENLABS_API_KEY not set - Speech features will not work")
        
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            warnings.append("Using default SECRET_KEY - change this in production!")
        
        return warnings
