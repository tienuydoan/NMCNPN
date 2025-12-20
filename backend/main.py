import sys
import os

sys.path.append(os.path.dirname(__file__))

from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.utils.config import Config
from backend.routes.auth import auth_bp
from backend.routes.conversation import conversation_bp
from backend.routes.vocab import vocab_bp

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['DEBUG'] = Config.DEBUG

CORS(app, supports_credentials=True)

app.register_blueprint(auth_bp)
app.register_blueprint(conversation_bp)
app.register_blueprint(vocab_bp)

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/chat')
def chat():
    return send_from_directory(FRONTEND_DIR, 'chat.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)

@app.route('/api/health')
def health():
    return {'status': 'ok', 'message': 'English Chat AI is running'}

if __name__ == '__main__':
    warnings = Config.validate()
    if warnings:
        print("\n⚠️  Configuration Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print()
    
    print(f"🚀 Starting English Chat AI on http://{Config.HOST}:{Config.PORT}")
    print(f"📝 Login page: http://{Config.HOST}:{Config.PORT}/")
    print(f"💬 Chat page: http://{Config.HOST}:{Config.PORT}/chat")
    print()
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
