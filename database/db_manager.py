import sqlite3
import os

class DatabaseManager:
    def __init__(self):
        self.db_path = "everypic.db"
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建图片信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                md5_hash TEXT NOT NULL,
                file_path TEXT NOT NULL,
                description TEXT,
                file_size INTEGER,
                created_time TEXT,
                modified_time TEXT,
                reserved1 TEXT,
                reserved2 TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_image(self, image_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO images (filename, md5_hash, file_path, description, 
                              file_size, created_time, modified_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', image_data)
        
        conn.commit()
        conn.close()
    
    def search_images(self, keyword):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM images 
            WHERE description LIKE ? OR filename LIKE ?
        ''', (f'%{keyword}%', f'%{keyword}%'))
        
        results = cursor.fetchall()
        conn.close()
        return results 
    
    def delete_image_by_path(self, file_path):
        """根据文件路径删除图片记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM images WHERE file_path = ?', (file_path,))
        
        conn.commit()
        conn.close() 