import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from flask import Blueprint, request, jsonify
from backend.app_context import auth_service, vocab_service

# Create blueprint
vocab_bp = Blueprint('vocab', __name__, url_prefix='/api/vocab')

def get_current_user():
    """Helper function to get current user from session"""
    token = request.headers.get('Authorization') or session.get('token')
    if not token:
        return None
    
    if token.startswith('Bearer '):
        token = token[7:]
    
    return auth_service.verify_session(token)

@vocab_bp.route('/lookup', methods=['POST'])
def lookup():
    """Tra cứu từ vựng"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        word = data.get('word', '').strip()
        
        if not word:
            return jsonify({'success': False, 'error': 'Word is required'}), 400
        
        # Lookup word
        result = vocab_service.lookup_word(word, user.UserID)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@vocab_bp.route('/history', methods=['GET'])
def history():
    """Lấy lịch sử từ vựng đã tra"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        result = vocab_service.get_user_vocabulary_history(user.UserID)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
