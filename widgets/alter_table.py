# commenting out the file, since it is not needed
import sys
sys.path.append("..")
from flask_app.db import dbManager

# alter table settings
# def alter_users_table():
#     with dbManager as conn:
#         # Step 1: Create a new table with the desired schema
#         conn.execute('''
#             CREATE TABLE IF NOT EXISTS new_users (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 username TEXT NOT NULL UNIQUE,
#                 password TEXT NOT NULL,
#                 projector_app_setting TEXT
#             )
#         ''')
        
#         # Step 2: Copy data from the old table to the new table
#         conn.execute('''
#             INSERT INTO new_users (username, password, projector_app_setting)
#             SELECT username, password, projector_app_setting FROM users
#         ''')
        
#         # Step 3: Drop the old table
#         conn.execute('DROP TABLE users')
        
#         # Step 4: Rename the new table to the original table name
#         conn.execute('ALTER TABLE new_users RENAME TO users')
        
#         conn.commit()
#         conn.close()

# # def alter_videos_table():
# #     with dbManager as conn:

# #         # Step 1: Drop the old 'video' table if it exists
# #         conn.execute('DROP TABLE IF EXISTS video')

# #         # Step 2: Create the new 'videos' table
# #         conn.execute('''
# #             CREATE TABLE IF NOT EXISTS videos (
# #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 video_name TEXT NOT NULL,
# #                 location TEXT NOT NULL,
# #                 created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
# #                 URL TEXT NOT NULL
# #             )
# #         ''')

# #         # Step 3: Create the new 'video_classification' table
# #         conn.execute('''
# #             CREATE TABLE IF NOT EXISTS video_classification (
# #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 video_id INTEGER NOT NULL,
# #                 cold_hot INTEGER NOT NULL,
# #                 dry_wet INTEGER NOT NULL,
# #                 clear_cloudy INTEGER NOT NULL,
# #                 calm_stormy INTEGER NOT NULL,
# #                 FOREIGN KEY (video_id) REFERENCES videos(id)
# #             )
# #         ''')

# #         conn.commit()
# #         conn.close()

# def alter_videos_table():
#     with dbManager as conn:

#         # Step 1: Create the new merged 'videos' table
#         conn.execute('''
#             CREATE TABLE IF NOT EXISTS new_videos (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 user_id INTEGER DEFAULT NULL,
#                 video_name TEXT NOT NULL,
#                 location TEXT NOT NULL,
#                 created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
#                 URL TEXT NOT NULL,
#                 cold_hot INTEGER DEFAULT NULL,
#                 dry_wet INTEGER DEFAULT NULL,
#                 clear_cloudy INTEGER DEFAULT NULL,
#                 calm_stormy INTEGER DEFAULT NULL
#             )
#         ''')

#         # Step 2: Copy data from the old 'video' table into the new 'videos' table
#         conn.execute('''
#             INSERT INTO new_videos (id, video_name, location, created_at, URL)
#             SELECT id, video_name, location, created_at, URL FROM videos
#         ''')

#         # Step 3: Update classification data by joining with 'video_classification'
#         conn.execute('''
#             UPDATE new_videos
#             SET cold_hot = vc.cold_hot,
#                 dry_wet = vc.dry_wet,
#                 clear_cloudy = vc.clear_cloudy,
#                 calm_stormy = vc.calm_stormy
#             FROM video_classification vc
#             WHERE new_videos.id = vc.video_id
#         ''')

#         # Step 4: Drop the old 'video' and 'video_classification' tables
#         conn.execute('DROP TABLE IF EXISTS videos')
#         conn.execute('DROP TABLE IF EXISTS video_classification')

#         # Step 5: Rename the new table to the original table name
#         conn.execute('ALTER TABLE new_videos RENAME TO videos')

#         conn.commit()

# # Call these functions to perform the alterations
# # alter_users_table()
# alter_videos_table()

# """
# I think the table can be further altered

# """

def add_stream_key_column():
    with dbManager as conn:
        conn.execute("ALTER TABLE videos ADD COLUMN keyword1 TEXT")
        conn.execute("ALTER TABLE videos ADD COLUMN keyword2 TEXT")
        conn.execute("ALTER TABLE videos ADD COLUMN description TEXT")
        conn.commit()

add_stream_key_column()