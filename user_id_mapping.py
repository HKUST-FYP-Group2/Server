import requests
import sqlite3
import urllib3
import os

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

print(get_user_id_mapping())