"""
测试脚本 - 验证各模块功能
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("舆情监测平台 - 模块测试")
print("=" * 60)

# 1. 测试数据库
print("\n1️⃣ 测试数据库模块...")
try:
    from database import init_db, SessionLocal, Article
    init_db()
    print("✅ 数据库模块正常")
except Exception as e:
    print(f"❌ 数据库模块错误: {e}")

# 2. 测试爬虫
print("\n2️⃣ 测试爬虫模块...")
try:
    from crawler import WebCrawler
    crawler = WebCrawler()
    print("✅ 爬虫模块正常")
except Exception as e:
    print(f"❌ 爬虫模块错误: {e}")

# 3. 测试情感分析
print("\n3️⃣ 测试情感分析模块...")
try:
    from analyzer import SentimentAnalyzer
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("这是一个很好的测试文本")
    print(f"✅ 情感分析模块正常 - 测试结果: {result}")
except Exception as e:
    print(f"❌ 情感分析模块错误: {e}")

# 4. 测试 LLM
print("\n4️⃣ 测试 LLM 模块...")
try:
    from analyzer import LLMAnalyzer
    llm = LLMAnalyzer()
    print("✅ LLM 模块正常（API 密钥已配置）")
except Exception as e:
    print(f"❌ LLM 模块错误: {e}")
    print("   提示：请检查 .env 文件中的 API 密钥配置")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)

# 显示下一步操作
print("\n📝 下一步操作：")
print("1. 启动后端：cd api && uvicorn main:app --reload")
print("2. 启动前端：cd frontend && streamlit run app.py")
print("3. 访问前端界面开始使用")
