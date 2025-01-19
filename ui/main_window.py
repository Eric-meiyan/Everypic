from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QLineEdit, QListWidget, QListWidgetItem,
                           QLabel, QFileDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon
import os
from ui.menu_bar import create_menu_bar
from database import db  # 使用统一的数据库接口
from utils.logger import Logger  # 添加日志支持

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = Logger()  # 初始化日志器
        self.setWindowTitle("Everypic")
        self.setMinimumSize(800, 600)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建搜索框
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("输入关键词搜索图片...")
        # 将搜索框的回车事件连接到搜索函数
        self.search_box.returnPressed.connect(self.search_images)
        layout.addWidget(self.search_box)
        
        # 创建图片列表
        self.image_list = QListWidget()
        self.image_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.image_list.setIconSize(QSize(200, 200))
        self.image_list.setSpacing(10)
        self.image_list.itemDoubleClicked.connect(self.open_image)
        layout.addWidget(self.image_list)
        
        # 创建菜单栏
        self.create_menus()
    
    def create_menus(self):
        menubar = self.menuBar()
        create_menu_bar(self, menubar)
    
    def search_images(self):
        """搜索图片并显示结果"""
        try:
            self.image_list.clear()
            
            keyword = self.search_box.text().strip()
            if not keyword:
                return
            
            self.logger.info(f"搜索关键词: {keyword}")
            results = db.search_similar_images(keyword)
            
            if not results:
                item = QListWidgetItem("没有找到匹配的图片")
                self.image_list.addItem(item)
                return
            
            for image_info in results:
                file_path = image_info['file_path']
                if not os.path.exists(file_path):
                    self.logger.warning(f"文件不存在: {file_path}")
                    continue
                    
                try:
                    # 创建缩略图
                    pixmap = QPixmap(file_path)
                    if pixmap.isNull():
                        self.logger.warning(f"无法加载图片: {file_path}")
                        continue
                        
                    # 缩放图片
                    scaled_pixmap = pixmap.scaled(
                        200, 200,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    
                    # 创建列表项
                    item = QListWidgetItem()
                    item.setIcon(QIcon(scaled_pixmap))  # 使用QIcon而不是直接使用QPixmap
                    item.setText(os.path.basename(file_path))
                    item.setData(Qt.ItemDataRole.UserRole, file_path)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    self.image_list.addItem(item)
                    
                except Exception as e:
                    self.logger.error(f"处理图片失败 {file_path}: {str(e)}")
                    continue
            
            self.logger.info(f"找到 {self.image_list.count()} 个匹配结果")
            
        except Exception as e:
            self.logger.error(f"搜索出错: {str(e)}")
            item = QListWidgetItem(f"搜索出错: {str(e)}")
            self.image_list.addItem(item)
    
    def open_image(self, item):
        """打开选中的图片"""
        try:
            file_path = item.data(Qt.ItemDataRole.UserRole)
            if file_path and os.path.exists(file_path):
                # 使用系统默认程序打开图片
                os.startfile(file_path)  # Windows
                # 对于其他系统可以使用：
                # import subprocess
                # subprocess.run(['xdg-open', file_path])  # Linux
                # subprocess.run(['open', file_path])      # macOS
        except Exception as e:
            self.logger.error(f"打开图片失败: {str(e)}") 