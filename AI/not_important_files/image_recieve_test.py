import socketio
import base64

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print("Connected to WebSocket server.")

@sio.on('receive_image')
def receive_image(data):
    """Receives an image from the server."""
    print(f"Received image from server: {data['filename']}")

    # Decode Base64 string to binary
    image_data = base64.b64decode(data['image'])

    # Save received image
    with open(f"downloaded_{data['filename']}", "wb") as file:
        file.write(image_data)
    print(f"Image saved as downloaded_{data['filename']}")

@sio.on('error')
def handle_error(data):
    """Handles error messages from the server."""
    print("Error:", data['message'])

def send_image(filename):
    """Sends an image to the server with a specified filename."""
    try:
        with open(filename, "rb") as file:
            image_data = base64.b64encode(file.read()).decode('utf-8')

        sio.emit('send_image', {'image': image_data, 'filename': filename})
        print(f"Sent image {filename} to server.")
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")

def request_image(filename):
    """Requests an image from the server by filename."""
    sio.emit('request_image', {'filename': filename})
    print(f"Requested image {filename} from server.")

# Connect to the server
try:
    sio.connect('http://localhost:8080')
except socketio.exceptions.ConnectionError as e:
    print(f"Connection failed: {e}")

# Example: Send an image to the server
# send_image("test_image.jpg")  # Replace with an actual image file

# Example: Request an image from the server
request_image("200.jpg")

sio.wait()
