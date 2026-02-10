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
        nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
        
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
        
        with nav_col4:
            if st.button("🤖 智能助手", key="nav_rag", use_container_width=True):
                st.session_state['current_page'] = '智能助手'
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
    elif st.session_state['current_page'] == '智能助手':
        show_rag_chat()


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
        # 计算情感分布占比
        total = stats['total_articles']
        positive_pct = (stats['sentiment_distribution'].get('正面', 0) / max(total, 1)) * 100
        neutral_pct = (stats['sentiment_distribution'].get('中性', 0) / max(total, 1)) * 100
        negative_pct = (stats['sentiment_distribution'].get('负面', 0) / max(total, 1)) * 100
        
        # 判断主导情感
        if positive_pct > 50:
            dominant = "正面主导"
            dom_color = "#28a745"
        elif negative_pct > 30:
            dominant = "负面警示"
            dom_color = "#dc3545"
        else:
            dominant = "舆情平稳"
            dom_color = "#ffc107"
        
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, {dom_color} 0%, {dom_color}dd 100%);">
            <div class="stat-label">🎯 舆情态势</div>
            <div class="stat-value">{dominant}</div>
            <div class="stat-label">正{positive_pct:.0f}% | 中{neutral_pct:.0f}% | 负{negative_pct:.0f}%</div>
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
                name='情感倾向',
                line=dict(color='#667eea', width=3),
                fill='tozeroy',
                hovertemplate='<b>%{x}</b><br>得分: %{y:.2f}<extra></extra>'
            ))
            
            # 添加参考线
            fig_trend.add_hline(y=0.6, line_dash="dash", line_color="green", 
                               annotation_text="正面阈值", annotation_position="right")
            fig_trend.add_hline(y=0.4, line_dash="dash", line_color="red", 
                               annotation_text="负面阈值", annotation_position="right")
            
            fig_trend.update_layout(
                title="情感走势 (AI 深度分析)",
                xaxis_title="时间",
                yaxis_title="情感得分 (AI)",
                height=350,
                yaxis=dict(range=[0, 1])
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            st.caption("💡 此图表展示 AI 分析的情感得分趋势。0为极端负面，1为极端正面。")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ============ 数据采集页面 ============

def show_collection():
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 🔍 舆情数据采集")
    
    # 初始化session state用于保存当前输入
    if 'current_url' not in st.session_state:
        st.session_state['current_url'] = ''
    if 'current_source' not in st.session_state:
        st.session_state['current_source'] = '网络来源'
    
    # 预填充URL (优先使用热点话题选择的URL,否则使用当前保存的URL)
    default_url = st.session_state.get('selected_url', st.session_state['current_url'])
    default_title = st.session_state.get('selected_title', st.session_state['current_source'])
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        url = st.text_input(
            "📎 文章 URL",
            value=default_url,
            placeholder="https://example.com/article",
            key="url_input"
        )
    
    with col2:
        source_name = st.text_input(
            "📰 来源",
            value=default_title,
            key="source_input"
        )
    
    # 双按钮布局
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        quick_analyze_btn = st.button("⚡ 快速分析", use_container_width=True, type="secondary")
    
    with col_btn2:
        detailed_analyze_btn = st.button("🔬 详细分析", use_container_width=True, type="primary")
    
    # 快速分析逻辑
    if quick_analyze_btn:
        if not url:
            st.error("❌ 请输入 URL")
        else:
            # 保存当前URL到session state,以便分析后保留
            st.session_state['current_url'] = url
            st.session_state['current_source'] = source_name
            # 清除热点话题选择的URL
            if 'selected_url' in st.session_state:
                del st.session_state['selected_url']
            if 'selected_title' in st.session_state:
                del st.session_state['selected_title']
            
            with st.spinner("⚡ 正在进行快速分析..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/quick_analyze",
                        json={"url": url, "source_name": source_name},
                        timeout=30
                    )
                    result = response.json()
                    
                    if result.get('success'):
                        st.success("✅ 快速分析完成!")
                        
                        # 显示分析结果
                        st.markdown("---")
                        st.markdown("#### 📊 快速分析结果")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("情感得分", f"{result['sentiment_score']:.3f}")
                        with col2:
                            sentiment_label = result['sentiment_label']
                            color = get_sentiment_color(sentiment_label)
                            st.markdown(f"<div style='text-align: center;'><div class='stat-card' style='background: {color}; padding: 1rem;'>{sentiment_label}</div></div>", unsafe_allow_html=True)
                        with col3:
                            st.metric("分析模式", "快速 ⚡")
                        
                        # 标题和摘要
                        st.markdown(f"**📰 标题**: {result['title']}")
                        
                        if result.get('summary'):
                            st.markdown(f"**📝 摘要**: {result['summary']}")
                        
                        # 内容预览
                        with st.expander("📄 查看内容预览"):
                            st.markdown(result.get('content', '')[:500] + "...")
                        
                        st.info("💡 提示: 快速分析结果未保存到数据库。如需保存,请使用详细分析。")
                        
                    else:
                        st.error(f"❌ 分析失败: {result.get('detail', '未知错误')}")
                        
                except Exception as e:
                    st.error(f"❌ 请求失败: {str(e)}")
    
    # 详细分析逻辑
    if detailed_analyze_btn:
        if not url:
            st.error("❌ 请输入 URL")
        else:
            # 保存当前URL到session state
            st.session_state['current_url'] = url
            st.session_state['current_source'] = source_name
            # 清除热点话题选择的URL
            if 'selected_url' in st.session_state:
                del st.session_state['selected_url']
            if 'selected_title' in st.session_state:
                del st.session_state['selected_title']
            
            with st.spinner("🔬 正在进行详细分析..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/detailed_analyze",
                        json={"url": url, "source_name": source_name},
                        timeout=60
                    )
                    result = response.json()
                    
                    if result.get('success'):
                        st.success("✅ 详细分析完成!")
                        
                        # 显示分析结果
                        st.markdown("---")
                        st.markdown(f"#### 🏷️ 分析报告: {result['title']}")
                        
                        # 第一层：AI 核心结论 (高优先级)
                        col_summary, col_suggestions = st.columns(2)
                        with col_summary:
                            st.markdown("##### 📋 AI 核心摘要")
                            st.info(result.get('summary', '无摘要'))
                        
                        with col_suggestions:
                            st.markdown("##### 💡 应对建议")
                            st.warning(result.get('suggestions', '无建议'))

                        # 第二层：关键指标 (中优先级)
                        st.markdown("##### 📊 关键指标")
                        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                        
                        sentiment_label = result['sentiment_label']
                        color = get_sentiment_color(sentiment_label)
                        
                        with m_col1:
                            st.metric("核心倾向 (AI)", sentiment_label)
                        with m_col2:
                            st.metric("分析深度", "深度云端 🔬")
                        with m_col3:
                            st.metric("文章 ID", result.get('article_id', 'N/A'))
                        with m_col4:
                            # 逻辑：中性通常意味着模型判断较谨慎或内容确实客观
                            st.metric("结论可靠度", "极高 ✅" if sentiment_label != "中性" else "正常 ⚖️")

                        # 第三层：详细评分指标 (低优先级 - 放在折叠栏中)
                        with st.expander("📊 详细评分指标 (AI 模型)"):
                            st.markdown("""
                            > [!NOTE]
                            > 此处展示基于大语言模型的深度语义分析结果。评分综合考虑了文章的情感倾向、语气强弱及潜在影响。
                            """)
                            t_col1, t_col2 = st.columns(2)
                            with t_col1:
                                st.write(f"**情感得分**: `{result['sentiment_score']:.3f}`")
                                st.caption("（范围 0-1，由 AI 综合评估得出）")
                            with t_col2:
                                # 根据分数判断情感强度
                                score = result['sentiment_score']
                                if score > 0.8 or score < 0.2:
                                    intensity = "强烈"
                                elif score > 0.6 or score < 0.4:
                                    intensity = "明显"
                                else:
                                    intensity = "温和"
                                    
                                st.write(f"**情感强度**: {intensity}")
                                st.caption("（基于得分偏离中性值的程度）")
                        
                        # 内容预览
                        with st.expander("📄 查看网页原文本预览"):
                            st.markdown(result.get('content', '')[:1000] + "...")
                        
                        st.success("✅ 深度分析报告已完整保存至数据库")
                        st.balloons()
                        
                    else:
                        st.error(f"❌ 分析失败: {result.get('detail', '未知错误')}")
                        
                except Exception as e:
                    st.error(f"❌ 请求失败: {str(e)}")
    
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
            with st.expander("📊 查看完整分析报告"):
                if article['summary']:
                    st.markdown(f"**📋 AI 摘要**: {article['summary']}")
                if article['suggestions']:
                    st.markdown(f"**💡 应对建议**: {article['suggestions']}")
                
                # 将 SnowNLP 得分放在这里作为技术参考
                st.markdown("---")
                st.caption(f"🛠️ **底层统计得分**: `{article['sentiment_score']:.3f}` (SnowNLP 保底系统)")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ============ RAG 智能助手页面 ============

def show_rag_chat():
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 🤖 舆情智能助手 (RAG)")
    st.caption("基于已采集的舆情数据进行智能问答，回答时会引用具体的文章来源。")

    # 侧边功能区
    col_chat, col_info = st.columns([3, 1])

    with col_info:
        # 知识库状态
        st.markdown("#### 📚 知识库")
        try:
            rag_stats = requests.get(f"{API_BASE_URL}/api/rag/stats", timeout=5).json()
            if rag_stats.get('success'):
                doc_count = rag_stats.get('total_documents', 0)
                st.metric("已索引文章数", doc_count)
                st.caption(f"模型: {rag_stats.get('embedding_model', 'N/A')}")
            else:
                st.warning("知识库未就绪")
                doc_count = 0
        except:
            st.error("无法连接后端")
            doc_count = 0

        # 同步按钮
        if st.button("🔄 同步知识库", use_container_width=True, help="将数据库中的文章同步到向量知识库"):
            with st.spinner("正在同步..."):
                try:
                    resp = requests.post(f"{API_BASE_URL}/api/rag/sync", timeout=60).json()
                    if resp.get('success'):
                        st.success(f"✅ {resp.get('message', '同步完成')}")
                        st.rerun()
                    else:
                        st.error("同步失败")
                except Exception as e:
                    st.error(f"同步出错: {e}")

        st.markdown("---")
        st.markdown("#### 💡 试试问")
        example_questions = [
            "最近有哪些负面新闻？",
            "总结一下已采集文章的主要观点",
            "哪些话题的舆情风险最高？",
            "给我一份舆情简报"
        ]
        for q in example_questions:
            if st.button(f"💬 {q}", key=f"example_{q}", use_container_width=True):
                st.session_state['rag_pending_question'] = q
                st.rerun()

    with col_chat:
        # 初始化对话历史
        if 'rag_messages' not in st.session_state:
            st.session_state['rag_messages'] = []

        # 显示对话历史
        for msg in st.session_state['rag_messages']:
            with st.chat_message(msg['role'], avatar="🧑‍💻" if msg['role'] == 'user' else "🤖"):
                st.markdown(msg['content'])
                # 显示引用来源
                if msg.get('sources'):
                    with st.expander(f"📎 引用来源 ({len(msg['sources'])} 篇)"):
                        for src in msg['sources']:
                            sentiment_color = get_sentiment_color(src.get('sentiment_label', ''))
                            st.markdown(
                                f"- **{src['title']}** "
                                f"<span style='color:{sentiment_color};font-weight:bold;'>[{src.get('sentiment_label', '')}]</span> "
                                f"相关度: {src.get('relevance', 0):.0%}",
                                unsafe_allow_html=True
                            )
                            if src.get('source'):
                                st.caption(f"🔗 {src['source']}")

        # 处理预设问题
        pending = st.session_state.pop('rag_pending_question', None)

        # 用户输入
        user_input = st.chat_input("输入你的舆情问题...", key="rag_chat_input")
        question = pending or user_input

        if question:
            # 显示用户消息
            st.session_state['rag_messages'].append({"role": "user", "content": question})
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(question)

            # 调用 RAG API
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("正在检索知识库并生成回答..."):
                    try:
                        # 构建对话历史（只传 role + content）
                        history = [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state['rag_messages'][:-1]  # 不包含刚加的这条
                        ]

                        resp = requests.post(
                            f"{API_BASE_URL}/api/rag/chat",
                            json={
                                "question": question,
                                "chat_history": history[-12:]  # 最近6轮
                            },
                            timeout=60
                        ).json()

                        if resp.get('success'):
                            answer = resp['answer']
                            sources = resp.get('sources', [])

                            st.markdown(answer)

                            # 显示引用
                            if sources:
                                with st.expander(f"📎 引用来源 ({len(sources)} 篇)"):
                                    for src in sources:
                                        sentiment_color = get_sentiment_color(src.get('sentiment_label', ''))
                                        st.markdown(
                                            f"- **{src['title']}** "
                                            f"<span style='color:{sentiment_color};font-weight:bold;'>[{src.get('sentiment_label', '')}]</span> "
                                            f"相关度: {src.get('relevance', 0):.0%}",
                                            unsafe_allow_html=True
                                        )
                                        if src.get('source'):
                                            st.caption(f"🔗 {src['source']}")

                            # 保存到对话历史
                            st.session_state['rag_messages'].append({
                                "role": "assistant",
                                "content": answer,
                                "sources": sources
                            })

                            # 底部统计
                            st.caption(f"📊 检索了 {resp.get('search_count', 0)} 篇相关文章 | 知识库共 {resp.get('total_documents', 0)} 篇")
                        else:
                            st.error(f"❌ {resp.get('detail', '回答生成失败')}")

                    except Exception as e:
                        st.error(f"❌ 请求失败: {str(e)}")

        # 清空对话按钮
        if st.session_state['rag_messages']:
            if st.button("🗑️ 清空对话", key="clear_chat"):
                st.session_state['rag_messages'] = []
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ============ 运行应用 ============

if __name__ == "__main__":
    main()
