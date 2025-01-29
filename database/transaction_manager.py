from typing import Optional, List, Set
from contextlib import contextmanager
from utils.logger import Logger
from .db_manager import DatabaseManager
from .vector_store import VectorStore

class TransactionManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_manager()
        return cls._instance
    
    def _init_manager(self):
        """初始化事务管理器"""
        self.logger = Logger()
        self.db_manager = DatabaseManager()
        self.vector_store = VectorStore()
        self._transaction_active = False
        self._pending_operations = []
        self._transaction_level = 0
        
        # 确保数据库初始化
        if not self._initialized:
            self._init_database()
            self._initialized = True
    
    def _init_database(self):
        """初始化数据库，创建必要的表"""
        try:
            with self.transaction():
                # SQLite表已经在DatabaseManager中创建
                self.logger.info("[TransactionManager._init_database] 数据库初始化成功")
        except Exception as e:
            self.logger.error(f"[TransactionManager._init_database] 数据库初始化失败: {str(e)}")
            raise
    
    def _record_operation(self, operation_type: str, **kwargs):
        """记录待执行的操作"""
        if self._transaction_active:
            self._pending_operations.append({
                'type': operation_type,
                'params': kwargs
            })
    
    def _execute_pending_operations(self):
        """执行所有待处理的操作"""
        try:
            for operation in self._pending_operations:
                if operation['type'] == 'add_vector':
                    self.vector_store.add_image(
                        operation['params']['file_path'],
                        operation['params']['description']
                    )
                elif operation['type'] == 'delete_vector':
                    self.vector_store.delete_image(
                        operation['params']['file_path']
                    )
        except Exception as e:
            self.logger.error(f"[TransactionManager._execute_pending_operations] 执行待处理操作时出错: {str(e)}")
        finally:
            self._pending_operations.clear()
    
    @contextmanager
    def transaction(self):
        """事务上下文管理器
        
        支持事务嵌套，只有最外层事务会实际提交或回滚
        """
        is_outermost = self._transaction_level == 0
        self._transaction_level += 1
        
        if not is_outermost:
            try:
                yield self
            finally:
                self._transaction_level -= 1
            return
            
        self._transaction_active = True
        self._pending_operations.clear()
        
        try:
            self.db_manager.begin_transaction()
            yield self
            
            if self._transaction_level == 1:
                self._execute_pending_operations()
                self.db_manager.commit_transaction()
            
        except Exception as e:
            self.logger.error(f"事务执行失败: {str(e)}")
            if self._transaction_level == 1:
                self.db_manager.rollback_transaction()
                self._pending_operations.clear()
            raise
            
        finally:
            self._transaction_level -= 1
            if self._transaction_level == 0:
                self._transaction_active = False
    
    def add_image(self, image_data: dict, description: str) -> str:
        """添加图片到数据库
        
        Args:
            image_data: 图片基本信息字典，包含：
                - file_path: 文件路径
                - file_name: 文件名
                - file_size: 文件大小
                - md5: MD5值
                - created_time: 创建时间
                - modified_time: 修改时间
            description: 图片描述文本
            
        Returns:
            str: 图片ID
            
        Raises:
            Exception: 当操作失败时抛出异常
        """
        try:
            # 生成图片ID
            image_id = self.generate_image_id(image_data['file_path'])
            image_data['id'] = image_id
            
            if self._transaction_active:
                # 在事务中：先执行SQLite操作，记录向量操作
                self.db_manager.add_image(image_data, in_transaction=True)
                self._record_operation('add_vector', 
                    file_path=image_data['file_path'],
                    description=description
                )
            else:
                # 非事务模式：按顺序执行，出错时回滚
                self.db_manager.add_image(image_data, in_transaction=False)
                try:
                    self.vector_store.add_image(
                        image_data['file_path'],
                        description
                    )
                except Exception as e:
                    # 向量数据库操作失败，回滚SQLite
                    self.db_manager.delete_image_by_path(
                        image_data['file_path'],
                        in_transaction=False
                    )
                    raise
                    
            return image_id
            
        except Exception as e:
            self.logger.error(f"[TransactionManager.add_image] 添加图片失败: {str(e)}")
            raise
    
    def delete_image(self, file_path: str):
        """删除图片
        
        Args:
            file_path: 图片文件路径
            
        Raises:
            Exception: 当操作失败时抛出异常
        """
        try:
            if self._transaction_active:
                # 在事务中：先执行SQLite操作，记录向量操作
                self.db_manager.delete_image_by_path(file_path, in_transaction=True)
                self._record_operation('delete_vector', file_path=file_path)
            else:
                # 非事务模式：直接执行
                self.db_manager.delete_image_by_path(file_path, in_transaction=False)
                self.vector_store.delete_image(file_path)
                
        except Exception as e:
            self.logger.error(f"[TransactionManager.delete_image] 删除图片失败: {str(e)}")
            raise
    
    def get_image_by_id(self, image_id: str) -> Optional[dict]:
        """根据ID获取图片信息
        
        Args:
            image_id: 图片ID
            
        Returns:
            dict: 图片信息字典，如果不存在返回None
        """
        return self.db_manager.get_image_by_id(image_id)
    
    def search_similar_images(self, query: str, limit: int = 10) -> List[dict]:
        """搜索相似图片
        
        Args:
            query: 搜索查询文本
            limit: 返回结果数量限制
            
        Returns:
            List[dict]: 相似图片列表，每个元素包含完整的图片信息
        """
        try:
            results = self.vector_store.search_images(query, limit)
            images = []
            
            # 获取完整的图片信息
            for result in results.get('metadatas', [[]])[0]:
                image_id = result.get('image_id')
                if image_id:
                    image_info = self.get_image_by_id(image_id)
                    if image_info:
                        images.append(image_info)
                        
            return images
            
        except Exception as e:
            self.logger.error(f"[TransactionManager.search_similar_images] 搜索图片失败: {str(e)}")
            raise 
    
    def generate_image_id(self, file_path: str) -> str:
        """生成图片唯一ID
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            str: 生成的唯一ID
        """
        return self.vector_store.generate_image_id(file_path) 
    
    def get_all_records(self) -> List[dict]:
        """获取数据库中所有图片记录
        
        Returns:
            List[dict]: 所有图片记录的列表，每个记录包含完整的图片信息
        """
        try:
            return self.db_manager.get_all_records()
        except Exception as e:
            self.logger.error(f"获取所有记录失败: {str(e)}")
            raise 
        
    def clear_database(self):
        """清空数据库"""
        self.db_manager.drop_table('images')
        self.vector_store.clear_database()
        self.logger.info("[TransactionManager.clear_database] 数据库已清空")

    #从chromadb中获得所有记录的id
    def get_all_records_ids(self) -> List[str]:
        return self.vector_store.collection.get()["ids"]
    
    def delete_record_by_id(self, ids: Set[str]):
        """从向量数据库中删除指定ID的记录
        
        Args:
            ids: 要删除的记录ID集合
            
        Raises:
            Exception: 当删除操作失败时抛出异常
        """
        try:
            self.vector_store.collection.delete(ids=list(ids))
            self.logger.info(f"[TransactionManager.delete_record_by_id] 成功从向量数据库删除记录: {ids}")
        except Exception as e:
            self.logger.error(f"[TransactionManager.delete_record_by_id] 从向量数据库删除记录失败: {str(e)}")
            raise
            
    def commit_transaction(self):   
        """提交事务"""
        self.db_manager.commit_transaction()
        self.logger.info("[TransactionManager.commit_transaction] 事务提交成功")
        
    def rollback_transaction(self):
        """回滚事务"""
        self.db_manager.rollback_transaction()
        self.logger.info("[TransactionManager.rollback_transaction] 事务回滚成功")

    def _reset_transaction_state(self):
        """重置事务状态"""
        self._transaction_active = False
        self._pending_operations.clear()
        self._transaction_level = 0
        if self.db_manager.conn is not None:
            self.db_manager.rollback_transaction()

