import sys
sys.path.append("..")
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from db import get_db_connection
from flask_login import login_required, UserMixin

# Create a Blueprint for users
users_bp = Blueprint('users', __name__)

# User model for flask_login
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# USER-related function
@users_bp.route('/users', methods=['GET'])
@login_required
def get_all_users():
    try:
        conn = get_db_connection()
        users = conn.execute('SELECT * FROM users').fetchall()
        conn.close()
        return jsonify([dict(user) for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@users_bp.route('/users/<int:user_id>/pjt', methods=['GET'])
@login_required
def get_pjt_setting_ByUserId(user_id):
    try:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        settings = user['projector_app_setting']
        
        if not settings:
            return jsonify({'error': 'No projector settings found for this user'}), 404
        
        conn.close()
        return jsonify(settings)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@users_bp.route('/users', methods=['POST'])
def create_user():
    try:
        new_user = request.get_json()
        username = new_user['username']
        password = new_user['password']
        settings = new_user.get('projector_app_setting')

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, password, projector_app_setting) VALUES (?, ?, ?)', 
                     (username, hashed_password, settings))
        conn.commit()
        conn.close()

        return jsonify(new_user), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
        
@users_bp.route('/users/<int:user_id>/pjt', methods=['PUT'])
@login_required
def update_PJT_ByUserId(user_id):
    try:
        updated_data = request.get_json()
        settings = updated_data.get('projector_app_setting')

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

        if user is None:
            return jsonify({'error': 'User not found'}), 404

        # Update only the projector_app_setting if it is provided.
        if settings:
            conn.execute('UPDATE users SET projector_app_setting = ? WHERE id = ?', 
                         (settings, user_id))
            conn.commit()

        conn.close()

        return jsonify({'projector_app_setting': settings}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user_ByUserId(user_id):
    try:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

        if user is None:
            return jsonify({'error': 'User not found'}), 404

        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()

        return jsonify({'message': f'Successfully deleted user with ID = {user_id}'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# git remote add origin https://github.com/HKUST-FYP-Group2/Server.git
# git branch -M main
# git push -u origin main