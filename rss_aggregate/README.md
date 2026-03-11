# RSS内容聚合器

RSS内容聚合器是一个用于聚合多个RSS源内容的工具，能够智能筛选和整理有价值的信息，并生成标准化的数据格式，便于后续的微信公众号文章创作技能处理。

## 功能特性

- 聚合多个RSS源内容
- 智能筛选和内容过滤
- 基于关键词的相关性评分
- 内容去重功能
- 支持多种输出格式（JSON、Markdown）
- 缓存机制防止重复处理
- 可配置的过滤规则
- 与wechat-tech-writer和wechat-article-formatter无缝集成

## 安装依赖

```bash
cd /Users/huangzhengyi/PycharmProjects/wechat_article_skills
pip install -r rss_aggregate/requirements.txt
```

## 快速开始

### 1. 运行演示
```bash
python demo_rss_aggregator.py
```

### 2. 基本聚合
```bash
python -m rss_aggregate.scripts.example_usage
```

### 3. 访问本地RSS源
```bash
python -m rss_aggregate.scripts.access_local_rss
```

## 主要组件

### aggregator.py
主聚合器类，协调各模块工作，提供统一的API接口。

### rss_parser.py
RSS/XML内容解析模块，提取标题、描述、链接、发布时间等字段。

### content_filter.py
内容过滤模块，基于关键词过滤内容、去重、质量评估。

### data_formatter.py
数据格式化模块，将聚合的数据转换为不同格式（JSON、Markdown）。

### cache_manager.py
缓存管理模块，存储已处理的文章ID，防止重复处理。

### source_manager.py
RSS源管理模块，负责管理RSS源的添加、删除、验证等功能。

## 与微信技能集成

### 与wechat-tech-writer集成

RSS聚合器生成的JSON格式数据可以直接作为wechat-tech-writer的输入，提供结构化数据供AI分析和改写。

### 与wechat-article-formatter集成

生成的Markdown格式可以被wechat-article-formatter进一步处理，转换为适合微信公众号的HTML格式。

## 输出格式

### JSON格式
标准的数据交换格式，包含完整的元数据和文章信息，适合程序处理。

### Markdown格式
人类可读的格式，适合审阅和手动编辑。

## 缓存机制

系统会自动缓存已处理的文章ID，防止重复处理相同内容。缓存文件默认为 `.rss_cache.json`，保留7天。

## 工作流程

完整的RSS内容到微信文章的工作流程：

```
RSS源 -> RSS聚合器 -> 标准化数据 -> wechat-tech-writer -> 格式化 -> wechat-article-formatter -> 微信文章
```

## 配置文件

`config.yaml` 文件允许您自定义各种参数：

### sources (RSS源列表)
- `name`: RSS源名称，用于标识和显示
- `url`: RSS源URL地址
- `category`: 分类标签，如"股票"、"财经"等
- `priority`: 优先级，数字越大优先级越高
- `enabled`: 是否启用该源，true/false

### filtering (内容过滤设置)
- `keywords.include`: 必须包含的关键词列表，文章必须包含其中任一关键词才会被保留
- `keywords.exclude`: 必须排除的关键词列表，包含其中任一关键词的文章会被过滤掉
- `min_relevance_score`: 最小相关性评分阈值，0.0-1.0之间，低于此值的文章会被过滤
- `max_age_hours`: 最大文章年龄（小时），只保留指定时间内的文章，用于控制内容时效性

### output (输出设置)
- `format`: 输出格式，支持"json"或"markdown"
- `max_articles`: 最大返回文章数量限制
- `include_full_content`: 是否包含完整内容

### caching (缓存设置)
- `enabled`: 是否启用缓存功能，true/false
- `retention_days`: 缓存保留天数
- `cache_file`: 缓存文件路径

### request (请求设置)
- `timeout`: HTTP请求超时时间（秒）
- `retry_attempts`: 请求失败时的重试次数
- `delay_between_requests`: 请求之间的延迟时间（秒）

## 扩展性

系统采用模块化设计，易于扩展：
- 可以添加新的RSS解析器
- 可以扩展过滤规则
- 可以增加新的输出格式
- 可以集成更多内容源