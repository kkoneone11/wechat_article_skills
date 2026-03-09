"""
缓存管理器模块
负责存储已处理的文章ID，防止重复处理，管理缓存生命周期
"""
import sys
import os
# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
from datetime import datetime, timedelta
from typing import Set


class CacheManager:
    def __init__(self, enabled: bool = True, retention_days: int = 7, cache_file: str = ".rss_cache.json"):
        """
        初始化缓存管理器
        
        Args:
            enabled: 是否启用缓存
            retention_days: 缓存保留天数
            cache_file: 缓存文件路径
        """
        self.enabled = enabled
        self.retention_days = retention_days
        self.cache_file = cache_file
        # 初始化cache_data属性
        self.cache_data = {"processed_ids": {}, "created_at": ""}
        self.cache_data = self._load_cache()

    def _load_cache(self) -> dict:
        """
        从文件加载缓存数据
        
        Returns:
            缓存数据字典
        """
        if not self.enabled:
            return {"processed_ids": {}, "created_at": datetime.now().isoformat()}
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                # 清理过期的缓存项
                self._cleanup_expired()
                return cache_data
        except FileNotFoundError:
            # 如果缓存文件不存在，创建一个新的
            cache_data = {"processed_ids": {}, "created_at": datetime.now().isoformat()}
            self._save_cache(cache_data)
            return cache_data
        except json.JSONDecodeError:
            # 如果缓存文件格式错误，创建一个新的
            print(f"警告: 缓存文件 {self.cache_file} 格式错误，将创建新的缓存文件")
            cache_data = {"processed_ids": {}, "created_at": datetime.now().isoformat()}
            self._save_cache(cache_data)
            return cache_data

    def _save_cache(self, cache_data: dict = None):
        """
        保存缓存数据到文件
        
        Args:
            cache_data: 要保存的缓存数据，默认使用当前实例的缓存数据
        """
        if not self.enabled:
            return
            
        data_to_save = cache_data if cache_data is not None else self.cache_data
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"警告: 无法保存缓存文件 {self.cache_file}: {str(e)}")

    def _cleanup_expired(self):
        """
        清理过期的缓存项
        """
        if not self.enabled:
            return
            
        cutoff_time = (datetime.now() - timedelta(days=self.retention_days)).timestamp()
        expired_ids = []
        
        for article_id, timestamp in self.cache_data.get("processed_ids", {}).items():
            if timestamp < cutoff_time:
                expired_ids.append(article_id)
        
        for article_id in expired_ids:
            del self.cache_data["processed_ids"][article_id]
        
        if expired_ids:
            self._save_cache()

    def is_processed(self, article_id: str) -> bool:
        """
        检查文章是否已经处理过
        
        Args:
            article_id: 文章ID
            
        Returns:
            是否已经处理过
        """
        if not self.enabled or not article_id:
            return False
            
        self._cleanup_expired()
        return article_id in self.cache_data.get("processed_ids", {})

    def mark_processed(self, article_id: str):
        """
        标记文章为已处理
        
        Args:
            article_id: 文章ID
        """
        if not self.enabled or not article_id:
            return
            
        self.cache_data.setdefault("processed_ids", {})
        self.cache_data["processed_ids"][article_id] = time.time()
        self._save_cache()

    def clear_cache(self):
        """
        清空缓存
        """
        self.cache_data = {"processed_ids": {}, "created_at": datetime.now().isoformat()}
        if self.enabled:
            self._save_cache()

    def get_cache_stats(self) -> dict:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计信息字典
        """
        processed_count = len(self.cache_data.get("processed_ids", {}))
        created_at = self.cache_data.get("created_at", "")
        
        return {
            "enabled": self.enabled,
            "retention_days": self.retention_days,
            "cache_file": self.cache_file,
            "processed_count": processed_count,
            "created_at": created_at
        }

    def get_processed_ids(self) -> Set[str]:
        """
        获取所有已处理的ID集合
        
        Returns:
            已处理ID的集合
        """
        self._cleanup_expired()
        return set(self.cache_data.get("processed_ids", {}).keys())

    def remove_from_cache(self, article_id: str):
        """
        从缓存中移除特定ID
        
        Args:
            article_id: 要移除的文章ID
        """
        if not self.enabled or not article_id:
            return
            
        if article_id in self.cache_data.get("processed_ids", {}):
            del self.cache_data["processed_ids"][article_id]
            self._save_cache()