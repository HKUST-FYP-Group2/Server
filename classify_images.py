from flask import Flask, request
from flask_cors import CORS
import dotenv
import os
import base64
import requests

dotenv.load_dotenv()
from db import DatabaseManager

app = Flask(__name__)

dbManager = DatabaseManager('database.db')

IMAGE_DIRECTORY = "images"  # this is a temporary container, it holds all the images, which needs to be classified
os.makedirs(IMAGE_DIRECTORY, exist_ok=True)

@app.before_request
def before_request(): # whenever the app is on, the database connection is open
    dbManager.start()
    app.logger.info('Database connection opened.')

@app.teardown_request
def teardown_request(exception):
    dbManager.stop()
    app.logger.error(exception)
    
app.secret_key = os.getenv("SECRET_KEY")  # Change this to a random secret key

CORS(app)

AI_model_URL = os.getenv("AI_MODEL_URL")  # Load AI model URL from environment

API_KEY = os.getenv("API_KEY")  # Load API key from environment
sessions = {}  # Dictionary to store session tokens (Token -> Client IP)

@app.route('/request_image', methods=['POST'])
def send_image():
    """Send an image only if the session token is valid."""
    data = request.get_json()
    video_name = data.get('video_name')
    if not video_name:
        return {'error': 'Missing video name'}, 400
    image_paths = data.get('image_paths')
    if not image_paths:
        return {'error': 'Missing image paths'}, 400
    
    image_list = {}
    for image_number, image_path in enumerate(image_paths):
        image_list[f"{video_name}_img{image_number}"] = (base64.encode(open(image_path, "rb").read()))
        
    response = requests.post(f"{AI_model_URL}/classify_image", json=image_list, headers={'API_KEY': API_KEY})
    
    return response.json(), response.status_code
    
if __name__ == '__main__':
    app.run(debug=True, port=8080)