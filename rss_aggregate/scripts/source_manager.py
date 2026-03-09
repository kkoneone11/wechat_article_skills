"""
RSS源管理器模块
负责管理RSS源的添加、删除、验证等功能
"""
import requests
import feedparser
from typing import Dict, List, Optional
from urllib.parse import urlparse


class SourceManager:
    def __init__(self):
        self.sources = []

    def add_source(self, url: str, name: str, category: str = None, priority: int = 1, enabled: bool = True):
        """
        添加RSS源
        
        Args:
            url: RSS源URL
            name: 源名称
            category: 分类
            priority: 优先级
            enabled: 是否启用
        """
        # 验证URL格式
        if not self._is_valid_url(url):
            raise ValueError(f"无效的URL格式: {url}")
        
        # 检查是否已存在相同的URL
        if self.get_source_by_url(url):
            raise ValueError(f"RSS源已存在: {url}")
        
        source = {
            "name": name,
            "url": url,
            "category": category or "通用",
            "priority": priority,
            "enabled": enabled,
            "added_at": self._get_current_timestamp(),
            "last_verified": None,
            "verified": False
        }
        
        self.sources.append(source)
        return source

    def remove_source(self, url: str) -> bool:
        """
        移除RSS源
        
        Args:
            url: 要移除的RSS源URL
            
        Returns:
            是否成功移除
        """
        original_count = len(self.sources)
        self.sources = [source for source in self.sources if source['url'] != url]
        return len(self.sources) < original_count

    def get_source_by_url(self, url: str) -> Optional[Dict]:
        """
        根据URL获取RSS源信息
        
        Args:
            url: RSS源URL
            
        Returns:
            RSS源信息或None
        """
        for source in self.sources:
            if source['url'] == url:
                return source
        return None

    def get_enabled_sources(self) -> List[Dict]:
        """
        获取所有启用的RSS源
        
        Returns:
            启用的RSS源列表
        """
        return [source for source in self.sources if source.get('enabled', True)]

    def get_sources_by_category(self, category: str) -> List[Dict]:
        """
        根据分类获取RSS源
        
        Args:
            category: 分类名称
            
        Returns:
            指定分类的RSS源列表
        """
        return [source for source in self.sources if source.get('category', '').lower() == category.lower()]

    def validate_source(self, url: str) -> Dict[str, any]:
        """
        验证RSS源的有效性
        
        Args:
            url: RSS源URL
            
        Returns:
            验证结果字典
        """
        result = {
            "url": url,
            "valid": False,
            "reachable": False,
            "is_rss": False,
            "title": "",
            "description": "",
            "item_count": 0,
            "error_message": ""
        }
        
        try:
            # 检查URL是否可达
            response = requests.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (compatible; RSS Validator)"
            })
            result["reachable"] = response.status_code == 200
            
            if not result["reachable"]:
                result["error_message"] = f"HTTP {response.status_code}: {response.reason}"
                return result
            
            # 尝试解析RSS内容
            feed = feedparser.parse(response.content)
            
            if feed.bozo and feed.bozo_exception:
                # RSS格式可能有问题，但仍尝试获取基本信息
                result["is_rss"] = bool(feed.feed or feed.entries)
            else:
                result["is_rss"] = True
            
            result["valid"] = result["reachable"] and result["is_rss"]
            
            # 提取RSS信息
            if hasattr(feed, 'feed'):
                result["title"] = getattr(feed.feed, 'title', '')
                result["description"] = getattr(feed.feed, 'description', '')
            
            if hasattr(feed, 'entries'):
                result["item_count"] = len(feed.entries)
                
        except requests.exceptions.RequestException as e:
            result["error_message"] = f"网络请求错误: {str(e)}"
        except Exception as e:
            result["error_message"] = f"解析错误: {str(e)}"
        
        return result

    def validate_all_sources(self) -> List[Dict[str, any]]:
        """
        验证所有RSS源
        
        Returns:
            所有RSS源的验证结果列表
        """
        results = []
        for source in self.sources:
            validation_result = self.validate_source(source['url'])
            validation_result["name"] = source["name"]
            results.append(validation_result)
        return results

    def update_source_status(self, url: str, verified: bool = None, enabled: bool = None):
        """
        更新RSS源状态
        
        Args:
            url: RSS源URL
            verified: 验证状态
            enabled: 启用状态
        """
        source = self.get_source_by_url(url)
        if not source:
            raise ValueError(f"未找到RSS源: {url}")
        
        if verified is not None:
            source["verified"] = verified
            source["last_verified"] = self._get_current_timestamp()
        
        if enabled is not None:
            source["enabled"] = enabled

    def get_sources_summary(self) -> Dict[str, any]:
        """
        获取RSS源汇总信息
        
        Returns:
            RSS源汇总信息
        """
        total_sources = len(self.sources)
        enabled_sources = len(self.get_enabled_sources())
        categories = list(set(source.get('category', '通用') for source in self.sources))
        
        return {
            "total_sources": total_sources,
            "enabled_sources": enabled_sources,
            "disabled_sources": total_sources - enabled_sources,
            "categories": categories,
            "sources_by_category": {
                category: len(self.get_sources_by_category(category)) 
                for category in categories
            }
        }

    def _is_valid_url(self, url: str) -> bool:
        """
        检查URL格式是否有效
        
        Args:
            url: URL字符串
            
        Returns:
            URL是否有效
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _get_current_timestamp(self) -> str:
        """
        获取当前时间戳
        
        Returns:
            ISO格式的时间戳字符串
        """
        from datetime import datetime
        return datetime.now().isoformat()