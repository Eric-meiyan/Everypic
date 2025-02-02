from PyQt6.QtCore import QThread, pyqtSignal
from utils.image_scanner import ImageScanner
from utils.logger import Logger

class ScanThread(QThread):
    # 定义信号
    progress_updated = pyqtSignal(str)  # 用于更新扫描进度
    scan_completed = pyqtSignal()       # 用于通知扫描完成
    
    def __init__(self):
        super().__init__()
        self.logger = Logger()
        self.scanner = None  # 初始化为 None
        
    def run(self):
        """执行扫描任务"""
        self.logger.info("进入线程run函数")
        
        try:
            self.logger.info("开始后台扫描图片...")
            self.progress_updated.emit("开始扫描图片...")
            
            self.scanner = ImageScanner()  # 移到这里，只在需要时创建
            self.scanner.start_scan()  # 执行实际的扫描
            
            self.logger.info("图片扫描完成")
            self.progress_updated.emit("扫描完成")
            self.scan_completed.emit()
            
        except Exception as e:
            error_msg = f"扫描过程出错: {str(e)}"
            self.logger.error(error_msg)
            self.progress_updated.emit(error_msg) 