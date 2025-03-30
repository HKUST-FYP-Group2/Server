import os
from flask import Flask, request, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_login import LoginManager
from flask_restful import Api, Resource
from flask_socketio import SocketIO, join_room, emit, send, disconnect

from flask_app.classes.users import users_bp, User
from flask_app.classes.videos import videos_bp
from flask_app.db import dbManager
from flask_app.logger import common_logger
from flask_app.user_auth import DeviceUUID, Login, Status, Logout, SyncSetting_socketIO

app = Flask(__name__)

# Blueprint registrations
app.register_blueprint(users_bp)
app.register_blueprint(videos_bp)

# For user session management
app.secret_key = os.getenv("SECRET_KEY")  # Change this to a random secret key
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")  # Change this to a secure key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

# Setup login manager and JWTManager
login_manager = LoginManager()
login_manager.init_app(app)
jwt = JWTManager(app)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Create tables

@login_manager.user_loader
def load_user(user_id):
    with dbManager as conn:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if user:
        return User(id=user['id'], username=user['username'], password=user['password'])
    return None

#Leo: i move it back here cuz it cannot get all rooms in user_auth.py
class QRLogin(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        if not data or 'device_uuid' not in data:
            return {'error': 'Invalid request'}, 400

        user_id = get_jwt_identity()
        device_uuid = data['device_uuid']
        room = f'device_{device_uuid}'
        print(socketio.server.manager.rooms)
        if room not in socketio.server.manager.rooms.get('/', {}):
            return {'error': 'Invalid device'}, 400
        access_token = create_access_token(identity=user_id)

        emit('QRLogin', {'login_success': 'true', 'user_id': user_id, 'token': access_token}, room=room, namespace='/')
        return 200

    @socketio.on('QRLogin')
    def QRLogin_socketIO(data):
        print(data)
        if not data or 'device_uuid' not in data:
            return
        device_uuid = data['device_uuid']
        room = f'device_{device_uuid}'
        join_room(room)
        emit('QRLogin', {'uuid': device_uuid, 'login_success': 'false'}, room=room)


# Setup API
api = Api(app)
api.add_resource(DeviceUUID, '/uuid')
api.add_resource(Login, '/login')
api.add_resource(Status, '/status')
api.add_resource(Logout, '/logout')
api.add_resource(QRLogin, '/QRLogin')
#---------until here------------

@app.route('/')
def index():
    print(socketio.server.manager.rooms)
    return render_template('index.html')

@socketio.on('message')
def handle_message(msg):
    common_logger.info('Received message: ' + msg)
    send(msg, broadcast=True)

@socketio.on('login')
def handle_login(data):
    user_id = data['user_id']
    common_logger.info(f'Login data received: {data}')
    room = f'room_{user_id}'
    join_room(room)
    common_logger.info(f'User {user_id} joined {room}')
    common_logger.info(f'{room} has been created')
    # Server Emits login Event Back to Client
    emit('login', {'user_id': user_id}, room=room)

socketio.on('SyncSetting')(SyncSetting_socketIO)

# Run the server
if __name__ == '__main__':
    with dbManager as conn:
        dbManager.init_db()
    # Path to your SSL certificate and key files
    ssl_context = ('./ssl_dynabot/cert.cert', './ssl_dynabot/key.key')
    socketio.run(app, host='0.0.0.0', port=8000, debug=True, ssl_context=ssl_context)
