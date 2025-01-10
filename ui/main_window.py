from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QLineEdit, QListWidget, QMenuBar)
from PyQt6.QtCore import Qt
from ui.menu_bar import create_menu_bar
from database.db_manager import DatabaseManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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
        self.search_box.textChanged.connect(self.search_images)
        layout.addWidget(self.search_box)
        
        # 创建图片列表
        self.image_list = QListWidget()
        self.image_list.itemDoubleClicked.connect(self.open_image)
        layout.addWidget(self.image_list)
        
        # 创建菜单栏
        self.create_menus()
        
        # 初始化数据库管理器
        self.db_manager = DatabaseManager()
        
    def create_menus(self):
        menubar = self.menuBar()
        create_menu_bar(self, menubar)
    
    def search_images(self, keyword):
        # TODO: 实现图片搜索功能
        pass
        
    def open_image(self, item):
        # TODO: 实现图片打开功能
        pass 