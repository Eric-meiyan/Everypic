import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.image_scanner import ImageScanner
from utils.file_monitor import FileMonitor
from utils.config_manager import ConfigManager
from database.db_manager import DatabaseManager

def init_directories():
    """初始化必要的目录结构"""
    directories = ['database', 'ui', 'utils']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def main():
    # 初始化应用程序目录
    init_directories()
    
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 检查是否首次运行
    is_first_run = not os.path.exists("settings.ini") 
    # 判断是否为调试模式
    if os.getenv("DEBUG", "false") == "true":
        print("Debug mode is enabled")
        is_first_run = True
    else:
        print("Debug mode is disabled")

    
    if is_first_run:
        # 首次运行初始化
        config_manager = ConfigManager()  # 会创建默认配置
        db_manager = DatabaseManager()    # 会创建数据库结构
        scanner = ImageScanner()
        scanner.start_scan()              # 执行首次全量扫描
    
    # 创建主窗口
    window = MainWindow()
    
    # 如果是第一次运行，启动图片扫描
    # if not os.path.exists("everypic.db"):
        # scanner = ImageScanner()
        # scanner.start_scan()
    
    # 创建并启动文件监控
    # file_monitor = FileMonitor()
    # file_monitor.start_monitoring()
    
    # 显示主窗口
    window.show()
    
    try:
        sys.exit(app.exec())
    finally:
        file_monitor.stop_monitoring()

if __name__ == "__main__":
    main() 