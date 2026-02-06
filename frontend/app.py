"""
Streamlit 前端界面
舆情监测平台可视化仪表板 - 现代化设计
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import pytz

# ============ 配置 ============

st.set_page_config(
    page_title="舆情监测平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"  # 默认收起侧边栏
)

# API 基础 URL
API_BASE_URL = "http://localhost:8000"

# 时区配置
TIMEZONES = {
    "北京时间 (UTC+8)": "Asia/Shanghai",
    "东京时间 (UTC+9)": "Asia/Tokyo",
    "纽约时间 (UTC-5)": "America/New_York",
    "伦敦时间 (UTC+0)": "Europe/London",
    "巴黎时间 (UTC+1)": "Europe/Paris"
}

# ============ 自定义样式 ============

st.markdown("""
<style>
    /* 隐藏默认侧边栏 */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* 全局样式 */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* 顶部导航栏 */
    .top-nav {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 1rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .nav-title {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(120deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
        margin-right: 2rem;
    }
    
    .nav-buttons {
        display: inline-flex;
        gap: 1rem;
        align-items: center;
    }
    
    /* 导航按钮样式 */
    .nav-btn {
        display: inline-block;
        padding: 0.6rem 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 25px;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
        border: none;
        font-size: 1rem;
    }
    
    .nav-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .nav-btn.active {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
    }
    
    /* 内容卡片 */
    .content-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    }
    
    /* 统计卡片 */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0.5rem 0;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* 实时时钟 */
    .realtime-clock {
        display: inline-block;
        font-size: 1rem;
        font-weight: 600;
        color: #667eea;
        padding: 0.5rem 1rem;
        background: rgba(102, 126, 234, 0.1);
        border-radius: 20px;
    }
    
    /* 热点话题卡片 */
    .trending-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 5px solid #667eea;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .trending-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }
    
    /* 标签样式 */
    .tag {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        font-size: 0.85rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* 情感标签 */
    .positive {
        color: #28a745;
        font-weight: bold;
        font-size: 1.1em;
    }
    .neutral {
        color: #ffc107;
        font-weight: bold;
        font-size: 1.1em;
    }
    .negative {
        color: #dc3545;
        font-weight: bold;
        font-size: 1.1em;
    }
    
    /* 按钮优化 */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        border: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
    }
    
    /* 输入框样式 */
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.8rem;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    
    /* 选择框样式 */
    .stSelectbox>div>div {
        border-radius: 10px;
    }
    
    /* 隐藏 Streamlit 默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============ 辅助函数 ============

def get_current_time(timezone_name):
    """获取指定时区的当前时间"""
    tz = pytz.timezone(TIMEZONES[timezone_name])
    return datetime.now(tz)


def get_stats():
    """获取统计数据"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/stats", timeout=5)
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
        
        response = requests.get(f"{API_BASE_URL}/api/get_data", params=params, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_trending_topics(category="综合"):
    """获取热点话题"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/trending", params={"category": category}, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"获取热点话题失败: {e}")
        return None


def collect_and_analyze(url, source_name):
    """触发爬取和分析"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/collect_and_analyze",
            json={"url": url, "source_name": source_name},
            timeout=60
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
    # 初始化页面状态
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = '数据概览'
    
    # 顶部导航栏
    st.markdown('<div class="top-nav">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 4, 2])
    
    with col1:
        st.markdown('<span class="nav-title">📊 舆情监测</span>', unsafe_allow_html=True)
    
    with col2:
        # 导航按钮
        nav_col1, nav_col2, nav_col3 = st.columns(3)
        
        with nav_col1:
            if st.button("📈 数据概览", key="nav_dashboard", use_container_width=True):
                st.session_state['current_page'] = '数据概览'
                st.rerun()
        
        with nav_col2:
            if st.button("🔍 数据采集", key="nav_collect", use_container_width=True):
                st.session_state['current_page'] = '数据采集'
                st.rerun()
        
        with nav_col3:
            if st.button("📋 详细列表", key="nav_list", use_container_width=True):
                st.session_state['current_page'] = '详细列表'
                st.rerun()
    
    with col3:
        # 时区选择和时钟
        selected_timezone = st.selectbox(
            "时区",
            list(TIMEZONES.keys()),
            index=0,
            label_visibility="collapsed",
            key="timezone_selector"
        )
        current_time = get_current_time(selected_timezone)
        st.markdown(
            f'<div class="realtime-clock">🕐 {current_time.strftime("%H:%M:%S")}</div>',
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 页面路由
    if st.session_state['current_page'] == '数据概览':
        show_dashboard()
    elif st.session_state['current_page'] == '数据采集':
        show_collection()
    elif st.session_state['current_page'] == '详细列表':
        show_data_list()


# ============ 数据概览页面 ============

def show_dashboard():
    # 获取统计数据
    stats = get_stats()
    
    if not stats:
        st.error("❌ 无法连接到后端服务")
        return
    
    # 统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">📚 总文章数</div>
            <div class="stat-value">{stats['total_articles']}</div>
            <div class="stat-label">今日 +{stats['today_count']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">📊 平均情感</div>
            <div class="stat-value">{stats['avg_sentiment_score']:.2f}</div>
            <div class="stat-label">0-1 区间</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        positive_count = stats['sentiment_distribution'].get('正面', 0)
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
            <div class="stat-label">😊 正面舆情</div>
            <div class="stat-value">{positive_count}</div>
            <div class="stat-label">{positive_count/max(stats['total_articles'], 1)*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        negative_count = stats['sentiment_distribution'].get('负面', 0)
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);">
            <div class="stat-label">😟 负面舆情</div>
            <div class="stat-value">{negative_count}</div>
            <div class="stat-label">{negative_count/max(stats['total_articles'], 1)*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 热点话题分类
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    col_title, col_refresh = st.columns([5, 1])
    with col_title:
        st.markdown("### 🔥 热点话题分类")
    with col_refresh:
        if st.button("🔄", key="refresh_trending", help="刷新全部分类"):
            keys_to_delete = [k for k in st.session_state.keys() if k.startswith('trending_cache_')]
            for key in keys_to_delete:
                del st.session_state[key]
            st.rerun()
    
    # 分类标签页
    categories = ["综合", "科技", "娱乐", "体育", "游戏", "美食"]
    category_icons = {"综合": "🌟", "科技": "💻", "娱乐": "🎬", "体育": "⚽", "游戏": "🎮", "美食": "🍜"}
    
    tabs = st.tabs([f"{category_icons[cat]} {cat}" for cat in categories])
    
    for tab, category in zip(tabs, categories):
        with tab:
            cache_key = f'trending_cache_{category}'
            
            if cache_key not in st.session_state:
                with st.spinner(f"加载{category}热点..."):
                    st.session_state[cache_key] = get_trending_topics(category)
            
            trending_data = st.session_state[cache_key]
            
            if trending_data and trending_data.get('success'):
                topics = trending_data.get('data', [])[:3]
                
                if topics:
                    for rank, topic in enumerate(topics, 1):
                        medal = ["🥇", "🥈", "🥉"][rank-1]
                        color = ["#FFD700", "#C0C0C0", "#CD7F32"][rank-1]
                        score = topic.get('score', 0) * 100
                        
                        st.markdown(f"""
                        <div class="trending-card" style="border-left-color: {color};">
                            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                                <span style="font-size: 2rem; margin-right: 0.8rem;">{medal}</span>
                                <a href="{topic['url']}" target="_blank" style="text-decoration: none;">
                                    <span style="font-size: 1.2rem; font-weight: 700; color: #2c3e50; cursor: pointer;">
                                        {topic['title'][:50]}... 🔗
                                    </span>
                                </a>
                            </div>
                            <div style="color: #7f8c8d; font-size: 0.9rem; margin-bottom: 0.5rem;">
                                {topic['content'][:100]}...
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span class="tag">热度: {score:.1f}</span>
                                <a href="{topic['url']}" target="_blank" style="text-decoration: none;">
                                    <span style="color: #667eea; font-size: 0.85rem;">📰 查看原文</span>
                                </a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"📊 分析", key=f"analyze_{category}_{rank}", use_container_width=True):
                            st.session_state['selected_url'] = topic['url']
                            st.session_state['selected_title'] = topic['title']
                            st.session_state['current_page'] = '数据采集'
                            st.rerun()
                else:
                    st.info(f"💡 {category}类别暂无热点")
            else:
                st.warning(f"⚠️ 无法获取{category}热点")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 图表区域
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 📊 数据分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        dist = stats['sentiment_distribution']
        if sum(dist.values()) > 0:
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(dist.keys()),
                values=list(dist.values()),
                marker=dict(colors=['#28a745', '#ffc107', '#dc3545']),
                hole=0.4
            )])
            fig_pie.update_layout(
                title="情感分布",
                height=350,
                showlegend=True
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
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
                line=dict(color='#667eea', width=3),
                fill='tozeroy'
            ))
            fig_trend.update_layout(
                title="情感走势",
                xaxis_title="时间",
                yaxis_title="情感得分",
                height=350
            )
            st.plotly_chart(fig_trend, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# ============ 数据采集页面 ============

def show_collection():
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 🔍 舆情数据采集")
    
    # 预填充URL
    default_url = st.session_state.get('selected_url', '')
    default_title = st.session_state.get('selected_title', '网络来源')
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        url = st.text_input(
            "📎 文章 URL",
            value=default_url,
            placeholder="https://example.com/article"
        )
    
    with col2:
        source_name = st.text_input(
            "📰 来源",
            value=default_title if default_url else "网络来源"
        )
    
    if st.button("🚀 开始分析", use_container_width=True, type="primary"):
        if 'selected_url' in st.session_state:
            del st.session_state['selected_url']
        if 'selected_title' in st.session_state:
            del st.session_state['selected_title']
        
        if not url:
            st.error("❌ 请输入 URL")
        else:
            with st.spinner("正在分析..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                result = collect_and_analyze(url, source_name)
                
                if result.get('success'):
                    st.success("✅ 分析完成!")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("文章 ID", result['article_id'])
                    with col2:
                        st.metric("情感得分", f"{result['sentiment_score']:.3f}")
                    with col3:
                        st.metric("标题", result['title'][:20] + "...")
                    with col4:
                        sentiment_label = result['sentiment_label']
                        color = get_sentiment_color(sentiment_label)
                        st.markdown(f"<div class='stat-card' style='background: {color};'>{sentiment_label}</div>", unsafe_allow_html=True)
                    
                    st.balloons()
                else:
                    st.error(f"❌ 分析失败: {result.get('detail', '未知错误')}")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ============ 详细列表页面 ============

def show_data_list():
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 📋 舆情数据列表")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        sentiment_filter = st.selectbox("情感筛选", ["全部", "正面", "中性", "负面"])
    
    with col2:
        limit = st.slider("显示数量", 10, 100, 50)
    
    with col3:
        search_keyword = st.text_input("🔍 搜索", placeholder="输入关键词...")
    
    filter_value = None if sentiment_filter == "全部" else sentiment_filter
    articles_data = get_articles(limit=limit, sentiment=filter_value)
    
    if not articles_data or not articles_data['data']:
        st.info("📭 暂无数据")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    articles = articles_data['data']
    if search_keyword:
        articles = [a for a in articles if search_keyword.lower() in a['title'].lower()]
    
    st.success(f"共 {len(articles)} 条数据")
    
    for article in articles:
        color = get_sentiment_color(article['sentiment_label'])
        
        st.markdown(f"""
        <div class="trending-card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.8rem;">
                <div style="flex: 1;">
                    <a href="{article['source']}" target="_blank" style="text-decoration: none;">
                        <h4 style="margin: 0; color: #2c3e50; cursor: pointer;">
                            {article['title']} 🔗
                        </h4>
                    </a>
                    <div style="margin-top: 0.5rem;">
                        <span class="tag" style="background: {color};">{article['sentiment_label']}</span>
                        <span class="tag">得分: {article['sentiment_score']:.3f}</span>
                        <span style="color: #95a5a6; font-size: 0.85rem; margin-left: 1rem;">
                            📅 {article['created_at']}
                        </span>
                    </div>
                </div>
            </div>
            <div style="color: #7f8c8d; font-size: 0.9rem; line-height: 1.6; margin-bottom: 0.8rem;">
                {article['content'][:200]}...
            </div>
            <div style="text-align: right;">
                <a href="{article['source']}" target="_blank" style="text-decoration: none;">
                    <span style="color: #667eea; font-size: 0.85rem;">📰 查看原文</span>
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if article['summary'] or article['suggestions']:
            with st.expander("查看详细分析"):
                if article['summary']:
                    st.markdown(f"**📋 摘要**: {article['summary']}")
                if article['suggestions']:
                    st.markdown(f"**💡 建议**: {article['suggestions']}")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ============ 运行应用 ============

if __name__ == "__main__":
    main()
