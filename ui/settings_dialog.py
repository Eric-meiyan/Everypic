from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QLineEdit, QFileDialog, QListWidget)
from PyQt6.QtCore import Qt
from utils.config_manager import ConfigManager

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setMinimumWidth(500)
        self.config_manager = ConfigManager()
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 扫描目录设置
        scan_group_layout = QVBoxLayout()
        scan_label = QLabel("图片扫描目录：")
        scan_group_layout.addWidget(scan_label)

        # 目录列表
        self.directory_list = QListWidget()
        scan_group_layout.addWidget(self.directory_list)

        # 添加和删除目录的按钮
        btn_layout = QHBoxLayout()
        self.add_dir_btn = QPushButton("添加目录")
        self.remove_dir_btn = QPushButton("删除目录")
        self.add_dir_btn.clicked.connect(self.add_directory)
        self.remove_dir_btn.clicked.connect(self.remove_directory)
        btn_layout.addWidget(self.add_dir_btn)
        btn_layout.addWidget(self.remove_dir_btn)
        scan_group_layout.addLayout(btn_layout)

        layout.addLayout(scan_group_layout)

        # 确定和取消按钮
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

    def load_settings(self):
        """从配置文件加载设置"""
        directories = self.config_manager.get_scan_directories()
        self.directory_list.clear()
        for directory in directories:
            if directory:  # 忽略空字符串
                self.directory_list.addItem(directory)

    def save_settings(self):
        """保存设置到配置文件"""
        directories = []
        for i in range(self.directory_list.count()):
            directories.append(self.directory_list.item(i).text())
        self.config_manager.set_scan_directories(directories)

    def add_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择扫描目录")
        if directory:
            self.directory_list.addItem(directory)

    def remove_directory(self):
        current_item = self.directory_list.currentItem()
        if current_item:
            self.directory_list.takeItem(self.directory_list.row(current_item))

    def accept(self):
        """点击确定按钮时保存设置"""
        self.save_settings()
        super().accept() 