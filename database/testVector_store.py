import chromadb
# import matplotlib.pyplot as plt
# from sklearn.decomposition import PCA
from vector_store import VectorStore

# 访问在 VectorStore 中创建的向量数据库
vector_store = VectorStore()
collection = vector_store.collection

# 获取向量数据
results = collection.get()
document_count = len(results)
print(f"向量数据库中集合中的文档数量: {document_count}")