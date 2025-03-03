import sqlite3

class DatabaseManager:
    def __init__(self, db_path:str):
        self.db_path = db_path
        self.db_connection = None
        self.connected = False
    
    def start(self):
        self.db_connection = sqlite3.connect(self.db_path)
        self.db_connection.row_factory = sqlite3.Row
        self.connected = True
    
    def stop(self):
        self.db_connection.close()
        self.connected = False

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
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_name VARCHAR(255) NOT NULL,
                location VARCHAR(255) NOT NULL,
                created_at TIMESTAMP NOT NULL,
                current_status INT NOT NULL
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS video_classification (
                id INT AUTO_INCREMENT PRIMARY KEY,
                video_id REFERENCES videos(id),
                cold_hot INT NOT NULL,
                dry_wet INT NOT NULL,
                clear_cloudy INT NOT NULL,
                calm_stormy INT NOT NULL     
            )      
        ''')
                     
        conn.commit()
        
    def execute(self, query:str, *args):
        return self.db_connection.execute(query, args)
        