"""
向量存储模块
使用 ChromaDB 实现舆情文章的向量化存储与检索
支持语义搜索，为 RAG 提供知识库

技术要点：
- ChromaDB 本地持久化存储
- DashScope text-embedding-v3 向量化
- 支持按元数据（情感、时间等）过滤检索
"""
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from typing import List, Dict, Optional
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class VectorStore:
    """
    向量存储器

    封装 ChromaDB 操作，提供：
    1. 文章向量化入库
    2. 语义检索（基于余弦相似度）
    3. 集合统计信息

    Embedding 使用 DashScope 的 text-embedding-v3 模型
    """

    def __init__(self, persist_directory: str = None):
        """
        初始化向量存储

        Args:
            persist_directory: ChromaDB 持久化目录路径
        """
        if persist_directory is None:
            # 默认存在项目根目录下
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            persist_directory = os.path.join(project_root, "chroma_db")

        self.persist_directory = persist_directory

        # 初始化 ChromaDB 客户端（持久化模式）
        self.client = chromadb.PersistentClient(path=persist_directory)

        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name="articles",
            metadata={"description": "舆情文章向量集合"}
        )

        # 初始化 Embedding 客户端（DashScope 兼容 OpenAI 接口）
        self.embedding_client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL")
        )
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")

        logger.info(f"✅ 向量存储初始化完成 - 持久化目录: {persist_directory}")
        logger.info(f"📊 当前集合文档数: {self.collection.count()}")

    def _get_embedding(self, text: str) -> List[float]:
        """
        获取文本的向量表示

        Args:
            text: 待向量化的文本

        Returns:
            List[float]: 向量列表
        """
        try:
            # 截断过长的文本（embedding 模型有 token 限制）
            text = text[:2000]

            response = self.embedding_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )

            return response.data[0].embedding

        except Exception as e:
            logger.error(f"❌ 向量化失败: {str(e)}")
            raise

    def add_article(self, article_id: int, title: str, content: str,
                    sentiment_label: str = None, sentiment_score: float = None,
                    source: str = None, summary: str = None) -> bool:
        """
        将文章添加到向量存储

        Args:
            article_id: 文章数据库 ID
            title: 文章标题
            content: 文章内容
            sentiment_label: 情感标签
            sentiment_score: 情感得分
            source: 来源 URL
            summary: AI 摘要

        Returns:
            bool: 是否成功
        """
        try:
            doc_id = f"article_{article_id}"

            # 检查是否已存在
            existing = self.collection.get(ids=[doc_id])
            if existing and existing['ids']:
                logger.info(f"⏭️ 文章 {article_id} 已在向量库中，跳过")
                return True

            # 拼接用于向量化的文本：标题 + 摘要 + 内容前段
            embed_text = f"标题：{title}\n"
            if summary:
                embed_text += f"摘要：{summary}\n"
            embed_text += f"内容：{content[:1500]}"

            # 获取向量
            embedding = self._get_embedding(embed_text)

            # 构建元数据
            metadata = {
                "article_id": article_id,
                "title": title,
                "source": source or "",
                "sentiment_label": sentiment_label or "未知",
                "sentiment_score": sentiment_score or 0.5
            }

            # 存入 ChromaDB
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[embed_text],
                metadatas=[metadata]
            )

            logger.info(f"✅ 文章 {article_id} 已向量化入库 - '{title[:30]}...'")
            return True

        except Exception as e:
            logger.error(f"❌ 文章向量化入库失败: {str(e)}")
            return False

    def search(self, query: str, top_k: int = 5,
               sentiment_filter: str = None) -> List[Dict]:
        """
        语义检索相关文章

        Args:
            query: 用户查询文本
            top_k: 返回结果数量
            sentiment_filter: 可选的情感过滤条件

        Returns:
            List[Dict]: 检索结果列表，每项包含文档内容、元数据和相似度
        """
        try:
            if self.collection.count() == 0:
                logger.warning("⚠️ 向量库为空，无法检索")
                return []

            # 获取查询向量
            query_embedding = self._get_embedding(query)

            # 构建过滤条件
            where_filter = None
            if sentiment_filter and sentiment_filter != "全部":
                where_filter = {"sentiment_label": sentiment_filter}

            # 执行检索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self.collection.count()),
                where=where_filter if where_filter else None
            )

            # 格式化结果
            formatted_results = []
            if results and results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    result = {
                        "id": results['ids'][0][i],
                        "document": results['documents'][0][i] if results['documents'] else "",
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0
                    }
                    formatted_results.append(result)

            logger.info(f"🔍 检索完成 - 查询: '{query[:30]}...' | 结果数: {len(formatted_results)}")
            return formatted_results

        except Exception as e:
            logger.error(f"❌ 检索失败: {str(e)}")
            return []

    def get_stats(self) -> Dict:
        """
        获取向量库统计信息

        Returns:
            Dict: 统计信息
        """
        count = self.collection.count()
        return {
            "total_documents": count,
            "persist_directory": self.persist_directory,
            "collection_name": "articles",
            "embedding_model": self.embedding_model
        }

    def sync_from_db(self, db_session) -> int:
        """
        从数据库同步所有文章到向量库

        Args:
            db_session: SQLAlchemy 数据库会话

        Returns:
            int: 新增同步的文章数量
        """
        from database import Article

        articles = db_session.query(Article).all()
        synced = 0

        for article in articles:
            success = self.add_article(
                article_id=article.id,
                title=article.title,
                content=article.content,
                sentiment_label=article.sentiment_label,
                sentiment_score=article.sentiment_score,
                source=article.source,
                summary=article.summary
            )
            if success:
                synced += 1

        logger.info(f"📦 数据库同步完成 - 共 {len(articles)} 篇，新增 {synced} 篇")
        return synced
