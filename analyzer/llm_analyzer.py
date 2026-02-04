"""
LLM 分析模块
集成通义千问 API 进行深度语义分析
生成摘要和应对建议
"""
from openai import OpenAI
from typing import Dict, Optional
import os
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """
    LLM 分析器
    
    使用通义千问 API 进行：
    1. 生成文章摘要（100-200字）
    2. 生成舆情应对建议
    3. 提供语义层面的深度分析
    
    技术特点：
    - 基于大语言模型的语义理解
    - 准确度高，能捕捉细微情感
    - 提供质化的分析结果
    """
    
    def __init__(self):
        """
        初始化 LLM 分析器
        从环境变量读取 API 配置
        """
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL")
        self.model_id = os.getenv("LLM_MODEL_ID", "qwen-max")
        
        if not self.api_key:
            raise ValueError("❌ 未找到 LLM_API_KEY 环境变量")
        
        # 初始化 OpenAI 客户端（兼容通义千问）
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        logger.info(f"✅ LLM 分析器初始化完成 - 模型: {self.model_id}")
    
    def generate_summary(self, title: str, content: str, sentiment_score: float) -> str:
        """
        生成文章摘要
        
        Args:
            title: 文章标题
            content: 文章内容
            sentiment_score: 情感得分
            
        Returns:
            str: 文章摘要（100-200字）
        """
        prompt = f"""请为以下舆情文章生成一个简洁的摘要（100-200字）：

标题：{title}
情感得分：{sentiment_score}（0-1，越接近1越正面）

内容：
{content[:1000]}  # 限制输入长度

要求：
1. 提炼核心观点和关键信息
2. 保持客观中立
3. 字数控制在100-200字
4. 突出舆情要点"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": "你是一个专业的舆情分析助手，擅长提炼文章要点。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"📝 摘要生成完成 - 长度: {len(summary)} 字")
            return summary
            
        except Exception as e:
            logger.error(f"❌ 摘要生成失败: {str(e)}")
            return "摘要生成失败，请稍后重试。"
    
    def generate_suggestions(self, title: str, content: str, sentiment_score: float, sentiment_label: str) -> str:
        """
        生成舆情应对建议
        
        Args:
            title: 文章标题
            content: 文章内容
            sentiment_score: 情感得分
            sentiment_label: 情感标签
            
        Returns:
            str: 应对建议
        """
        prompt = f"""作为舆情分析专家，请针对以下舆情提供应对建议：

标题：{title}
情感倾向：{sentiment_label}（得分：{sentiment_score}）

内容摘要：
{content[:800]}

请提供：
1. 舆情风险评估（高/中/低）
2. 具体应对策略（2-3条）
3. 注意事项

要求简洁明了，每条建议不超过50字。"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": "你是一个专业的舆情应对顾问，擅长风险评估和危机公关。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            suggestions = response.choices[0].message.content.strip()
            logger.info(f"💡 建议生成完成 - 长度: {len(suggestions)} 字")
            return suggestions
            
        except Exception as e:
            logger.error(f"❌ 建议生成失败: {str(e)}")
            return "建议生成失败，请稍后重试。"
    
    def analyze(self, title: str, content: str, sentiment_score: float, sentiment_label: str) -> Dict[str, str]:
        """
        完整的 LLM 分析流程
        
        Args:
            title: 文章标题
            content: 文章内容
            sentiment_score: 情感得分
            sentiment_label: 情感标签
            
        Returns:
            dict: 包含 summary 和 suggestions 的字典
        """
        logger.info("🤖 开始 LLM 分析...")
        
        # 生成摘要
        summary = self.generate_summary(title, content, sentiment_score)
        
        # 生成建议
        suggestions = self.generate_suggestions(title, content, sentiment_score, sentiment_label)
        
        logger.info("✅ LLM 分析完成")
        
        return {
            "summary": summary,
            "suggestions": suggestions
        }


# 示例用法
if __name__ == "__main__":
    analyzer = LLMAnalyzer()
    
    # 测试数据
    test_title = "某品牌新品发布会引发热议"
    test_content = "今日，某知名品牌举行新品发布会，推出了多款创新产品。消费者反响热烈，社交媒体上讨论度极高。"
    
    result = analyzer.analyze(
        title=test_title,
        content=test_content,
        sentiment_score=0.75,
        sentiment_label="正面"
    )
    
    print(f"摘要: {result['summary']}")
    print(f"建议: {result['suggestions']}")
