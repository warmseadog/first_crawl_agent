"""
测试 SnowNLP 情感分析的输出范围
检查是否真的会产生极化的 0/1 值
"""
from snownlp import SnowNLP

# 测试不同情感倾向的文本
test_texts = [
    "这个产品非常好用，我很满意！",
    "质量一般，价格有点贵。",
    "太差了，完全不推荐购买。",
    "今天天气不错",
    "这篇文章讨论了经济发展的趋势",
    "服务态度还可以，但是效率有待提高",
    "整体来说比较满意，有一些小瑕疵",
    "产品质量很好，但价格偏高",
    "一般般吧，没什么特别的",
    "非常失望，完全达不到预期"
]

print("=" * 60)
print("SnowNLP 情感分析测试")
print("=" * 60)

for text in test_texts:
    s = SnowNLP(text)
    score = s.sentiments
    print(f"{text[:30]:30s} -> {score:.4f}")

print("=" * 60)
