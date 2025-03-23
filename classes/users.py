from flask import Blueprint, request
from flask_login import current_user, login_required, UserMixin
from flask_jwt_extended import create_access_token
from flask_restful import Api, Resource
from db import dbManager as db

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
    
    @login_required
    def get(self, user_id):
        """Get a user by ID."""
        try:
            with db as conn:
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

    @login_required
    def delete(self, user_id):
        """Delete a user by ID."""
        try:
            with db as conn:
                user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

                if user is None:
                    return ({'error': 'User not found'}), 404

                conn.execute('DELETE FROM users WHERE id = ?', (user_id,))

            access_token = create_access_token(identity=current_user.get_id())
            return ({
                'message': f'Successfully deleted user with ID = {user_id}',
                'token': access_token
            }), 200
        except Exception as e:
            return ({'error': str(e)}), 400

class UserListResource(Resource):
    
    @login_required
    def get(self):
        """Get all users."""
        try:
            with db as conn:
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

            with db as conn:
                conn.execute('INSERT INTO users (username, password, projector_app_setting) VALUES (?, ?, ?)', 
                            (username, password, settings))

            access_token = create_access_token(identity=username)
            return ({'message': 'A new user has been successfully created', 'token': access_token}), 201
        except Exception as e:
            return ({'error': str(e)}), 400

# Projector settings resource
class ProjectorSettingsResource(Resource):
    
    @login_required
    def get(self, user_id):
        """Get projector settings for a user by ID."""
        try:
            with db as conn:
                user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            settings = user['projector_app_setting']
            
            if not settings:
                return ({'error': 'No projector settings found for this user'}), 404
            
            access_token = create_access_token(identity=current_user.get_id())
            return ({
                'settings': settings,
                'token': access_token
            }), 200
        except Exception as e:
            return ({'error': str(e)}), 400

    @login_required
    def put(self, user_id):
        """Update projector settings for a user by ID."""
        try:
            updated_data = request.get_json()
            settings = updated_data.get('projector_app_setting')

            with db as conn:
                user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

                if user is None:
                    return ({'error': 'User not found'}), 404

                # Update only if settings are provided
                if settings:
                    conn.execute('UPDATE users SET projector_app_setting = ? WHERE id = ?', 
                                (settings, user_id))

            access_token = create_access_token(identity=current_user.get_id())
            return ({
                'projector_app_setting': settings,
                'token': access_token
            }), 200
        except Exception as e:
            return ({'error': str(e)}), 400

# Register the resources with the API
api.add_resource(UserListResource, '/users')
api.add_resource(UserResource, '/users/<int:user_id>')
api.add_resource(ProjectorSettingsResource, '/users/<int:user_id>/pjt')
