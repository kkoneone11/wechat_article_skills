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
    from .fallback_manager import FallbackManager
except ImportError:
    # 当作为独立模块运行时
    from rss_aggregate.scripts.rss_parser import RSSParser
    from rss_aggregate.scripts.content_filter import ContentFilter
    from rss_aggregate.scripts.data_formatter import DataFormatter
    from rss_aggregate.scripts.cache_manager import CacheManager
    from rss_aggregate.scripts.fallback_manager import FallbackManager


class RSSAggregator:
    def __init__(self, config_path: str = None):
        """
        初始化聚合器
        
        Args:
            config_path: 配置文件路径
        """
        if config_path:
            self.config = self._load_config(config_path)
        else:
            self.config = self._default_config()
        
        # 确保配置不为None
        if self.config is None:
            self.config = self._default_config()
        
        # 确保必要的配置项存在
        if 'filtering' not in self.config:
            self.config['filtering'] = self._default_config()['filtering']
        if 'caching' not in self.config:
            self.config['caching'] = self._default_config()['caching']
        if 'output' not in self.config:
            self.config['output'] = self._default_config()['output']
        if 'request' not in self.config:
            self.config['request'] = self._default_config()['request']
        if 'caching' not in self.config:
            self.config['caching'] = self._default_config()['caching']
        
        self.cache_manager = CacheManager(
            enabled=self.config['caching']['enabled'],
            retention_days=self.config['caching']['retention_days'],
            cache_file=self.config['caching']['cache_file']
        )
        self.content_filter = ContentFilter(self.config['filtering'])
        self.data_formatter = DataFormatter()
        self.rss_parser = RSSParser()
        self.fallback_manager = FallbackManager(self.config)

    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        import yaml
        import os
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    # 确保配置不为None
                    if config is None:
                        config = self._default_config()
                    return config
            else:
                # 如果配置文件不存在，返回默认配置
                return self._default_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}，使用默认配置")
            return self._default_config()

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
        # 使用更真实的浏览器头部信息
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Ch-Ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Connection": "keep-alive",
            "Referer": source.get('referer', 'https://www.google.com/')
        }
        
        for attempt in range(self.config['request']['retry_attempts']):
            try:
                # 增加更具体的超时设置
                timeout = aiohttp.ClientTimeout(total=self.config['request']['timeout'], 
                                              connect=5, 
                                              sock_connect=5, 
                                              sock_read=10)
                async with session.get(
                    url, 
                    headers=headers, 
                    timeout=timeout,
                    allow_redirects=True  # 允许重定向
                ) as response:
                    if response.status == 200:
                        content = await response.text()
                        return {
                            'source': source,
                            'content': content,
                            'success': True,
                            'status_code': response.status,
                            'headers': dict(response.headers)  # 记录响应头信息，有助于调试
                        }
                    elif response.status == 404:
                        print(f"获取RSS源失败 {url}: 状态码 {response.status} - 页面不存在")
                        # 对于404错误，立即返回失败，不进行重试
                        break
                    elif response.status == 403:
                        print(f"获取RSS源被拒绝 {url}: 状态码 {response.status} - 可能被防火墙拦截或需要认证")
                        # 对于403错误，记录特殊处理
                        if attempt < self.config['request']['retry_attempts'] - 1:
                            await asyncio.sleep(self.config['request']['delay_between_requests'] * (attempt + 1))  # 递增延迟
                    elif response.status == 429:
                        print(f"获取RSS源频率受限 {url}: 状态码 {response.status} - 等待后重试")
                        # 对于429错误，使用更长的延迟
                        if attempt < self.config['request']['retry_attempts'] - 1:
                            await asyncio.sleep(self.config['request']['delay_between_requests'] * (attempt + 2) * 2)  # 更长的延迟
                    elif response.status >= 500:
                        print(f"服务器内部错误 {url}: 状态码 {response.status} - 可能是服务器暂时不可用")
                        # 5xx错误通常表示服务器问题，值得重试
                        if attempt < self.config['request']['retry_attempts'] - 1:
                            await asyncio.sleep(self.config['request']['delay_between_requests'] * (attempt + 2))
                    else:
                        print(f"获取RSS源失败 {url}: 状态码 {response.status}")
                        if attempt < self.config['request']['retry_attempts'] - 1:
                            await asyncio.sleep(self.config['request']['delay_between_requests'] * (attempt + 1))  # 递增延迟
            except aiohttp.ClientConnectorError as e:
                print(f"连接错误 {url} (尝试 {attempt+1}/{self.config['request']['retry_attempts']}): {str(e)} - 可能是网络连接问题或服务器不可达")
                if attempt < self.config['request']['retry_attempts'] - 1:
                    await asyncio.sleep(self.config['request']['delay_between_requests'] * (attempt + 1))
            except aiohttp.ServerTimeoutError as e:
                print(f"服务器超时 {url} (尝试 {attempt+1}/{self.config['request']['retry_attempts']}): {str(e)}")
                if attempt < self.config['request']['retry_attempts'] - 1:
                    await asyncio.sleep(self.config['request']['delay_between_requests'] * (attempt + 2))  # 更长的延迟
            except aiohttp.ClientOSError as e:
                print(f"客户端操作系统错误 {url} (尝试 {attempt+1}/{self.config['request']['retry_attempts']}): {str(e)}")
                if attempt < self.config['request']['retry_attempts'] - 1:
                    await asyncio.sleep(self.config['request']['delay_between_requests'] * (attempt + 1))
            except asyncio.TimeoutError as e:
                print(f"异步超时错误 {url} (尝试 {attempt+1}/{self.config['request']['retry_attempts']}): {str(e)}")
                if attempt < self.config['request']['retry_attempts'] - 1:
                    await asyncio.sleep(self.config['request']['delay_between_requests'] * (attempt + 2))  # 更长的延迟
            except UnicodeDecodeError as e:
                print(f"编码错误 {url} (尝试 {attempt+1}/{self.config['request']['retry_attempts']}): {str(e)} - 内容编码问题")
                # 编码错误通常不需要重试
                break
            except Exception as e:
                print(f"获取RSS源异常 {url} (尝试 {attempt+1}/{self.config['request']['retry_attempts']}): {str(e)} - {type(e).__name__}")
                if attempt < self.config['request']['retry_attempts'] - 1:
                    await asyncio.sleep(self.config['request']['delay_between_requests'] * (attempt + 1))
        
        # RSS源获取失败，尝试使用兜底策略
        print(f"RSS源 {url} 获取失败，尝试使用兜底策略...")
        
        if self.fallback_manager.should_attempt_fallback(source):
            fallback_result = await self.fallback_manager.get_content_with_fallback(source, session)
            if fallback_result:
                print(f"兜底策略成功，获取到 {len(fallback_result.get('entries', []))} 条内容")
                return {
                    'source': source,
                    'content': fallback_result,  # 使用fallback结果
                    'success': True,
                    'status_code': 200,
                    'is_fallback': True  # 标记为使用了兜底策略
                }
        
        print(f"所有获取方式均失败，RSS源: {url}")
        return {'source': source, 'content': None, 'success': False, 'status_code': None}

    async def _process_source(self, session: aiohttp.ClientSession, source: dict) -> List[Dict]:
        """处理单个RSS源"""
        if not source.get('enabled', True):
            return []
            
        result = await self._fetch_rss_content(session, source)
        if not result['success'] or not result['content']:
            # 记录失败的源
            status_code = result.get('status_code', 'N/A')
            print(f"警告: 无法处理RSS源 '{source['name']}' ({source['url']})，状态码: {status_code}")
            return []
        
        # 检查是否使用了兜底策略
        if result.get('is_fallback'):
            # 如果使用了兜底策略，内容已经是解析好的格式
            parsed_feed = result['content']
            print(f"使用兜底策略处理源: {source['name']}")
        else:
            # 解析RSS内容
            parsed_feed = self.rss_parser.parse(result['content'], source)
            
            # 检查解析是否成功
            if 'error' in parsed_feed:
                print(f"警告: 解析RSS源 '{source['name']}' 失败: {parsed_feed['error']}")
                return []
        
        # 统计过滤信息
        total_entries = len(parsed_feed.get('entries', []))
        processed_entries = 0
        filtered_out = 0
        already_processed = 0
        
        # 过滤内容
        filtered_articles = []
        for entry in parsed_feed.get('entries', []):
            entry_id = entry.get('id') or entry.get('link')
            
            if not self.cache_manager.is_processed(entry_id):
                processed_entries += 1
                if self.content_filter.is_relevant(entry):
                    entry_with_source = {**entry, 'source': result['source']}
                    filtered_articles.append(entry_with_source)
                else:
                    filtered_out += 1
            else:
                already_processed += 1
        
        # 打印过滤统计信息
        print(f"RSS源 '{source['name']}' 处理统计:")
        print(f"  - 总条目数: {total_entries}")
        print(f"  - 已缓存跳过: {already_processed}")
        print(f"  - 新条目处理: {processed_entries}")
        print(f"  - 符合条件: {len(filtered_articles)}")
        print(f"  - 过滤掉: {filtered_out}")
        if result.get('is_fallback'):
            print(f"  - 使用兜底策略: 是")
        
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
        
        print(f"开始处理 {len(enabled_sources)} 个RSS源...")
        
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
        
        print(f"\n聚合完成！最终保留 {len(all_articles)} 篇文章，来自 {sources_count} 个数据源")
        
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