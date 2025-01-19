import os
import time
import hashlib
from datetime import datetime
from PIL import Image
from database.transaction_manager import TransactionManager
from .ImageToText import ImageToText
from .config_manager import ConfigManager
from utils.logger import Logger


class ImageScanner:
    def __init__(self):
        self.transaction_manager = TransactionManager()  # 更清晰的变量命名
        self.supported_formats = ConfigManager().get_supported_formats()
        self.image_to_text = ImageToText()
        self.image_to_text.load_model()
        self.logger = Logger()
    
    def get_file_md5(self, filepath):
        """计算文件的MD5值"""
        md5_hash = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    
    def get_image_description(self, image_path):
        """获取图片描述"""
        return self.image_to_text.caption_image(image_path)
    
    def scan_directory(self, directory):
        """扫描指定目录下的所有图片"""
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(fmt) for fmt in self.supported_formats):
                    file_path = os.path.join(root, file)
                    try:
                        self.process_single_image(file_path)
                    except Exception as e:
                        self.logger.error(f"处理文件 {file_path} 时出错: {str(e)}")
    
    def start_scan(self):
        """开始扫描系统中的图片"""
        # 从配置管理器获取图片目录
        picture_dirs = ConfigManager().get_scan_directories()        
        
        # 扫描所有配置的目录
        for directory in picture_dirs:
            if os.path.exists(directory):
                self.scan_directory(directory) 
    
    def process_single_image(self, file_path):
        """处理单个图片文件"""
        try:
            # 获取文件信息
            file_stats = os.stat(file_path)
            file_name = os.path.basename(file_path)
            created_time = datetime.fromtimestamp(file_stats.st_ctime)
            modified_time = datetime.fromtimestamp(file_stats.st_mtime)
            
            # 生成图片描述
            start_time = time.time()
            description = self.get_image_description(file_path)
            end_time = time.time()
            print(f"获取图片 {file_name} 描述耗时: {end_time - start_time} 秒")
            
            # 构建图片数据
            image_data = {
                'file_path': file_path,
                'file_name': file_name,
                'file_size': file_stats.st_size,
                'md5': self.get_file_md5(file_path),
                'created_time': created_time.strftime('%Y-%m-%d %H:%M:%S'),
                'modified_time': modified_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 使用事务添加图片信息到数据库
            with self.transaction_manager.transaction():
                image_id = self.transaction_manager.add_image(image_data, description)
                self.logger.info(f"成功处理图片: {file_path}")
            
        except Exception as e:
            self.logger.error(f"处理文件 {file_path} 时出错: {str(e)}")
            raise 
