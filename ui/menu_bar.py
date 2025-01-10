from PyQt6.QtWidgets import QMenu, QMenuBar
from PyQt6.QtGui import QAction

def create_menu_bar(window, menubar):
    # 文件菜单
    file_menu = menubar.addMenu("文件(&F)")
    
    new_action = QAction("新建", window)
    exit_action = QAction("退出", window)
    file_menu.addAction(new_action)
    file_menu.addAction(exit_action)
    
    # 编辑菜单
    edit_menu = menubar.addMenu("编辑(&E)")
    
    cut_action = QAction("剪切", window)
    copy_action = QAction("复制", window)
    paste_action = QAction("粘贴", window)
    edit_menu.addAction(cut_action)
    edit_menu.addAction(copy_action)
    edit_menu.addAction(paste_action)
    
    # 工具菜单
    tools_menu = menubar.addMenu("工具(&T)")
    
    options_action = QAction("选项", window)
    tools_menu.addAction(options_action)
    
    # 帮助菜单
    help_menu = menubar.addMenu("帮助(&H)")
    
    help_action = QAction("帮助", window)
    about_action = QAction("关于", window)
    help_menu.addAction(help_action)
    help_menu.addAction(about_action) 