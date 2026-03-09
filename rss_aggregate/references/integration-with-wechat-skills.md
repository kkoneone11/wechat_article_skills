# 与微信技能集成指南

## 整体架构

RSS聚合器在整个微信文章创作流程中的位置：

```
RSS源 -> RSS聚合器 -> 标准化数据 -> wechat-tech-writer -> 格式化 -> wechat-article-formatter -> 微信文章
```

## 与wechat-tech-writer集成

### 数据格式兼容性

RSS聚合器生成的JSON格式与wechat-tech-writer的输入格式兼容：

```json
{
  "meta": {
    "generated_at": "2026-03-07T10:30:00Z",
    "total_articles": 25,
    "sources_used": 5,
    "time_range": {
      "from": "2026-03-06T10:30:00Z",
      "to": "2026-03-07T10:30:00Z"
    }
  },
  "articles": [
    {
      "id": "unique_identifier",
      "title": "文章标题",
      "summary": "文章摘要",
      "content": "完整内容（可选）",
      "link": "https://original-link.com",
      "pub_date": "2026-03-07T09:15:00Z",
      "source": {
        "name": "雪球",
        "url": "https://xueqiu.com/rss",
        "category": "股票"
      },
      "tags": ["A股", "科技股", "投资策略"],
      "relevance_score": 0.85
    }
  ]
}
```

### 集成步骤

#### 1. 生成数据
```bash
# 运行RSS聚合器
python -m rss_aggregate.scripts.access_local_rss
```

#### 2. 为tech-writer准备数据
聚合器会自动生成适合tech-writer使用的格式：
- `rss_for_tech_writer.md` - Markdown格式的聚合内容
- `local_rss_for_tech_writer.md` - 本地RSS源内容

#### 3. 传递给tech-writer
tech-writer可以直接使用这些文件作为输入源，提取关键信息并生成微信文章。

### 数据处理流程

```
RSS源内容
    ↓
RSS聚合器解析
    ↓
提取关键字段（标题、摘要、内容、链接等）
    ↓
应用过滤规则（关键词、相关性评分）
    ↓
标准化数据格式
    ↓
输出JSON/Markdown格式
    ↓
tech-writer接收数据
    ↓
AI分析和改写
    ↓
生成微信文章
```

## 与wechat-article-formatter集成

### 格式兼容性

RSS聚合器生成的Markdown格式可以直接被formatter处理：

```markdown
# RSS聚合内容报告
*生成时间：2026-03-07 10:30*

## 聚合统计
- 总文章数：25篇
- 数据源：5个RSS源
- 时间范围：过去24小时

## 文章列表

### [文章标题1](https://link1.com)
- **来源**：雪球
- **时间**：2026-03-07 09:15
- **摘要**：文章内容摘要...
- **标签**：#A股 #科技股

### [文章标题2](https://link2.com)
- **来源**：东方财富
- **时间**：2026-03-07 08:45
- **摘要**：文章内容摘要...
- **标签**：#基金 #投资策略
```

### 集成步骤

#### 1. tech-writer生成文章
tech-writer基于RSS数据生成初稿

#### 2. 使用formatter美化
```bash
# 将tech-writer生成的文章转换为微信优化格式
python -m wechat_article_formatter.scripts.markdown_to_html \
  --input "generated_article.md" \
  --theme tech
```

## 工作流程示例

### 完整流程
```bash
# 步骤1：聚合RSS内容
cd /Users/huangzhengyi/PycharmProjects/wechat_article_skills
python -m rss_aggregate.scripts.access_local_rss

# 步骤2：tech-writer处理数据
# (tech-writer使用rss_for_tech_writer.md作为输入)

# 步骤3：formatter美化格式
python -m wechat_article_formatter.scripts.markdown_to_html \
  --input "final_article.md" \
  --theme tech
```

### 自动化脚本示例
```bash
#!/bin/bash
# 自动化RSS到微信文章的完整流程

echo "步骤1: 聚合RSS内容..."
python -m rss_aggregate.scripts.access_local_rss

echo "步骤2: tech-writer处理内容..."
# (此处调用tech-writer处理rss_for_tech_writer.md)

echo "步骤3: 格式化文章..."
python -m wechat_article_formatter.scripts.markdown_to_html \
  --input "processed_article.md" \
  --theme tech

echo "完成!"
```

## 数据流转注意事项

### 字段映射
- RSS聚合器的`title` → tech-writer的标题参考
- RSS聚合器的`summary` → tech-writer的内容参考
- RSS聚合器的`content` → tech-writer的详细信息源
- RSS聚合器的`tags` → tech-writer的关键词提取

### 质量控制
- 确保相关性评分符合要求
- 验证发布时间在合理范围内
- 检查内容完整性

## 错误处理

### 数据格式错误
- 验证JSON格式是否正确
- 检查必需字段是否存在

### 集成故障
- 检查文件路径是否正确
- 验证数据格式是否兼容
- 确认依赖工具是否正常安装

## 性能优化

### 批量处理
- 可以一次聚合多个RSS源
- 支持批量处理文章

### 缓存机制
- RSS聚合器内置缓存，避免重复处理
- 提高整体流程效率