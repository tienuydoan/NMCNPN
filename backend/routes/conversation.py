import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from flask import Blueprint, request, jsonify, session
from backend.app_context import auth_service, llm_service, stt_service, tts_service, db
from database.conversation_db import ConversationDB, MessageDB
from backend.utils.validators import validate_message
import base64

conversation_bp = Blueprint('conversation', __name__, url_prefix='/api/conversation')

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
    try:
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        if request.content_type and 'multipart/form-data' in request.content_type:
            return handle_audio_message(user)
        else:
            return handle_text_message(user)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def handle_text_message(user):
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    conversation_id = data.get('conversation_id')
    message_text = data.get('message', '').strip()
    
    if not conversation_id or not message_text:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    valid, error = validate_message(message_text)
    if not valid:
        return jsonify({'success': False, 'error': error}), 400
    
    conversation = conversation_db.get_conversation(conversation_id)
    if not conversation or conversation.UserID != user.UserID:
        return jsonify({'success': False, 'error': 'Invalid conversation'}), 403
    
    user_msg = message_db.create_user_message(conversation_id, message_text)
    
    messages = message_db.get_conversation_messages(conversation_id)
    history = []
    for msg in messages[:-1]:
        if msg['type'] == 'user':
            history.append({"role": "user", "content": msg['message'].Message})
        else:
            history.append({"role": "assistant", "content": msg['message'].Message})
    
    llm_result = llm_service.chat_completion(
        messages=[{"role": "user", "content": message_text}],
        conversation_history=history
    )
    
    if not llm_result['success']:
        return jsonify({'success': False, 'error': llm_result['error']}), 500
    
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
    
    conversation = conversation_db.get_conversation(int(conversation_id))
    if not conversation or conversation.UserID != user.UserID:
        return jsonify({'success': False, 'error': 'Invalid conversation'}), 403
    
    audio_content = audio_file.read()
    
    audio_format = audio_file.filename.split('.')[-1] if '.' in audio_file.filename else 'wav'
    
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
        
        ai_msg = message_db.get_ai_message(message_id)
        if not ai_msg:
            return jsonify({'success': False, 'error': 'Message not found'}), 404
        
        conversation = conversation_db.get_conversation(ai_msg.ConversationID)
        if not conversation or conversation.UserID != user.UserID:
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        
        tts_result = tts_service.synthesize_speech(ai_msg.Message)
        
        if not tts_result['success']:
            return jsonify({'success': False, 'error': tts_result['error']}), 500
        
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
