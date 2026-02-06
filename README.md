# 舆情监测平台

基于网络爬虫与情感分析的舆情监测平台 - 毕业设计项目

## 📋 项目简介

本项目是一个完整的舆情监测系统，集成了网络爬虫、情感分析和大语言模型，能够自动抓取网络文章、分析情感倾向、生成摘要和应对建议。

### 核心功能

- 🕷️ **智能爬虫**:使用 BeautifulSoup 抓取非结构化网页内容
- 🔥 **热点话题推荐**:集成 Tavily API 自动获取当日热门新闻
- 📊 **双层情感分析**:
  - SnowNLP:快速量化分析（0-1 评分）
  - 通义千问:深度语义理解
- 🤖 **AI 增强**:自动生成摘要和舆情应对建议
- 📈 **数据可视化**:实时展示情感走势和分布
- 💾 **数据持久化**:SQLite 数据库存储

## 🛠️ 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | Streamlit + Plotly |
| 后端 | FastAPI + SQLAlchemy |
| 爬虫 | Requests + BeautifulSoup |
| 热点话题 | Tavily Search API |
| 分析 | SnowNLP + 通义千问 API |
| 数据库 | SQLite |

## 📁 项目结构

```
2.4爬虫项目谷歌/
├── .env                    # 环境变量配置
├── requirements.txt        # Python 依赖
├── README.md              # 项目说明
├── database/              # 数据库模块
│   ├── models.py         # 数据模型
│   └── database.py       # 数据库配置
├── crawler/               # 爬虫模块
│   └── web_crawler.py    # 网页爬虫
├── analyzer/              # 分析模块
│   ├── sentiment.py      # SnowNLP 情感分析
│   └── llm_analyzer.py   # LLM 集成
├── api/                   # FastAPI 后端
│   └── main.py           # API 服务
└── frontend/              # Streamlit 前端
    └── app.py            # 可视化界面
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件,填入 API 密钥:

```env
# 通义千问 API
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_ID=qwen3-max

# Tavily API (热点话题获取)
TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. 启动后端服务

```bash
cd api
uvicorn main:app --reload --port 8000
```

后端服务将在 `http://localhost:8000` 启动

### 4. 启动前端界面

新开一个终端窗口：

```bash
cd frontend
streamlit run app.py
```

前端界面将在浏览器自动打开（通常是 `http://localhost:8501`）

## 📖 使用指南

### 数据采集

1. 在前端选择 "🔍 数据采集" 页面
2. 输入新闻文章的 URL
3. 点击 "开始分析"
4. 系统将自动完成：爬取 → 情感分析 → AI 摘要 → 保存

### 数据查看

- **数据概览**：查看统计数据、情感分布图、走势图
- **详细列表**：浏览所有文章，查看完整分析结果

### API 接口

访问 `http://localhost:8000/docs` 查看完整 API 文档

主要接口：
- `POST /api/collect_and_analyze` - 触发分析流程
- `GET /api/get_data` - 获取舆情数据
- `GET /api/stats` - 获取统计信息

## 🎯 技术亮点

### 1. 非结构化数据处理

使用灵活的 CSS 选择器策略，能够适配不同网站结构：

```python
# 支持多种选择器优先级
title_selectors = ['h1', 'title', '.article-title', ...]
content_selectors = ['article', '.content', 'main', ...]
```

### 2. 双层情感分析对比

| 方法 | SnowNLP | 通义千问 LLM |
|------|---------|-------------|
| 类型 | 统计学习 | 深度语义理解 |
| 速度 | 快 | 较慢 |
| 准确度 | 中等 | 高 |
| 输出 | 量化得分 | 质化分析 |
| 适用场景 | 批量处理 | 深度分析 |

### 3. 模块化设计

- 各模块独立，易于测试和扩展
- 清晰的接口定义
- 完善的错误处理

## 📊 数据库设计

### articles 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| title | String(500) | 文章标题 |
| content | Text | 文章内容 |
| source | String(200) | 来源 URL |
| sentiment_score | Float | 情感得分 (0-1) |
| sentiment_label | String(20) | 情感标签 |
| summary | Text | AI 摘要 |
| suggestions | Text | 应对建议 |
| created_at | DateTime | 创建时间 |

## 🔧 开发说明

### 测试单个模块

```bash
# 测试爬虫
python crawler/web_crawler.py

# 测试情感分析
python analyzer/sentiment.py

# 测试 LLM
python analyzer/llm_analyzer.py
```

### 数据库初始化

数据库会在首次启动 API 服务时自动创建。

## 📝 注意事项

1. **API 密钥**：确保 `.env` 文件中配置了有效的通义千问 API 密钥
2. **网络访问**：某些网站可能有反爬虫机制，建议使用公开的新闻网站测试
3. **依赖安装**：建议使用虚拟环境安装依赖

## 🎓 毕业设计要点

本项目体现了以下技术要点：

1. ✅ 非结构化数据抓取与处理
2. ✅ 多种情感分析方法对比
3. ✅ 大语言模型集成应用
4. ✅ RESTful API 设计
5. ✅ 数据可视化实现
6. ✅ 完整的全栈开发流程

## 📄 许可证

本项目仅用于学习和毕业设计，请勿用于商业用途。

## 👨‍💻 作者

毕业设计项目 - 2026

---

**祝您使用愉快！如有问题，请查看代码注释或 API 文档。** 🎉
