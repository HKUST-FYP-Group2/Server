import sys
sys.path.append("..")
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_login import current_user, login_required
from flask_app.db import dbManager
import os

# Create a Blueprint for users
videos_bp = Blueprint('videos', __name__)

class Video:
    def __init__(self, id, video_name):
        self.id = id
        self.video_name = video_name

# VIDEO-related functions
# @videos_bp.route('/videos', methods=['GET'])
# @login_required
# def get_all_videos():
#     try:
#         with dbManager as conn:
#             videos = conn.execute('SELECT * FROM videos').fetchall()

#         return jsonify([dict(video) for video in videos])
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

@videos_bp.route('/get_videos', methods=['POST'])
@jwt_required()
def list_videos():
    try:
        # Get the user ID of the current user
        user_id = get_jwt_identity()
        
        if not user_id:
            return jsonify({'error': f'User not authenticated with user_id {user_id}'}), 401
        
        # Make an internal API call to get the stream key
        with current_app.test_client() as client:
            # Use the JWT token of the current user for authentication
            headers = {
                'Authorization': f'Bearer {create_access_token(identity=user_id)}'
            }
            response = client.get(f'/users/{user_id}/sk', headers=headers)
            
        
        # Parse the response from the StreamKeyResource API
        if response.status_code != 200:
            return jsonify({'error': f'Failed to retrieve stream key with response {response}'}), response.status_code

        stream_key = response.get_json().get('stream_key')
        if not stream_key:
            return jsonify({'error': 'Stream key not found'}), 400

        # Define the target directory using the stream key
        directory = f'/home/user/recordings/{stream_key}'

        # Check if the directory exists
        if not os.path.exists(directory):
            return jsonify({'error': f'Directory {directory} does not exist'}), 400

        # List all videos in the directory
        videos = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

        return jsonify({'videos': videos}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@videos_bp.route('/videos', methods=['POST'])
@jwt_required()
def create_video():
    try:
        new_video = request.get_json()
        video_name = new_video.get('video_name')
        location = new_video.get('location')
        created_at = new_video.get('created_at')
        video_url = new_video.get('video_url')

        with dbManager as conn:
            conn.execute('''
                         INSERT INTO videos (video_name, location, created_at, URL) 
                         VALUES (?, ?, ?, ?)''', (video_name, location, created_at, video_url))

        return jsonify(new_video), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@videos_bp.route('/videos/<int:video_id>', methods=['PUT'])
@jwt_required()
def update_video():
    try:
        updated_data = request.get_json()
        video_id = updated_data.get('video_id')
        new_status = updated_data.get('new_status')
        new_location = updated_data.get('new_location')

        with dbManager as conn:
            video = conn.execute('SELECT * FROM videos WHERE id = ?', (video_id,)).fetchone()

            if video is None:
                return jsonify({'error': 'Video not found'}), 404

            conn.execute('''UPDATE videos 
                                SET location = ?
                                WHERE id = ?''', (new_status, new_location, video_id))

        return jsonify(updated_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@videos_bp.route('/videos/<int:video_id>', methods=['DELETE'])
@jwt_required()
def delete_video(video_id):
    try:
        with dbManager as conn:
            video = conn.execute('SELECT * FROM videos WHERE id = ?', (video_id,)).fetchone()

            if video is None:
                return jsonify({'error': 'Video not found'}), 404

            conn.execute('DELETE FROM videos WHERE id = ?', (video_id,))

        return jsonify({'message': f'Successfully deleted video with ID = {video_id}'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@videos_bp.route('/videos', methods=['DELETE'])
@jwt_required()
def delete_all_videos():
    try:
        with dbManager as conn:
            conn.execute('DELETE FROM videos')
            
        return jsonify({'message': 'Successfully deleted all videos'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400