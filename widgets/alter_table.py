
#commenting out the file, since it is not needed
# import sys
# sys.path.append("..")
# from db import get_db_connection

# # alter table settings
# def alter_users_table():
#     conn = get_db_connection()
#     # Step 1: Create a new table with the desired schema
#     conn.execute('''
#         CREATE TABLE IF NOT EXISTS new_users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT NOT NULL UNIQUE,
#             password TEXT NOT NULL,
#             projector_app_setting TEXT
#         )
#     ''')
    
#     # Step 2: Copy data from the old table to the new table
#     conn.execute('''
#         INSERT INTO new_users (username, password, projector_app_setting)
#         SELECT username, password, projector_app_setting FROM users
#     ''')
    
#     # Step 3: Drop the old table
#     conn.execute('DROP TABLE users')
    
#     # Step 4: Rename the new table to the original table name
#     conn.execute('ALTER TABLE new_users RENAME TO users')
    
#     conn.commit()
#     conn.close()

# def alter_videos_table():
#     conn = get_db_connection()

#     # Step 1: Drop the old 'video' table if it exists
#     conn.execute('DROP TABLE IF EXISTS video')

#     # Step 2: Create the new 'videos' table
#     conn.execute('''
#         CREATE TABLE IF NOT EXISTS videos (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             video_name TEXT NOT NULL,
#             location TEXT NOT NULL,
#             created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
#             URL TEXT NOT NULL
#         )
#     ''')

#     # Step 3: Create the new 'video_classification' table
#     conn.execute('''
#         CREATE TABLE IF NOT EXISTS video_classification (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             video_id INTEGER NOT NULL,
#             cold_hot INTEGER NOT NULL,
#             dry_wet INTEGER NOT NULL,
#             clear_cloudy INTEGER NOT NULL,
#             calm_stormy INTEGER NOT NULL,
#             FOREIGN KEY (video_id) REFERENCES videos(id)
#         )
#     ''')

#     conn.commit()
#     conn.close()

# # Call these functions to perform the alterations
# alter_users_table()
# alter_videos_table()

# """
# I think the table can be further altered

# """