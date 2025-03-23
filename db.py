import sqlite3

class DatabaseManager:
    def __init__(self, db_path:str, logger):
        self.db_path = db_path
        self.db_connection = None
        self.logger = logger
    
    def __enter__(self):
        self.db_connection = sqlite3.connect(self.db_path)
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
        if self.db_connection is None:
            self.start()
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
                video_name VARCHAR(255) NOT NULL,
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

dbManager = DatabaseManager('database.db')
