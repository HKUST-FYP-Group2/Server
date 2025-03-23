from flask import Flask, request
from flask_cors import CORS
from pydantic import BaseModel, Field, field_validator
import dotenv
import os
import base64
import requests

dotenv.load_dotenv()

app = Flask(__name__)    
app.secret_key = os.getenv("SECRET_KEY")  # Change this to a random secret key

CORS(app)

AI_model_URL = os.getenv("AI_MODEL_URL")  # Load AI model URL from environment

API_KEY = os.getenv("API_KEY")  # Load API key from environment

class SENDIMAGE_SCHEMA(BaseModel):
    video_name: str = Field(min_length=1)
    image_paths: list = Field(min_items=1)
    
    @field_validator('image_paths')
    def check_image_paths(cls, value):
        for image_path in value:
            if not os.path.isfile(image_path):
                raise ValueError('Invalid image path')
        return value
    

@app.route('/send_images', methods=['GET'])
def send_image():
    """Send an image only if the session token is valid."""
    data = SENDIMAGE_SCHEMA.model_validate_json(request.json)
    
    image_list = {}
    for image_number, image_path in enumerate(data.image_paths):
        image_list[f"{data.video_name}_img{image_number}"] = (base64.encode(open(image_path, "rb").read()))
    input_data = {"num_images": len(data.image_paths), "images": image_list}
    
    response = requests.get(f"{AI_model_URL}/classify_images", json=image_list, headers={'API_KEY': API_KEY})
    
    return response.json(), response.status_code
    
if __name__ == '__main__':
    app.run(debug=True, port=8080)