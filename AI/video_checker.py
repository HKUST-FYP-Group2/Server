import os
from datetime import datetime

from AI.classify_images import send_image
from AI.Adapter.video_classifier_adapter import extract_images_from_video
from flask.db import dbManager

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
    output_dir = os.path.join(IMAGE_DIR, video_name)
    output_dir = extract_images_from_video(video_file, output_dir)
    return output_dir
    

if __name__ == "__main__":
    video_files = get_video_name_after_prev_run(CHECK_DIR, CRON_PERIOD)
    for video_name in video_files:
        image_dir = download_images_of_video(video_name)
        image_paths = [os.path.join(image_dir, image) for image in os.listdir(image_dir)]
        response, status_code = send_image(video_name, image_paths)
        
        video_path = os.path.join(CHECK_DIR, video_name)
        with dbManager as conn:
            id = conn.execute('''
                INSERT INTO videos (video_name, location, created_at, URL)
                VALUES (?, ?, ?, ?)
                RETURNING id'''
                , (video_name, video_path, os.path.getmtime(video_path), f"https://virtualwindow.cam/recordings/{video_name}"))
            id = id.fetchone()[0]
            conn.execute('''
                INSERT INTO video_classification (video_id, cold_hot, dry_wet, clear_cloudy, calm_stormy)
                VALUES (?, ?, ?, ?, ?)'''
                , (id, response['cold_hot'], response['dry_wet'], response['clear_cloudy'], response['calm_stormy']))