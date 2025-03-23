import sys
sys.path.append("..")
from flask import Blueprint, request, jsonify
from flask_login import login_required
from enum import Enum
from db import dbManager as db

# Create a Blueprint for users
videos_bp = Blueprint('videos', __name__)

class VIDEO_STATE(Enum):
    STORED_UNCLASSIFIED = 1
    STORED_CLASSIFIED = 2
    
    LIVE_UNCLASSIFIED = 3
    LIVE_CLASSIFIED = 4

    DELETED = 5
class Video:
    def __init__(self, id, video_name: str, video_state = VIDEO_STATE.STORED_UNCLASSIFIED):
        self.id = id
        self.video_name = video_name
        self.classification:list[Enum] = None
        self.state = video_state
        self.images_location = None # should only be used when the 

# VIDEO-related functions
@videos_bp.route('/videos', methods=['GET'])
@login_required
def get_all_videos():
    try:
        with db as conn:
            videos = conn.execute('SELECT * FROM videos').fetchall()
        return jsonify([dict(video) for video in videos])
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@videos_bp.route('/videos', methods=['POST'])
@login_required
def create_video():
    try:
        new_video = request.get_json()
        video_name = new_video.get('video_name')

        with db as conn:
            conn.execute('INSERT INTO videos (video_name) VALUES (?)', (video_name,))

        return jsonify(new_video), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@videos_bp.route('/videos/<int:video_id>', methods=['PUT'])
@login_required
def update_video(video_id):
    try:
        updated_data = request.get_json()
        video_name = updated_data.get('video_name')

        with db as conn:
            video = conn.execute('SELECT * FROM videos WHERE id = ?', (video_id,)).fetchone()

            if video is None:
                return jsonify({'error': 'Video not found'}), 404

            conn.execute('UPDATE videos SET video_name = ? WHERE id = ?', (video_name, video_id))

        return jsonify(updated_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@videos_bp.route('/videos/<int:video_id>', methods=['DELETE'])
@login_required
def delete_video(video_id):
    try:
        with db as conn:
            video = conn.execute('SELECT * FROM videos WHERE id = ?', (video_id,)).fetchone()

            if video is None:
                return jsonify({'error': 'Video not found'}), 404

            conn.execute('DELETE FROM videos WHERE id = ?', (video_id,))

        return jsonify({'message': f'Successfully deleted video with ID = {video_id}'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@videos_bp.route('/videos', methods=['DELETE'])
@login_required
def delete_all_videos():
    try:
        with db as conn:
            conn.execute('DELETE FROM videos')
            
        return jsonify({'message': 'Successfully deleted all videos'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400