from flask import Flask, request, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from classes.users import users_bp, User
from classes.videos import videos_bp, Video
from db import get_db_connection
from flask_jwt_extended import JWTManager, create_access_token
from flask_cors import CORS
import uuid

app = Flask(__name__)

# blueprint registrations
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

@app.route('/uuid', methods=['GET'])
def device_uuid():
    random_uuid = uuid.uuid4()
    return jsonify(random_uuid)

# uuid --> connect with web socket url
# log in-out logics
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        user_obj = User(id=user['id'], username=user['username'], password=user['password'])
        login_user(user_obj)

        # Create a token for the authenticated user
        access_token = create_access_token(identity=user['id'])

        return jsonify({'message': 'Logged in successfully', 'user_id': user['id'], 'token': access_token}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/status', methods=['GET'])
def status():
    if current_user.is_authenticated:
        return jsonify({'logged_in': True, 'username': current_user.username, 'user_id': current_user.get_id()}), 200
    else:
        return jsonify({'logged_in': False}), 200
    
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

# Run the server
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port ='5000', debug=True) # specify the server host/port and activate debug mode here
