import sys
sys.path.append("..")
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_restful import Api, Resource
from flask_app.db import dbManager
import os

# Create a Blueprint for videos
videos_bp = Blueprint('videos', __name__)
api = Api(videos_bp)

# Video list resource
class VideoListResource(Resource):
    @jwt_required()
    def get(self):
        """List all videos for the current user."""
        try:
            user_id = get_jwt_identity()

            if not user_id:
                return {'error': 'User not authenticated'}, 401
            
            # Make an internal API call to get the stream key
            with current_app.test_client() as client:
                headers = {
                    'Authorization': f'Bearer {create_access_token(identity=user_id)}'
                }
                response = client.get(f'/users/{user_id}/sk', headers=headers)

            if response.status_code != 200:
                return {'error': 'Failed to retrieve stream key'}, response.status_code

            stream_key = response.get_json().get('stream_key')
            if not stream_key:
                return {'error': 'Stream key not found'}, 400

            directory = f'/home/user/recordings/{stream_key}'
            if not os.path.exists(directory):
                return {'error': f'Directory {directory} does not exist'}, 400

            videos = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
            return {'videos': videos}, 200
        except Exception as e:
            return {'error': str(e)}, 400

    @jwt_required()
    def post(self):
        """Create a new video."""
        try:
            new_video = request.get_json()
            
            user_id = new_video.get('user_id')
            video_name = new_video.get('video_name')
            location = new_video.get('location')
            created_at = new_video.get('created_at')
            video_url = new_video.get('video_url')
            description = new_video.get('description')
            keyword1 = new_video.get('keyword1')
            keyword2 = new_video.get('keyword2')
            cold_hot = new_video.get('cold_hot')
            dry_wet = new_video.get('dry_wet')
            clear_cloudy = new_video.get('clear_cloudy')
            calm_stormy = new_video.get('calm_stormy')

            with dbManager as conn:
                conn.execute('''
                    INSERT INTO videos (user_id, video_name, location, created_at, url, description, keyword1, keyword2, cold_hot, dry_wet, clear_cloudy, calm_stormy) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                    (user_id, video_name, location, created_at, video_url, description, keyword1, keyword2, cold_hot, dry_wet, clear_cloudy, calm_stormy))

            return new_video, 201
        except Exception as e:
            return {'error': str(e)}, 400

    @jwt_required()
    def delete(self):
        """Delete all videos."""
        try:
            with dbManager as conn:
                conn.execute('DELETE FROM videos')
            return {'message': 'Successfully deleted all videos'}, 200
        except Exception as e:
            return {'error': str(e)}, 400


# Video resource
class VideoResource(Resource):
    @jwt_required()
    def put(self, video_id):
        """Update a specific video."""
        try:
            updated_data = request.get_json()
            new_status = updated_data.get('new_status')
            new_location = updated_data.get('new_location')

            with dbManager as conn:
                video = conn.execute('SELECT * FROM videos WHERE id = ?', (video_id,)).fetchone()

                if video is None:
                    return {'error': 'Video not found'}, 404

                conn.execute('''
                    UPDATE videos 
                    SET location = ?
                    WHERE id = ?''', (new_status, new_location, video_id))

            return updated_data, 200
        except Exception as e:
            return {'error': str(e)}, 400

    @jwt_required()
    def delete(self, video_id):
        """Delete a specific video."""
        try:
            with dbManager as conn:
                video = conn.execute('SELECT * FROM videos WHERE id = ?', (video_id,)).fetchone()

                if video is None:
                    return {'error': 'Video not found'}, 404

                conn.execute('DELETE FROM videos WHERE id = ?', (video_id,))
            return {'message': f'Successfully deleted video with ID = {video_id}'}, 200
        except Exception as e:
            return {'error': str(e)}, 400


# Register the resources with the API
api.add_resource(VideoListResource, '/videos')
api.add_resource(VideoResource, '/videos/<int:video_id>')