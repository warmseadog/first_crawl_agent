"""
数据库模型定义
定义舆情文章的数据结构
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from datetime import datetime
from .database import Base


class Article(Base):
    """
    舆情文章数据模型
    
    字段说明：
    - id: 主键，自增
    - title: 文章标题
    - content: 文章正文内容
    - source: 数据来源 URL
    - sentiment_score: SnowNLP 情感得分 (0-1)
    - sentiment_label: 情感标签（正面/中性/负面）
    - summary: LLM 生成的文章摘要
    - suggestions: LLM 生成的应对建议
    - created_at: 创建时间
    """
    __tablename__ = "articles"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 文章基本信息
    title = Column(String(500), nullable=False, comment="文章标题")
    content = Column(Text, nullable=False, comment="文章内容")
    source = Column(String(200), nullable=False, comment="数据来源URL")
    
    # 情感分析结果
    sentiment_score = Column(Float, nullable=True, comment="情感得分(0-1)")
    sentiment_label = Column(String(20), nullable=True, comment="情感标签")
    
    # LLM 分析结果
    summary = Column(Text, nullable=True, comment="文章摘要")
    suggestions = Column(Text, nullable=True, comment="应对建议")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def __repr__(self):
        """字符串表示"""
        return f"<Article(id={self.id}, title='{self.title[:20]}...', sentiment={self.sentiment_label})>"
    
    def to_dict(self):
        """
        将模型转换为字典
        
        Returns:
            dict: 包含所有字段的字典
        """
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "source": self.source,
            "sentiment_score": self.sentiment_score,
            "sentiment_label": self.sentiment_label,
            "summary": self.summary,
            "suggestions": self.suggestions,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
