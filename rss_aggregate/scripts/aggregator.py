"""
RSS内容聚合器主模块
负责聚合多个RSS源内容，智能筛选和整理有价值的信息
"""
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp
import feedparser
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from .rss_parser import RSSParser
    from .content_filter import ContentFilter
    from .data_formatter import DataFormatter
    from .cache_manager import CacheManager
except ImportError:
    # 当作为独立模块运行时
    from rss_aggregate.scripts.rss_parser import RSSParser
    from rss_aggregate.scripts.content_filter import ContentFilter
    from rss_aggregate.scripts.data_formatter import DataFormatter
    from rss_aggregate.scripts.cache_manager import CacheManager


class RSSAggregator:
    def __init__(self, config_path: str = None):
        """
        初始化聚合器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path) if config_path else self._default_config()
        self.cache_manager = CacheManager(
            enabled=self.config['caching']['enabled'],
            retention_days=self.config['caching']['retention_days'],
            cache_file=self.config['caching']['cache_file']
        )
        self.content_filter = ContentFilter(self.config['filtering'])
        self.data_formatter = DataFormatter()
        self.rss_parser = RSSParser()

    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _default_config(self) -> dict:
        """默认配置"""
        return {
            "sources": [],
            "filtering": {
                "keywords": {
                    "include": ["股票", "股市", "A股", "港股", "美股", "基金", "投资"],
                    "exclude": ["广告", "推广", "招聘"]
                },
                "min_relevance_score": 0.3,
                "max_age_hours": 24
            },
            "output": {
                "format": "json",
                "max_articles": 50,
                "include_full_content": False
            },
            "caching": {
                "enabled": True,
                "retention_days": 7,
                "cache_file": ".rss_cache.json"
            },
            "request": {
                "timeout": 10,
                "retry_attempts": 3,
                "delay_between_requests": 1
            }
        }

    def add_source(self, url: str, name: str, category: str = None, priority: int = 1, enabled: bool = True):
        """添加RSS源"""
        source = {
            "name": name,
            "url": url,
            "category": category or "通用",
            "priority": priority,
            "enabled": enabled
        }
        self.config['sources'].append(source)

    def remove_source(self, url: str):
        """移除RSS源"""
        self.config['sources'] = [source for source in self.config['sources'] if source['url'] != url]

    async def _fetch_rss_content(self, session: aiohttp.ClientSession, source: dict) -> Optional[dict]:
        """异步获取单个RSS源内容"""
        url = source['url']
        headers = {
            "Accept": "application/xml,text/xml,application/html,*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (compatible; RSS Reader; +http://localhost:1200)",
            "Connection": "keep-alive"
        }
        
        for attempt in range(self.config['request']['retry_attempts']):
            try:
                async with session.get(
                    url, 
                    headers=headers, 
                    timeout=aiohttp.ClientTimeout(total=self.config['request']['timeout'])
                ) as response:
                    if response.status == 200:
                        content = await response.text()
                        return {
                            'source': source,
                            'content': content,
                            'success': True
                        }
                    else:
                        print(f"获取RSS源失败 {url}: 状态码 {response.status}")
            except Exception as e:
                print(f"获取RSS源异常 {url} (尝试 {attempt+1}/{self.config['request']['retry_attempts']}): {str(e)}")
                if attempt < self.config['request']['retry_attempts'] - 1:
                    await asyncio.sleep(self.config['request']['delay_between_requests'])
        
        return {'source': source, 'content': None, 'success': False}

    async def _process_source(self, session: aiohttp.ClientSession, source: dict) -> List[Dict]:
        """处理单个RSS源"""
        if not source.get('enabled', True):
            return []
            
        result = await self._fetch_rss_content(session, source)
        if not result['success'] or not result['content']:
            return []
        
        # 解析RSS内容
        parsed_feed = self.rss_parser.parse(result['content'], source)
        
        # 过滤内容
        filtered_articles = []
        for entry in parsed_feed.get('entries', []):
            if not self.cache_manager.is_processed(entry.get('id') or entry.get('link')):
                if self.content_filter.is_relevant(entry):
                    entry_with_source = {**entry, 'source': result['source']}
                    filtered_articles.append(entry_with_source)
        
        # 缓存已处理的文章ID
        for article in filtered_articles:
            self.cache_manager.mark_processed(article.get('id') or article.get('link'))
        
        return filtered_articles

    async def aggregate(self, max_articles: int = None) -> dict:
        """
        执行聚合操作
        
        Args:
            max_articles: 最大文章数量限制
            
        Returns:
            聚合结果字典
        """
        max_articles = max_articles or self.config['output']['max_articles']
        
        # 过滤启用的源
        enabled_sources = [source for source in self.config['sources'] if source.get('enabled', True)]
        
        if not enabled_sources:
            print("没有启用的RSS源")
            return {
                "meta": {
                    "generated_at": datetime.now().isoformat(),
                    "total_articles": 0,
                    "sources_used": 0,
                    "time_range": {
                        "from": (datetime.now() - timedelta(hours=self.config['filtering']['max_age_hours'])).isoformat(),
                        "to": datetime.now().isoformat()
                    }
                },
                "articles": []
            }
        
        # 异步获取所有RSS源内容
        async with aiohttp.ClientSession() as session:
            tasks = [self._process_source(session, source) for source in enabled_sources]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并所有文章
        all_articles = []
        for result in results:
            if isinstance(result, Exception):
                print(f"处理RSS源时发生异常: {result}")
                continue
            all_articles.extend(result)
        
        # 按时间排序（最新的在前）
        all_articles.sort(key=lambda x: x.get('pub_date', ''), reverse=True)
        
        # 限制文章数量
        all_articles = all_articles[:max_articles]
        
        # 计算统计信息
        sources_count = len(set([article['source']['name'] for article in all_articles]))
        
        aggregation_result = {
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "total_articles": len(all_articles),
                "sources_used": sources_count,
                "time_range": {
                    "from": (datetime.now() - timedelta(hours=self.config['filtering']['max_age_hours'])).isoformat(),
                    "to": datetime.now().isoformat()
                }
            },
            "articles": all_articles
        }
        
        return aggregation_result

    def get_latest_articles(self, hours: int = 24) -> list:
        """
        获取最新文章（同步方法，从缓存或其他持久化存储中获取）
        
        Args:
            hours: 获取最近几小时的文章
            
        Returns:
            最新文章列表
        """
        # 此方法可以用于获取已缓存的最新文章
        # 实际实现可能需要查询数据库或文件缓存
        pass

    def export_to_json(self, data: dict, filepath: str):
        """导出为JSON格式"""
        self.data_formatter.export_to_json(data, filepath)

    def export_to_markdown(self, data: dict, filepath: str):
        """导出为Markdown格式"""
        self.data_formatter.export_to_markdown(data, filepath)