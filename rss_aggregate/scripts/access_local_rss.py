#!/usr/bin/env python3
"""
访问本地RSS源脚本
用于访问 http://localhost:1200/taoguba/blog/11056656 并处理返回的内容
"""

import asyncio
import requests
import sys
import os
from pathlib import Path
import json
from datetime import datetime

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from rss_aggregate.scripts.rss_parser import RSSParser
from rss_aggregate.scripts.content_filter import ContentFilter
from rss_aggregate.scripts.data_formatter import DataFormatter


def fetch_local_rss_content():
    """
    获取本地RSS内容
    对应命令: curl -X GET "http://localhost:1200/taoguba/blog/11056656" \
      -H "Accept: application/xml,text/xml,application/html,*/*" \
      -H "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8" \
      -H "User-Agent: Mozilla/5.0 (compatible; RSS Reader; +http://localhost:1200)" \
      -H "Connection: keep-alive" \
      --compressed \
      --location \
      --max-time 30
    """
    url = "http://localhost:1200/taoguba/blog/11056656"
    
    headers = {
        "Accept": "application/xml,text/xml,application/html,*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "User-Agent": "Mozilla/5.0 (compatible; RSS Reader; +http://localhost:1200)",
        "Connection": "keep-alive"
    }
    
    print(f"正在访问本地RSS源: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print(f"✓ 成功获取RSS内容，响应大小: {len(response.content)} 字节")
            return response.text
        else:
            print(f"✗ 获取RSS内容失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}...")  # 只显示前500字符
            return None
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到本地RSS源，请确保 http://localhost:1200/taoguba/blog/11056656 可访问")
        print("  提示: 您可能需要先启动RSSHub服务")
        return None
    except requests.exceptions.Timeout:
        print("✗ 请求超时，请检查网络连接或RSS源状态")
        return None
    except Exception as e:
        print(f"✗ 获取RSS内容时发生错误: {str(e)}")
        return None


def process_rss_content(rss_content: str):
    """
    处理RSS内容
    
    Args:
        rss_content: RSS内容字符串
        
    Returns:
        处理后的文章列表
    """
    # 创建解析器
    parser = RSSParser()
    
    # 模拟源信息
    source_info = {
        "name": "淘股吧博客",
        "url": "http://localhost:1200/taoguba/blog/11056656",
        "category": "股票"
    }
    
    # 解析RSS内容
    parsed_data = parser.parse(rss_content, source_info)
    
    if 'error' in parsed_data:
        print(f"✗ RSS解析错误: {parsed_data['error']}")
        return []
    
    print(f"✓ RSS解析成功，获取到 {len(parsed_data['entries'])} 个条目")
    
    # 创建过滤器
    filtering_config = {
        "keywords": {
            "include": ["股票", "股市", "A股", "港股", "美股", "基金", "投资", "证券", "理财", "金融", "taoguba", "淘股吧"],
            "exclude": ["广告", "推广", "招聘", "活动"]
        },
        "min_relevance_score": 0.1,  # 降低阈值以捕获更多内容
        "max_age_hours": 168  # 一周内，因为这是博客内容
    }
    
    content_filter = ContentFilter(filtering_config)
    
    # 过滤文章
    filtered_entries = content_filter.filter_articles(parsed_data['entries'])
    print(f"✓ 过滤后剩余 {len(filtered_entries)} 篇相关文章")
    
    # 去重
    deduplicated_entries = content_filter.deduplicate(filtered_entries, threshold=0.8)
    print(f"✓ 去重后剩余 {len(deduplicated_entries)} 篇独特文章")
    
    # 添加源信息到每篇文章
    for entry in deduplicated_entries:
        entry['source'] = source_info
    
    return deduplicated_entries


def format_for_tech_writer(articles: list):
    """
    为wechat-tech-writer格式化数据
    
    Args:
        articles: 文章列表
    """
    if not articles:
        print("没有文章需要格式化")
        return
    
    # 构建聚合结果格式
    aggregation_result = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "total_articles": len(articles),
            "sources_used": 1,  # 只有一个源
            "time_range": {
                "from": (datetime.now().timestamp() - 7*24*3600),  # 一周前
                "to": datetime.now().isoformat()
            }
        },
        "articles": articles
    }
    
    # 使用DataFormatter格式化
    formatter = DataFormatter()
    
    # 导出为JSON格式（供wechat-tech-writer使用）
    formatter.export_to_json(aggregation_result, "local_rss_data.json")
    print("✓ 已导出JSON格式数据到 local_rss_data.json")
    
    # 导出为Markdown格式
    formatter.export_to_markdown(aggregation_result, "local_rss_data.md")
    print("✓ 已导出Markdown格式数据到 local_rss_data.md")
    
    # 为wechat-tech-writer格式化数据
    tech_writer_format = formatter.format_for_tech_writer(aggregation_result)
    
    with open("local_rss_for_tech_writer.md", "w", encoding="utf-8") as f:
        f.write(tech_writer_format)
    print("✓ 已为wechat-tech-writer格式化数据到 local_rss_for_tech_writer.md")
    
    # 显示前几篇文章的摘要
    print(f"\n前5篇文章预览:")
    for i, article in enumerate(articles[:5], 1):
        print(f"{i}. {article['title']}")
        print(f"   链接: {article['link']}")
        print(f"   发布时间: {article['pub_date']}")
        print(f"   相关性: {article['relevance_score']:.2f}")
        print(f"   摘要: {article['summary'][:100]}...")
        print()


def main():
    print("本地RSS源处理器")
    print("="*50)
    print("目标RSS源: http://localhost:1200/taoguba/blog/11056656")
    print()
    
    # 获取RSS内容
    rss_content = fetch_local_rss_content()
    
    if rss_content:
        # 处理RSS内容
        articles = process_rss_content(rss_content)
        
        # 格式化输出
        format_for_tech_writer(articles)
        
        print(f"\n✓ 处理完成！共处理 {len(articles)} 篇文章")
        print("输出文件:")
        print("  - local_rss_data.json: JSON格式数据，供wechat-tech-writer使用")
        print("  - local_rss_data.md: Markdown格式数据")
        print("  - local_rss_for_tech_writer.md: 专为tech-writer优化的格式")
    else:
        print("\n无法获取RSS内容，请检查本地RSS服务是否正常运行")
        print("如果您还没有设置本地RSS服务，请按以下步骤操作：")
        print("1. 安装Node.js")
        print("2. 安装RSSHub: npm install -g rsshub")
        print("3. 启动RSSHub: rsshub")
        print("4. 等待服务启动后再次运行此脚本")


if __name__ == "__main__":
    main()
