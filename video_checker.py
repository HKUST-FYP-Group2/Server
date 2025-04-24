import logging
import pdb
import os
from datetime import datetime
from collections import Counter
from pathlib import Path

from AI_Adapter.classify_images import send_image
from AI_Adapter.video_classifier_adapter import extract_images_from_video
from flask_app.db import dbManager, videos_SCHEMA
from flask_login import current_user

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("video_checker.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


CHECK_DIRS = [
    f"/home/user/recordings/{dir}"
    for dir in os.listdir("/home/user/recordings")
    if "_key" in dir
]  # very simple check for now
IMAGE_DIR = "/home/user/images/"
CRON_PERIOD = 60 * 10  # 10 minutes


def get_video_name_after_prev_run(video_dirs: list[str], cron_period: int) -> list[str]:
    logger.info(f"Fetching video files modified in the last {cron_period} seconds.")
    current_time = datetime.now()
    files_need_updating = []
    for video_dir in video_dirs:
        for file in os.listdir(video_dir):
            if not file.endswith(".mp4"):
                continue
            video_abs_path = os.path.abspath(os.path.join(video_dir, file))
            if (
                os.path.getmtime(video_abs_path)
                > current_time.timestamp() - cron_period
            ):
                files_need_updating.append(video_abs_path)
        logger.info(f"Files needing update: {files_need_updating}")
    return files_need_updating


def download_images_of_video(video_name: str):
    logger.info(f"Downloading images for video: {video_name}")
    dir_name = Path(video_name).stem
    output_dir = os.path.join(IMAGE_DIR, dir_name)
    # adjusted this to 1 image per 10 seconds, but I think can be reduced even further
    output_dir = extract_images_from_video(video_name, output_dir, 0.1)

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
    # pdb.set_trace()
    logger.info("Starting video processing.")
    video_paths = get_video_name_after_prev_run(CHECK_DIRS, CRON_PERIOD)
    for video_path in video_paths:
        try:
            logger.info(f"Processing video: {video_path}")
            image_dir = download_images_of_video(video_path)
            image_paths = [
                os.path.join(image_dir, image) for image in os.listdir(image_dir)
            ]
            response, status_code = send_image(video_path, image_paths)

            if status_code != 200:
                logger.error(f"Error in send_image response: {response}")
                continue

            keywords: list[str] = response.get("keywords", ["", ""])
            description: str = response.get("description", "")
            images: dict = response.get("images", {})

            classification_dict = []
            for key in images.keys():
                classification_dict.append(response["images"][key])
            cold_hot, dry_wet, clear_cloudy, calm_stormy = get_majority_classification(
                classification_dict
            )

            key_type = video_path.split("_key")[0]

            user_id = None
            with dbManager as conn:
                user_id = conn.execute(
                    """
                    SELECT id FROM users WHERE username = ?
                                       """
                ).fetchone()

            new_video_path = video_path.replace(
                ".mp4", f"_{response["weather_word"]}.mp4"
            )
            os.rename(video_path, new_video_path)
            logger.info(f"Renamed video to: {new_video_path}")

            table_insert = videos_SCHEMA(
                user_id=user_id,
                video_name=Path(new_video_path).stem,
                location=new_video_path,
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
            logger.info(f"Video {new_video_path} inserted into database.")
        except Exception as e:
            logger.exception(f"Error processing video {video_path}: {e}")
