import sqlite3
import os
from utils.logger import Logger

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_database()
        return cls._instance
    
    def _init_database(self):
        """初始化数据库"""
        self.db_path = "everypic.db"
        self.logger = Logger()
        self.conn = None
        self.create_tables()
    
    def create_tables(self):
        """创建数据库表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS images (
                        id TEXT PRIMARY KEY,
                        file_path TEXT NOT NULL UNIQUE,
                        file_name TEXT NOT NULL,
                        file_size INTEGER,
                        md5 TEXT,
                        created_time TEXT,
                        modified_time TEXT
                    )
                ''')
                conn.commit()
        except Exception as e:
            self.logger.error(f"创建数据库表失败: {str(e)}")
            raise

    def begin_transaction(self):
        """开始事务"""
        if self.conn is not None:
            self.logger.warning("已有未完成的事务")
            return
        self.conn = sqlite3.connect(self.db_path)
        self.conn.isolation_level = 'IMMEDIATE'  # 设置隔离级别
    
    def commit_transaction(self):
        """提交事务"""
        if self.conn is None:
            self.logger.error("没有活动的事务")
            return
        try:
            self.conn.commit()
        finally:
            self.conn.close()
            self.conn = None
    
    def rollback_transaction(self):
        """回滚事务"""
        if self.conn is None:
            self.logger.error("没有活动的事务")
            return
        try:
            self.conn.rollback()
        finally:
            self.conn.close()
            self.conn = None

    def add_image(self, image_data: dict, in_transaction=False):
        """添加图片信息到数据库"""
        try:
            if not in_transaction:
                self.begin_transaction()
            
            # 先检查是否存在
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM images WHERE file_path = ?', (image_data['file_path'],))
            existing = cursor.fetchone()
            
            if existing:
                # 更新
                cursor.execute('''
                    UPDATE images SET
                        file_name = ?, file_size = ?, md5 = ?,
                        created_time = ?, modified_time = ?
                    WHERE id = ?
                ''', (
                    image_data['file_name'],
                    image_data['file_size'],
                    image_data['md5'],
                    image_data['created_time'],
                    image_data['modified_time'],
                    existing[0]
                ))
            else:
                # 插入新记录
                cursor.execute('''
                    INSERT INTO images (
                        id, file_path, file_name, file_size, md5,
                        created_time, modified_time
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    image_data['id'],
                    image_data['file_path'],
                    image_data['file_name'],
                    image_data['file_size'],
                    image_data['md5'],
                    image_data['created_time'],
                    image_data['modified_time']
                ))
            
            if not in_transaction:
                self.commit_transaction()
                
        except Exception as e:
            if not in_transaction:
                self.rollback_transaction()
            self.logger.error(f"添加图片记录失败: {str(e)}")
            raise

    def delete_image_by_path(self, file_path: str, in_transaction=False):
        """根据文件路径删除图片记录"""
        try:
            if not in_transaction:
                self.begin_transaction()
                
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM images WHERE file_path = ?', (file_path,))
            
            if not in_transaction:
                self.commit_transaction()
                
        except Exception as e:
            if not in_transaction:
                self.rollback_transaction()
            self.logger.error(f"删除图片记录失败: {str(e)}")
            raise

    def get_image_by_id(self, image_id: str) -> dict:
        """根据ID获取图片信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, file_path, file_name, file_size, md5, 
                           created_time, modified_time 
                    FROM images WHERE id = ?
                ''', (image_id,))
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'file_path': row[1],
                        'file_name': row[2],
                        'file_size': row[3],
                        'md5': row[4],
                        'created_time': row[5],
                        'modified_time': row[6]
                    }
                return None
        except Exception as e:
            self.logger.error(f"获取图片记录失败: {str(e)}")
            raise 
    
    def drop_table(self, table_name: str):
        """删除指定的表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
                conn.commit()
                self.logger.info(f"已删除表: {table_name}")
        except Exception as e:
            self.logger.error(f"删除表失败: {str(e)}")
            raise