# 快速分析性能优化说明

## 问题分析

快速分析慢的主要原因:

### 1. **网页爬取是最大瓶颈** (占总时间80-90%)

当前爬虫配置:
- `timeout=10秒` - 等待服务器响应的最大时间
- `max_retries=3` - 失败后会重试3次
- 每次重试有指数退避延迟 (2秒, 4秒, 8秒)

**慢的原因**:
- 如果目标网站在国外(如外国新闻网站),没有梯子会非常慢
- 网站响应慢或不稳定时,会触发重试机制
- **与Tavily无关** - Tavily只用于热点话题获取,不参与文章分析

### 2. **本地LLM推理** (占总时间10-20%)

- Ollama首次调用需要加载模型到内存
- `qwen2:1.5b` 虽然是轻量模型,但仍需1-3秒推理时间

## 优化建议

### 方案1: 优化爬虫配置 (已实现)

修改 `api/main.py` 的 `quick_analyze` 函数:

```python
# 使用更短的超时时间
quick_crawler = WebCrawler(timeout=5, max_retries=1)
```

**效果**: 减少等待时间,失败快速返回

### 方案2: 测试国内网站

使用国内新闻网站测试,避免网络延迟:
- 新浪新闻
- 网易新闻  
- 腾讯新闻
- 澎湃新闻

### 方案3: 预热Ollama模型

在后端启动时预先调用一次模型:

```python
# 在 api/main.py 的 startup_event 中添加
@app.on_event("startup")
async def startup_event():
    init_db()
    # 预热本地LLM
    try:
        local_llm_analyzer.quick_analyze("测试", "这是一个测试文本")
        print("✅ 本地LLM预热完成")
    except:
        print("⚠️ 本地LLM预热失败,请确保Ollama正在运行")
```

### 方案4: 使用代理(如果分析国外网站)

如果需要分析国外网站,配置HTTP代理:

修改 `crawler/web_crawler.py`:

```python
def fetch_page(self, url: str) -> Optional[str]:
    proxies = {
        'http': 'http://127.0.0.1:7890',  # 你的代理地址
        'https': 'http://127.0.0.1:7890'
    }
    
    response = requests.get(
        url,
        headers=self.headers,
        timeout=self.timeout,
        proxies=proxies  # 添加代理
    )
```

## 性能对比

| 场景 | 预期耗时 |
|------|---------|
| 国内网站 + 模型已加载 | 2-5秒 |
| 国内网站 + 模型未加载 | 5-8秒 |
| 国外网站无代理 | 10-30秒+ |
| 国外网站有代理 | 3-8秒 |

## 诊断步骤

1. 查看后端终端日志,会显示:
   ```
   ⏱️ 爬取耗时: X.XX秒
   ⏱️ LLM推理耗时: X.XX秒
   ✅ 快速分析完成,总耗时: X.XX秒
   ```

2. 根据日志判断瓶颈:
   - 如果爬取耗时>5秒 → 网络问题,考虑使用代理或国内网站
   - 如果LLM耗时>3秒 → Ollama未启动或模型未加载

## 立即可行的优化

**最简单的方法**: 测试国内新闻网站

例如:
- `https://news.sina.com.cn/c/2024-01-01/xxx.shtml`
- `https://www.163.com/news/article/xxx.html`

这样可以避免网络延迟,快速分析应该在3-5秒内完成。
