from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QLineEdit, QFileDialog, QListWidget,
                           QComboBox, QGroupBox)
from PyQt6.QtCore import Qt
from utils.config_manager import ConfigManager
from utils.translations import get_text

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager()
        self.current_language = self.config_manager.get_language()
        self.setWindowTitle(get_text('settings', self.current_language))
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 语言设置
        language_group = QGroupBox()
        language_layout = QHBoxLayout(language_group)
        language_label = QLabel(get_text('language', self.current_language))
        self.language_combo = QComboBox()
        self.language_combo.addItem("中文", "zh_CN")
        self.language_combo.addItem("English", "en_US")
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        layout.addWidget(language_group)

        # 扫描目录设置
        scan_group = QGroupBox()
        scan_group_layout = QVBoxLayout(scan_group)
        scan_label = QLabel(get_text('scan_directories', self.current_language))
        scan_group_layout.addWidget(scan_label)

        # 目录列表
        self.directory_list = QListWidget()
        scan_group_layout.addWidget(self.directory_list)

        # 添加和删除目录的按钮
        btn_layout = QHBoxLayout()
        self.add_dir_btn = QPushButton(get_text('add_directory', self.current_language))
        self.remove_dir_btn = QPushButton(get_text('remove_directory', self.current_language))
        self.add_dir_btn.clicked.connect(self.add_directory)
        self.remove_dir_btn.clicked.connect(self.remove_directory)
        btn_layout.addWidget(self.add_dir_btn)
        btn_layout.addWidget(self.remove_dir_btn)
        scan_group_layout.addLayout(btn_layout)
        
        layout.addWidget(scan_group)

        # 文件类型设置
        filetype_group = QGroupBox(get_text('file_types', self.current_language))
        filetype_layout = QVBoxLayout(filetype_group)
        
        self.filetype_edit = QLineEdit()
        self.filetype_edit.setPlaceholderText(".jpg;.jpeg;.png;.gif;.bmp")
        filetype_layout.addWidget(self.filetype_edit)
        
        layout.addWidget(filetype_group)

        # 确定和取消按钮
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton(get_text('ok', self.current_language))
        cancel_button = QPushButton(get_text('cancel', self.current_language))
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

    def load_settings(self):
        """从配置文件加载设置"""
        # 加载语言设置
        current_language = self.config_manager.get_language()
        index = self.language_combo.findData(current_language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

        # 加载目录设置
        directories = self.config_manager.get_scan_directories()
        self.directory_list.clear()
        for directory in directories:
            if directory:
                self.directory_list.addItem(directory)

        # 加载文件类型设置
        formats = self.config_manager.get_supported_formats()
        self.filetype_edit.setText(';'.join(formats))

    def save_settings(self):
        """保存设置到配置文件"""
        # 保存语言设置
        new_language = self.language_combo.currentData()
        self.config_manager.set_language(new_language)
        
        # 保存目录设置
        directories = []
        for i in range(self.directory_list.count()):
            directories.append(self.directory_list.item(i).text())
        self.config_manager.set_scan_directories(directories)

        # 保存文件类型设置
        formats = self.filetype_edit.text().strip()
        self.config_manager.set_supported_formats(formats)

    def add_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self, 
            get_text('select_directory', self.current_language)
        )
        if directory:
            self.directory_list.addItem(directory)

    def remove_directory(self):
        current_item = self.directory_list.currentItem()
        if current_item:
            self.directory_list.takeItem(self.directory_list.row(current_item))

    def accept(self):
        """点击确定按钮时保存设置"""
        old_language = self.config_manager.get_language()
        self.save_settings()
        new_language = self.language_combo.currentData()
        
        # 如果语言发生变化，提示需要重启应用
        if old_language != new_language:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                get_text('settings', self.current_language),
                "Language change will take effect after restart." if new_language == "en_US" else
                "语言更改将在重启后生效。"
            )
        
        super().accept() 