"""
数据库连接配置模块
使用 SQLAlchemy 创建数据库引擎和会话
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 数据库文件路径
DATABASE_URL = "sqlite:///./opinion_monitor.db"

# 创建数据库引擎
# check_same_thread=False 允许多线程访问 SQLite
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False  # 设置为 True 可以看到 SQL 语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类，所有模型都继承此类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖函数
    用于 FastAPI 的依赖注入
    
    Yields:
        Session: 数据库会话对象
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库，创建所有表
    """
    from .models import Article  # 导入模型以注册到 Base
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库初始化完成")
