# RSS聚合器使用指南

## 快速开始

### 1. 安装依赖
```bash
cd /Users/huangzhengyi/PycharmProjects/wechat_article_skills
pip install -r rss_aggregate/requirements.txt
```

### 2. 运行演示
```bash
python demo_rss_aggregator.py
```

### 3. 访问本地RSS源
```bash
python -m rss_aggregate.access_local_rss
```

## 与微信技能的协作流程

### 步骤1: 配置RSS源
编辑 `rss_aggregate/config.yaml` 文件，添加您感兴趣的RSS源：

```yaml
sources:
  - name: "淘股吧博客"
    url: "http://localhost:1200/taoguba/blog/11056656"
    category: "股票"
    priority: 1
    enabled: true
```

### 步骤2: 运行聚合器
```bash
# 使用示例脚本
python -m rss_aggregate.example_usage
```

### 步骤3: 获取输出文件
聚合器会生成以下文件：
- `output_rss_data.json` - 供wechat-tech-writer使用的JSON格式
- `output_rss_data.md` - Markdown格式数据
- `rss_for_tech_writer.md` - 为tech-writer优化的格式

### 步骤4: 与wechat-tech-writer集成
将生成的JSON或Markdown文件作为输入提供给wechat-tech-writer进行内容处理。

### 步骤5: 与wechat-article-formatter集成
将tech-writer处理后的结果传递给formatter进行样式优化。

## 本地RSS源设置

要访问 `http://localhost:1200/taoguba/blog/11056656`，需要先启动RSSHub服务：

1. 安装Node.js
2. 安装RSSHub: `npm install -g rsshub`
3. 启动RSSHub: `rsshub`
4. 等待服务启动后运行访问脚本

## 高级配置

您可以编辑 `config.yaml` 文件来自定义过滤规则、输出格式和其他选项：

```yaml
filtering:
  keywords:
    include: ["股票", "股市", "A股", "港股", "美股", "基金", "投资", "证券", "理财", "金融"]
    exclude: ["广告", "推广", "招聘", "活动"]
  min_relevance_score: 0.3  # 最低相关性阈值
  max_age_hours: 24         # 最大文章年龄（小时）
```

## 输出示例

聚合器生成的标准输出格式：

```json
{
  "meta": {
    "generated_at": "2026-03-07T10:30:00Z",
    "total_articles": 5,
    "sources_used": 1
  },
  "articles": [
    {
      "id": "unique_id",
      "title": "文章标题",
      "summary": "文章摘要",
      "content": "文章内容",
      "link": "原文链接",
      "pub_date": "发布时间",
      "source": {
        "name": "来源名称",
        "url": "来源URL",
        "category": "分类"
      },
      "tags": ["标签"],
      "relevance_score": 0.85
    }
  ]
}
```

这个格式可以直接被wechat-tech-writer处理，用于生成微信公众号文章。