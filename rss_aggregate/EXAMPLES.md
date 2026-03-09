# RSS聚合器使用示例

## 示例1：基本RSS聚合

### 场景
需要聚合多个股票相关的RSS源，获取最新的市场信息。

### 步骤
1. 配置RSS源
2. 运行聚合器
3. 检查输出结果

### 详细操作

**1. 配置RSS源 (`config.yaml`)**
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
    include: ["股票", "股市", "A股", "港股", "美股", "基金", "投资"]
    exclude: ["广告", "推广", "招聘"]
  min_relevance_score: 0.3
  max_age_hours: 24
```

**2. 运行聚合器**
```bash
cd /Users/huangzhengyi/PycharmProjects/wechat_article_skills
python -m rss_aggregate.scripts.example_usage
```

**3. 查看输出**
```bash
# 检查生成的JSON文件
head -20 output_rss_data.json

# 检查生成的Markdown文件
head -20 output_rss_data.md
```

### 预期输出
- `output_rss_data.json` - 供wechat-tech-writer使用的结构化数据
- `output_rss_data.md` - Markdown格式的文章列表
- `rss_for_tech_writer.md` - 为tech-writer优化的格式

---

## 示例2：访问本地RSS源

### 场景
需要访问本地RSSHub服务提供的淘股吧博客RSS源。

### 步骤
1. 确保RSSHub服务运行
2. 运行本地RSS访问脚本
3. 处理返回的内容

### 详细操作

**1. 启动RSSHub服务（如果尚未启动）**
```bash
# 安装RSSHub（如果未安装）
npm install -g rsshub

# 启动RSSHub
rsshub
```

**2. 运行本地RSS访问脚本**
```bash
cd /Users/huangzhengyi/PycharmProjects/wechat_article_skills
python -m rss_aggregate.scripts.access_local_rss
```

**3. 或使用curl命令直接访问**
```bash
curl -X GET "http://localhost:1200/taoguba/blog/11056656" \
  -H "Accept: application/xml,text/xml,application/html,*/*" \
  -H "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8" \
  -H "User-Agent: Mozilla/5.0 (compatible; RSS Reader; +http://localhost:1200)" \
  -H "Connection: keep-alive" \
  --compressed \
  --location \
  --max-time 30
```

### 预期输出
- `local_rss_data.json` - 本地RSS源的结构化数据
- `local_rss_data.md` - 本地RSS源的Markdown格式
- `local_rss_for_tech_writer.md` - 本地RSS源供tech-writer使用的格式

---

## 示例3：与微信技能集成

### 场景
将RSS聚合器的结果用于微信公众号文章创作。

### 步骤
1. 运行RSS聚合器获取内容
2. 将结果传递给wechat-tech-writer
3. 使用wechat-article-formatter美化格式

### 详细操作

**1. 运行RSS聚合器**
```bash
cd /Users/huangzhengyi/PycharmProjects/wechat_article_skills
python -m rss_aggregate.scripts.access_local_rss
```

**2. 将输出传递给wechat-tech-writer**
```bash
# tech-writer可以使用生成的JSON或Markdown文件作为输入
# 例如使用rss_for_tech_writer.md作为输入
```

**3. 使用formatter美化格式**
```bash
# tech-writer生成文章后，使用formatter转换为微信兼容格式
cd /Users/huangzhengyi/PycharmProjects/wechat_article_skills
python -m wechat_article_formatter.scripts.markdown_to_html --input "generated_article.md" --theme tech
```

### 预期输出
- 从RSS源获取的结构化数据
- 由tech-writer处理后的文章内容
- 由formatter转换后的微信兼容HTML

---

## 示例4：自定义过滤规则

### 场景
需要根据特定关键词过滤RSS内容。

### 步骤
1. 修改配置文件中的过滤规则
2. 运行聚合器
3. 检查过滤结果

### 详细操作

**1. 修改过滤规则 (`config.yaml`)**
```yaml
filtering:
  keywords:
    include: ["人工智能", "机器学习", "深度学习", "AI", "神经网络"]
    exclude: ["招聘", "广告", "培训", "课程"]
  min_relevance_score: 0.5  # 提高相关性要求
  max_age_hours: 12        # 只获取12小时内内容
```

**2. 运行聚合器**
```bash
cd /Users/huangzhengyi/PycharmProjects/wechat_article_skills
python -m rss_aggregate.scripts.example_usage
```

**3. 检查结果**
```bash
# 查看过滤后的文章数量和内容
cat output_rss_data.json | python -m json.tool
```

### 预期输出
- 仅包含指定关键词的文章
- 排除包含排除关键词的文章
- 符合时间范围和相关性要求的文章

---

## 示例5：批量处理多个RSS源

### 场景
需要同时处理多个不同类型的RSS源。

### 步骤
1. 配置多个RSS源
2. 设置不同源的优先级
3. 运行聚合器
4. 检查合并结果

### 详细操作

**1. 配置多个RSS源 (`config.yaml`)**
```yaml
sources:
  - name: "技术博客"
    url: "https://example.com/tech/rss"
    category: "技术"
    priority: 1
    enabled: true
  - name: "财经新闻"
    url: "https://example.com/finance/rss"
    category: "财经"
    priority: 2
    enabled: true
  - name: "市场分析"
    url: "http://localhost:1200/taoguba/blog/11056656"
    category: "股票"
    priority: 3
    enabled: true

output:
  max_articles: 100  # 增加最大文章数量
  include_full_content: true  # 包含完整内容
```

**2. 运行聚合器**
```bash
cd /Users/huangzhengyi/PycharmProjects/wechat_article_skills
python -m rss_aggregate.scripts.example_usage
```

**3. 检查按源分类的结果**
```bash
# 查看聚合结果的统计信息
python -c "
import json
with open('output_rss_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(f'总文章数: {data[\"meta\"][\"total_articles\"]}')
    print(f'数据源数量: {data[\"meta\"][\"sources_used\"]}')
    for article in data['articles'][:5]:
        print(f'- {article[\"title\"]} ({article[\"source\"][\"name\"]})')
"
```

### 预期输出
- 来自多个源的合并文章列表
- 按优先级和时间排序
- 包含源信息的文章数据