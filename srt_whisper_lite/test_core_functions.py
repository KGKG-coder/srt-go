#!/usr/bin/env python3
"""
測試核心功能 - 不涉及 GUI
"""

import sys
import os
from pathlib import Path
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_core_imports():
    """測試核心模組匯入"""
    try:
        from simplified_subtitle_core import SimplifiedSubtitleCore
        from audio_processor import AudioProcessor
        from semantic_processor import SemanticSegmentProcessor
        from subtitle_formatter import SubtitleFormatter
        from config_manager import ConfigManager
        
        logger.info("✅ 所有核心模組匯入成功")
        return True
    except Exception as e:
        logger.error(f"❌ 模組匯入失敗: {e}")
        return False

def test_whisper_model_loading():
    """測試 Whisper 模型載入"""
    try:
        from simplified_subtitle_core import SimplifiedSubtitleCore
        
        logger.info("正在測試 Whisper 模型載入...")
        core = SimplifiedSubtitleCore(model_size="tiny", device="cpu")
        core.initialize()
        
        logger.info("✅ Whisper 模型載入成功")
        return True
    except Exception as e:
        logger.error(f"❌ Whisper 模型載入失敗: {e}")
        return False

def test_audio_processor():
    """測試音頻處理器"""
    try:
        from audio_processor import AudioProcessor
        
        processor = AudioProcessor()
        logger.info("✅ 音頻處理器初始化成功")
        return True
    except Exception as e:
        logger.error(f"❌ 音頻處理器失敗: {e}")
        return False

def test_config_manager():
    """測試配置管理"""
    try:
        from config_manager import ConfigManager
        
        config = ConfigManager()
        default_config = config.get_default_config()
        logger.info(f"✅ 配置管理正常，預設語言: {default_config.get('language', 'auto')}")
        return True
    except Exception as e:
        logger.error(f"❌ 配置管理失敗: {e}")
        return False

def test_semantic_processor():
    """測試語義處理器"""
    try:
        from semantic_processor import SemanticSegmentProcessor
        
        processor = SemanticSegmentProcessor()
        
        # 測試中文文本處理
        test_text = "你好世界。這是一個測試。"
        result = processor.segment_text(test_text, "zh")
        logger.info(f"✅ 語義處理器正常，處理結果: {len(result)} 個段落")
        return True
    except Exception as e:
        logger.error(f"❌ 語義處理器失敗: {e}")
        return False

def main():
    """運行所有測試"""
    logger.info("=== 開始核心功能測試 ===")
    
    tests = [
        ("核心模組匯入", test_core_imports),
        ("配置管理", test_config_manager),
        ("音頻處理器", test_audio_processor),
        ("語義處理器", test_semantic_processor),
        ("Whisper 模型載入", test_whisper_model_loading),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- 測試: {test_name} ---")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} - 通過")
            else:
                logger.error(f"❌ {test_name} - 失敗")
        except Exception as e:
            logger.error(f"❌ {test_name} - 異常: {e}")
    
    logger.info(f"\n=== 測試結果 ===")
    logger.info(f"通過: {passed}/{total}")
    logger.info(f"成功率: {(passed/total)*100:.1f}%")
    
    if passed == total:
        logger.info("🎉 所有測試通過！")
        return True
    else:
        logger.error("⚠️ 部分測試失敗")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)