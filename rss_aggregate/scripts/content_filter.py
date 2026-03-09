"""
内容过滤器模块
负责基于关键词过滤内容、去重、质量评估等
"""
import sys
import os
# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from datetime import datetime, timedelta
from typing import Dict, List


class ContentFilter:
    def __init__(self, filtering_config: dict):
        """
        初始化内容过滤器
        
        Args:
            filtering_config: 过滤配置字典
        """
        self.filtering_config = filtering_config
        self.include_keywords = filtering_config.get('keywords', {}).get('include', [])
        self.exclude_keywords = filtering_config.get('keywords', {}).get('exclude', [])
        self.min_relevance_score = filtering_config.get('min_relevance_score', 0.3)
        self.max_age_hours = filtering_config.get('max_age_hours', 24)

    def is_relevant(self, article: dict) -> bool:
        """
        判断文章是否相关
        
        Args:
            article: 文章字典
            
        Returns:
            是否相关
        """
        # 检查相关性评分
        if article.get('relevance_score', 0) < self.min_relevance_score:
            return False
            
        # 检查时间是否在有效范围内
        if not self._is_recent_enough(article):
            return False
            
        # 检查排除关键词
        if self._has_excluded_keywords(article):
            return False
            
        # 检查包含关键词
        if not self._has_included_keywords(article):
            return False
            
        return True

    def _is_recent_enough(self, article: dict) -> bool:
        """
        检查文章发布时间是否足够新
        
        Args:
            article: 文章字典
            
        Returns:
            是否足够新
        """
        pub_date_str = article.get('pub_date', '')
        if not pub_date_str:
            return True  # 如果没有发布日期，则认为是新的
            
        try:
            pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
            time_diff = datetime.now(pub_date.tzinfo if pub_date.tzinfo else None) - pub_date
            return time_diff.total_seconds() <= self.max_age_hours * 3600
        except ValueError:
            # 如果日期格式不正确，则认为是有效的
            return True

    def _has_excluded_keywords(self, article: dict) -> bool:
        """
        检查是否包含排除关键词
        
        Args:
            article: 文章字典
            
        Returns:
            是否包含排除关键词
        """
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        content = article.get('content', '').lower()
        
        combined_text = f"{title} {summary} {content}"
        
        for keyword in self.exclude_keywords:
            if keyword.lower() in combined_text:
                return True
                
        return False

    def _has_included_keywords(self, article: dict) -> bool:
        """
        检查是否包含包含关键词
        
        Args:
            article: 文章字典
            
        Returns:
            是否包含包含关键词
        """
        if not self.include_keywords:
            # 如果没有指定包含关键词，则认为都符合条件
            return True
            
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        content = article.get('content', '').lower()
        
        combined_text = f"{title} {summary} {content}"
        
        for keyword in self.include_keywords:
            if keyword.lower() in combined_text:
                return True
                
        return False

    def filter_articles(self, articles: List[dict]) -> List[dict]:
        """
        过滤文章列表
        
        Args:
            articles: 文章列表
            
        Returns:
            过滤后的文章列表
        """
        return [article for article in articles if self.is_relevant(article)]

    def deduplicate(self, articles: List[dict], threshold: float = 0.8) -> List[dict]:
        """
        去除重复文章
        
        Args:
            articles: 文章列表
            threshold: 相似度阈值，超过此值认为是重复
            
        Returns:
            去重后的文章列表
        """
        if not articles:
            return []
            
        unique_articles = []
        processed_ids = set()
        
        for article in articles:
            # 首先检查是否有明确的唯一标识符
            article_id = article.get('id')
            if article_id and article_id in processed_ids:
                continue
                
            # 检查是否与其他已保留的文章过于相似
            is_duplicate = False
            for unique_article in unique_articles:
                if self._is_similar(article, unique_article, threshold):
                    is_duplicate = True
                    break
                    
            if not is_duplicate:
                unique_articles.append(article)
                if article_id:
                    processed_ids.add(article_id)
                    
        return unique_articles

    def _is_similar(self, article1: dict, article2: dict, threshold: float = 0.8) -> bool:
        """
        检查两篇文章是否相似
        
        Args:
            article1: 文章1
            article2: 文章2
            threshold: 相似度阈值
            
        Returns:
            是否相似
        """
        # 比较标题相似度
        title_similarity = self._text_similarity(
            article1.get('title', ''), 
            article2.get('title', '')
        )
        
        if title_similarity >= threshold:
            return True
            
        # 如果标题不够相似，比较内容相似度
        content_similarity = self._text_similarity(
            article1.get('content', ''), 
            article2.get('content', '')
        )
        
        return content_similarity >= threshold

    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            相似度 (0-1)
        """
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
            
        # 移除特殊字符，只保留中文、英文和数字
        text1_clean = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text1.lower())
        text2_clean = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text2.lower())
        
        # 如果文本太短，直接比较
        if len(text1_clean) < 5 or len(text2_clean) < 5:
            return 1.0 if text1_clean == text2_clean else 0.0
            
        # 使用最长公共子序列算法计算相似度
        def lcs_length(s1, s2):
            m, n = len(s1), len(s2)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if s1[i - 1] == s2[j - 1]:
                        dp[i][j] = dp[i - 1][j - 1] + 1
                    else:
                        dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
                        
            return dp[m][n]
        
        lcs_len = lcs_length(text1_clean, text2_clean)
        max_len = max(len(text1_clean), len(text2_clean))
        
        return lcs_len / max_len if max_len > 0 else 0.0