# RSS内容聚合器 - 项目规划文档

## 1. 项目概述

### 1.1 项目名称
RSS内容聚合器 (RSS Content Aggregator)

### 1.2 项目目标
- 聚合多个股票相关的RSS源内容
- 智能筛选和整理有价值的信息
- 生成标准化的数据格式，便于后续其他技能处理
- 为微信公众号文章创作提供素材来源

### 1.3 业务价值
- 自动化收集股票市场信息
- 减少人工搜集信息的时间成本
- 提供高质量的原始素材给写作技能
- 实现信息聚合与内容创作的自动化流程

## 2. 系统架构设计

### 2.1 整体架构
```
RSS源1 ──┐
RSS源2 ──┤
RSS源3 ──┤
         ├──> RSS聚合器 ──> 标准化数据格式 ──> 输出JSON/MD
其他源  ──┤
         └──> 智能过滤器 ──> 内容去重/排序 ──> 缓存管理
```

### 2.2 组件设计

#### 2.2.1 RSS解析器 (rss_parser.py)
- 解析RSS/XML格式内容
- 提取标题、描述、链接、发布时间等字段
- 处理不同的RSS格式变体

#### 2.2.2 内容过滤器 (content_filter.py)
- 基于关键词过滤（股票、股市、财经等）
- 内容质量评估
- 重复内容检测

#### 2.2.3 数据标准化器 (data_formatter.py)
- 统一数据格式
- 生成Markdown或JSON格式输出
- 添加元数据标签

#### 2.2.4 缓存管理器 (cache_manager.py)
- 存储已处理的文章ID
- 防止重复处理
- 定期清理过期缓存

## 3. 数据模型设计

### 3.1 RSS文章数据结构
```json
{
  "id": "文章唯一标识符（URL或生成的UUID）",
  "title": "文章标题",
  "summary": "文章摘要/描述",
  "content": "文章正文内容（可选）",
  "link": "原文链接",
  "pub_date": "发布时间",
  "source": {
    "name": "RSS源名称",
    "url": "RSS源地址",
    "category": "内容分类（如：股票、基金、宏观）"
  },
  "tags": ["标签数组"],
  "relevance_score": "相关性评分（0-1）",
  "processed_at": "处理时间戳"
}
```

### 3.2 聚合结果数据结构
```json
{
  "aggregation_id": "本次聚合任务ID",
  "created_at": "聚合时间",
  "total_articles": "聚合文章总数",
  "sources_count": "RSS源数量",
  "articles": [
    // RSS文章数据结构数组
  ],
  "summary_stats": {
    "by_source": {},
    "by_category": {},
    "by_date_range": {}
  }
}
```

## 4. 功能模块设计

### 4.1 RSS源管理模块
- 支持添加/删除RSS源
- 验证RSS源有效性
- 配置源的优先级和权重
- 支持定时更新

### 4.2 内容聚合模块
- 并发获取多个RSS源
- 解析RSS内容
- 提取关键信息
- 错误处理和重试机制

### 4.3 内容过滤模块
- 基于关键词的过滤
- 基于内容相似度的去重
- 基于时间的新鲜度筛选
- 基于来源可信度的权重计算

### 4.4 输出格式化模块
- JSON格式输出（供其他程序处理）
- Markdown格式输出（供人工审阅）
- 摘要模式（仅标题和摘要）
- 详细模式（包含全文内容）

## 5. 与现有技能的集成

### 5.1 与wechat-tech-writer集成
- 输出格式与tech-writer输入格式兼容
- 提供结构化数据供AI分析和改写
- 支持直接生成写作提示

### 5.2 与wechat-article-formatter集成
- 输出格式可直接被formatter处理
- 提供Markdown格式的文章内容
- 包含适当的标题和段落结构

### 5.3 与wechat-draft-publisher集成
- 提供完整的文章数据结构
- 包含标题、内容、发布时间等必要字段
- 支持批量文章发布

## 6. 技术实现方案

### 6.1 技术栈
- **主语言**: Python 3.8+
- **RSS解析**: feedparser库
- **HTTP请求**: requests库
- **并发处理**: asyncio + aiohttp
- **数据存储**: JSON文件或SQLite
- **配置管理**: YAML文件

### 6.2 核心依赖库
```txt
feedparser>=6.0.0
requests>=2.25.0
beautifulsoup4>=4.9.0
lxml>=4.6.0
asyncio
aiohttp
PyYAML
```

