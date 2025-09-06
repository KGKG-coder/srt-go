#!/usr/bin/env python3
"""
優化模型管理器
支援高壓縮模型的運行時解壓和管理
"""

import os
import sys
import lzma
import json
import time
import shutil
import zipfile
import logging
import tempfile
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class OptimizedModelManager:
    """優化模型管理器"""
    
    def __init__(self):
        # 確定模型路徑
        if hasattr(sys, '_MEIPASS'):  # PyInstaller 打包環境
            self.app_models_dir = Path(sys._MEIPASS) / "models"
        else:
            self.app_models_dir = Path(__file__).parent / "models"
        
        # 運行時模型緩存
        self.runtime_cache = Path.home() / ".srt_go_cache" / "models"
        self.runtime_cache.mkdir(parents=True, exist_ok=True)
        
        # 模型配置
        self.model_config = {
            "base": {
                "compressed_file": "whisper-base-model.zip",
                "target_name": "whisper-base-model.zip",
                "size_mb": 128,
                "compression": "zip"
            },
            "medium": {
                "compressed_file": "whisper-medium-model.zip", 
                "target_name": "whisper-medium-model.zip",
                "size_mb": 539,
                "compression": "zip"
            },
            "large": {
                "compressed_file": "compressed/whisper-large-model_ultra.xz",
                "fallback_file": "whisper-large-model.zip",
                "target_name": "whisper-large-model.zip", 
                "size_mb": 278,  # 壓縮後大小
                "compression": "lzma"
            }
        }
    
    def check_model_availability(self, model_name: str) -> Tuple[bool, str, Optional[Path]]:
        """檢查模型可用性"""
        try:
            config = self.model_config.get(model_name)
            if not config:
                return False, "unsupported_model", None
            
            # 檢查運行時緩存
            cached_model = self.runtime_cache / config["target_name"]
            if cached_model.exists() and cached_model.stat().st_size > 1024 * 1024:  # > 1MB
                logger.info(f"發現緩存模型: {model_name}")
                return True, "cached", cached_model
            
            # 檢查應用程式內建模型
            app_model = self.app_models_dir / config["compressed_file"]
            fallback_model = self.app_models_dir / config.get("fallback_file", "")
            
            if app_model.exists():
                return True, "app_compressed", app_model
            elif fallback_model.exists():
                return True, "app_fallback", fallback_model
            
            return False, "not_found", None
            
        except Exception as e:
            logger.error(f"檢查模型可用性失敗: {e}")
            return False, "error", None
    
    def prepare_model(self, model_name: str, progress_callback=None) -> Tuple[bool, Optional[Path]]:
        """準備模型（解壓、緩存等）"""
        try:
            available, source, source_path = self.check_model_availability(model_name)
            
            if not available:
                logger.error(f"模型 {model_name} 不可用: {source}")
                return False, None
            
            config = self.model_config[model_name]
            target_path = self.runtime_cache / config["target_name"]
            
            # 如果已經緩存且有效，直接使用
            if source == "cached":
                logger.info(f"使用緩存模型: {model_name}")
                return True, target_path
            
            if progress_callback:
                progress_callback(10, f"準備 {model_name} 模型...")
            
            # 需要解壓或複製
            if source == "app_compressed" and config["compression"] == "lzma":
                success = self._decompress_lzma_model(source_path, target_path, progress_callback)
            elif source == "app_compressed" and config["compression"] == "zip":
                success = self._copy_model(source_path, target_path, progress_callback)
            elif source == "app_fallback":
                success = self._copy_model(source_path, target_path, progress_callback)
            else:
                logger.error(f"未知的模型源類型: {source}")
                return False, None
            
            if success:
                logger.info(f"模型 {model_name} 準備完成: {target_path}")
                return True, target_path
            else:
                logger.error(f"模型 {model_name} 準備失敗")
                return False, None
                
        except Exception as e:
            logger.error(f"準備模型失敗: {e}")
            return False, None
    
    def _decompress_lzma_model(self, compressed_path: Path, target_path: Path, progress_callback=None) -> bool:
        """解壓 LZMA 格式的模型"""
        try:
            logger.info(f"解壓 LZMA 模型: {compressed_path} -> {target_path}")
            
            if progress_callback:
                progress_callback(30, "正在解壓 LZMA 模型...")
            
            # 分塊解壓以顯示進度
            with lzma.LZMAFile(compressed_path, 'rb') as f_in:
                with open(target_path, 'wb') as f_out:
                    total_size = compressed_path.stat().st_size
                    processed = 0
                    chunk_size = 8192 * 1024  # 8MB chunks
                    
                    while True:
                        chunk = f_in.read(chunk_size)
                        if not chunk:
                            break
                        
                        f_out.write(chunk)
                        processed += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = 30 + int((processed / total_size) * 50)
                            progress_callback(progress, f"解壓中... {processed//1024//1024}MB")
            
            if progress_callback:
                progress_callback(85, "解壓完成，正在驗證...")
            
            # 驗證解壓結果
            if not target_path.exists() or target_path.stat().st_size < 1024 * 1024:
                logger.error(f"解壓後文件無效: {target_path}")
                return False
            
            logger.info(f"LZMA 解壓成功: {target_path.stat().st_size / 1024 / 1024:.1f}MB")
            return True
            
        except Exception as e:
            logger.error(f"LZMA 解壓失敗: {e}")
            return False
    
    def _copy_model(self, source_path: Path, target_path: Path, progress_callback=None) -> bool:
        """複製模型文件"""
        try:
            logger.info(f"複製模型: {source_path} -> {target_path}")
            
            if progress_callback:
                progress_callback(50, "正在複製模型文件...")
            
            shutil.copy2(source_path, target_path)
            
            if progress_callback:
                progress_callback(90, "模型文件複製完成")
            
            return True
            
        except Exception as e:
            logger.error(f"模型複製失敗: {e}")
            return False
    
    def get_model_path(self, model_name: str, progress_callback=None) -> Optional[str]:
        """獲取模型路徑（自動準備）"""
        try:
            success, model_path = self.prepare_model(model_name, progress_callback)
            
            if success and model_path:
                return str(model_path.parent)  # 返回模型目錄
            else:
                # 嘗試使用標準路徑讓 faster-whisper 自動下載
                logger.warning(f"模型 {model_name} 準備失敗，使用標準名稱")
                return model_name
                
        except Exception as e:
            logger.error(f"獲取模型路徑失敗: {e}")
            return model_name
    
    def cleanup_old_cache(self, max_age_days: int = 7):
        """清理舊的模型緩存"""
        try:
            if not self.runtime_cache.exists():
                return
            
            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 3600
            
            for model_file in self.runtime_cache.iterdir():
                if model_file.is_file():
                    age = current_time - model_file.stat().st_mtime
                    if age > max_age_seconds:
                        logger.info(f"清理舊緩存: {model_file.name}")
                        model_file.unlink()
                        
        except Exception as e:
            logger.error(f"清理緩存失敗: {e}")
    
    def get_cache_status(self) -> dict:
        """獲取緩存狀態"""
        status = {
            "cache_dir": str(self.runtime_cache),
            "cache_size_mb": 0,
            "models": {}
        }
        
        try:
            # 計算緩存大小
            total_size = 0
            if self.runtime_cache.exists():
                for file_path in self.runtime_cache.rglob('*'):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                        
            status["cache_size_mb"] = total_size / 1024 / 1024
            
            # 檢查各模型狀態
            for model_name in self.model_config.keys():
                available, source, path = self.check_model_availability(model_name)
                status["models"][model_name] = {
                    "available": available,
                    "source": source,
                    "path": str(path) if path else None
                }
                
        except Exception as e:
            logger.error(f"獲取緩存狀態失敗: {e}")
            
        return status


def test_optimized_manager():
    """測試優化模型管理器"""
    manager = OptimizedModelManager()
    
    print("=== 優化模型管理器測試 ===")
    
    # 檢查緩存狀態
    status = manager.get_cache_status()
    print(f"緩存目錄: {status['cache_dir']}")
    print(f"緩存大小: {status['cache_size_mb']:.1f}MB")
    
    # 測試各模型
    for model_name in ["base", "medium", "large"]:
        print(f"\n--- 測試 {model_name} 模型 ---")
        
        def progress_callback(percent, message):
            print(f"[{percent:3d}%] {message}")
        
        success, path = manager.prepare_model(model_name, progress_callback)
        print(f"準備結果: {'成功' if success else '失敗'}")
        if path:
            print(f"模型路徑: {path}")
            print(f"文件大小: {path.stat().st_size / 1024 / 1024:.1f}MB")


if __name__ == "__main__":
    test_optimized_manager()