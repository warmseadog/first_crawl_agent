"""
RAG 引擎模块
实现检索增强生成（Retrieval Augmented Generation）

核心流程：
1. 接收用户问题
2. 从向量库中检索相关文章
3. 将检索结果作为上下文注入 Prompt
4. 调用 LLM 生成基于证据的回答

技术要点：
- Context Window 管理
- 对话历史维护
- 引用来源追踪
"""
from openai import OpenAI
from typing import List, Dict, Optional
import os
import logging
from dotenv import load_dotenv
from .vector_store import VectorStore

load_dotenv()
logger = logging.getLogger(__name__)


class RAGEngine:
    """
    RAG 引擎

    将向量检索与 LLM 生成相结合，实现：
    1. 基于已采集舆情数据的智能问答
    2. 回答时引用具体的文章来源
    3. 支持多轮对话
    """

    # 系统提示词 - 定义 AI 的角色和回答规范
    SYSTEM_PROMPT = """你是一个专业的舆情分析助手。你的职责是根据已采集的舆情数据，回答用户关于舆情动态的问题。

【核心规则】
1. 只基于「参考资料」中提供的文章内容进行回答，不要编造信息
2. 回答时必须引用具体的文章标题作为依据
3. 如果参考资料中没有相关信息，请如实告知用户
4. 对情感分析保持专业，给出客观的舆情研判

【回答格式】
- 先直接回答用户的问题
- 然后列出引用的来源文章
- 如有必要，给出舆情趋势研判或建议"""

    def __init__(self, vector_store: VectorStore = None):
        """
        初始化 RAG 引擎

        Args:
            vector_store: 向量存储实例，如果为 None 则自动创建
        """
        self.vector_store = vector_store or VectorStore()

        # 初始化 LLM 客户端
        self.llm_client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL")
        )
        self.llm_model = os.getenv("LLM_MODEL_ID", "qwen-max")

        logger.info("✅ RAG 引擎初始化完成")

    def _build_context(self, search_results: List[Dict]) -> str:
        """
        将检索结果构建为 LLM 可用的上下文文本

        Args:
            search_results: 向量检索结果列表

        Returns:
            str: 格式化的上下文文本
        """
        if not search_results:
            return "【参考资料】\n暂无相关舆情数据。"

        context_parts = ["【参考资料】\n以下是与用户问题相关的舆情文章：\n"]

        for i, result in enumerate(search_results, 1):
            metadata = result.get('metadata', {})
            title = metadata.get('title', '未知标题')
            sentiment = metadata.get('sentiment_label', '未知')
            source = metadata.get('source', '未知来源')
            distance = result.get('distance', 0)
            document = result.get('document', '')

            # 取文档内容的关键部分
            content_preview = document[:500] if document else "无内容"

            context_parts.append(
                f"--- 文章 {i} ---\n"
                f"标题：{title}\n"
                f"情感倾向：{sentiment}\n"
                f"来源：{source}\n"
                f"相关度：{1 - distance:.2f}\n"
                f"内容：{content_preview}\n"
            )

        return "\n".join(context_parts)

    def chat(self, question: str, chat_history: List[Dict] = None,
             top_k: int = 5, sentiment_filter: str = None) -> Dict:
        """
        RAG 对话接口

        完整流程：检索 -> 构建上下文 -> LLM 生成 -> 返回结果

        Args:
            question: 用户问题
            chat_history: 对话历史 [{"role": "user/assistant", "content": "..."}]
            top_k: 检索文档数量
            sentiment_filter: 可选的情感过滤

        Returns:
            Dict: 包含回答、引用来源、检索统计
        """
        logger.info(f"💬 RAG 对话 - 问题: {question[:50]}...")

        # 1. 向量检索
        search_results = self.vector_store.search(
            query=question,
            top_k=top_k,
            sentiment_filter=sentiment_filter
        )

        # 2. 构建上下文
        context = self._build_context(search_results)

        # 3. 组装消息列表
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        # 添加对话历史（保留最近 6 轮）
        if chat_history:
            recent_history = chat_history[-12:]  # 6轮 = 12条消息
            messages.extend(recent_history)

        # 用户问题 + 检索上下文
        user_message = f"{context}\n\n【用户问题】\n{question}"
        messages.append({"role": "user", "content": user_message})

        # 4. LLM 生成
        try:
            response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )

            answer = response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"❌ LLM 生成失败: {str(e)}")
            answer = f"抱歉，生成回答时出现错误：{str(e)}"

        # 5. 提取引用来源
        sources = []
        for result in search_results:
            metadata = result.get('metadata', {})
            sources.append({
                "title": metadata.get('title', '未知'),
                "source": metadata.get('source', ''),
                "sentiment_label": metadata.get('sentiment_label', '未知'),
                "relevance": round(1 - result.get('distance', 0), 3)
            })

        logger.info(f"✅ RAG 回答生成完成 - 引用 {len(sources)} 篇文章")

        return {
            "answer": answer,
            "sources": sources,
            "search_count": len(search_results),
            "total_documents": self.vector_store.get_stats()["total_documents"]
        }
