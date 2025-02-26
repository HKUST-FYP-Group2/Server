import uuid

from flask import Flask, request, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_restful import Api, Resource
from flask_socketio import SocketIO, join_room, emit, send, disconnect

from classes.users import users_bp, User
from classes.videos import videos_bp
from db import get_db_connection

app = Flask(__name__)

# Blueprint registrations
app.register_blueprint(users_bp)
app.register_blueprint(videos_bp)

# For user session management
app.secret_key = 'your_secret_key'  # Change this to a random secret key
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this to a secure key

# Setup login manager and JWTManager
login_manager = LoginManager()
login_manager.init_app(app)
jwt = JWTManager(app)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Create tables
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            projector_app_setting TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_name TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(id=user['id'], username=user['username'], password=user['password'])
    return None

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

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and (user['password'] == password):
            user_obj = User(id=user['id'], username=user['username'], password=user['password'])
            login_user(user_obj)

            # Create a token for the authenticated user
            access_token = create_access_token(identity=user['id'])
            print(access_token)
            return {'message': 'Logged in successfully', 'user_id': user['id'], 'token': access_token}, 200
        return {'error': 'Invalid credentials'}, 401

# Leo: changed to JWT
class Status(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()

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

# Setup API
api = Api(app)
api.add_resource(DeviceUUID, '/uuid')
api.add_resource(Login, '/login')
api.add_resource(Status, '/status')
api.add_resource(Logout, '/logout')

#code below added by Leo
# u may tidy up
class QRLogin(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        if not data or 'device_uuid' not in data:
            return {'error': 'Invalid request'}, 400

        username = current_user.username
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        device_uuid = data['device_uuid']
        room = f'device_{device_uuid}'

        if room not in socketio.server.manager.rooms.get('/', {}):
            return {'error': 'Invalid device'}, 400
        access_token = create_access_token(identity=user['id'])

        emit('QRLogin', {'login_success': 'true', 'username': user['username'], 'token': access_token}, room=room, namespace='/')
        disconnect()
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

api.add_resource(QRLogin, '/QRLogin')


class TokenLogin(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()

        if user:
            user_obj = User(id=user['id'], username=user['username'], password=user['password'])
            login_user(user_obj)
            return {'message': 'Logged in successfully', 'user_id': user['id']}, 200
        return {'error': 'Invalid token'}, 401

api.add_resource(TokenLogin, '/token_login')
#---------until here------------

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(msg):
    print('Received message: ' + msg)
    send(msg, broadcast=True)

@socketio.on('login')
def handle_login(data):
    user_id = data['user_id']
    room = f'room_{user_id}'
    join_room(room)
    print(f'User {user_id} joined {room}')
    print(f'{room} has been created')
    # Server Emits login Event Back to Client
    emit('login', {'user_id': user_id}, room=room)


# Run the server
if __name__ == '__main__':
    init_db()
    socketio.run(app, host='localhost', port=8080, debug=True, allow_unsafe_werkzeug=True)