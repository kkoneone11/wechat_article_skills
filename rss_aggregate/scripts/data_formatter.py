
"""
数据格式化模块
负责将聚合的数据转换为不同格式（JSON、Markdown等）
"""
import sys
import os
# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime
from typing import Dict, List


class DataFormatter:
    def __init__(self):
        pass

    def export_to_json(self, data: dict, filepath: str):
        """
        导出为JSON格式
        
        Args:
            data: 要导出的数据
            filepath: 输出文件路径
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def export_to_markdown(self, data: dict, filepath: str):
        """
        导出为Markdown格式
        
        Args:
            data: 要导出的数据
            filepath: 输出文件路径
        """
        markdown_content = self._format_as_markdown(data)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

    def _format_as_markdown(self, data: dict) -> str:
        """
        将数据格式化为Markdown字符串
        
        Args:
            data: 聚合的数据
            
        Returns:
            Markdown格式的字符串
        """
        markdown_lines = []
        
        # 添加标题和元信息
        meta = data.get('meta', {})
        markdown_lines.append(f"# RSS聚合内容报告")
        markdown_lines.append(f"*生成时间：{self._format_datetime_for_markdown(meta.get('generated_at', ''))}*")
        markdown_lines.append("")
        
        # 添加统计信息
        markdown_lines.append("## 聚合统计")
        markdown_lines.append(f"- 总文章数：{meta.get('total_articles', 0)}篇")
        markdown_lines.append(f"- 数据源：{meta.get('sources_used', 0)}个RSS源")
        
        time_range = meta.get('time_range', {})
        if time_range:
            markdown_lines.append(f"- 时间范围：{self._format_time_range(time_range)}")
        markdown_lines.append("")
        
        # 添加文章列表
        markdown_lines.append("## 文章列表")
        markdown_lines.append("")
        
        articles = data.get('articles', [])
        for article in articles:
            markdown_lines.extend(self._format_article_as_markdown(article))
            markdown_lines.append("")  # 在文章之间添加空行
        
        return "\n".join(markdown_lines)

    def _format_article_as_markdown(self, article: dict) -> List[str]:
        """
        将单篇文章格式化为Markdown格式
        
        Args:
            article: 文章字典
            
        Returns:
            Markdown格式的行列表
        """
        lines = []
        
        title = article.get('title', '无标题')
        link = article.get('link', '')
        pub_date = article.get('pub_date', '')
        source_name = article.get('source', {}).get('name', '未知来源')
        summary = article.get('summary', '无摘要')
        tags = article.get('tags', [])
        
        # 添加文章标题（带链接）
        if link:
            lines.append(f"### [{title}]({link})")
        else:
            lines.append(f"### {title}")
        
        # 添加文章信息
        lines.append(f"- **来源**：{source_name}")
        if pub_date:
            lines.append(f"- **时间**：{self._format_datetime_for_markdown(pub_date)}")
        
        # 添加摘要
        if summary:
            lines.append(f"- **摘要**：{summary}")
        
        # 添加标签
        if tags:
            tag_list = " ".join([f"#{tag}" for tag in tags[:5]])  # 只显示前5个标签
            lines.append(f"- **标签**：{tag_list}")
        
        lines.append("")  # 在文章末尾添加空行
        return lines

    def _format_datetime_for_markdown(self, datetime_str: str) -> str:
        """
        格式化日期时间为适合Markdown显示的格式
        
        Args:
            datetime_str: ISO格式的日期时间字符串
            
        Returns:
            格式化后的日期时间字符串
        """
        try:
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            return datetime_str

    def _format_time_range(self, time_range: dict) -> str:
        """
        格式化时间范围
        
        Args:
            time_range: 包含from和to的字典
            
        Returns:
            格式化后的时间范围字符串
        """
        from_time = time_range.get('from', '')
        to_time = time_range.get('to', '')
        
        if from_time and to_time:
            formatted_from = self._format_datetime_for_markdown(from_time)
            formatted_to = self._format_datetime_for_markdown(to_time)
            return f"从 {formatted_from} 到 {formatted_to}"
        elif to_time:
            return f"截止至 {self._format_datetime_for_markdown(to_time)}"
        else:
            return "未知时间范围"

    def format_for_tech_writer(self, data: dict) -> str:
        """
        为wechat-tech-writer格式化数据
        
        Args:
            data: 聚合的数据
            
        Returns:
            适合tech-writer处理的格式
        """
        articles = data.get('articles', [])
        formatted_content = []
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', '无标题')
            summary = article.get('summary', '无摘要')
            content = article.get('content', '')
            link = article.get('link', '')
            source_name = article.get('source', {}).get('name', '未知来源')
            pub_date = article.get('pub_date', '')
            tags = article.get('tags', [])
            
            # 构建文章内容块
            article_block = f"## 文章 {i}: {title}\n\n"
            article_block += f"**来源**: {source_name}\n\n"
            article_block += f"**发布时间**: {self._format_datetime_for_markdown(pub_date)}\n\n"
            article_block += f"**原文链接**: {link}\n\n"
            article_block += f"**摘要**: \n{summary}\n\n"
            
            if content:
                article_block += f"**详细内容**: \n{content}\n\n"
            
            if tags:
                article_block += f"**相关标签**: {', '.join(tags)}\n\n"
            
            formatted_content.append(article_block)
        
        # 组合成完整的提示内容
        full_content = "# RSS聚合内容 - 供微信文章创作参考\n\n"
        full_content += f"本报告聚合了来自 {len(articles)} 个RSS源的最新内容，供微信文章创作参考。\n\n"
        full_content += "".join(formatted_content)
        
        return full_content
