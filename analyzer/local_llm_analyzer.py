"""
本地 LLM 分析模块
使用 Ollama 本地模型进行快速情感分析
优化速度,适合实时分析场景
"""
from openai import OpenAI
from typing import Dict, Optional
import os
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)


class LocalLLMAnalyzer:
    """
    本地 LLM 分析器
    
    使用 Ollama 本地部署的轻量级模型进行快速分析:
    1. 快速情感分析
    2. 生成简短摘要
    
    技术特点:
    - 本地部署,响应速度快
    - 无需网络请求,隐私性好
    - 适合批量处理和实时分析
    """
    
    def __init__(self):
        """
        初始化本地 LLM 分析器
        从环境变量读取 Ollama 配置
        """
        self.api_key = os.getenv("LOCAL_LLM_API_KEY", "ollama")
        self.base_url = os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:11434/v1")
        self.model_id = os.getenv("LOCAL_LLM_MODEL", "qwen2:1.5b")
        
        # 初始化 OpenAI 兼容客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        logger.info(f"✅ 本地 LLM 分析器初始化完成 - 模型: {self.model_id}")
    
    def quick_analyze(self, title: str, content: str) -> Dict[str, any]:
        """
        快速分析文章
        
        Args:
            title: 文章标题
            content: 文章内容
            
        Returns:
            dict: 包含情感分析和简短摘要
        """
        logger.info("⚡ 开始快速分析...")
        
        # 限制内容长度以提高速度
        content_preview = content[:800]
        
        prompt = f"""请对以下文章进行快速分析:

标题: {title}

内容:
{content_preview}

请提供:
1. 情感倾向 (正面/中性/负面)
2. 情感得分 (0-1之间的数字,越接近1越正面)
3. 一句话摘要 (不超过50字)

请严格按照以下JSON格式返回:
{{
    "sentiment_label": "正面/中性/负面",
    "sentiment_score": 0.75,
    "summary": "一句话摘要"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": "你是一个专业的舆情分析助手,擅长快速判断文章情感倾向。请始终返回有效的JSON格式。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 降低温度以获得更稳定的输出
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            logger.info(f"📊 快速分析完成: {result_text}")
            
            # 尝试解析JSON响应
            import json
            try:
                # 提取JSON部分
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()
                
                result = json.loads(result_text)
                
                # 验证必需字段
                if "sentiment_label" not in result or "sentiment_score" not in result:
                    raise ValueError("缺少必需字段")
                
                # 确保得分在0-1范围内
                result["sentiment_score"] = max(0.0, min(1.0, float(result["sentiment_score"])))
                
                # 如果没有摘要,使用默认值
                if "summary" not in result:
                    result["summary"] = "快速分析完成"
                
                return result
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"⚠️ JSON解析失败,使用备用方案: {e}")
                # 备用方案: 基于关键词的简单分析
                return self._fallback_analysis(result_text, content)
            
        except Exception as e:
            logger.error(f"❌ 快速分析失败: {str(e)}")
            return {
                "sentiment_label": "中性",
                "sentiment_score": 0.5,
                "summary": "分析失败,请稍后重试"
            }
    
    def _fallback_analysis(self, llm_response: str, content: str) -> Dict[str, any]:
        """
        备用分析方案 - 当LLM返回格式不正确时使用
        
        Args:
            llm_response: LLM的原始响应
            content: 文章内容
            
        Returns:
            dict: 分析结果
        """
        # 从响应中提取情感标签
        sentiment_label = "中性"
        if "正面" in llm_response:
            sentiment_label = "正面"
        elif "负面" in llm_response:
            sentiment_label = "负面"
        
        # 简单的情感得分计算
        positive_words = ["好", "优秀", "成功", "进步", "提升", "增长", "喜", "赞"]
        negative_words = ["差", "失败", "下降", "问题", "危机", "担忧", "批评", "质疑"]
        
        pos_count = sum(1 for word in positive_words if word in content)
        neg_count = sum(1 for word in negative_words if word in content)
        
        total = pos_count + neg_count
        if total > 0:
            sentiment_score = pos_count / total
        else:
            sentiment_score = 0.5
        
        # 调整得分以匹配标签
        if sentiment_label == "正面" and sentiment_score < 0.6:
            sentiment_score = 0.7
        elif sentiment_label == "负面" and sentiment_score > 0.4:
            sentiment_score = 0.3
        
        return {
            "sentiment_label": sentiment_label,
            "sentiment_score": round(sentiment_score, 3),
            "summary": llm_response[:100] if llm_response else "快速分析完成"
        }


# 示例用法
if __name__ == "__main__":
    analyzer = LocalLLMAnalyzer()
    
    # 测试数据
    test_title = "某品牌新品发布会引发热议"
    test_content = "今日,某知名品牌举行新品发布会,推出了多款创新产品。消费者反响热烈,社交媒体上讨论度极高。"
    
    result = analyzer.quick_analyze(
        title=test_title,
        content=test_content
    )
    
    print(f"情感标签: {result['sentiment_label']}")
    print(f"情感得分: {result['sentiment_score']}")
    print(f"摘要: {result['summary']}")
