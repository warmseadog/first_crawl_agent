"""
网页爬虫模块
使用 requests 和 BeautifulSoup 抓取网页内容
支持处理非结构化数据
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebCrawler:
    """
    网页爬虫类
    
    功能：
    1. 发送 HTTP 请求获取网页内容
    2. 使用 BeautifulSoup 解析 HTML
    3. 提取标题和正文文本
    4. 处理非结构化数据
    """
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """
        初始化爬虫
        
        Args:
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.timeout = timeout
        self.max_retries = max_retries
        
        # 设置请求头，模拟浏览器访问
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        获取网页 HTML 内容
        
        Args:
            url: 目标网页 URL
            
        Returns:
            str: HTML 内容，失败返回 None
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"正在抓取: {url} (尝试 {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    url, 
                    headers=self.headers, 
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                # 检查响应状态
                response.raise_for_status()
                
                # 自动检测编码
                response.encoding = response.apparent_encoding
                
                logger.info(f"✅ 成功抓取: {url}")
                return response.text
                
            except requests.exceptions.Timeout:
                logger.warning(f"⏱️ 请求超时: {url}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ 请求失败: {url}, 错误: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
        
        return None
    
    def extract_content(self, html: str, title_selectors: list = None, content_selectors: list = None) -> Dict[str, str]:
        """
        从 HTML 中提取标题和正文内容
        
        Args:
            html: HTML 内容
            title_selectors: 标题选择器列表（优先级从高到低）
            content_selectors: 正文选择器列表（优先级从高到低）
            
        Returns:
            dict: 包含 title 和 content 的字典
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # 移除脚本和样式标签
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # 默认标题选择器
        if title_selectors is None:
            title_selectors = [
                'h1',
                'title',
                '.article-title',
                '.post-title',
                '[class*="title"]'
            ]
        
        # 默认正文选择器
        if content_selectors is None:
            content_selectors = [
                'article',
                '.article-content',
                '.post-content',
                '.content',
                'main',
                '[class*="content"]',
                'body'
            ]
        
        # 提取标题
        title = self._extract_by_selectors(soup, title_selectors)
        if not title:
            title = "未找到标题"
        
        # 提取正文
        content = self._extract_by_selectors(soup, content_selectors)
        if not content:
            # 如果没有找到，尝试获取所有段落
            paragraphs = soup.find_all('p')
            content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        if not content:
            content = "未找到正文内容"
        
        return {
            "title": title.strip(),
            "content": content.strip()
        }
    
    def _extract_by_selectors(self, soup: BeautifulSoup, selectors: list) -> str:
        """
        按选择器优先级提取内容
        
        Args:
            soup: BeautifulSoup 对象
            selectors: CSS 选择器列表
            
        Returns:
            str: 提取的文本内容
        """
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(separator='\n', strip=True)
                    if text and len(text) > 10:  # 确保内容有意义
                        return text
            except Exception as e:
                logger.debug(f"选择器 {selector} 失败: {str(e)}")
                continue
        
        return ""
    
    def crawl(self, url: str, title_selectors: list = None, content_selectors: list = None) -> Optional[Dict[str, str]]:
        """
        完整的爬取流程：获取页面 -> 解析内容
        
        Args:
            url: 目标 URL
            title_selectors: 自定义标题选择器
            content_selectors: 自定义正文选择器
            
        Returns:
            dict: 包含 title, content, source 的字典，失败返回 None
        """
        # 获取 HTML
        html = self.fetch_page(url)
        if not html:
            return None
        
        # 提取内容
        extracted = self.extract_content(html, title_selectors, content_selectors)
        
        # 添加来源 URL
        extracted['source'] = url
        
        logger.info(f"📄 提取完成 - 标题: {extracted['title'][:50]}...")
        logger.info(f"📝 正文长度: {len(extracted['content'])} 字符")
        
        return extracted


# 示例用法
if __name__ == "__main__":
    crawler = WebCrawler()
    
    # 测试 URL（可以替换为实际新闻网站）
    test_url = "https://example.com"
    
    result = crawler.crawl(test_url)
    if result:
        print(f"标题: {result['title']}")
        print(f"内容: {result['content'][:200]}...")
