# RSS聚合器快速入门

## 1. 安装依赖

```bash
cd /Users/huangzhengyi/PycharmProjects/wechat_article_skills
pip install -r rss_aggregate/requirements.txt
```

## 2. 设置本地RSS源（可选）

如果要访问本地RSS源如 `http://localhost:1200/taoguba/blog/11056656`：

```bash
# 安装RSSHub
npm install -g rsshub

# 启动RSSHub服务
rsshub
```

服务将在 `http://localhost:1200` 启动。

## 3. 运行演示

```bash
python demo_rss_aggregator.py
```

查看RSS聚合器的基本功能演示。

## 4. 基本使用

### 访问本地RSS源

```bash
python -m rss_aggregate.scripts.access_local_rss
```

这将：
1. 访问本地RSS源
2. 解析RSS内容
3. 过滤相关文章
4. 生成适合wechat-tech-writer使用的格式

输出文件：
- `local_rss_data.json` - JSON格式数据
- `local_rss_data.md` - Markdown格式数据  
- `local_rss_for_tech_writer.md` - 为tech-writer优化的格式

### 基本聚合

```bash
python -m rss_aggregate.scripts.example_usage
```

## 5. 配置RSS源

编辑 `rss_aggregate/config.yaml` 文件：

```yaml
sources:
  - name: "淘股吧博客"
    url: "http://localhost:1200/taoguba/blog/11056656"
    category: "股票"
    priority: 1
    enabled: true

filtering:
  keywords:
    include: ["股票", "股市", "A股", "港股", "美股", "基金", "投资"]
    exclude: ["广告", "推广", "招聘"]
  min_relevance_score: 0.3
  max_age_hours: 24
```

## 6. 与微信技能集成

### 与wechat-tech-writer集成

RSS聚合器生成的JSON和Markdown文件可直接作为tech-writer的输入：

```bash
# tech-writer可以使用以下文件作为输入
# - local_rss_for_tech_writer.md
# - output_rss_data.json
# - output_rss_data.md
```

### 与wechat-article-formatter集成

tech-writer处理后的文章可使用formatter美化格式：

```bash
python -m wechat_article_formatter.scripts.markdown_to_html \
  --input "generated_article.md" \
  --theme tech
```

## 7. 常用命令

### 直接访问RSS源
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

### 查看输出结果
```bash
# 查看JSON输出
head -20 local_rss_data.json

# 查看Markdown输出
head -20 local_rss_for_tech_writer.md
```

## 8. 故障排除

### 依赖安装问题
如果pip安装失败，尝试：
```bash
pip install --user -r rss_aggregate/requirements.txt
```

### RSS源访问问题
- 确保RSSHub服务正在运行
- 检查URL是否正确
- 验证网络连接

### 模块导入问题
确保在项目根目录下运行脚本：
```bash
cd /Users/huangzhengyi/PycharmProjects/wechat_article_skills
python -m rss_aggregate.scripts.access_local_rss
```

## 9. 进阶配置

### 自定义过滤规则
修改 `config.yaml` 中的 `filtering` 部分，调整关键词和相关性阈值。

### 添加多个RSS源
在 `config.yaml` 的 `sources` 部分添加更多RSS源配置。

### 调整输出格式
修改 `config.yaml` 中的 `output` 部分，设置输出格式和文章数量限制。

现在您已经掌握了RSS聚合器的基本使用方法，可以开始聚合RSS内容并用于微信文章创作了！
