"""
RSS源兜底管理器
当RSS源失效时，提供备用的数据获取策略，通过引导大模型使用工具访问网页
"""
import asyncio
import logging
from typing import Dict, Optional, Any
from urllib.parse import urlparse
import time


class FallbackManager:
    """
    RSS源兜底管理器，提供AI驱动的网页访问策略
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._ai_fallback_stats = {
            'attempts': 0,
            'successes': 0,
            'last_attempt_time': 0,
            'daily_limit_start_time': time.time(),
            'daily_attempts': 0
        }
        
    async def get_content_with_fallback(
        self, 
        source_config: Dict[str, Any], 
        session = None  # 保持接口一致性，但不再使用session
    ) -> Optional[Dict[str, Any]]:
        """
        使用兜底策略获取内容，生成AI提示来引导大模型使用工具访问网页
        
        Args:
            source_config: 源配置信息
            session: HTTP会话（此处主要用于保持接口一致性，实际不再使用）
            
        Returns:
            获取到的内容或None
        """
        # 检查是否启用了兜底
        if not source_config.get('fallback_enabled', False):
            self.logger.info(f"兜底未启用，跳过 {source_config.get('name')}")
            return None
            
        raw_url = source_config.get('raw_url')
        if not raw_url:
            self.logger.warning(f"未找到备用URL，无法执行兜底策略 {source_config.get('name')}")
            return None
            
        fallback_strategy = source_config.get('fallback_strategy', 'ai_crawl')
        
        self.logger.info(f"正在为 {source_config.get('name')} 执行兜底策略: {fallback_strategy}")
        
        if fallback_strategy == 'ai_crawl':
            return await self._ai_crawl_fallback(raw_url)
        else:
            self.logger.warning(f"未知的兜底策略: {fallback_strategy}，使用默认的ai_crawl")
            return await self._ai_crawl_fallback(raw_url)
    
    def generate_ai_prompt_for_web_access(self, url: str) -> str:
        """
        生成AI提示，引导大模型使用工具访问指定网页并提取内容
        
        Args:
            url: 目标URL
            
        Returns:
            AI提示字符串
        """
        prompt = f"""
        请使用网页访问工具访问以下URL并提取有用的内容：
        URL: {url}
        
        请提取以下信息：
        1. 页面标题
        2. 主要内容（正文）
        3. 发布时间（如果有）
        4. 作者（如果有）
        
        请以结构化格式返回这些信息。
        """
        return prompt
    
    async def _ai_crawl_fallback(self, url: str) -> Optional[Dict[str, Any]]:
        """
        生成AI提示，引导大模型使用工具访问网页
        
        Args:
            url: 目标URL
            
        Returns:
            包含AI提示的结构化内容
        """
        # 检查是否达到最大AI兜底尝试次数
        max_attempts = self.config.get('fallback', {}).get('max_ai_fallback_attempts', 3)
        if self._ai_fallback_stats['attempts'] >= max_attempts:
            self.logger.warning(f"AI兜底尝试总次数已达上限({max_attempts})，跳过URL: {url}")
            return None

        # 检查每日限制
        current_time = time.time()
        # 重置每日统计（如果超过24小时）
        if current_time - self._ai_fallback_stats['daily_limit_start_time'] > 24 * 3600:  # 24小时
            self._ai_fallback_stats['daily_limit_start_time'] = current_time
            self._ai_fallback_stats['daily_attempts'] = 0

        # 检查是否达到每日AI兜底限制（例如每天最多10次）
        daily_limit = self.config.get('fallback', {}).get('daily_ai_fallback_limit', 10)
        if self._ai_fallback_stats['daily_attempts'] >= daily_limit:
            self.logger.warning(f"AI兜底今日尝试次数已达上限({daily_limit})，跳过URL: {url}")
            return None

        # 检查最小间隔时间
        min_delay = self.config.get('fallback', {}).get('ai_fallback_delay', 30)
        if current_time - self._ai_fallback_stats['last_attempt_time'] < min_delay:
            self.logger.info(f"AI兜底冷却时间内，跳过URL: {url}")
            wait_time = min_delay - (current_time - self._ai_fallback_stats['last_attempt_time'])
            await asyncio.sleep(wait_time)

        # 增加尝试计数
        self._ai_fallback_stats['attempts'] += 1
        self._ai_fallback_stats['daily_attempts'] += 1
        self._ai_fallback_stats['last_attempt_time'] = current_time

        try:
            # 生成AI提示，引导大模型使用工具访问网页
            ai_prompt = self.generate_ai_prompt_for_web_access(url)
            
            # 创建包含AI提示的结构化响应
            fallback_item = {
                'title': f'AI工具访问-{urlparse(url).netloc}',
                'link': url,
                'description': f'需要使用AI工具访问网页以获取内容: {url}',
                'pubDate': '',
                'guid': url,
                'ai_task': {
                    'type': 'web_access',
                    'url': url,
                    'prompt': ai_prompt,
                    'instructions': '请使用适当的工具访问上述URL并提取相关内容'
                }
            }
            
            # 增加成功计数
            self._ai_fallback_stats['successes'] += 1
            
            self.logger.info(f"AI兜底提示已生成: {url}")
            return {'entries': [fallback_item], 'ai_task_required': True}
            
        except Exception as e:
            self.logger.error(f"AI兜底提示生成失败: {str(e)}, URL: {url}")
            return None

    def get_ai_fallback_stats(self) -> Dict[str, Any]:
        """
        获取AI兜底统计信息
        
        Returns:
            统计信息字典
        """
        current_time = time.time()
        time_since_daily_reset = current_time - self._ai_fallback_stats['daily_limit_start_time']
        hours_since_reset = time_since_daily_reset / 3600
        
        return {
            'attempts': self._ai_fallback_stats['attempts'],
            'successes': self._ai_fallback_stats['successes'],
            'attempts_remaining': max(0, self.config.get('fallback', {}).get('max_ai_fallback_attempts', 3) - self._ai_fallback_stats['attempts']),
            'daily_attempts': self._ai_fallback_stats['daily_attempts'],
            'daily_attempts_remaining': max(0, self.config.get('fallback', {}).get('daily_ai_fallback_limit', 10) - self._ai_fallback_stats['daily_attempts']),
            'hours_since_daily_reset': round(hours_since_reset, 2),
            'last_attempt_time': self._ai_fallback_stats['last_attempt_time']
        }
    
    def should_attempt_fallback(self, source_config: Dict[str, Any]) -> bool:
        """
        判断是否应该尝试兜底策略
        
        Args:
            source_config: 源配置信息
            
        Returns:
            是否应该尝试兜底
        """
        fallback_enabled_global = self.config.get('fallback', {}).get('enabled', True)
        fallback_enabled_source = source_config.get('fallback_enabled', False)
        
        return fallback_enabled_global and fallback_enabled_source