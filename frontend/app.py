"""
Streamlit 前端界面
舆情监测平台可视化仪表板
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# ============ 配置 ============

st.set_page_config(
    page_title="舆情监测平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API 基础 URL
API_BASE_URL = "http://localhost:8000"

# ============ 自定义样式 ============

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .positive {
        color: #28a745;
        font-weight: bold;
    }
    .neutral {
        color: #ffc107;
        font-weight: bold;
    }
    .negative {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============ 辅助函数 ============

def get_stats():
    """获取统计数据"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/stats")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_articles(limit=100, sentiment=None):
    """获取文章数据"""
    try:
        params = {"limit": limit}
        if sentiment:
            params["sentiment"] = sentiment
        
        response = requests.get(f"{API_BASE_URL}/api/get_data", params=params)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def collect_and_analyze(url, source_name):
    """触发爬取和分析"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/collect_and_analyze",
            json={"url": url, "source_name": source_name}
        )
        return response.json()
    except Exception as e:
        return {"success": False, "detail": str(e)}


def get_sentiment_color(label):
    """根据情感标签返回颜色"""
    colors = {
        "正面": "#28a745",
        "中性": "#ffc107",
        "负面": "#dc3545"
    }
    return colors.get(label, "#6c757d")


# ============ 主界面 ============

def main():
    # 标题
    st.markdown('<h1 class="main-header">📊 舆情监测平台</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 功能菜单")
        page = st.radio(
            "选择功能",
            ["📈 数据概览", "🔍 数据采集", "📋 详细列表"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 关于系统")
        st.info("""
        **舆情监测平台 v1.0**
        
        - 🕷️ 网络爬虫
        - 📊 情感分析 (SnowNLP)
        - 🤖 AI 摘要 (通义千问)
        - 📈 数据可视化
        """)
    
    # 页面路由
    if page == "📈 数据概览":
        show_dashboard()
    elif page == "🔍 数据采集":
        show_collection()
    elif page == "📋 详细列表":
        show_data_list()


# ============ 数据概览页面 ============

def show_dashboard():
    st.header("📈 数据概览")
    
    # 获取统计数据
    stats = get_stats()
    
    if not stats:
        st.error("❌ 无法连接到后端服务，请确保 API 服务已启动（运行: cd api && uvicorn main:app --reload）")
        return
    
    # 顶部指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📚 总文章数",
            value=stats['total_articles'],
            delta=f"今日 +{stats['today_count']}"
        )
    
    with col2:
        st.metric(
            label="📊 平均情感得分",
            value=f"{stats['avg_sentiment_score']:.3f}",
            delta="0-1 区间"
        )
    
    with col3:
        positive_count = stats['sentiment_distribution'].get('正面', 0)
        st.metric(
            label="😊 正面舆情",
            value=positive_count,
            delta=f"{positive_count/max(stats['total_articles'], 1)*100:.1f}%"
        )
    
    with col4:
        negative_count = stats['sentiment_distribution'].get('负面', 0)
        st.metric(
            label="😟 负面舆情",
            value=negative_count,
            delta=f"{negative_count/max(stats['total_articles'], 1)*100:.1f}%"
        )
    
    st.markdown("---")
    
    # 图表区域
    col1, col2 = st.columns(2)
    
    with col1:
        # 情感分布饼图
        st.subheader("🥧 情感分布")
        
        dist = stats['sentiment_distribution']
        if sum(dist.values()) > 0:
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(dist.keys()),
                values=list(dist.values()),
                marker=dict(colors=['#28a745', '#ffc107', '#dc3545']),
                hole=0.4
            )])
            fig_pie.update_layout(
                showlegend=True,
                height=350,
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("暂无数据")
    
    with col2:
        # 情感分布柱状图
        st.subheader("📊 情感统计")
        
        dist = stats['sentiment_distribution']
        if sum(dist.values()) > 0:
            df_bar = pd.DataFrame({
                '情感': list(dist.keys()),
                '数量': list(dist.values())
            })
            
            fig_bar = px.bar(
                df_bar,
                x='情感',
                y='数量',
                color='情感',
                color_discrete_map={
                    '正面': '#28a745',
                    '中性': '#ffc107',
                    '负面': '#dc3545'
                },
                text='数量'
            )
            fig_bar.update_layout(
                showlegend=False,
                height=350,
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("暂无数据")
    
    # 情感走势图
    st.subheader("📈 情感走势")
    
    articles_data = get_articles(limit=50)
    if articles_data and articles_data['data']:
        df = pd.DataFrame(articles_data['data'])
        df['created_at'] = pd.to_datetime(df['created_at'])
        df = df.sort_values('created_at')
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=df['created_at'],
            y=df['sentiment_score'],
            mode='lines+markers',
            name='情感得分',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=8)
        ))
        
        # 添加阈值线
        fig_trend.add_hline(y=0.6, line_dash="dash", line_color="green", annotation_text="正面阈值")
        fig_trend.add_hline(y=0.4, line_dash="dash", line_color="red", annotation_text="负面阈值")
        
        fig_trend.update_layout(
            xaxis_title="时间",
            yaxis_title="情感得分",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("暂无数据，请先采集一些舆情数据")


# ============ 数据采集页面 ============

def show_collection():
    st.header("🔍 数据采集")
    
    st.markdown("""
    输入新闻文章 URL，系统将自动：
    1. 🕷️ 爬取网页内容
    2. 📊 分析情感倾向（SnowNLP）
    3. 🤖 生成摘要和建议（通义千问）
    4. 💾 保存到数据库
    """)
    
    st.markdown("---")
    
    # 输入表单
    with st.form("collection_form"):
        url = st.text_input(
            "📎 文章 URL",
            placeholder="https://example.com/article",
            help="输入要分析的新闻文章链接"
        )
        
        source_name = st.text_input(
            "📰 来源名称",
            placeholder="例如：新浪新闻",
            value="网络来源"
        )
        
        submitted = st.form_submit_button("🚀 开始分析", use_container_width=True)
        
        if submitted:
            if not url:
                st.error("❌ 请输入 URL")
            else:
                with st.spinner("正在处理，请稍候..."):
                    # 显示进度
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("🕷️ 正在爬取网页...")
                    progress_bar.progress(25)
                    time.sleep(0.5)
                    
                    status_text.text("📊 正在分析情感...")
                    progress_bar.progress(50)
                    time.sleep(0.5)
                    
                    status_text.text("🤖 正在生成摘要...")
                    progress_bar.progress(75)
                    
                    # 调用 API
                    result = collect_and_analyze(url, source_name)
                    
                    progress_bar.progress(100)
                    status_text.empty()
                    progress_bar.empty()
                    
                    if result.get('success'):
                        st.success("✅ 分析完成！")
                        
                        # 显示结果
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("文章 ID", result['article_id'])
                            st.metric("情感得分", f"{result['sentiment_score']:.3f}")
                        
                        with col2:
                            st.metric("标题", result['title'][:30] + "...")
                            sentiment_label = result['sentiment_label']
                            color = get_sentiment_color(sentiment_label)
                            st.markdown(f"**情感标签**: <span style='color:{color}; font-size:1.2em;'>{sentiment_label}</span>", unsafe_allow_html=True)
                        
                        st.balloons()
                    else:
                        st.error(f"❌ 分析失败: {result.get('detail', '未知错误')}")
    
    st.markdown("---")
    
    # 示例 URL
    with st.expander("💡 示例 URL（供测试）"):
        st.code("""
