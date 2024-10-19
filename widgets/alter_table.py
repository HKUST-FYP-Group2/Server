import sys
sys.path.append("..")
from db import get_db_connection

# alter table settings
def alter_users_table():
    conn = get_db_connection()
    # Step 1: Create a new table with the desired schema
    conn.execute('''
        CREATE TABLE IF NOT EXISTS new_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            projector_app_setting TEXT
        )
    ''')
    
    # Step 2: Copy data from the old table to the new table
    conn.execute('''
        INSERT INTO new_users (username, password, projector_app_setting)
        SELECT username, password, projector_app_setting FROM users
    ''')
    
    # Step 3: Drop the old table
    conn.execute('DROP TABLE users')
    
    # Step 4: Rename the new table to the original table name
    conn.execute('ALTER TABLE new_users RENAME TO users')
    
    conn.commit()
    conn.close()

def alter_videos_table():
    conn = get_db_connection()
    # Step 1: Create a new table with the desired schema
    conn.execute('''
        CREATE TABLE IF NOT EXISTS new_videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_name TEXT NOT NULL
        )
    ''')
    
    # Step 2: Copy data from the old table to the new table
    conn.execute('''
        INSERT INTO new_videos (video_name)
        SELECT video_name FROM videos
    ''')
    
    # Step 3: Drop the old table
    conn.execute('DROP TABLE videos')
    
    # Step 4: Rename the new table to the original table name
    conn.execute('ALTER TABLE new_videos RENAME TO videos')
    
    conn.commit()
    conn.close()

# Call these functions to perform the alterations
alter_users_table()
alter_videos_table()