### 6.3 代码结构
```
wechat-rss-aggregator/
├── __init__.py
├── aggregator.py              # 主聚合器类
├── rss_parser.py             # RSS解析模块
├── content_filter.py         # 内容过滤模块
├── data_formatter.py         # 数据格式化模块
├── cache_manager.py          # 缓存管理模块
├── source_manager.py         # RSS源管理模块
├── config.yaml               # 配置文件
├── requirements.txt          # 依赖列表
├── scripts/
│   ├── aggregate_rss.py      # 聚合脚本
│   ├── validate_sources.py   # 验证RSS源脚本
│   └── export_data.py        # 数据导出脚本
├── examples/
│   ├── sample_output.json    # 示例输出
│   └── config_example.yaml   # 配置示例
├── tests/                    # 测试文件
└── README.md                 # 使用说明
```

## 7. API接口设计

### 7.1 主要方法
```python
class RSSAggregator:
    def __init__(self, config_path: str):
        """初始化聚合器"""
    
    def add_source(self, url: str, name: str, category: str = None):
        """添加RSS源"""
    
    def remove_source(self, url: str):
        """移除RSS源"""
    
    def aggregate(self, max_articles: int = 50) -> dict:
        """执行聚合操作"""
    
    def get_latest_articles(self, hours: int = 24) -> list:
        """获取最新文章"""
    
    def export_to_json(self, data: dict, filepath: str):
        """导出为JSON格式"""
    
    def export_to_markdown(self, data: dict, filepath: str):
        """导出为Markdown格式"""
```

## 8. 配置文件设计

### 8.1 config.yaml 示例
```yaml
# RSS聚合器配置文件
sources:
  - name: "雪球精选"
    url: "https://xueqiu.com/rss"
    category: "股票"
    priority: 1
    enabled: true
  - name: "东方财富"
    url: "http://eastmoney.com/rss"
    category: "财经"
    priority: 2
    enabled: true

filtering:
  keywords:
    include: ["股票", "股市", "A股", "港股", "美股", "基金", "投资"]
    exclude: ["广告", "推广", "招聘"]
  min_relevance_score: 0.3
  max_age_hours: 24

output:
  format: "json"  # json, markdown
  max_articles: 50
  include_full_content: false

caching:
  enabled: true
  retention_days: 7
  cache_file: ".rss_cache.json"

request:
  timeout: 10
  retry_attempts: 3
  delay_between_requests: 1
```

## 9. 输出格式设计

### 9.1 JSON输出格式
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

### 9.2 Markdown输出格式
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

## 10. 部署与使用

### 10.1 安装依赖
```bash
pip install -r requirements.txt
```

### 10.2 配置RSS源
编辑 `config.yaml` 文件，添加所需的RSS源

### 10.3 运行聚合
```bash
python scripts/aggregate_rss.py
```

### 10.4 与现有技能集成
```bash
# 聚合RSS内容
python scripts/aggregate_rss.py

# 将聚合结果传给写作技能
# (可以作为wechat-tech-writer的输入源)
```

## 11. 性能优化考虑

### 11.1 并发处理
- 使用异步请求提高获取效率
- 控制并发数量避免被封IP
- 合理设置请求间隔

### 11.2 缓存策略
- 缓存已处理的文章ID
- 定期清理过期缓存
- 支持增量更新

### 11.3 错误处理
- 网络请求异常处理
- RSS格式解析错误处理
- 数据验证和清洗

## 12. 扩展性设计

### 12.1 插件化架构
- 支持自定义过滤规则
- 可扩展的输出格式
- 灵活的RSS源验证机制

### 12.2 定时任务支持
- 集成定时聚合功能
- 支持Cron表达式配置
- 自动化内容更新

## 13. 安全考虑

- 验证RSS源的安全性
- 防止恶意内容注入
- 合理设置请求频率限制
- 数据传输加密（HTTPS）

## 14. 与现有技能的协作流程

### 14.1 完整工作流
```
RSS源 -> RSS聚合器 -> 标准化数据 -> wechat-tech-writer -> 格式化 -> 发布
```

### 14.2 与wechat-tech-writer的协作
- RSS聚合器输出结构化数据
- tech-writer根据数据生成文章
- 可以将RSS文章作为参考内容
- 自动生成文章大纲和要点

### 14.3 与wechat-article-formatter的协作
- RSS聚合器提供Markdown格式内容
- formatter进行样式美化
- 输出适合微信公众号的HTML

## 15. 未来扩展方向

- 支持更多内容源（Twitter、微博等）
- 集成情感分析功能
- 支持个性化推荐算法
- 集成图表生成能力
- 支持多语言内容处理

---

**总结**: RSS聚合器将成为整个微信公众号文章创作流程的起始环节，为后续的AI写作、格式化和发布提供高质量的原始素材。通过标准化的数据格式和良好的接口设计，确保与现有技能的良好集成。