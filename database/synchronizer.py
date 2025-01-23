import os
import hashlib
from datetime import datetime
from typing import Dict, List, Set
from utils.logger import Logger
from utils.config_manager import ConfigManager
from utils.image_scanner import ImageScanner
from database import db

class DatabaseSynchronizer:
    def __init__(self):
        """初始化数据库同步器"""
        self.logger = Logger()
        self.config_manager = ConfigManager()
        self.image_scanner = ImageScanner()
        self.supported_formats = self.config_manager.get_supported_formats()
        self.batch_size = 100  # 批处理大小
    
    def sync_database(self, directories: List[str]):
        """同步数据库和文件系统"""
        try:
            self.logger.info("[DatabaseSynchronizer.sync_database] 开始数据库同步...")
            # 0. 先检查两个数据库的一致性
            self._check_database_consistency()
            
            # 1. 获取数据库中所有记录
            db_records = {record['file_path']: record for record in db.get_all_records()}
            db_md5s = {record['md5']: record for record in db_records.values() 
                      if record['md5'] is not None}
            
            # 2. 获取文件系统中的所有图片（不计算MD5）
            fs_files = self.scan_directories(directories)
            
            # 3. 处理已删除的文件
            self._process_deleted_files(db_records.keys(), fs_files.keys())
            
            # 4. 处理新文件和修改的文件（分批处理）
            self._process_changed_files(db_records, db_md5s, fs_files)
            
            self.logger.info("数据库同步完成")
            
        except Exception as e:
            self.logger.error(f"[DatabaseSynchronizer.sync_database] 数据库同步失败: {str(e)}")
            raise
    
    def _check_database_consistency(self):
        """检查 SQLite 和 ChromaDB 数据一致性"""
        try:
            # 获取 SQLite 中的所有记录
            sqlite_records = db.get_all_records()
            sqlite_ids = {record['id'] for record in sqlite_records}
            
            # 获取 ChromaDB 中的所有记录
            try:
                chroma_ids = set(db.get_all_records_ids())
            except Exception as e:
                self.logger.error(f"获取 ChromaDB 记录失败: {str(e)}")
                raise
            
            # 检查不一致
            only_in_sqlite = sqlite_ids - chroma_ids
            only_in_chroma = chroma_ids - sqlite_ids
            
            if only_in_sqlite or only_in_chroma:
                self.logger.warning("检测到数据库不一致:")
                if only_in_sqlite:
                    self.logger.warning(f"仅在 SQLite 中存在的记录: {len(only_in_sqlite)} 条")
                    # 可以选择从 SQLite 中删除这些记录
                    with db.transaction():
                        for image_id in only_in_sqlite:
                            record = next(r for r in sqlite_records if r['id'] == image_id)
                            db.delete_image(record['file_path'])
                            self.logger.info(f"从 SQLite 删除不一致记录: {record['file_path']}")
                
                if only_in_chroma:
                    self.logger.warning(f"仅在 ChromaDB 中存在的记录: {len(only_in_chroma)} 条")
                    # 从 ChromaDB 中删除这些记录
                    db.delete_record_by_id(list(only_in_chroma))
                    self.logger.info(f"从 ChromaDB 删除 {len(only_in_chroma)} 条不一致记录")
                
                self.logger.info("数据库一致性已修复")
            else:
                self.logger.info("数据库一致性检查通过")
            
        except Exception as e:
            self.logger.error(f"数据库一致性检查失败: {str(e)}")
            raise
    
    def _process_deleted_files(self, db_paths: Set[str], fs_paths: Set[str]):
        """处理已删除的文件（批量处理）"""
        deleted_paths = db_paths - fs_paths
        if not deleted_paths:
            return
            
        # 分批处理删除操作
        for i in range(0, len(deleted_paths), self.batch_size):
            batch = list(deleted_paths)[i:i + self.batch_size]
            try:
                with db.transaction():
                    for file_path in batch:
                        self.logger.info(f"删除数据库中的丢失文件记录: {file_path}")
                        db.delete_image(file_path)
            except Exception as e:
                self.logger.error(f"处理删除文件批次时出错: {str(e)}")
                raise
    
    def _process_changed_files(self, db_records, db_md5s, fs_files):
        """处理新文件和修改的文件"""
        try:
            # 收集需要处理的文件
            to_process = []
            for file_path, file_info in fs_files.items():
                if file_path not in db_records:
                    to_process.append((file_path, file_info, True))
                else:
                    if self._is_file_modified_quick(file_info, db_records[file_path]):
                        to_process.append((file_path, file_info, False))
            
            # 每个文件单独事务
            total = len(to_process)
            for i, (file_path, file_info, is_new) in enumerate(to_process):
                try:
                    self.logger.info(f"[DatabaseSynchronizer._process_changed_files] 开始处理第 {i+1}/{total} 个文件: {file_path}")
                    
                    with db.transaction():
                        self._process_single_file(file_path, file_info, is_new, db_records, db_md5s)
                        
                    self.logger.info(f"[DatabaseSynchronizer._process_changed_files] 完成第 {i+1}/{total} 个文件")
                    
                except Exception as e:
                    self.logger.error(f"[DatabaseSynchronizer._process_changed_files] 处理文件 {file_path} 失败: {str(e)}")
                    # 记录错误但继续处理下一个文件
                    continue
                
        except Exception as e:
            self.logger.error(f"[DatabaseSynchronizer._process_changed_files] 处理文件列表时出错: {str(e)}")
            raise
    
    def _process_single_file(self, file_path: str, file_info: Dict, is_new: bool, 
                           db_records: Dict, db_md5s: Dict):
        """处理单个文件"""
        try:
            if is_new:
                self.logger.info(f"[DatabaseSynchronizer._process_single_file] 处理新文件: {file_path}")
                # 计算MD5，检查是否是移动的文件
                md5 = self.get_file_md5(file_path)
                if md5 in db_md5s:
                    # 文件被移动
                    old_record = db_md5s[md5]
                    self.logger.info(f"处理移动的文件: {old_record['file_path']} -> {file_path}")
                    db.delete_image(old_record['file_path'])
                
            self.logger.info(f"{'处理新文件' if is_new else '更新修改的文件'}: {file_path}")
            self.image_scanner.process_single_image(file_path)
            
        except Exception as e:
            self.logger.error(f"处理文件 {file_path} 时出错: {str(e)}")
            raise
    
    def _is_file_modified_quick(self, file_info: Dict, db_record: Dict) -> bool:
        """快速检查文件是否被修改（不计算MD5）"""
        # 1. 比较文件大小
        if file_info['size'] != db_record['file_size']:
            return True
            
        # 2. 比较修改时间
        file_mtime = file_info['mtime']
        db_mtime = datetime.fromisoformat(db_record['modified_time'])
        return file_mtime > db_mtime
    
    def scan_directories(self, directories: List[str]) -> Dict:
        """扫描目录获取所有图片文件信息（不计算MD5）"""
        fs_files = {}
        for directory in directories:
            if not os.path.exists(directory):
                self.logger.warning(f"目录不存在: {directory}")
                continue
                
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if not any(file_path.lower().endswith(fmt) for fmt in self.supported_formats):
                        continue
                    
                    try:
                        fs_files[file_path] = {
                            'size': os.path.getsize(file_path),
                            'mtime': datetime.fromtimestamp(os.path.getmtime(file_path)),
                            'md5': None  # 延迟计算MD5
                        }
                    except Exception as e:
                        self.logger.error(f"获取文件 {file_path} 信息时出错: {str(e)}")
                        continue
                        
        return fs_files
    
    def get_file_md5(self, filepath: str) -> str:
        """计算文件的MD5值"""
        md5_hash = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest() 