import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.image_scanner import ImageScanner

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
    
    # 创建主窗口
    window = MainWindow()
    
    # 如果是第一次运行，启动图片扫描
    # if not os.path.exists("everypic.db"):
        # scanner = ImageScanner()
        # scanner.start_scan()
    
    # 显示主窗口
    window.show()
    
    # 运行应用程序主循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 