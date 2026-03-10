#!/usr/bin/env python3
"""
RSS聚合器示例脚本
演示如何使用RSS聚合器从本地RSS源获取内容并处理
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from rss_aggregate.scripts.aggregator import RSSAggregator
from rss_aggregate.scripts.source_manager import SourceManager


def main():
    print("RSS内容聚合器示例")
    print("=" * 50)

    # 创建聚合器实例
    aggregator = RSSAggregator(config_path="./wechat_article_skills/rss_aggregate/scripts/config.yaml")

    # 添加本地RSS源 (模拟 http://localhost:1200/taoguba/blog/11056656)
    # aggregator.add_source(
    #     url="http://localhost:1200/taoguba/blog/11056656",
    #     name="淘股吧博客",
    #     category="股票",
    #     priority=1
    # )
    #
    # # 可以添加更多RSS源
    # aggregator.add_source(
    #     url="https://rsshub.app/telegram/channel/bitcoinnewsinfo",
    #     name="比特币新闻",
    #     category="加密货币",
    #     priority=2
    # )

    print(f"已配置 {len(aggregator.config['sources'])} 个RSS源")

    # 执行聚合
    print("\n开始聚合RSS内容...")
    try:
        # 运行异步聚合函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(aggregator.aggregate(max_articles=20))

        print(f"\n聚合完成！共获取 {result['meta']['total_articles']} 篇文章")
        print(f"数据源数量: {result['meta']['sources_used']}")
        print(f"时间范围: {result['meta']['time_range']['from']} 到 {result['meta']['time_range']['to']}")

        # 显示前几篇文章的标题
        print("\n前5篇文章:")
        for i, article in enumerate(result['articles'][:5], 1):
            print(f"{i}. {article['title']}")
            print(f"   来源: {article['source']['name']}")
            print(f"   时间: {article['pub_date']}")
            print(f"   相关性: {article['relevance_score']:.2f}")
            print()

        # 导出为JSON格式（供wechat-tech-writer使用）
        aggregator.export_to_json(result, "output_rss_data.json")
        print("✓ 已导出JSON格式数据到 output_rss_data.json")

        # 导出为Markdown格式
        aggregator.export_to_markdown(result, "output_rss_data.md")
        print("✓ 已导出Markdown格式数据到 output_rss_data.md")

        # 为wechat-tech-writer格式化数据
        from rss_aggregate.scripts.data_formatter import DataFormatter
        formatter = DataFormatter()
        tech_writer_format = formatter.format_for_tech_writer(result)

        with open("rss_for_tech_writer.md", "w", encoding="utf-8") as f:
            f.write(tech_writer_format)
        print("✓ 已为wechat-tech-writer格式化数据到 rss_for_tech_writer.md")

    except Exception as e:
        print(f"聚合过程中出现错误: {str(e)}")
        print("请确保RSS源可访问且格式正确")


def setup_local_rss_demo():
    """
    设置本地RSS源演示
    注意：这只是一个演示，实际使用时需要运行RSSHub或其他RSS服务
    """
    print("本地RSS源设置说明:")
    print("- 如果您想测试本地RSS源，需要先启动RSSHub服务")
    print("- 安装RSSHub: npm install -g rsshub")
    print("- 启动RSSHub: rsshub")
    print("- 然后访问类似 http://localhost:1200/taoguba/blog/11056656 的地址")
    print()


if __name__ == "__main__":
    setup_local_rss_demo()
    main()
