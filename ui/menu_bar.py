from PyQt6.QtWidgets import QMenu, QMenuBar
from PyQt6.QtGui import QAction
from .settings_dialog import SettingsDialog
from utils.scan_thread import ScanThread
from utils.image_scanner import ImageScanner
from utils.logger import Logger
from database.transaction_manager import TransactionManager
from database.synchronizer import DatabaseSynchronizer
from utils.config_manager import ConfigManager

def create_menu_bar(window, menubar):
    # 文件菜单
    file_menu = menubar.addMenu("文件(&F)")
    
    new_action = QAction("新建", window)
    exit_action = QAction("退出", window)
    exit_action.triggered.connect(window.close)
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
    
    options_action = QAction("设置", window)
    options_action.triggered.connect(lambda: show_settings_dialog(window))
    scan_action = QAction("扫描", window)
    scan_action.triggered.connect(lambda: start_scan(window))
    
    tools_menu.addAction(options_action)
    tools_menu.addAction(scan_action)
    
    # 帮助菜单
    help_menu = menubar.addMenu("帮助(&H)")
    
    help_action = QAction("帮助", window)
    about_action = QAction("关于", window)
    help_menu.addAction(help_action)
    help_menu.addAction(about_action)

def show_settings_dialog(parent):
    dialog = SettingsDialog(parent)
    if dialog.exec() == SettingsDialog.Accepted:
        # 设置已经在对话框的 accept() 方法中保存了
        pass

def start_scan(parent):
    """开始扫描图片"""
    try:
        # 对比库中的数据与图片目录中图片文件的差异
        synchronizer = DatabaseSynchronizer()
        # 通过配置文件，得到图片目录
        picture_dirs = ConfigManager().get_scan_directories()
        
        Logger().info("[MenuBar.start_scan] 开始扫描图片目录...")
        Logger().info(f"[MenuBar.start_scan] 待扫描目录: {picture_dirs}")
        
        try:
            synchronizer.sync_database(picture_dirs)
            Logger().info("[MenuBar.start_scan] 扫描完成")
        except Exception as e:
            Logger().error(f"[MenuBar.start_scan] 同步数据库时出错: {str(e)}")
            import traceback
            Logger().error(f"[MenuBar.start_scan] 错误详情: {traceback.format_exc()}")
            raise
            
    except Exception as e:
        Logger().error(f"[MenuBar.start_scan] 扫描过程出错: {str(e)}")
        import traceback
        Logger().error(f"[MenuBar.start_scan] 错误详情: {traceback.format_exc()}")

    # """开始扫描图片"""
    # logger = Logger()
    # scanner = ImageScanner()
    # try:
    #     scanner.start_scan()
    #     logger.info("图片扫描完成")
    #     scanner.scan_completed.emit()
    # except Exception as e:
    #     error_msg = f"扫描过程出错: {str(e)}"
    #     logger.error(error_msg)


    # logger = Logger()
    # try:
    #     # 创建并启动扫描线程
    #     scan_thread = ScanThread()
    #     scan_thread.progress_updated.connect(lambda msg: logger.info(msg))
    #     scan_thread.scan_completed.connect(lambda: logger.info("扫描完成"))
    #     scan_thread.start()
    #     logger.info("开始扫描图片...")
    # except Exception as e:
    #     logger.error(f"启动扫描失败: {str(e)}") 

    # transaction_manager = TransactionManager()
    # try:
    #     results = transaction_manager.search_similar_images("小朋友")
    #     print("查询结果:")
    #     # 先打印完整的结果对象，看看实际的数据结构
    #     print("原始结果:", results)
    #     for result in results:
    #         # 打印每个结果的所有可用键
    #         print("可用的键:", result.keys())
    #         # 安全地访问数据
    #         print(f"图片ID: {result.get('id', 'N/A')}")
    #         print(f"文件路径: {result.get('file_path', 'N/A')}")
    #         # 使用 get 方法避免 KeyError
    #         print(f"描述: {result.get('description', 'N/A')}")
    # except Exception as e:
    #     print(f"查询失败: {str(e)}")
    #     import traceback
    #     traceback.print_exc()