# RAG系统构建各阶段图解

## 阶段1：数据采集与预处理
```mermaid
graph LR
    A[原始网页] --> B[爬虫提取]
    B --> C[标题+内容+摘要]
    C --> D[文本清洗]
    D --> E[结构化存储]

    style A fill:#e1f5fe
    style E fill:#e8f5e8
```
策略：提取网页关键信息，去除无关内容，标准化文本格式

## 阶段2：向量化处理
```mermaid
graph LR
    A[清洗后文本] --> B[组合策略]
    B --> C["标题+摘要+内容片段"]
    C --> D[截断2000字符]
    D --> E[获取向量]
    E --> F[1536维向量]

    style C fill:#fff3e0
    style D fill:#f3e5f5
```
策略：组合关键信息进行向量化，限制文本长度防超限

## 阶段3：知识库存储
```mermaid
graph LR
    A[向量+元数据] --> B[ChromaDB]
    B --> C[文档ID: article_X]
    C --> D[向量: 1536维]
    D --> E[元数据: 情感标签等]
    E --> F[持久化存储]

    style C fill:#e1f5fe
    style E fill:#e8f5e8
```
策略：按ID建立映射，保留元数据便于检索过滤

## 阶段4：检索与匹配
```mermaid
graph LR
    A[用户查询] --> B[向量化查询]
    B --> C[ChromaDB检索]
    C --> D[相似度计算]
    D --> E[Top-K匹配]
    E --> F[返回结果]

    style B fill:#fff3e0
    style D fill:#f3e5f5
```
策略：语义相似度检索，支持情感过滤，返回最相关结果

## 阶段5：上下文构建
```mermaid
graph LR
    A[检索结果] --> B[格式化组装]
    B --> C["文章1+情感+来源"]
    C --> D["文章2+情感+来源"]
    D --> E[构建上下文]
    E --> F[注入提示词]

    style C fill:#e1f5fe
    style E fill:#e8f5e8
```
策略：结构化组装检索结果，构建LLM可理解的上下文

## 阶段6：生成与输出
```mermaid
graph LR
    A[上下文+问题] --> B[LLM生成]
    B --> C[基于证据回答]
    C --> D[引用来源标注]
    D --> E[返回结果]

    style B fill:#fff3e0
    style C fill:#f3e5f5
```
策略：要求基于检索内容生成，必须标注引用来源