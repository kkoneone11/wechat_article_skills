"""
RSS解析器模块
负责解析RSS/XML格式内容，提取关键信息
"""
import sys
import os
# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import feedparser
from datetime import datetime
from typing import Dict, List, Optional


class RSSParser:
    def __init__(self):
        pass

    def parse(self, rss_content: str, source_info: dict) -> dict:
        """
        解析RSS内容
        
        Args:
            rss_content: RSS内容字符串
            source_info: 源信息字典
            
        Returns:
            解析后的字典，包含feed信息和条目列表
        """
        try:
            # 使用feedparser解析RSS内容
            feed = feedparser.parse(rss_content)
            
            # 提取feed级别的信息
            feed_data = {
                'title': getattr(feed.feed, 'title', ''),
                'description': getattr(feed.feed, 'description', ''),
                'link': getattr(feed.feed, 'link', ''),
                'language': getattr(feed.feed, 'language', ''),
                'last_build_date': getattr(feed.feed, 'updated', ''),
            }
            
            # 提取条目信息
            entries = []
            for entry in feed.entries:
                entry_data = self._parse_entry(entry, source_info)
                entries.append(entry_data)
                
            return {
                'feed': feed_data,
                'entries': entries,
                'source': source_info
            }
        except Exception as e:
            print(f"RSS解析错误: {str(e)}")
            return {
                'feed': {},
                'entries': [],
                'source': source_info,
                'error': str(e)
            }

    def _parse_entry(self, entry, source_info: dict) -> dict:
        """
        解析单个RSS条目
        
        Args:
            entry: feedparser解析的单个条目
            source_info: 源信息
            
        Returns:
            解析后的条目字典
        """
        # 处理发布时间
        pub_date = ''
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            pub_date = datetime(*entry.published_parsed[:6]).isoformat()
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            pub_date = datetime(*entry.updated_parsed[:6]).isoformat()
        elif hasattr(entry, 'published'):
            pub_date = str(entry.published)
        
        # 处理内容
        content = ''
        if hasattr(entry, 'content') and entry.content:
            # 通常content是列表，取第一个内容
            content = entry.content[0].value if entry.content else ''
        elif hasattr(entry, 'summary'):
            content = entry.summary
        elif hasattr(entry, 'description'):
            content = entry.description
        
        # 清理HTML标签
        import re
        clean_content = re.sub('<[^<]+?>', '', content)
        
        # 处理链接
        link = getattr(entry, 'link', '')
        
        # 生成条目ID（如果原RSS没有提供）
        entry_id = getattr(entry, 'id', '') or link or f"{source_info['url']}#{hash(content[:50])}"
        
        # 提取标签
        tags = []
        if hasattr(entry, 'tags'):
            tags = [tag.term for tag in entry.tags]
        elif hasattr(entry, 'category'):
            tags = [entry.category]
        elif hasattr(entry, 'categories'):
            tags = [cat[1] for cat in entry.categories]
            
        # 计算相关性评分（基础版本，可以根据关键词匹配程度计算）
        relevance_score = self._calculate_relevance_score(entry, source_info)
        
        return {
            "id": entry_id,
            "title": getattr(entry, 'title', ''),
            "summary": getattr(entry, 'summary', ''),
            "content": clean_content.strip(),
            "link": link,
            "pub_date": pub_date,
            "author": getattr(entry, 'author', ''),
            "tags": tags,
            "relevance_score": relevance_score,
            "source": {
                "name": source_info['name'],
                "url": source_info['url'],
                "category": source_info.get('category', '通用')
            },
            "processed_at": datetime.now().isoformat()
        }

    def _calculate_relevance_score(self, entry, source_info: dict) -> float:
        """
        计算条目的相关性评分
        
        Args:
            entry: feedparser解析的条目
            source_info: 源信息
            
        Returns:
            相关性评分 (0-1)
        """
        title = getattr(entry, 'title', '').lower()
        summary = getattr(entry, 'summary', '').lower()
        content = getattr(entry, 'summary', '').lower()
        
        # 基础关键词列表（可以从配置中读取）
        keywords = ["股票", "股市", "A股", "港股", "美股", "基金", "投资", "金融", "证券", "理财"]
        
        # 计算关键词匹配分数
        matched_keywords = 0
        total_text = f"{title} {summary} {content}"
        
        for keyword in keywords:
            if keyword.lower() in total_text:
                matched_keywords += 1
                
        score = min(matched_keywords / len(keywords), 1.0) if keywords else 0.0
        
        # 根据源的类别调整分数
        if source_info.get('category', '').lower() in ['股票', '财经', '金融', '投资']:
            score = min(score * 1.2, 1.0)
            
        return round(score, 2)