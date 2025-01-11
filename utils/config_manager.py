import os
import configparser
from typing import List

class ConfigManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = "settings.ini"
        self.load_config()

    def load_config(self):
        """加载配置文件，如果不存在则创建默认配置"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            self._create_default_config()

    def _create_default_config(self):
        """创建默认配置"""
        self.config['Directories'] = {
            'scan_dirs': '',  # 用分号分隔的目录列表
            'last_open_dir': ''
        }
        
        self.config['FileTypes'] = {
            'supported_formats': '.jpg;.jpeg;.png;.gif;.bmp'
        }
        
        self.config['Database'] = {
            'db_path': 'everypic.db'
        }
        
        self.config['General'] = {
            'language': 'zh_CN'  # 默认使用中文
        }
        
        self.save_config()

    def save_config(self):
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)

    def get_scan_directories(self) -> List[str]:
        """获取扫描目录列表"""
        dirs_str = self.config.get('Directories', 'scan_dirs', fallback='')
        return [d for d in dirs_str.split(';') if d]

    def set_scan_directories(self, directories: List[str]):
        """设置扫描目录列表"""
        self.config['Directories']['scan_dirs'] = ';'.join(directories)
        self.save_config()

    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式"""
        formats_str = self.config.get('FileTypes', 'supported_formats', fallback='')
        return formats_str.split(';')

    def get_db_path(self) -> str:
        """获取数据库路径"""
        return self.config.get('Database', 'db_path', fallback='everypic.db') 

    def get_language(self) -> str:
        """获取当前语言设置"""
        return self.config.get('General', 'language', fallback='zh_CN')

    def set_language(self, language: str):
        """设置语言"""
        self.config['General']['language'] = language
        self.save_config() 

    def set_supported_formats(self, formats: str):
        """设置支持的文件格式"""
        self.config['FileTypes']['supported_formats'] = formats
        self.save_config() 