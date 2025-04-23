import logging
import pdb
import os
from datetime import datetime
from collections import Counter
from pathlib import Path

from AI_Adapter.classify_images import send_image
from AI_Adapter.video_classifier_adapter import extract_images_from_video
from flask_app.db import dbManager, videos_SCHEMA
from flask import Flask
from flask_jwt_extended import create_access_token
from flask_login import current_user

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("video_checker.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def get_stream_key():
    try:
        logger.info("Attempting to retrieve stream key.")
        user_id = current_user.get_id()
        logger.debug(f"Current user ID: {user_id}")

        app = Flask(__name__)
        with app.app_context():
            with app.test_client() as client:
                headers = {
                    "Authorization": f"Bearer {create_access_token(identity=user_id)}"
                }
                response = client.get(f"/users/{user_id}/sk", headers=headers)

            if response.status_code != 200:
                logger.error("Failed to retrieve stream key.")
                raise ValueError("Failed to retrieve stream key")

            stream_key = response.get_json().get("stream_key")
            if not stream_key:
                logger.error("Stream key not found.")
                raise ValueError("Stream key not found")

            logger.info("Stream key retrieved successfully.")
            return stream_key
    except Exception as e:
        logger.exception("Error retrieving stream key.")
        raise ValueError(f"Error retrieving stream key: {str(e)}")


try:
    stream_key = get_stream_key()
    CHECK_DIR = f"/home/user/recordings/{stream_key}"
    logger.info(f"CHECK_DIR set to: {CHECK_DIR}")
except ValueError as e:
    logger.error(f"Error: {e}")
    CHECK_DIR = "/home/user/recordings"
    logger.info(f"CHECK_DIR set to fallback directory: {CHECK_DIR}")

IMAGE_DIR = "/home/user/images/"
CRON_PERIOD = 60 * 10  # 10 minutes


def get_video_name_after_prev_run(video_dir: str, cron_period: int):
    logger.info(f"Fetching video files modified in the last {cron_period} seconds.")
    current_time = datetime.now()
    files_need_updating = []
    for file in os.listdir(video_dir):
        if file.endswith(".mp4"):
            if (
                os.path.getmtime(os.path.join(video_dir, file))
                > current_time.timestamp() - cron_period
            ):
                files_need_updating.append(file)
    logger.info(f"Files needing update: {files_need_updating}")
    return files_need_updating


def download_images_of_video(video_name: str):
    logger.info(f"Downloading images for video: {video_name}")
    video_file = os.path.join(CHECK_DIR, video_name)
    dir_name = Path(video_file).stem
    output_dir = os.path.join(IMAGE_DIR, dir_name)
    output_dir = extract_images_from_video(video_file, output_dir, 0.1)
    logger.info(f"Images extracted to: {output_dir}")
    return output_dir


def get_majority_classification(classifications):
    logger.info("Calculating majority classification.")
    cold_hot = Counter(
        [int(classification["cold-hot"]) for classification in classifications]
    ).most_common(1)[0][0]
    dry_wet = Counter(
        [int(classification["dry-wet"]) for classification in classifications]
    ).most_common(1)[0][0]
    clear_cloudy = Counter(
        [int(classification["clear-cloudy"]) for classification in classifications]
    ).most_common(1)[0][0]
    calm_stormy = Counter(
        [int(classification["calm-stormy"]) for classification in classifications]
    ).most_common(1)[0][0]
    logger.info("Majority classification calculated.")
    return cold_hot, dry_wet, clear_cloudy, calm_stormy


if __name__ == "__main__":
    logger.info("Starting video processing.")
    video_files = get_video_name_after_prev_run(CHECK_DIR, CRON_PERIOD)
    for video_name in video_files:
        try:
            logger.info(f"Processing video: {video_name}")
            image_dir = download_images_of_video(video_name)
            image_paths = [
                os.path.join(image_dir, image) for image in os.listdir(image_dir)
            ]
            response, status_code = send_image(video_name, image_paths)

            if status_code != 200:
                logger.error(f"Error in send_image response: {response}")
                continue

            keywords: list[str] = response.get("keywords", ["", ""])
            description: str = response.get("description", "")
            images: dict = response.get("images", {})

            video_path = os.path.join(CHECK_DIR, video_name)
            classification_dict = []
            for key in images.keys():
                classification_dict.append(response["images"][key])
            cold_hot, dry_wet, clear_cloudy, calm_stormy = get_majority_classification(
                classification_dict
            )
            new_video_name = f'{Path(video_name).stem}_{response["weather_word"]}{Path(video_name).suffix}'
            new_video_path = os.path.join(CHECK_DIR, new_video_name)
            os.rename(video_path, new_video_path)
            logger.info(f"Renamed video to: {new_video_name}")

            table_insert = videos_SCHEMA(
                user_id=current_user.get_id(),
                video_name=new_video_name,
                location=os.path.join(CHECK_DIR, video_name),
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                url=new_video_path,
                description=description,
                keyword1=keywords[0],
                keyword2=keywords[1],
                cold_hot=cold_hot,
                dry_wet=dry_wet,
                clear_cloudy=clear_cloudy,
                calm_stormy=calm_stormy,
            )

            with dbManager as conn:
                cursor = conn.execute(
                    """
                INSERT INTO videos (user_id, video_name, location, created_at, url, description, keyword1, keyword2, cold_hot, dry_wet, clear_cloudy, calm_stormy)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    tuple(table_insert.model_dump().values()),
                )
            logger.info(f"Video {new_video_name} inserted into database.")
        except Exception as e:
            logger.exception(f"Error processing video {video_name}: {e}")
