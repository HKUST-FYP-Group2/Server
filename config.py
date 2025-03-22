
import os
from flask import Flask, request, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_restful import Api
from flask_socketio import SocketIO, join_room, emit, send, disconnect

from classes.users import users_bp, User
from classes.videos import videos_bp
from db import DatabaseManager
from user_auth import DeviceUUID, Login, Status, Logout, QRLogin

app = Flask(__name__)

dbManager = DatabaseManager('database.db')

@app.before_request
def before_request(): # whenever the app is on, the database connection is open
    dbManager.start()
    app.logger.info('Database connection opened.')

@app.teardown_request
def teardown_request(exception):
    dbManager.stop()
    if exception:
        app.logger.error(exception)
    else:
        app.logger.info('Database connection closed.')

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
    user = dbManager.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if user:
        return User(id=user['id'], username=user['username'], password=user['password'])
    return None


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
    return render_template('index.html')

@socketio.on('message')
def handle_message(msg):
    print('Received message: ' + msg)
    send(msg, broadcast=True)

@socketio.on('login')
def handle_login(data):
    user_id = data['user_id']
    print(data)
    room = f'room_{user_id}'
    join_room(room)
    print(f'User {user_id} joined {room}')
    print(f'{room} has been created')
    # Server Emits login Event Back to Client
    emit('login', {'user_id': user_id}, room=room)

# Run the server
if __name__ == '__main__':
    # Path to your SSL certificate and key files
    ssl_context = ('./ssl_dynabot/cert.cert', './ssl_dynabot/key.key')
    socketio.run(app, host='0.0.0.0', port=8000, debug=True, ssl_context=ssl_context)