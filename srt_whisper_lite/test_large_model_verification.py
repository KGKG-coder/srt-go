#!/usr/bin/env python3
"""
驗證 LARGE-v3 模型是否真正被使用
"""

import sys
import logging
from pathlib import Path

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_direct_model_load():
    """直接測試模型載入"""
    logger.info("=" * 60)
    logger.info("開始驗證 LARGE 模型載入")
    logger.info("=" * 60)
    
    try:
        from faster_whisper import WhisperModel
        
        # 強制使用 large-v3
        logger.info("嘗試載入 large-v3 模型...")
        model = WhisperModel(
            "large-v3",
            device="cpu",
            compute_type="int8"
        )
        
        logger.info("✅ 成功載入 large-v3 模型！")
        logger.info(f"模型類型: {type(model)}")
        
        # 測試模型信息
        logger.info("檢查模型屬性...")
        if hasattr(model, 'model'):
            logger.info(f"內部模型: {type(model.model)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 載入 large-v3 失敗: {e}")
        
        # 嘗試 large-v2
        try:
            logger.info("嘗試載入 large-v2 模型...")
            model = WhisperModel(
                "large-v2",
                device="cpu",
                compute_type="int8"
            )
            logger.info("✅ 成功載入 large-v2 模型")
            return True
        except Exception as e2:
            logger.error(f"❌ 載入 large-v2 也失敗: {e2}")
            
        # 嘗試 large
        try:
            logger.info("嘗試載入 large 模型...")
            model = WhisperModel(
                "large",
                device="cpu",
                compute_type="int8"
            )
            logger.info("✅ 成功載入 large 模型")
            return True
        except Exception as e3:
            logger.error(f"❌ 載入 large 也失敗: {e3}")
            
    return False

def check_model_manager():
    """檢查模型管理器狀態"""
    logger.info("\n" + "=" * 60)
    logger.info("檢查 LARGE 模型管理器")
    logger.info("=" * 60)
    
    try:
        from large_only_model_manager import LargeOnlyModelManager
        
        manager = LargeOnlyModelManager()
        available, source, path = manager.check_model_availability()
        
        logger.info(f"模型可用: {available}")
        logger.info(f"模型來源: {source}")
        logger.info(f"模型路徑: {path}")
        
        # 獲取模型路徑
        success, model_path = manager.get_model_path()
        logger.info(f"獲取模型成功: {success}")
        logger.info(f"模型路徑: {model_path}")
        
        return available
        
    except Exception as e:
        logger.error(f"檢查模型管理器失敗: {e}")
        return False

def check_simplified_core():
    """檢查 SimplifiedSubtitleCore 的實際行為"""
    logger.info("\n" + "=" * 60)
    logger.info("檢查 SimplifiedSubtitleCore")
    logger.info("=" * 60)
    
    try:
        from simplified_subtitle_core import SimplifiedSubtitleCore
        
        # 創建實例，明確指定 large
        logger.info("創建 SimplifiedSubtitleCore 實例（指定 large）...")
        core = SimplifiedSubtitleCore(
            model_size="large",
            device="cpu"
        )
        
        logger.info("✅ 成功創建實例")
        
        # 檢查實際載入的模型
        if hasattr(core, 'model'):
            logger.info(f"實際載入的模型: {type(core.model)}")
            if hasattr(core, 'model_size'):
                logger.info(f"模型大小: {core.model_size}")
        
        return True
        
    except Exception as e:
        logger.error(f"創建 SimplifiedSubtitleCore 失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    logger.info("開始 LARGE 模型驗證測試")
    logger.info("Python 版本: " + sys.version)
    
    # 1. 直接測試模型載入
    direct_success = test_direct_model_load()
    
    # 2. 檢查模型管理器
    manager_success = check_model_manager()
    
    # 3. 檢查實際使用的核心
    core_success = check_simplified_core()
    
    # 總結
    logger.info("\n" + "=" * 60)
    logger.info("測試總結")
    logger.info("=" * 60)
    logger.info(f"直接載入測試: {'✅ 成功' if direct_success else '❌ 失敗'}")
    logger.info(f"模型管理器測試: {'✅ 成功' if manager_success else '❌ 失敗'}")
    logger.info(f"核心模組測試: {'✅ 成功' if core_success else '❌ 失敗'}")
    
    if direct_success and manager_success and core_success:
        logger.info("\n🎉 所有測試通過！LARGE 模型可用")
    else:
        logger.warning("\n⚠️ 部分測試失敗，需要檢查配置")

if __name__ == "__main__":
    main()