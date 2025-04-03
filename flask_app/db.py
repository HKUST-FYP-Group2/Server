import sqlite3
from flask_app.logger import common_logger
import os
from pydantic import BaseModel
from logging import getLogger


class videos_SCHEMA(BaseModel):
    user_id: int
    video_name: str
    location: str
    created_at: str
    url: str
    cold_hot: int
    dry_wet: int
    clear_cloudy: int
    calm_stormy: int

class DatabaseManager:
    def __init__(self, db_path:str, logger):
        self.db_path = db_path
        self.db_connection = None
        self.logger = logger
    
    def __enter__(self):
        self.db_connection = sqlite3.connect(self.db_path)
        self.db_connection.row_factory = sqlite3.Row
        self.connected = True
        self.logger.info('Connected to database')
        return self.db_connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db_connection:
            if exc_type is None:
                self.logger.info("queries successful, commiting changes")
                self.db_connection.commit()
            else:
                self.logger.error(f"Exception occured ({exc_type}): {exc_val} {exc_tb}")
                self.logger.info("Rolling back changes")
                self.db_connection.rollback()
            self.db_connection.close()
            self.db_connection = None

    def init_db(self):
        conn = self.db_connection
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                projector_app_setting TEXT
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                video_name TEXT NOT NULL,
                location TEXT NOT NULL,
                created_at TEXT NOT NULL,
                url TEXT NOT NULL,
                cold_hot INTEGER NOT NULL,
                dry_wet INTEGER NOT NULL,
                clear_cloudy INTEGER NOT NULL,
                calm_stormy INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
                     ''')     
        conn.commit()

current_directory = os.path.dirname(os.path.abspath(__file__))
dbManager = DatabaseManager(current_directory+'/database.db',common_logger)
