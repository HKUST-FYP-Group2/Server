from flask import request
from flask_restful import Resource
import uuid
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import login_user, logout_user
from flask_jwt_extended import create_access_token
from flask_socketio import join_room, emit

from flask_app.db import dbManager
from flask_app.classes.users import User
from flask_app.logger import common_logger

class DeviceUUID(Resource):
    def get(self):
        random_uuid = uuid.uuid4()
        return {'uuid': str(random_uuid)}

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']
        projector_app_setting = data.get('projector_app_setting')

        if not projector_app_setting:
            video_link = 'retrieved from server action?'

        with dbManager as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user and (user['password'] == password):
            user_obj = User(id=user['id'], username=user['username'], password=user['password'])
            login_user(user_obj)

            # Create a token for the authenticated user
            access_token = create_access_token(identity=user['id'])
            common_logger.info(f'Access token created: {access_token}')
            return {'message': 'Logged in successfully', 'user_id': user['id'], 'token': access_token}, 200
        return {'error': 'Invalid credentials'}, 401

# Leo: changed to JWT
class Status(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        with dbManager as conn:
            user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

        if user:
            return {
                'logged_in': True,
                'username': user['username'],
                'password': user['password'],
                'user_id': user['id']
            }, 200
        else:
            return {'logged_in': False}, 401

#Leo: I think the logout_user function is only for flask-login which is session, but not JWT
class Logout(Resource):
    @jwt_required()
    def post(self):
        logout_user()
        return {'message': 'Logged out successfully'}, 200
    
class QRLogin(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        if not data or 'device_uuid' not in data:
            return {'error': 'Invalid request'}, 400

        user_id = get_jwt_identity()
        device_uuid = data['device_uuid']
        room = f'device_{device_uuid}'

        # Check if the room exists before emitting
        from config import socketio
        if room not in socketio.server.manager.rooms.get('/', {}):
            return {'error': 'Invalid device'}, 400

        access_token = create_access_token(identity=user_id)
        emit('QRLogin', {'login_success': 'true', 'user_id': user_id, 'token': access_token}, room=room, namespace='/')

        return {}, 200  # Correct return format


def QRLogin_socketIO(data):
    common_logger.info(f'QRLogin_socketIO data: {data}')
    if not data or 'device_uuid' not in data:
        return
    device_uuid = data['device_uuid']
    room = f'device_{device_uuid}'
    join_room(room)
    emit('QRLogin', {'uuid': device_uuid, 'login_success': 'false'}, room=room)

@jwt_required()
def SyncSetting_socketIO(data):
    common_logger.info(f'SyncSetting_socketIO data: {data}')
    user_id = get_jwt_identity()
    room = f'room_{user_id}'
    join_room(room)
    emit('SyncSetting', data, room=room)

