import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
# from utils.image_scanner import ImageScanner
from utils.file_monitor import FileMonitor
from utils.config_manager import ConfigManager
from database.transaction_manager import TransactionManager
from utils.scan_thread import ScanThread

def is_debugging():
    """检查是否在调试模式下运行"""
    # 方法1：检查是否使用调试器
    gettrace = getattr(sys, 'gettrace', None)
    if gettrace is not None and gettrace():
        return True
    

        
    return False

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

    config_manager = ConfigManager()  # 会创建默认配置
    
    # 创建主窗口
    window = MainWindow()    
    
    # 显示主窗口
    window.show()

    # file_monitor = FileMonitor()

    # 检查是否首次运行
    is_first_run = not os.path.exists("settings.ini") 
    # 判断是否为调试模式
    if is_debugging():
        print("Debug mode is enabled")
        is_first_run = True
    else:
        print("Debug mode is disabled")

    

    # if is_first_run:
    #     # 首次运行初始化        
    #     db_manager = DatabaseManager()    # 会创建数据库结构
        
    #     # 创建并启动扫描线程        
    #     scan_thread = ScanThread()
    #     # scan_thread.progress_updated.connect(lambda msg: print(msg))  # 可以连接到状态栏显示
    #     scan_thread.start()
    # else:
    #     # 非首次运行，确保数据库已初始化，启动文件监控
    #     db_manager = DatabaseManager()    # 确保数据库已初始化        
        
    #     file_monitor.start_monitoring()


    
    
    try:
        sys.exit(app.exec())
    finally:
        print("应用程序已关闭")
        # file_monitor.stop_monitoring()



if __name__ == "__main__":
    main() 
    # onetest()