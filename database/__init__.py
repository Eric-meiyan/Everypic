from .transaction_manager import TransactionManager

# 创建全局数据库管理器实例
db = TransactionManager()

# 导出常用函数，方便直接使用
def add_image(image_data: dict, description: str) -> str:
    """添加图片到数据库"""
    return db.add_image(image_data, description)

def delete_image(file_path: str):
    """删除图片"""
    db.delete_image(file_path)

def get_image_by_id(image_id: str) -> dict:
    """根据ID获取图片信息"""
    return db.get_image_by_id(image_id)

def search_similar_images(query: str, limit: int = 10) -> list:
    """搜索相似图片"""
    return db.search_similar_images(query, limit)

def transaction():
    """获取事务上下文管理器"""
    return db.transaction() 