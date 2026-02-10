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
    
    def analyze(self, title: str, content: str) -> Dict[str, any]:
        """
        完整的 LLM 分析流程：情感分析 + 摘要 + 建议
        
        Args:
            title: 文章标题
            content: 文章内容
            
        Returns:
            dict: 包含 sentiment_score, sentiment_label, summary, suggestions
        """
        logger.info("🤖 开始 LLM 全量分析...")
        
        prompt = f"""请对以下舆情文章进行深度分析，并仅以 JSON 格式返回结果：

标题：{title}

内容：
{content[:1500]}  # 限制输入长度

请返回如下 JSON 结构（不要包含 markdown 代码块标记）：
{{
    "sentiment_score": float,  # 情感得分，0.0-1.0，精确到小数点后2位。0代表极端负面，1代表极端正面。
    "sentiment_label": string, # "正面"、"中性" 或 "负面"
    "summary": string,         # 100-200字的精炼摘要
    "suggestions": string      # 针对该舆情的具体应对建议（50字以内）
}}

注意：
1. 评分需客观反映内容的实际情感倾向，不要盲目给高分。
2. 负面舆情（如投诉、丑闻、批评）分数应低于0.4。
3. 中性报道（如客观陈述、公告）分数应在0.4-0.6之间。
4. 正面报道（如表彰、成果）分数应高于0.6。
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": "你是一个专业的舆情分析专家。请严格按照 JSON 格式输出分析结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3, # 降低温度以保证格式稳定
                max_tokens=600,
                response_format={"type": "json_object"} # 强制 JSON 模式
            )
            
            result_json = response.choices[0].message.content.strip()
            
            # 简单的容错处理，防止返回 markdown 标记
            if result_json.startswith("```json"):
                result_json = result_json[7:]
            if result_json.endswith("```"):
                result_json = result_json[:-3]
                
            import json
            result = json.loads(result_json)
            
            logger.info(f"✅ LLM 分析完成: {result.get('sentiment_label')} ({result.get('sentiment_score')})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ LLM 分析失败: {str(e)}")
            # 返回兜底数据
            return {
                "sentiment_score": 0.5,
                "sentiment_label": "中性",
                "summary": "分析服务暂时不可用，请稍后重试。",
                "suggestions": "请人工审查该内容。"
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
