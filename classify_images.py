from flask import Flask, request, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, emit, send, disconnect
import dotenv
import os
import base64

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
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('send_image')
def handle_image(data):
    """
    Handles receiving an image from the client.
    Data should be a base64 encoded image string.
    """
    print("Received image from client.")

    # Decode the base64 image
    image_data = base64.b64decode(data['image'])

    # Save the image with the given filename
    filename = data.get('filename', 'received_image.jpg')
    file_path = os.path.join(IMAGE_DIRECTORY, filename)

    with open(file_path, "wb") as file:
        file.write(image_data)

    print(f"Image saved as {file_path}")

    # Send confirmation
    emit('image_saved', {'message': f'Image {filename} saved successfully'})
    
    
if __name__ == '__main__':
    socketio.run(app, host='localhost', port=81, debug=True)