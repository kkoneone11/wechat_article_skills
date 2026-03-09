#!/usr/bin/env python3
"""
RSS聚合器快速演示
展示如何使用RSS聚合器访问本地RSS源并处理内容
"""

import sys
import os
from datetime import datetime

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

def demo_basic_usage():
    """演示RSS聚合器基本用法"""
    print("演示1: RSS聚合器基本用法")
    print("-" * 40)
    
    from rss_aggregate.scripts.aggregator import RSSAggregator
    
    # 创建聚合器实例
    aggregator = RSSAggregator()
    
    # 添加一个示例RSS源
    aggregator.add_source(
        url="https://feeds.bbci.co.uk/news/rss.xml",
        name="BBC News",
        category="新闻",
        priority=1
    )
    
    print(f"已添加 {len(aggregator.config['sources'])} 个RSS源")
    print(f"配置的源: {[source['name'] for source in aggregator.config['sources']]}")
    
    # 显示配置信息
    print(f"过滤关键词 (包含): {aggregator.config['filtering']['keywords']['include']}")
    print(f"最大文章数: {aggregator.config['output']['max_articles']}")
    print()


def demo_local_rss_access():
    """演示访问本地RSS源"""
    print("演示2: 访问本地RSS源 (http://localhost:1200/taoguba/blog/11056656)")
    print("-" * 40)
    
    # 显示对应的curl命令
    print("等效的curl命令:")
    print('''curl -X GET "http://localhost:1200/taoguba/blog/11056656" \\
  -H "Accept: application/xml,text/xml,application/html,*/*" \\
  -H "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8" \\
  -H "User-Agent: Mozilla/5.0 (compatible; RSS Reader; +http://localhost:1200)" \\
  -H "Connection: keep-alive" \\
  --compressed \\
  --location \\
  --max-time 30''')
    print()
    
    # 展示如何添加这个本地源到聚合器
    from rss_aggregate.scripts.aggregator import RSSAggregator
    
    aggregator = RSSAggregator()
    aggregator.add_source(
        url="http://localhost:1200/taoguba/blog/11056656",
        name="淘股吧博客",
        category="股票"
    )
    
    print(f"已添加本地RSS源: {aggregator.config['sources'][0]['name']}")
    print(f"源URL: {aggregator.config['sources'][0]['url']}")
    print(f"分类: {aggregator.config['sources'][0]['category']}")
    print()


def demo_data_flow():
    """演示数据流向"""
    print("演示3: 数据流向 - RSS内容到微信文章")
    print("-" * 40)
    
    print("""
RSS 源 (http://localhost:1200/taoguba/blog/11056656)
    ↓
curl 获取内容 (XML/RSS 格式)
    ↓
RSS 解析器 (提取标题、摘要、正文、发布时间等)
    ↓
内容预处理 (清理 HTML 标签、提取关键信息)
    ↓
wechat-tech-writer (进行内容改写、分析、润色)
    ↓
生成 Markdown 格式文章
    ↓
wechat-article-formatter (转换为微信优化的 HTML)
    ↓
最终微信公众号文章
    """)
    

def demo_integration_with_existing_skills():
    """演示与现有技能的集成"""
    print("演示4: 与现有技能的集成")
    print("-" * 40)
    
    print("# wechat-tech-writer 的集成示例:")
    print("""
from rss_aggregate.scripts.data_formatter import DataFormatter

# 假设我们有聚合结果
aggregation_result = {
    "meta": {...},
    "articles": [...]
}

# 为 tech-writer 格式化数据
formatter = DataFormatter()
tech_writer_content = formatter.format_for_tech_writer(aggregation_result)

# 保存供 tech-writer 使用
with open("rss_for_tech_writer.md", "w", encoding="utf-8") as f:
    f.write(tech_writer_content)
    """)
    
    print("\n# wechat-article-formatter 的集成示例:")
    print("""
# tech-writer 处理完成后，将结果传递给 formatter
# (假设 tech-writer 已经处理了内容)

from wechat_article_formatter.scripts.markdown_to_html import convert_markdown_to_html

# 将 tech-writer 的输出转换为微信优化的HTML
with open("final_article.md", "r", encoding="utf-8") as f:
    markdown_content = f.read()

html_content = convert_markdown_to_html(markdown_content)
    """)


def main():
    print("RSS聚合器快速演示")
    print("=" * 50)
    print(f"演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    demo_basic_usage()
    demo_local_rss_access()
    demo_data_flow()
    demo_integration_with_existing_skills()
    
    print("=" * 50)
    print("演示完成!")
    print()
    print("要实际运行RSS聚合器，请执行:")
    print("  python -m rss_aggregate.scripts.example_usage")
    print()
    print("要访问本地RSS源，请执行:")
    print("  python -m rss_aggregate.scripts.access_local_rss")
    print()
    print("注意: 访问 http://localhost:1200/taoguba/blog/11056656 需要先启动RSSHub服务")


if __name__ == "__main__":
    main()
