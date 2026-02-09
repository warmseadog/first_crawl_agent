"""
FastAPI 主服务
提供舆情监测平台的 RESTful API 接口
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, init_db, Article
from crawler import WebCrawler, TrendingFetcher
from analyzer import SentimentAnalyzer, LLMAnalyzer, LocalLLMAnalyzer

# 创建 FastAPI 应用
app = FastAPI(
    title="舆情监测平台 API",
    description="基于网络爬虫与情感分析的舆情监测系统",
    version="1.0.0"
)

# 配置 CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化组件
crawler = WebCrawler()
sentiment_analyzer = SentimentAnalyzer()
llm_analyzer = LLMAnalyzer()
local_llm_analyzer = LocalLLMAnalyzer()
trending_fetcher = TrendingFetcher()


# ============ Pydantic 模型 ============

class CollectRequest(BaseModel):
    """爬取请求模型"""
    url: str
    source_name: Optional[str] = "未知来源"
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/article",
                "source_name": "示例网站"
            }
        }


class ArticleResponse(BaseModel):
    """文章响应模型"""
    id: int
    title: str
    content: str
    source: str
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]
    summary: Optional[str]
    suggestions: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    """统计响应模型"""
    total_articles: int
    sentiment_distribution: dict
    avg_sentiment_score: float
    today_count: int


# ============ API 路由 ============

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_db()
    print("🚀 舆情监测平台 API 已启动")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用舆情监测平台 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/api/collect_and_analyze", response_model=dict)
async def collect_and_analyze(request: CollectRequest, db: Session = Depends(get_db)):
    """
    完整的舆情分析流程：爬取 -> 情感分析 -> LLM 分析 -> 入库
    
    Args:
        request: 包含 URL 和来源名称的请求
        db: 数据库会话
        
    Returns:
        dict: 分析结果摘要
    """
    try:
        # 1. 爬取网页内容
        print(f"📡 开始爬取: {request.url}")
        crawl_result = crawler.crawl(request.url)
        
        if not crawl_result:
            raise HTTPException(status_code=400, detail="网页爬取失败，请检查 URL 是否有效")
        
        title = crawl_result['title']
        content = crawl_result['content']
        
        if len(content) < 50:
            raise HTTPException(status_code=400, detail="提取的内容过短，可能不是有效文章")
        
        # 2. SnowNLP 情感分析
        print("📊 进行情感分析...")
        sentiment_result = sentiment_analyzer.analyze(content)
        sentiment_score = sentiment_result['score']
        sentiment_label = sentiment_result['label']
        
        # 3. LLM 深度分析
        print("🤖 调用 LLM 生成摘要和建议...")
        llm_result = llm_analyzer.analyze(
            title=title,
            content=content,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label
        )
        
        # 4. 保存到数据库
        article = Article(
            title=title,
            content=content,
            source=request.url,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            summary=llm_result['summary'],
            suggestions=llm_result['suggestions']
        )
        
        db.add(article)
        db.commit()
        db.refresh(article)
        
        print(f"✅ 分析完成，文章 ID: {article.id}")
        
        return {
            "success": True,
            "article_id": article.id,
            "title": title,
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "message": "分析完成并已保存"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@app.post("/api/quick_analyze", response_model=dict)
async def quick_analyze(request: CollectRequest, db: Session = Depends(get_db)):
    """
    快速分析流程：爬取 -> 本地LLM快速分析
    不保存到数据库，仅返回分析结果
    
    Args:
        request: 包含 URL 和来源名称的请求
        db: 数据库会话
        
    Returns:
        dict: 快速分析结果
    """
    try:
        # 1. 爬取网页内容
        print(f"⚡ 快速分析: {request.url}")
        crawl_result = crawler.crawl(request.url)
        
        if not crawl_result:
            raise HTTPException(status_code=400, detail="网页爬取失败，请检查 URL 是否有效")
        
        title = crawl_result['title']
        content = crawl_result['content']
        
        if len(content) < 50:
            raise HTTPException(status_code=400, detail="提取的内容过短，可能不是有效文章")
        
        # 2. 本地LLM快速分析
        print("⚡ 使用本地模型进行快速分析...")
        analysis_result = local_llm_analyzer.quick_analyze(title, content)
        
        print(f"✅ 快速分析完成")
        
        return {
            "success": True,
            "mode": "quick",
            "title": title,
            "content": content[:500],  # 返回部分内容预览
            "sentiment_score": analysis_result['sentiment_score'],
            "sentiment_label": analysis_result['sentiment_label'],
            "summary": analysis_result.get('summary', ''),
            "message": "快速分析完成（未保存到数据库）"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 快速分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"快速分析失败: {str(e)}")


@app.post("/api/detailed_analyze", response_model=dict)
async def detailed_analyze(request: CollectRequest, db: Session = Depends(get_db)):
    """
    详细分析流程：爬取 -> 情感分析 -> 云端LLM深度分析 -> 入库
    完整分析并保存到数据库
    
    Args:
        request: 包含 URL 和来源名称的请求
        db: 数据库会话
        
    Returns:
        dict: 详细分析结果
    """
    try:
        # 1. 爬取网页内容
        print(f"🔬 详细分析: {request.url}")
        crawl_result = crawler.crawl(request.url)
        
        if not crawl_result:
            raise HTTPException(status_code=400, detail="网页爬取失败，请检查 URL 是否有效")
        
        title = crawl_result['title']
        content = crawl_result['content']
        
        if len(content) < 50:
            raise HTTPException(status_code=400, detail="提取的内容过短，可能不是有效文章")
        
        # 2. SnowNLP 情感分析
        print("📊 进行情感分析...")
        sentiment_result = sentiment_analyzer.analyze(content)
        sentiment_score = sentiment_result['score']
        sentiment_label = sentiment_result['label']
        
        # 3. 云端LLM 深度分析
        print("🤖 调用云端 LLM 生成摘要和建议...")
        llm_result = llm_analyzer.analyze(
            title=title,
            content=content,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label
        )
        
        # 4. 保存到数据库
        article = Article(
            title=title,
            content=content,
            source=request.url,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            summary=llm_result['summary'],
            suggestions=llm_result['suggestions']
        )
        
        db.add(article)
        db.commit()
        db.refresh(article)
        
        print(f"✅ 详细分析完成，文章 ID: {article.id}")
        
        return {
            "success": True,
            "mode": "detailed",
            "article_id": article.id,
            "title": title,
            "content": content[:500],
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "summary": llm_result['summary'],
            "suggestions": llm_result['suggestions'],
            "message": "详细分析完成并已保存到数据库"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 详细分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"详细分析失败: {str(e)}")


@app.get("/api/get_data", response_model=dict)
async def get_data(
    limit: int = 100,
    sentiment: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取舆情数据
    
    Args:
        limit: 返回数量限制
        sentiment: 按情感标签筛选（正面/中性/负面）
        db: 数据库会话
        
    Returns:
        dict: 包含总数和数据列表
    """
    try:
        # 构建查询
        query = db.query(Article)
        
        # 按情感筛选
        if sentiment:
            query = query.filter(Article.sentiment_label == sentiment)
        
        # 按时间倒序
        query = query.order_by(Article.created_at.desc())
        
        # 获取总数
        total = query.count()
        
        # 限制数量
        articles = query.limit(limit).all()
        
        # 转换为字典
        data = [article.to_dict() for article in articles]
        
        return {
            "success": True,
            "total": total,
            "count": len(data),
            "data": data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """
    获取统计数据
    
    Args:
        db: 数据库会话
        
    Returns:
        StatsResponse: 统计信息
    """
    try:
        # 总文章数
        total_articles = db.query(Article).count()
        
        # 情感分布
        positive_count = db.query(Article).filter(Article.sentiment_label == "正面").count()
        neutral_count = db.query(Article).filter(Article.sentiment_label == "中性").count()
        negative_count = db.query(Article).filter(Article.sentiment_label == "负面").count()
        
        sentiment_distribution = {
            "正面": positive_count,
            "中性": neutral_count,
            "负面": negative_count
        }
        
        # 平均情感得分
        articles = db.query(Article).filter(Article.sentiment_score.isnot(None)).all()
        if articles:
            avg_score = sum([a.sentiment_score for a in articles]) / len(articles)
        else:
            avg_score = 0.0
        
        # 今日新增
        today = datetime.now().date()
        today_count = db.query(Article).filter(
            Article.created_at >= datetime.combine(today, datetime.min.time())
        ).count()
        
        return StatsResponse(
            total_articles=total_articles,
            sentiment_distribution=sentiment_distribution,
            avg_sentiment_score=round(avg_score, 4),
            today_count=today_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"统计失败: {str(e)}")


@app.delete("/api/article/{article_id}")
async def delete_article(article_id: int, db: Session = Depends(get_db)):
    """
    删除文章
    
    Args:
        article_id: 文章 ID
        db: 数据库会话
        
    Returns:
        dict: 删除结果
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    db.delete(article)
    db.commit()
    
    return {
        "success": True,
        "message": f"文章 {article_id} 已删除"
    }


@app.get("/api/trending", response_model=dict)
async def get_trending_topics(category: Optional[str] = "综合"):
    """
    获取热点话题
    
    Args:
        category: 话题类别（综合、科技、财经、社会、娱乐、国际）
        
    Returns:
        dict: 热点话题列表
    """
    try:
        if not trending_fetcher.is_available():
            return {
                "success": False,
                "message": "Tavily API 未配置或不可用",
                "data": [],
                "hint": "请在 .env 文件中配置 TAVILY_API_KEY"
            }
        
        # 获取热点话题
        topics = trending_fetcher.get_trending_by_category(category)
        
        return {
            "success": True,
            "category": category,
            "count": len(topics),
            "data": topics,
            "message": f"成功获取 {len(topics)} 个热点话题"
        }
        
    except Exception as e:
        print(f"❌ 获取热点话题失败: {str(e)}")
        return {
            "success": False,
            "message": f"获取失败: {str(e)}",
            "data": []
        }


# ============ 运行服务 ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
