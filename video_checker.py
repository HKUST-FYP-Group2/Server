import pdb
import os
from datetime import datetime
from collections import Counter
from pathlib import Path
from pydantic import BaseModel

from AI_Adapter.classify_images import send_image
from AI_Adapter.video_classifier_adapter import extract_images_from_video
from flask_app.db import dbManager, videos_SCHEMA
import requests
import sqlite3
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_dir = "/home/user/recordings/"
stream_keys = [folder for folder in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, folder))]

def get_user_id_mapping():
    user_id_mapping = {}
    for stream_key in stream_keys:
        # Call the API to get user ID by stream key
        response = requests.post('https://localhost:8000/users/sk', json={'stream_key': stream_key}, verify=False)

        # Parse the response
        if response.status_code == 200:
            user_id = (response.json().get('user_id'))
            user_id_mapping[stream_key] = user_id
        else:
            print(f"Error: Failed to retrieve user ID for stream key {stream_key}")

    return user_id_mapping

def get_video_name_after_prev_run(video_dir:str, cron_period:int):
    current_time = datetime.now()
    files_need_updating = []
    for file in os.listdir(video_dir):
        if file.endswith(".mp4"):
            if os.path.getmtime(os.path.join(video_dir, file)) > current_time.timestamp() - cron_period:
                files_need_updating.append(file)
    return files_need_updating

def download_images_of_video(video_name:str):
    video_file = os.path.join(CHECK_DIR, video_name)
    dir_name = Path(video_file).stem
    output_dir = os.path.join(IMAGE_DIR, dir_name)
    output_dir = extract_images_from_video(video_file, output_dir)
    return output_dir

def get_majority_classification(classifications):
    cold_hot = Counter([int(classification['cold-hot'] )for classification in classifications]).most_common(1)[0][0]
    dry_wet = Counter([int(classification['dry-wet']) for classification in classifications]).most_common(1)[0][0]
    clear_cloudy = Counter([int(classification['clear-cloudy']) for classification in classifications]).most_common(1)[0][0]
    calm_stormy = Counter([int(classification['calm-stormy']) for classification in classifications]).most_common(1)[0][0]
    return cold_hot, dry_wet, clear_cloudy, calm_stormy

user_id_mapping = get_user_id_mapping()

IMAGE_DIR = "/home/user/images/"
CRON_PERIOD = 60*10 # 10 minutes
URL_PREFIX = "https://virtualwindow.cam/recordings"

if __name__ == "__main__":
    # pdb.set_trace()
    for stream_key in stream_keys:

        CHECK_DIR = f"/home/user/recordings/{stream_key}"
        user_id = user_id_mapping.get(stream_key, None)

        video_files = get_video_name_after_prev_run(CHECK_DIR, CRON_PERIOD)

        for video_name in video_files:
            # Check if the video_name already exists in the database
            with dbManager as conn:
                existing_video = conn.execute('SELECT id FROM videos WHERE video_name = ?', (video_name,)).fetchone()

            if existing_video:
                print(f"Skipping {video_name}: already exists in the database.")
                continue

            image_dir = download_images_of_video(video_name)
            image_paths = [os.path.join(image_dir, image) for image in os.listdir(image_dir)]
            response, status_code = send_image(video_name, image_paths)

            if status_code != 200:
                print(f"Error: {response}")  # basic error handling
                continue

            video_path = os.path.join(CHECK_DIR, video_name)
            classification_dict = []
            for key in response.keys():
                classification_dict.append(response[key])
            cold_hot, dry_wet, clear_cloudy, calm_stormy = get_majority_classification(classification_dict)

            try:
                with dbManager as conn:
                    cursor = conn.execute('''
                    INSERT INTO videos (user_id, video_name, location, created_at, url, cold_hot, dry_wet, clear_cloudy, calm_stormy)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (user_id, video_name, os.path.join(CHECK_DIR, video_name), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                        f"{URL_PREFIX}/{stream_key}/{video_name}", cold_hot, dry_wet, clear_cloudy, calm_stormy))
            
            except sqlite3.IntegrityError as e:
                print(f"Error inserting {video_name}: {e}")