# 可以使用这些类型的网站测试：
https://www.example.com
https://news.example.com/article/123

注意：某些网站可能有反爬虫机制，建议使用公开的新闻网站测试。
        """)


# ============ 详细列表页面 ============

def show_data_list():
    st.header("📋 舆情数据列表")
    
    # 筛选选项
    col1, col2 = st.columns([1, 3])
    
    with col1:
        sentiment_filter = st.selectbox(
            "按情感筛选",
            ["全部", "正面", "中性", "负面"]
        )
    
    with col2:
        limit = st.slider("显示数量", 10, 100, 50)
    
    # 获取数据
    filter_value = None if sentiment_filter == "全部" else sentiment_filter
    articles_data = get_articles(limit=limit, sentiment=filter_value)
    
    if not articles_data or not articles_data['data']:
        st.info("📭 暂无数据，请先采集一些舆情")
        return
    
    st.success(f"共找到 {articles_data['total']} 条数据，显示前 {articles_data['count']} 条")
    
    # 显示数据
    for article in articles_data['data']:
        with st.expander(f"📄 {article['title'][:60]}... | {article['sentiment_label']} ({article['sentiment_score']:.3f})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**📰 标题**: {article['title']}")
                st.markdown(f"**🔗 来源**: {article['source']}")
                st.markdown(f"**🕐 时间**: {article['created_at']}")
            
            with col2:
                color = get_sentiment_color(article['sentiment_label'])
                st.markdown(f"**情感**: <span style='color:{color}; font-size:1.2em;'>{article['sentiment_label']}</span>", unsafe_allow_html=True)
                st.metric("情感得分", f"{article['sentiment_score']:.3f}")
            
            st.markdown("---")
            
            st.markdown("**📝 正文内容**:")
            st.text_area("", article['content'][:500] + "...", height=100, key=f"content_{article['id']}", label_visibility="collapsed")
            
            if article['summary']:
                st.markdown("**📋 AI 摘要**:")
                st.info(article['summary'])
            
            if article['suggestions']:
                st.markdown("**💡 应对建议**:")
                st.warning(article['suggestions'])


# ============ 运行应用 ============

if __name__ == "__main__":
    main()
