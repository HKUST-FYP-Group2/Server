from flask import Flask, request
from flask_cors import CORS
from pydantic import BaseModel, Field, field_validator
import os
import base64
import requests
import dotenv

dotenv.load_dotenv(override=True)

AI_model_URL = os.getenv("AI_SERVER_URL")  # Load AI server URL from environment
API_KEY = os.getenv("AI_SERVER_VALID_API_KEY")  # Load API key from environment
class SENDIMAGE_SCHEMA(BaseModel):
    video_name: str = Field(min_length=1)
    image_paths: list = Field(min_items=1)
    
    @field_validator('image_paths')
    def check_image_paths(cls, value):
        for image_path in value:
            if not os.path.isfile(image_path):
                raise ValueError('Invalid image path')
        return value
    

def send_image(video_name, image_paths):
    """Send an image only if the session token is valid."""
    if AI_model_URL is None or API_KEY is None:
        return {"error": "AI server URL or API key is not set"}, 500
    image_list = {}
    for image_number, image_path in enumerate(image_paths):
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            image_list[f"{video_name}_img{image_number}"] = encoded_image
    input_data = {"num_images": len(image_paths), "images": image_list}

    response = requests.post(f"{AI_model_URL}/classify_images", json=input_data, headers={'API-KEY': API_KEY})
    
    return response, response.status_code