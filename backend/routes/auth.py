import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from flask import Blueprint, request, jsonify, session
from backend.app_context import auth_service

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        tai_khoan = data.get('tai_khoan', '').strip()
        mat_khau = data.get('mat_khau', '')
        ho_ten = data.get('ho_ten', '').strip()
        
        if not tai_khoan or not mat_khau or not ho_ten:
            return jsonify({
                'success': False, 
                'error': 'Vui lòng điền đầy đủ thông tin'
            }), 400
        
        result = auth_service.register(tai_khoan, mat_khau, ho_ten)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        tai_khoan = data.get('tai_khoan', '').strip()
        mat_khau = data.get('mat_khau', '')
        
        if not tai_khoan or not mat_khau:
            return jsonify({
                'success': False,
                'error': 'Vui lòng điền đầy đủ thông tin'
            }), 400
        
        result = auth_service.login(tai_khoan, mat_khau)
        
        if result['success']:
            session['token'] = result['token']
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Đăng xuất"""
    try:
        token = request.headers.get('Authorization') or session.get('token')
        
        if token:
            if token.startswith('Bearer '):
                token = token[7:]
            
            auth_service.logout(token)
        
        session.clear()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/verify', methods=['GET'])
def verify():
    """Verify session token"""
    try:
        token = request.headers.get('Authorization') or session.get('token')
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'No token provided'
            }), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        user = auth_service.verify_session(token)
        
        if user:
            return jsonify({
                'success': True,
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid token'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
