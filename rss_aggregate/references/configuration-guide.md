# RSS聚合器配置指南

## 配置文件结构

RSS聚合器使用 `config.yaml` 文件进行配置，主要包含以下几个部分：

### sources
定义要聚合的RSS源列表：

```yaml
sources:
  - name: "源名称"
    url: "RSS源URL"
    category: "分类"
    priority: 优先级数值
    enabled: true/false
```

### filtering
定义内容过滤规则：

```yaml
filtering:
  keywords:
    include: ["包含的关键词列表"]
    exclude: ["排除的关键词列表"]
  min_relevance_score: 最小相关性分数
  max_age_hours: 最大文章年龄（小时）
```

### output
定义输出格式和选项：

```yaml
output:
  format: "json" 或 "markdown"
  max_articles: 最大文章数量
  include_full_content: 是否包含完整内容
```

### caching
定义缓存设置：

```yaml
caching:
  enabled: true/false
  retention_days: 缓存保留天数
  cache_file: 缓存文件路径
```

### request
定义HTTP请求参数：

```yaml
request:
  timeout: 超时时间
  retry_attempts: 重试次数
  delay_between_requests: 请求间隔
```

## 配置示例

```yaml
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
    include: ["股票", "股市", "A股", "港股", "美股", "基金", "投资", "证券", "理财", "金融"]
    exclude: ["广告", "推广", "招聘", "活动"]
  min_relevance_score: 0.3
  max_age_hours: 24

output:
  format: "json"
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

## 配置最佳实践

### 关键词设置
- `include` 关键词应与您的关注领域相关
- `exclude` 关键词应包含无关内容的标识
- 定期审查和更新关键词列表

### 相关性阈值
- 较高的阈值（0.5-0.8）：获得更精确但较少的结果
- 较低的阈值（0.1-0.3）：获得更广泛但可能包含噪声的结果

### 时间范围
- 对于新闻类RSS源：设置较短的时间范围（1-6小时）
- 对于博客类RSS源：设置较长的时间范围（24-168小时）

### 缓存策略
- 启用缓存以避免重复处理相同内容
- 根据内容更新频率设置合适的保留天数