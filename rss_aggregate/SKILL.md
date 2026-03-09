---
name: rss-aggregator
description: 聚合多个RSS源内容，智能筛选和整理有价值的信息，生成标准化的数据格式，便于后续的微信公众号文章创作技能处理。特别适用于聚合股票相关的RSS源内容。当用户需要聚合RSS内容、获取实时信息、或为微信文章创作寻找素材时使用。
allowed-tools: Read, Write, Bash
---

# RSS内容聚合器

**目标**：聚合多个RSS源内容，智能筛选和整理有价值的信息，生成标准化的数据格式，便于后续的微信公众号文章创作技能处理。

**核心价值**：自动化收集信息，减少人工搜集时间，为微信文章创作提供高质量素材。

---

## ⚡ 执行流程（严格遵守）

### 步骤1：安装依赖

首次使用前需要安装依赖包：

```bash
cd /Users/huangzhengyi/PycharmProjects/wechat_article_skills
pip install -r rss_aggregate/requirements.txt
```

### 步骤2：配置RSS源

**场景判断**：

| 场景 | 如何处理 |
|------|---------|
| 使用默认配置 | 直接运行聚合器 |
| 需要添加自定义RSS源 | 编辑 `config.yaml` 文件 |
| 访问本地RSS源 | 使用 `access_local_rss.py` 脚本 |

**配置文件位置**：`/Users/huangzhengyi/PycharmProjects/wechat_article_skills/rss_aggregate/config.yaml`

**配置示例**：
```yaml
sources:
  - name: "淘股吧博客"
    url: "http://localhost:1200/taoguba/blog/11056656"
    category: "股票"
    priority: 1
    enabled: true

filtering:
  keywords:
    include: ["股票", "股市", "A股", "港股", "美股", "基金", "投资", "证券", "理财", "金融"]
    exclude: ["广告", "推广", "招聘", "活动"]
  min_relevance_score: 0.3
  max_age_hours: 24
```

### 步骤3：运行聚合器

**标准聚合命令**：
```bash
cd /Users/huangzhengyi/PycharmProjects/wechat_article_skills
python -m rss_aggregate.scripts.example_usage
```

**访问本地RSS源**：
```bash
cd /Users/huangzhengyi/PycharmProjects/wechat_article_skills
python -m rss_aggregate.scripts.access_local_rss
```

**直接使用curl命令访问本地RSS源**：
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

### 步骤4：检查输出结果

**输出文件**：
- `output_rss_data.json` - 供wechat-tech-writer使用的JSON格式
- `output_rss_data.md` - Markdown格式数据
- `rss_for_tech_writer.md` - 为tech-writer优化的格式
- `local_rss_data.json` - 本地RSS源数据
- `local_rss_data.md` - 本地RSS源Markdown格式
- `local_rss_for_tech_writer.md` - 本地RSS源供tech-writer使用

**检查命令**：
```bash
# 查看JSON输出文件
head -20 output_rss_data.json

# 查看Markdown输出文件
head -20 output_rss_data.md
```

### 步骤5：与微信技能集成

**与wechat-tech-writer集成**：
- 使用生成的JSON或Markdown文件作为输入
- 文件格式与tech-writer输入格式兼容

**与wechat-article-formatter集成**：
- 输出格式可直接被formatter处理
- 提供Markdown格式的文章内容

---

## 🔄 与微信技能集成

### 与 wechat-tech-writer 的协作流程

**完整工作流**：
```
RSS源 -> RSS聚合器 -> 标准化数据 -> wechat-tech-writer -> 格式化 -> wechat-article-formatter -> 微信文章
```

**集成方式**：
1. RSS聚合器输出结构化数据
2. tech-writer根据数据生成文章
3. 可以将RSS文章作为参考内容
4. 自动生成文章大纲和要点

**数据格式**：
```json
{
  "meta": {
    "generated_at": "2026-03-07T10:30:00Z",
    "total_articles": 25,
    "sources_used": 5
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

### 与 wechat-article-formatter 的协作

**协作方式**：
- RSS聚合器提供Markdown格式内容
- formatter进行样式美化
- 输出适合微信公众号的HTML

---

## 📚 参考文档

**详细配置指南**：`references/configuration-guide.md`
**API使用说明**：`references/api-usage.md`
**本地RSS源设置**：`references/local-rss-setup.md`
**与微信技能集成**：`references/integration-with-wechat-skills.md`
**常见问题**：`references/troubleshooting.md`

---

## ❌ 错误处理表

| 错误信息 | 原因 | Claude 应该做什么 |
|---------|------|-----------------|
| `ModuleNotFoundError: No module named 'rss_aggregate'` | 未正确设置Python路径 | 确保在项目根目录运行脚本 |
| `pip install` 失败 | 依赖包安装问题 | 检查网络连接和权限 |
| `ConnectionError` | RSS源无法访问 | 检查URL是否正确，服务是否运行 |
| `Permission denied` | 文件权限问题 | 检查输出目录权限 |
| `JSON decode error` | RSS格式错误 | 检查RSS源格式是否正确 |

---

## 📖 使用示例

**示例1：基本聚合**
```python
from rss_aggregate.scripts.aggregator import RSSAggregator

# 创建聚合器实例
aggregator = RSSAggregator()

# 添加RSS源
aggregator.add_source(
    url="http://localhost:1200/taoguba/blog/11056656",
    name="淘股吧博客",
    category="股票"
)

# 执行聚合
import asyncio
result = asyncio.run(aggregator.aggregate(max_articles=20))

# 导出结果
aggregator.export_to_json(result, 'output.json')
aggregator.export_to_markdown(result, 'output.md')
```

**示例2：访问本地RSS源**
```bash
# 使用专用脚本访问本地RSS源
python -m rss_aggregate.scripts.access_local_rss
```

---

## ✅ 执行检查清单（每次执行完毕后确认）

- [ ] 已安装所需依赖包
- [ ] 已配置RSS源（可选）
- [ ] 已成功运行聚合器
- [ ] 已检查输出文件内容
- [ ] 已确认与微信技能的兼容性
- [ ] 已处理可能出现的错误

---

**记住**：这个技能的核心是**自动化信息收集 + 标准化输出**，为微信文章创作提供高质量的原始素材！