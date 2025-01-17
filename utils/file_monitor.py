import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from database.transaction_manager import TransactionManager
from utils.image_scanner import ImageScanner
from utils.config_manager import ConfigManager
from utils.logger import Logger

class ImageFileHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.db = TransactionManager()
        self.image_scanner = ImageScanner()
        self.config_manager = ConfigManager()
        self.supported_formats = self.config_manager.get_supported_formats()
        self.logger = Logger()

    def is_valid_image(self, file_path):
        """检查文件是否为支持的图片格式"""
        return any(file_path.lower().endswith(fmt) for fmt in self.supported_formats)

    def on_created(self, event):
        """处理新创建的文件"""
        if event.is_directory:
            return
        if self.is_valid_image(event.src_path):
            try:
                self.image_scanner.process_single_image(event.src_path)
                self.logger.info(f"新增图片: {event.src_path}")
            except Exception as e:
                self.logger.error(f"处理新增图片时出错: {e}")

    def on_modified(self, event):
        """处理修改的文件"""
        if event.is_directory:
            return
        if self.is_valid_image(event.src_path):
            try:
                with self.db.transaction():
                    self.db.delete_image(event.src_path)
                    self.image_scanner.process_single_image(event.src_path)
                self.logger.info(f"更新图片: {event.src_path}")
            except Exception as e:
                self.logger.error(f"处理修改图片时出错: {e}")

    def on_deleted(self, event):
        """处理删除的文件"""
        if event.is_directory:
            return
        if self.is_valid_image(event.src_path):
            try:
                with self.db.transaction():
                    self.db.delete_image(event.src_path)
                self.logger.info(f"删除图片: {event.src_path}")
            except Exception as e:
                self.logger.error(f"处理删除图片时出错: {e}")

    def on_moved(self, event):
        """处理移动或重命名的文件"""
        if event.is_directory:
            return
        if self.is_valid_image(event.dest_path):
            try:
                with self.db.transaction():
                    self.db.delete_image(event.src_path)
                    self.image_scanner.process_single_image(event.dest_path)
                self.logger.info(f"移动/重命名图片: {event.src_path} -> {event.dest_path}")
            except Exception as e:
                self.logger.error(f"处理移动/重命名图片时出错: {e}")

class FileMonitor:
    def __init__(self):
        self.observer = Observer()
        self.handler = ImageFileHandler()
        self.config_manager = ConfigManager()
        self.watching = False
        self.logger = Logger()

    def start_monitoring(self):
        """开始监控所有配置的目录"""
        if self.watching:
            return

        directories = self.config_manager.get_scan_directories()
        for directory in directories:
            if os.path.exists(directory):
                self.observer.schedule(self.handler, directory, recursive=True)
                self.logger.info(f"开始监控目录: {directory}")

        self.observer.start()
        self.watching = True
        self.logger.info("文件监控服务已启动")

    def stop_monitoring(self):
        """停止监控"""
        if self.watching:
            self.observer.stop()
            self.observer.join()
            self.watching = False
            self.logger.info("停止所有目录监控")

    def restart_monitoring(self):
        """重启监控（用于配置更改后）"""
        self.stop_monitoring()
        self.start_monitoring() 