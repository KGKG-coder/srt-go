#!/usr/bin/env python3
"""
LARGE 專用模型管理器
簡化版本，只處理 LARGE 模型
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class LargeOnlyModelManager:
    """LARGE 專用模型管理器"""
    
    def __init__(self):
        # 路徑配置
        if hasattr(sys, '_MEIPASS'):  # PyInstaller 環境
            self.app_models_dir = Path(sys._MEIPASS) / "models"
        else:
            self.app_models_dir = Path(__file__).parent / "models"
        
        self.cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        
        # 只有 LARGE 模型配置
        self.model_name = "large"
        self.model_file = "whisper-large-model.zip"
        
    def check_model_availability(self) -> Tuple[bool, str, Optional[Path]]:
        """檢查 LARGE 模型可用性"""
        try:
            # 優先檢查內建模型 - LARGE 專用版優先使用 bundled
            bundled_path = self.app_models_dir / self.model_file
            if bundled_path.exists():
                logger.info(f"發現內建 LARGE 模型: {bundled_path}")
                return True, "bundled", bundled_path.parent
            
            # 檢查緩存模型 - 只有在 bundled 不存在時才使用
            cached_paths = [
                self.cache_dir / "models--Systran--faster-whisper-large-v3",
                self.cache_dir / "models--Systran--faster-whisper-large",
                self.cache_dir / "models--openai--whisper-large"
            ]
            
            for cached_path in cached_paths:
                if cached_path.exists() and (cached_path / "model.bin").exists():
                    logger.info(f"發現有效緩存 LARGE 模型: {cached_path}")
                    return True, "cached", cached_path
            
            # 模型不可用
            logger.warning("LARGE 模型未找到，將嘗試載入")
            return False, "not_found", None
            
        except Exception as e:
            logger.error(f"檢查模型時發生錯誤: {e}")
            return False, "error", None
    
    def get_model_path(self, progress_callback=None) -> Tuple[bool, Optional[str]]:
        """獲取 LARGE 模型路徑"""
        try:
            if progress_callback:
                progress_callback(5, "檢查 LARGE 模型...")
            
            available, source, path = self.check_model_availability()
            
            if available and source == "bundled":
                # 處理 bundled zip 模型
                if progress_callback:
                    progress_callback(10, "正在解壓縮內建 LARGE 模型...")
                
                extracted_path = self._extract_bundled_model(progress_callback)
                if extracted_path:
                    if progress_callback:
                        progress_callback(20, "內建 LARGE 模型解壓完成")
                    return True, str(extracted_path)
                else:
                    logger.warning("內建模型解壓失敗，嘗試其他選項")
            
            if available and source == "cached":
                if progress_callback:
                    progress_callback(20, "使用緩存 LARGE 模型")
                return True, str(path)
            
            # 模型不可用，讓 faster-whisper 使用模型名稱處理
            if progress_callback:
                progress_callback(10, "正在載入 LARGE 模型...")
            
            logger.info("LARGE 模型將由系統處理")
            return True, "large"  # 返回模型名稱，讓 faster-whisper 處理
            
        except Exception as e:
            logger.error(f"獲取 LARGE 模型時發生錯誤: {e}")
            return False, None
    
    def _extract_bundled_model(self, progress_callback=None) -> Optional[Path]:
        """解壓縮內建模型"""
        try:
            import zipfile
            import tempfile
            
            bundled_zip = self.app_models_dir / self.model_file
            if not bundled_zip.exists():
                return None
            
            # 創建臨時解壓目錄
            temp_dir = Path(tempfile.gettempdir()) / "srtgo_large_model"
            temp_dir.mkdir(exist_ok=True)
            
            # 檢查是否已經解壓
            if (temp_dir / "model.bin").exists():
                logger.info(f"發現已解壓的 LARGE 模型: {temp_dir}")
                return temp_dir
            
            if progress_callback:
                progress_callback(15, "正在解壓縮模型文件...")
            
            # 解壓縮模型文件
            with zipfile.ZipFile(bundled_zip, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # 驗證解壓結果
            if (temp_dir / "model.bin").exists():
                logger.info(f"LARGE 模型解壓成功: {temp_dir}")
                return temp_dir
            else:
                logger.error("模型解壓後找不到 model.bin 文件")
                return None
                
        except Exception as e:
            logger.error(f"解壓縮內建模型失敗: {e}")
            return None
    
    def get_model_info(self) -> dict:
        """獲取模型資訊"""
        available, source, _ = self.check_model_availability()
        
        return {
            "name": "Large",
            "size_mb": 1550,
            "description": "最高準確度 - 專業版",
            "available": available,
            "source": source,
            "status_text": self._get_status_text(available, source)
        }
    
    def _get_status_text(self, available: bool, source: str) -> str:
        """獲取狀態文字"""
        if available:
            if source == "bundled":
                return "已安裝"
            elif source == "cached":
                return "已緩存"
            else:
                return "可用"
        else:
            return "需要下載"


def test_large_only_manager():
    """測試 LARGE 專用管理器"""
    manager = LargeOnlyModelManager()
    
    print("=== LARGE 專用模型管理器測試 ===")
    
    # 檢查模型狀態
    info = manager.get_model_info()
    print(f"模型: {info['name']}")
    print(f"大小: {info['size_mb']}MB")
    print(f"狀態: {info['status_text']}")
    print(f"描述: {info['description']}")
    
    # 測試獲取模型路徑
    def progress(percent, message):
        print(f"[{percent:3d}%] {message}")
    
    success, path = manager.get_model_path(progress)
    if success:
        print(f"✅ 模型路徑: {path}")
    else:
        print("❌ 無法獲取模型")


if __name__ == "__main__":
    test_large_only_manager()