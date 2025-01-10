import os
import hashlib
from datetime import datetime
from PIL import Image
from database.db_manager import DatabaseManager

class ImageScanner:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    
    def get_file_md5(self, filepath):
        """计算文件的MD5值"""
        md5_hash = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    
    def get_image_description(self, image_path):
        """获取图片描述（此处可以后续集成AI模型）"""
        # TODO: 集成AI模型进行图片描述
        return "图片描述待完善"
    
    def scan_directory(self, directory):
        """扫描指定目录下的所有图片"""
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(fmt) for fmt in self.supported_formats):
                    file_path = os.path.join(root, file)
                    try:
                        # 获取文件信息
                        file_stats = os.stat(file_path)
                        created_time = datetime.fromtimestamp(file_stats.st_ctime)
                        modified_time = datetime.fromtimestamp(file_stats.st_mtime)
                        
                        # 构建图片数据
                        image_data = (
                            file,  # filename
                            self.get_file_md5(file_path),  # md5_hash
                            file_path,  # file_path
                            self.get_image_description(file_path),  # description
                            file_stats.st_size,  # file_size
                            created_time.strftime('%Y-%m-%d %H:%M:%S'),  # created_time
                            modified_time.strftime('%Y-%m-%d %H:%M:%S')  # modified_time
                        )
                        
                        # 添加到数据库
                        self.db_manager.add_image(image_data)
                        
                    except Exception as e:
                        print(f"处理文件 {file_path} 时出错: {str(e)}")
    
    def start_scan(self):
        """开始扫描系统中的图片"""
        # 获取常见的图片目录
        picture_dirs = []
        
        # Windows系统的图片文件夹
        user_profile = os.environ.get('USERPROFILE')
        if user_profile:
            picture_dirs.extend([
                os.path.join(user_profile, 'Pictures'),
                os.path.join(user_profile, 'Downloads'),
                os.path.join(user_profile, 'Desktop')
            ])
        
        # 扫描所有配置的目录
        for directory in picture_dirs:
            if os.path.exists(directory):
                self.scan_directory(directory) 