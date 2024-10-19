import sys
sys.path.append("..")
from flask import Blueprint, request, jsonify
from db import get_db_connection
from flask_login import login_required

# Create a Blueprint for users
videos_bp = Blueprint('videos', __name__)

class Video:
    def __init__(self, id, video_name):
        self.id = id
        self.video_name = video_name

# VIDEO-related functions
@videos_bp.route('/videos', methods=['GET'])
@login_required
def get_all_videos():
    try:
        conn = get_db_connection()
        videos = conn.execute('SELECT * FROM videos').fetchall()
        conn.close()
        return jsonify([dict(video) for video in videos])
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@videos_bp.route('/videos', methods=['POST'])
@login_required
def create_video():
    try:
        new_video = request.get_json()
        video_name = new_video.get('video_name')

        conn = get_db_connection()
        conn.execute('INSERT INTO videos (video_name) VALUES (?)', (video_name,))
        conn.commit()
        conn.close()

        return jsonify(new_video), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@videos_bp.route('/videos/<int:video_id>', methods=['PUT'])
@login_required
def update_video(video_id):
    try:
        updated_data = request.get_json()
        video_name = updated_data.get('video_name')

        conn = get_db_connection()
        video = conn.execute('SELECT * FROM videos WHERE id = ?', (video_id,)).fetchone()

        if video is None:
            return jsonify({'error': 'Video not found'}), 404

        conn.execute('UPDATE videos SET video_name = ? WHERE id = ?', (video_name, video_id))
        conn.commit()
        conn.close()

        return jsonify(updated_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@videos_bp.route('/videos/<int:video_id>', methods=['DELETE'])
@login_required
def delete_video(video_id):
    try:
        conn = get_db_connection()
        video = conn.execute('SELECT * FROM videos WHERE id = ?', (video_id,)).fetchone()

        if video is None:
            return jsonify({'error': 'Video not found'}), 404

        conn.execute('DELETE FROM videos WHERE id = ?', (video_id,))
        conn.commit()
        conn.close()

        return jsonify({'message': f'Successfully deleted video with ID = {video_id}'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@videos_bp.route('/videos', methods=['DELETE'])
@login_required
def delete_all_videos():
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM videos')
        conn.commit()
        conn.close()

        return jsonify({'message': 'Successfully deleted all videos'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400