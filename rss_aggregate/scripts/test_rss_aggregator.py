#!/usr/bin/env python3
"""
RSS聚合器测试脚本
用于验证所有模块是否能正常工作
"""

import sys
import os

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        from rss_aggregate.scripts.aggregator import RSSAggregator
        print("✓ RSSAggregator 导入成功")
    except ImportError as e:
        print(f"✗ RSSAggregator 导入失败: {e}")
        return False
    
    try:
        from rss_aggregate.scripts.rss_parser import RSSParser
        print("✓ RSSParser 导入成功")
    except ImportError as e:
        print(f"✗ RSSParser 导入失败: {e}")
        return False
    
    try:
        from rss_aggregate.scripts.content_filter import ContentFilter
        print("✓ ContentFilter 导入成功")
    except ImportError as e:
        print(f"✗ ContentFilter 导入失败: {e}")
        return False
    
    try:
        from rss_aggregate.scripts.data_formatter import DataFormatter
        print("✓ DataFormatter 导入成功")
    except ImportError as e:
        print(f"✗ DataFormatter 导入失败: {e}")
        return False
    
    try:
        from rss_aggregate.scripts.cache_manager import CacheManager
        print("✓ CacheManager 导入成功")
    except ImportError as e:
        print(f"✗ CacheManager 导入失败: {e}")
        return False
    
    try:
        from rss_aggregate.scripts.source_manager import SourceManager
        print("✓ SourceManager 导入成功")
    except ImportError as e:
        print(f"✗ SourceManager 导入失败: {e}")
        return False
    
    return True

def test_basic_functionality():
    """测试基本功能"""
    print("\n测试基本功能...")
    
    try:
        from rss_aggregate.scripts.aggregator import RSSAggregator
        
        # 创建聚合器实例
        agg_instance = RSSAggregator()
        print("✓ RSSAggregator 实例创建成功")
        
        # 测试添加源
        agg_instance.add_source(
            url="http://example.com/rss",
            name="示例源",
            category="示例"
        )
        print("✓ 添加RSS源成功")
        
        # 验证源是否添加成功
        if len(agg_instance.config['sources']) > 0:
            print("✓ RSS源列表验证成功")
        else:
            print("✗ RSS源列表验证失败")
            return False
            
    except Exception as e:
        print(f"✗ 基本功能测试失败: {e}")
        return False
    
    return True

def main():
    print("RSS聚合器测试")
    print("="*50)
    
    # 测试导入
    if not test_imports():
        print("\n模块导入测试失败，停止测试。")
        return
    
    # 测试基本功能
    if not test_basic_functionality():
        print("\n基本功能测试失败。")
        return
    
    print("\n✓ 所有测试通过！RSS聚合器模块正常工作。")

if __name__ == "__main__":
    main()