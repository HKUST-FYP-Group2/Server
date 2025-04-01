import os
from datetime import datetime
from collections import Counter
from pathlib import Path

from AI_Adapter.classify_images import send_image
from AI_Adapter.video_classifier_adapter import extract_images_from_video
from flask_app.db import dbManager

CHECK_DIR = "/home/user/recordings"
IMAGE_DIR = "/home/user/images/"
CRON_PERIOD = 60*10  # 10 minutes

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
    cold_hot = Counter([classification['cold_hot'] for classification in classifications]).most_common(1)[0][0]
    dry_wet = Counter([classification['dry_wet'] for classification in classifications]).most_common(1)[0][0]
    clear_cloudy = Counter([classification['clear_cloudy'] for classification in classifications]).most_common(1)[0][0]
    calm_stormy = Counter([classification['calm_stormy'] for classification in classifications]).most_common(1)[0][0]
    return cold_hot, dry_wet, clear_cloudy, calm_stormy

if __name__ == "__main__":
    video_files = get_video_name_after_prev_run(CHECK_DIR, CRON_PERIOD)
    for video_name in video_files:
        image_dir = download_images_of_video(video_name)
        image_paths = [os.path.join(image_dir, image) for image in os.listdir(image_dir)]
        response, status_code = send_image(video_name, image_paths)
        if status_code != 200:
            print(f"Error: {response}") # basic error handling
            continue
        video_path = os.path.join(CHECK_DIR, video_name)
        with dbManager as conn:
            id = conn.execute('''
                INSERT INTO videos (video_name, location, created_at, URL)
                VALUES (?, ?, ?, ?)
                RETURNING id'''
                , (video_name, video_path, os.path.getmtime(video_path), f"https://virtualwindow.cam/recordings/{video_name}"))
            id = id.fetchone()[0]
            hot_cold, dry_wet, clear_cloudy, calm_stormy = get_majority_classification(response.json())
            conn.execute('''
                INSERT INTO video_classification (video_id, cold_hot, dry_wet, clear_cloudy, calm_stormy)
                VALUES (?, ?, ?, ?, ?)'''
                , (id, response['cold_hot'], response['dry_wet'], response['clear_cloudy'], response['calm_stormy']))