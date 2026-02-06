"""
Tavily 热点话题获取模块
使用 Tavily Search API 获取当日热门新闻话题
"""
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("⚠️ Tavily 未安装，热点话题功能将不可用")


class TrendingFetcher:
    """热点话题获取器"""
    
    def __init__(self):
        """初始化 Tavily 客户端"""
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.client = None
        
        if not TAVILY_AVAILABLE:
            print("⚠️ Tavily 库未安装，请运行: pip install tavily-python")
            return
            
        if not self.api_key:
            print("⚠️ 未配置 TAVILY_API_KEY，热点话题功能将不可用")
            return
        
        try:
            self.client = TavilyClient(api_key=self.api_key)
            print("✅ Tavily 客户端初始化成功")
        except Exception as e:
            print(f"❌ Tavily 客户端初始化失败: {e}")
    
    def is_available(self) -> bool:
        """检查 Tavily 是否可用"""
        return TAVILY_AVAILABLE and self.client is not None
    
    def get_trending_topics(
        self, 
        query: str = "中国热点新闻", 
        max_results: int = 5,
        days: int = 1
    ) -> List[Dict]:
        """
        获取热点话题
        
        Args:
            query: 搜索查询词
            max_results: 最大返回结果数
            days: 搜索最近几天的内容
            
        Returns:
            List[Dict]: 热点话题列表，每个包含 title, url, content, score
        """
        if not self.is_available():
            return []
        
        try:
            # 使用 Tavily 搜索
            response = self.client.search(
                query=query,
                search_depth="basic",
                max_results=max_results,
                include_domains=[],
                exclude_domains=[]
            )
            
            # 格式化结果
            topics = []
            for idx, result in enumerate(response.get('results', []), 1):
                topic = {
                    'id': idx,
                    'title': result.get('title', '无标题'),
                    'url': result.get('url', ''),
                    'content': result.get('content', '')[:200] + '...',  # 摘要
                    'score': result.get('score', 0.0),
                    'published_date': result.get('published_date', ''),
                    'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                topics.append(topic)
            
            print(f"✅ 成功获取 {len(topics)} 个热点话题")
            return topics
            
        except Exception as e:
            print(f"❌ 获取热点话题失败: {e}")
            return []
    
    def get_trending_by_category(self, category: str = "综合") -> List[Dict]:
        """
        按类别获取热点话题
        
        Args:
            category: 类别（综合、科技、财经、社会、娱乐等）
            
        Returns:
            List[Dict]: 热点话题列表
        """
        category_queries = {
            "综合": "中国热门话题 娱乐 科技 生活",
            "科技": "最新科技产品 人工智能 数码评测",
            "娱乐": "明星八卦 影视综艺 音乐新歌",
            "体育": "体育赛事 NBA CBA 足球",
            "游戏": "热门游戏 电竞赛事 游戏攻略",
            "美食": "网红美食 餐厅推荐 美食教程"
        }
        
        query = category_queries.get(category, category_queries["综合"])
        return self.get_trending_topics(query=query, max_results=10)


# 测试代码
if __name__ == "__main__":
    fetcher = TrendingFetcher()
    
    if fetcher.is_available():
        print("\n" + "="*50)
        print("测试获取热点话题")
        print("="*50 + "\n")
        
        topics = fetcher.get_trending_topics(query="中国今日热点新闻", max_results=3)
        
        for topic in topics:
            print(f"\n📰 {topic['title']}")
            print(f"🔗 {topic['url']}")
            print(f"📝 {topic['content']}")
            print(f"⭐ 评分: {topic['score']:.2f}")
            print("-" * 50)
    else:
        print("❌ Tavily 不可用，请检查配置")
