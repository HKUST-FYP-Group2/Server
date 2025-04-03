from flask import Blueprint, request
from flask_login import current_user, UserMixin
from flask_jwt_extended import create_access_token, jwt_required
from flask_restful import Api, Resource
import json

from flask_app.db import dbManager

# Create a Blueprint for users
users_bp = Blueprint('users', __name__)
api = Api(users_bp)

# User model for flask_login
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# User resource for RESTful API
class UserResource(Resource):
    @jwt_required()
    def get(self, user_id):
        """Get a user by ID."""
        try:
            with dbManager as conn:
                user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

            if user is None:
                return ({'error': 'User not found'}), 404
            
            access_token = create_access_token(identity=current_user.get_id())
            return ({
                'user': dict(user),
                'token': access_token
            }), 200
        except Exception as e:
            return ({'error': str(e)}), 400

    @jwt_required()
    def delete(self, user_id):
        """Delete a user by ID."""
        try:
            with dbManager as conn:
                user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

                if user is None:
                    return ({'error': 'User not found'}), 404

                conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
                conn.commit()

            access_token = create_access_token(identity=current_user.get_id())
            return ({
                'message': f'Successfully deleted user with ID = {user_id}',
                'token': access_token
            }), 200
        except Exception as e:
            return ({'error': str(e)}), 400

class UserListResource(Resource):
    @jwt_required()
    def get(self):
        """Get all users."""
        try:
            with dbManager as conn:
                users = conn.execute('SELECT * FROM users').fetchall()
            
            access_token = create_access_token(identity=current_user.get_id())
            return ({
                'users': [dict(user) for user in users],
                'token': access_token
            }), 200
        except Exception as e:
            return ({'error': str(e)}), 400

    def post(self):
        """Create a new user."""
        try:
            new_user = request.get_json()
            username = new_user['username']
            password = new_user['password']
            settings = new_user.get('projector_app_setting')
            stream_key = new_user.get('stream_key')

            with dbManager as conn:
                conn.execute('INSERT INTO users (username, password, projector_app_setting, stream_key) VALUES (?, ?, ?, ?)', 
                            (username, password, settings, stream_key))
                conn.commit()

            access_token = create_access_token(identity=username)
            return ({'message': 'A new user has been successfully created', 'token': access_token}), 201
        except Exception as e:
            return ({'error': str(e)}), 400

# Projector settings resource
class ProjectorSettingsResource(Resource):
    @jwt_required()
    def get(self, user_id):
        """Get projector settings for a user by ID."""
        try:
            with dbManager as conn:
                user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
                settings_json = user['projector_app_setting']

            if not settings_json:
                return ({'error': 'No projector settings found for this user'}), 400

            # Parse JSON string back to dictionary
            settings = json.loads(settings_json)

            access_token = create_access_token(identity=current_user.get_id())
            return ({
                'settings': settings,
                'token': access_token
            }), 200
        except Exception as e:
            return ({'error': str(e)}), 400

    @jwt_required()
    def put(self, user_id):
        """Update projector settings for a user by ID."""
        try:
            updated_data = request.get_json()
            settings = updated_data.get('projector_app_setting')

            with dbManager as conn:
                user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

                if user is None:
                    return ({'error': 'User not found'}), 404

                if settings:
                    settings_json = json.dumps(settings)
                    conn.execute('UPDATE users SET projector_app_setting = ? WHERE id = ?',
                                (settings_json, user_id))
                    conn.commit()

            access_token = create_access_token(identity=current_user.get_id())
            return ({
                'projector_app_setting': settings,
                'token': access_token
            }), 200
        except Exception as e:
            return ({'error': str(e)}), 200

# Projector settings resource
class StreamKeyResource(Resource):
    @jwt_required()
    def get(self, user_id):
        """Get stream key for a user by ID."""
        try:
            with dbManager as conn:
                user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
                stream_key = user['stream_key']

            if not stream_key:
                return ({'error': 'No stream key found for this user'}), 400

            access_token = create_access_token(identity=current_user.get_id())
            return ({
                'stream_key': stream_key,
                'token': access_token
            }), 200
        except Exception as e:
            return ({'error': str(e)}), 400

    @jwt_required()
    def put(self, user_id):
        """Update stream key for a user by ID."""
        try:
            updated_data = request.get_json()
            stream_key = updated_data.get('stream_key')

            with dbManager as conn:
                user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

                if user is None:
                    return ({'error': 'User not found'}), 404

                if stream_key:
                    conn.execute('UPDATE users SET stream_key = ? WHERE id = ?',
                                (stream_key, user_id))
                    conn.commit()

            access_token = create_access_token(identity=current_user.get_id())
            return ({
                'stream_key': stream_key,
                'token': access_token
            }), 200
        except Exception as e:
            return ({'error': str(e)}), 200
        
    @jwt_required()
    def post(self):
        """Get user ID by stream key."""
        try:
            data = request.get_json()
            stream_key = data.get('stream_key')

            if not stream_key:
                return ({'error': 'Stream key is required'}), 400

            with dbManager as conn:
                user = conn.execute('SELECT id FROM users WHERE stream_key = ?', (stream_key,)).fetchone()

            if user is None:
                return ({'error': 'No user found with this stream key'}), 404

            access_token = create_access_token(identity=current_user.get_id())
            return ({
                'user_id': user['id'],
                'token': access_token
            }), 200
        except Exception as e:
            return ({'error': str(e)}), 400
    

# Register the resources with the API
api.add_resource(UserListResource, '/users')
api.add_resource(UserResource, '/users/<int:user_id>')
api.add_resource(ProjectorSettingsResource, '/users/<int:user_id>/pjt')
api.add_resource(StreamKeyResource, '/users/<int:user_id>/sk', '/users/sk')

