#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試中文繁簡轉換功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simplified_subtitle_core import SimplifiedSubtitleCore
import logging

# 設置日誌
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_chinese_conversion():
    """測試中文轉換功能"""
    
    print("測試中文繁簡轉換功能")
    print("="*50)
    
    # 創建字幕核心實例
    core = SimplifiedSubtitleCore(model_size="base", device="cpu", compute_type="int8")
    
    # 測試文本
    test_texts = [
        "这是一个简体中文的测试文本。",  # 簡體中文
        "這是一個繁體中文的測試文本。",  # 繁體中文
        "这是简体，這是繁體，混合文本测试。",  # 混合文本
        "我们来学习人工智能技术。",  # 含有技術詞彙的簡體
        "我們來學習人工智慧技術。",  # 含有技術詞彙的繁體
    ]
    
    print("\n測試轉換為繁體中文:")
    print("-" * 30)
    for i, text in enumerate(test_texts, 1):
        try:
            result = core._convert_to_traditional(text)
            print(f"{i}. 原文: {text}")
            print(f"   結果: {result}")
            print(f"   轉換: {'成功' if result != text else '無變化'}")
            print()
        except Exception as e:
            print(f"{i}. 錯誤: {e}")
            print()
    
    print("\n測試轉換為簡體中文:")
    print("-" * 30)
    for i, text in enumerate(test_texts, 1):
        try:
            result = core._convert_to_simplified(text)
            print(f"{i}. 原文: {text}")
            print(f"   結果: {result}")
            print(f"   轉換: {'成功' if result != text else '無變化'}")
            print()
        except Exception as e:
            print(f"{i}. 錯誤: {e}")
            print()
    
    print("\n測試強化繁體轉換:")
    print("-" * 30)
    for i, text in enumerate(test_texts, 1):
        try:
            result = core._basic_convert_to_traditional_robust(text)
            print(f"{i}. 原文: {text}")
            print(f"   結果: {result}")
            print(f"   轉換: {'成功' if result != text else '無變化'}")
            print()
        except Exception as e:
            print(f"{i}. 錯誤: {e}")
            print()

def test_opencc_availability():
    """測試 OpenCC 可用性"""
    print("\n檢查 OpenCC 可用性:")
    print("-" * 30)
    
    try:
        import opencc
        print("OpenCC 可用")
        
        # 測試轉換器
        try:
            s2t = opencc.OpenCC('s2t')
            t2s = opencc.OpenCC('t2s')
            
            test_text = "简体测试"
            result = s2t.convert(test_text)
            print(f"   簡體轉繁體: '{test_text}' -> '{result}'")
            
            test_text = "繁體測試"
            result = t2s.convert(test_text)
            print(f"   繁體轉簡體: '{test_text}' -> '{result}'")
            
        except Exception as e:
            print(f"OpenCC 轉換器錯誤: {e}")
            
    except ImportError:
        print("OpenCC 不可用，將使用基本字符映射")

if __name__ == "__main__":
    test_opencc_availability()
    test_chinese_conversion()
    
    print("\n" + "="*50)
    print("中文轉換測試完成")