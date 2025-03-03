import base64
import os
from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

IMAGE_DIRECTORY = "images"  # Directory where images are stored

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
    if not os.path.exists(IMAGE_DIRECTORY):
        os.makedirs(IMAGE_DIRECTORY)  # Create image directory if it doesn't exist
    socketio.run(app, host='localhost', port=8080, debug=True)
