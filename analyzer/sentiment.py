"""
情感分析模块
使用 SnowNLP 进行中文情感分析
提供量化的情感得分
"""
from snownlp import SnowNLP
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    情感分析器
    
    使用 SnowNLP 进行情感分析，提供：
    1. 情感得分（0-1，越接近1越正面）
    2. 情感标签（正面/中性/负面）
    
    技术特点：
    - 基于统计学习的方法
    - 速度快，适合批量处理
    - 提供量化的情感指标
    """
    
    def __init__(self, positive_threshold: float = 0.6, negative_threshold: float = 0.4):
        """
        初始化情感分析器
        
        Args:
            positive_threshold: 正面情感阈值（≥此值为正面）
            negative_threshold: 负面情感阈值（<此值为负面）
        """
        self.positive_threshold = positive_threshold
        self.negative_threshold = negative_threshold
    
    def analyze(self, text: str) -> Dict[str, any]:
        """
        分析文本情感
        
        Args:
            text: 待分析的文本
            
        Returns:
            dict: 包含 score 和 label 的字典
                - score: 情感得分 (0-1)
                - label: 情感标签 (正面/中性/负面)
        """
        try:
            # 使用 SnowNLP 分析
            s = SnowNLP(text)
            score = s.sentiments
            
            # 根据阈值确定标签
            if score >= self.positive_threshold:
                label = "正面"
            elif score < self.negative_threshold:
                label = "负面"
            else:
                label = "中性"
            
            logger.info(f"📊 情感分析完成 - 得分: {score:.3f}, 标签: {label}")
            
            return {
                "score": round(score, 4),
                "label": label
            }
            
        except Exception as e:
            logger.error(f"❌ 情感分析失败: {str(e)}")
            return {
                "score": 0.5,
                "label": "中性"
            }
    
    def batch_analyze(self, texts: list) -> list:
        """
        批量分析文本情感
        
        Args:
            texts: 文本列表
            
        Returns:
            list: 分析结果列表
        """
        results = []
        for i, text in enumerate(texts):
            logger.info(f"正在分析 {i+1}/{len(texts)}...")
            result = self.analyze(text)
            results.append(result)
        
        return results
    
    def get_statistics(self, scores: list) -> Dict[str, any]:
        """
        计算情感得分统计信息
        
        Args:
            scores: 得分列表
            
        Returns:
            dict: 统计信息（平均值、最大值、最小值）
        """
        if not scores:
            return {
                "avg": 0,
                "max": 0,
                "min": 0,
                "count": 0
            }
        
        return {
            "avg": round(sum(scores) / len(scores), 4),
            "max": round(max(scores), 4),
            "min": round(min(scores), 4),
            "count": len(scores)
        }


# 示例用法
if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    
    # 测试文本
    test_texts = [
        "这个产品非常好用，我很满意！",
        "质量一般，价格有点贵。",
        "太差了，完全不推荐购买。"
    ]
    
    for text in test_texts:
        result = analyzer.analyze(text)
        print(f"文本: {text}")
        print(f"结果: {result}\n")
