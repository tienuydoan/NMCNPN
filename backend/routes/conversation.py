import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from flask import Blueprint, request, jsonify, session
from backend.app_context import auth_service, llm_service, stt_service, tts_service, db
from database.conversation_db import ConversationDB, MessageDB
from backend.utils.validators import validate_message
import base64

# Create blueprint
conversation_bp = Blueprint('conversation', __name__, url_prefix='/api/conversation')

# Initialize database managers
conversation_db = ConversationDB(db)
message_db = MessageDB(db)

def get_current_user():
    """Helper function to get current user from session"""
    token = request.headers.get('Authorization') or session.get('token')
    if not token:
        return None
    
    if token.startswith('Bearer '):
        token = token[7:]
    
    return auth_service.verify_session(token)

@conversation_bp.route('/new', methods=['POST'])
def new_conversation():
    """Tạo cuộc hội thoại mới"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.get_json() or {}
        mode = data.get('mode', 'text')
        
        if mode not in ['text', 'continuous']:
            mode = 'text'
        
        conversation = conversation_db.create_conversation(user.UserID, mode)
        
        return jsonify({
            'success': True,
            'conversation': conversation.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@conversation_bp.route('/list', methods=['GET'])
def list_conversations():
    """Lấy danh sách hội thoại của user"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conversations = conversation_db.get_user_conversations(user.UserID)
        
        return jsonify({
            'success': True,
            'conversations': [c.to_dict() for c in conversations]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@conversation_bp.route('/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Lấy chi tiết cuộc hội thoại"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conversation = conversation_db.get_conversation(conversation_id)
        
        if not conversation:
            return jsonify({'success': False, 'error': 'Conversation not found'}), 404
        
        if conversation.UserID != user.UserID:
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        
        # Get messages
        messages = message_db.get_conversation_messages(conversation_id)
        
        return jsonify({
            'success': True,
            'conversation': conversation.to_dict(),
            'messages': [
                {
                    'type': msg['type'],
                    'message': msg['message'].to_dict(),
                    'time': msg['time']
                }
                for msg in messages
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@conversation_bp.route('/message/send', methods=['POST'])
def send_message():
    """Gửi tin nhắn (text hoặc audio)"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Check if it's form data (audio) or JSON (text)
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Audio message
            return handle_audio_message(user)
        else:
            # Text message
            return handle_text_message(user)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def handle_text_message(user):
    """Handle text message"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    conversation_id = data.get('conversation_id')
    message_text = data.get('message', '').strip()
    
    if not conversation_id or not message_text:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    # Validate message
    valid, error = validate_message(message_text)
    if not valid:
        return jsonify({'success': False, 'error': error}), 400
    
    # Verify conversation belongs to user
    conversation = conversation_db.get_conversation(conversation_id)
    if not conversation or conversation.UserID != user.UserID:
        return jsonify({'success': False, 'error': 'Invalid conversation'}), 403
    
    # Save user message
    user_msg = message_db.create_user_message(conversation_id, message_text)
    
    # Get conversation history for context
    messages = message_db.get_conversation_messages(conversation_id)
    history = []
    for msg in messages[:-1]:  # Exclude the just-added message
        if msg['type'] == 'user':
            history.append({"role": "user", "content": msg['message'].Message})
        else:
            history.append({"role": "assistant", "content": msg['message'].Message})
    
    # Get AI response
    llm_result = llm_service.chat_completion(
        messages=[{"role": "user", "content": message_text}],
        conversation_history=history
    )
    
    if not llm_result['success']:
        return jsonify({'success': False, 'error': llm_result['error']}), 500
    
    # Save AI message
    ai_msg = message_db.create_ai_message(
        conversation_id,
        llm_result['response'],
        llm_result.get('action_id')
    )
    
    return jsonify({
        'success': True,
        'user_message': user_msg.to_dict(),
        'ai_message': ai_msg.to_dict()
    }), 200

def handle_audio_message(user):
    """Handle audio message (Speech-to-Text)"""
    conversation_id = request.form.get('conversation_id')
    audio_file = request.files.get('audio')
    
    if not conversation_id or not audio_file:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    # Verify conversation
    conversation = conversation_db.get_conversation(int(conversation_id))
    if not conversation or conversation.UserID != user.UserID:
        return jsonify({'success': False, 'error': 'Invalid conversation'}), 403
    
    # Read audio content
    audio_content = audio_file.read()
    
    # Get audio format from filename
    audio_format = audio_file.filename.split('.')[-1] if '.' in audio_file.filename else 'wav'
    
    # Transcribe audio
    stt_result = stt_service.transcribe_audio(audio_content, audio_format)
    
    if not stt_result['success']:
        return jsonify({'success': False, 'error': stt_result['error']}), 500
    
    transcript = stt_result['transcript']
    
    return jsonify({
        'success': True,
        'transcript': transcript,
        'action_id': stt_result.get('action_id')
    }), 200

@conversation_bp.route('/message/tts/<int:message_id>', methods=['GET'])
def text_to_speech(message_id):
    """Convert AI message to speech"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Get AI message
        ai_msg = message_db.get_ai_message(message_id)
        if not ai_msg:
            return jsonify({'success': False, 'error': 'Message not found'}), 404
        
        # Verify user owns this conversation
        conversation = conversation_db.get_conversation(ai_msg.ConversationID)
        if not conversation or conversation.UserID != user.UserID:
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        
        # Generate speech
        tts_result = tts_service.synthesize_speech(ai_msg.Message)
        
        if not tts_result['success']:
            return jsonify({'success': False, 'error': tts_result['error']}), 500
        
        # Read audio file and return as base64
        audio_content = tts_service.get_audio_content(tts_result['audio_path'])
        if not audio_content:
            return jsonify({'success': False, 'error': 'Failed to read audio file'}), 500
        
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
        
        return jsonify({
            'success': True,
            'audio': audio_base64,
            'audio_path': tts_result['audio_path']
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
