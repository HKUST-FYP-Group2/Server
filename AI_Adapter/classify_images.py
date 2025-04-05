from pydantic import BaseModel, Field, field_validator
import os
import requests
import dotenv

dotenv.load_dotenv(override=True)

AI_model_URL = "http://127.0.0.1:8080"
API_KEY = os.getenv("AI_SERVER_VALID_API_KEY")  # Load API key from environment

class SENDIMAGE_SCHEMA(BaseModel):
    video_name: str = Field(min_length=1)
    image_paths: list[str] = Field(min_items=1)  # Specify list of strings
    
    @field_validator('image_paths')
    def check_image_paths(cls, value):
        for image_path in value:
            if not os.path.isfile(image_path):
                raise ValueError(f"Invalid image path: {image_path}")
        return value

def send_image(video_name: str, image_paths: list[str]):
    """Send images to the classification API."""
    try:
        validated_data = SENDIMAGE_SCHEMA(video_name=video_name, image_paths=image_paths)

        files = []
        open_files = []  # Store file handles to keep them open

        try:
            for image_number, image_path in enumerate(validated_data.image_paths):
                file = open(image_path, "rb")  # Keep file open
                open_files.append(file)
                files.append((f"files", (f"{video_name}_img{image_number}.jpg", file, 'image/jpeg')))

            response = requests.post(
                f"{AI_model_URL}/classify_images",
                files=files,
                headers={'API-KEY': API_KEY}
            )
            
            response.raise_for_status()
            return response.json(), response.status_code

        finally:
            # Close all file handles after request completes
            for file in open_files:
                file.close()

    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {e}"}, 500
    except ValueError as e:
        return {"error": str(e)}, 400
    
    
# # Example Usage
# response, status_code = send_image(
#     "video1", 
#     ["/home/hvgupta/FYP/test.jpg",]
# )
# print(response)
