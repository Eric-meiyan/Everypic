import chromadb
from chromadb.config import Settings
import hashlib
from utils.logger import Logger

class VectorStore:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_store()
        return cls._instance
    
    def _init_store(self):
        """初始化ChromaDB"""
        self.logger = Logger()
        try:
            # 使用持久化存储
            self.client = chromadb.PersistentClient(path="./vector_db")
            # 获取或创建集合
            self.collection = self.client.get_or_create_collection(
                name="image_descriptions",
                metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
            )
            self.logger.info("向量数据库初始化成功")
        except Exception as e:
            self.logger.error(f"向量数据库初始化失败: {str(e)}")
            raise
    
    def generate_image_id(self, file_path: str) -> str:
        """生成图片唯一ID"""
        return hashlib.sha256(file_path.encode()).hexdigest()
    
    def add_image(self, file_path: str, description: str):
        """添加图片描述到向量数据库"""
        try:
            image_id = self.generate_image_id(file_path)
            # ChromaDB会自动处理事务，如果发生异常会自动回滚
            self.collection.add(
                documents=[description],
                metadatas=[{"image_id": image_id, "file_path": file_path}],
                ids=[image_id]
            )
            self.logger.info(f"添加图片描述到向量数据库: {file_path}")
            return image_id
        except Exception as e:
            self.logger.error(f"添加图片描述失败: {str(e)}")
            raise
    
    def delete_image(self, file_path: str):
        """从向量数据库删除图片描述"""
        try:
            image_id = self.generate_image_id(file_path)
            self.collection.delete(ids=[image_id])
            self.logger.info(f"从向量数据库删除图片描述: {file_path}")
        except Exception as e:
            self.logger.error(f"删除图片描述失败: {str(e)}")
            raise
    
    def search_images(self, query: str, limit: int = 10) -> list:
        """搜索相似图片"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            return results
        except Exception as e:
            self.logger.error(f"搜索图片失败: {str(e)}")
            raise 
        
    def clear_database(self):
        """清空向量数据库"""
        try:
            # 获取所有文档ID
            ids = self.collection.get()["ids"]
            if ids:  # 只在有数据时执行删除操作
                self.collection.delete(ids=ids)
                self.logger.info("向量数据库已清空")
            else:
                self.logger.info("向量数据库已经为空，无需清理")
        except Exception as e:
            self.logger.error(f"清空向量数据库失败: {str(e)}")
            raise
