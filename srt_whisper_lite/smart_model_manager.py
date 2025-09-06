#!/usr/bin/env python3
"""
智能模型管理器
混合策略：預置基礎模型 + 智能下載 + 備用方案
"""

import os
import sys
import json
import time
import shutil
import logging
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional, Tuple, Dict

logger = logging.getLogger(__name__)


class SmartModelManager:
    """智能模型管理器"""
    
    def __init__(self):
        # 路徑配置
        if hasattr(sys, '_MEIPASS'):  # PyInstaller 環境
            self.app_models_dir = Path(sys._MEIPASS) / "models"
        else:
            self.app_models_dir = Path(__file__).parent / "models"
        
        self.cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        
        # 模型配置
        self.model_config = {
            "base": {
                "size_mb": 142,
                "bundled": True,  # 內建在安裝程式中
                "fallback_priority": 1,
                "description": "快速模型，離線可用"
            },
            "medium": {
                "size_mb": 1500,
                "bundled": True,  # 內建在安裝程式中
                "fallback_priority": 2,
                "description": "推薦模型，離線可用"
            },
            "large": {
                "size_mb": 5800,
                "bundled": False,  # 需要下載
                "fallback_priority": 3,
                "description": "最高精度，需要網路下載"
            }
        }
        
        # 下載源配置
        self.download_sources = [
            "https://huggingface.co/Systran/faster-whisper-{model}",
            # 可以添加備用下載源
        ]
    
    def check_network_connectivity(self) -> bool:
        """檢查網路連接"""
        test_urls = [
            "https://huggingface.co",
            "https://github.com",
            "https://www.google.com"
        ]
        
        for url in test_urls:
            try:
                urllib.request.urlopen(url, timeout=5)
                logger.info(f"網路連接正常: {url}")
                return True
            except:
                continue
        
        logger.warning("網路連接不可用")
        return False
    
    def get_model_availability(self, model_name: str) -> Dict[str, any]:
        """獲取模型可用性狀態"""
        config = self.model_config.get(model_name, {})
        status = {
            "model": model_name,
            "bundled": config.get("bundled", False),
            "cached": False,
            "downloadable": False,
            "available": False,
            "source": None,
            "path": None,
            "fallback_options": []
        }
        
        # 檢查內建模型
        if config.get("bundled"):
            bundled_path = self.app_models_dir / f"whisper-{model_name}-model.zip"
            if bundled_path.exists():
                status["available"] = True
                status["source"] = "bundled"
                status["path"] = str(bundled_path.parent)
                logger.info(f"發現內建模型: {model_name}")
        
        # 檢查緩存模型
        cached_paths = [
            self.cache_dir / f"models--Systran--faster-whisper-{model_name}",
            self.cache_dir / f"models--openai--whisper-{model_name}"
        ]
        
        for cached_path in cached_paths:
            if cached_path.exists():
                status["cached"] = True
                if not status["available"]:  # 優先使用內建
                    status["available"] = True
                    status["source"] = "cached"
                    status["path"] = str(cached_path)
                logger.info(f"發現緩存模型: {model_name} at {cached_path}")
                break
        
        # 檢查下載可能性
        if not status["available"] and self.check_network_connectivity():
            status["downloadable"] = True
            logger.info(f"模型 {model_name} 可通過網路下載")
        
        # 設置備用選項
        if not status["available"]:
            for alt_name, alt_config in self.model_config.items():
                if (alt_name != model_name and 
                    alt_config.get("bundled") and 
                    alt_config.get("fallback_priority", 99) < config.get("fallback_priority", 99)):
                    alt_bundled = self.app_models_dir / f"whisper-{alt_name}-model.zip"
                    if alt_bundled.exists():
                        status["fallback_options"].append({
                            "model": alt_name,
                            "reason": f"自動降級到可用的 {alt_name} 模型"
                        })
        
        return status
    
    def get_best_available_model(self, requested_model: str, progress_callback=None) -> Tuple[bool, str, Optional[str]]:
        """獲取最佳可用模型"""
        try:
            if progress_callback:
                progress_callback(5, f"檢查 {requested_model} 模型...")
            
            status = self.get_model_availability(requested_model)
            
            # 如果請求的模型可用
            if status["available"]:
                if progress_callback:
                    source_msg = {
                        "bundled": "使用內建模型",
                        "cached": "使用緩存模型"
                    }.get(status["source"], "模型已就緒")
                    progress_callback(20, f"{requested_model}: {source_msg}")
                
                return True, requested_model, status["path"]
            
            # 如果可以下載
            if status["downloadable"]:
                if progress_callback:
                    progress_callback(10, f"正在下載 {requested_model} 模型...")
                
                # 讓 faster-whisper 自己處理下載
                logger.info(f"將使用自動下載: {requested_model}")
                return True, requested_model, None  # None 讓 faster-whisper 自動下載
            
            # 使用備用模型
            if status["fallback_options"]:
                fallback = status["fallback_options"][0]
                fallback_model = fallback["model"]
                
                if progress_callback:
                    progress_callback(15, f"降級到 {fallback_model} 模型...")
                
                fallback_status = self.get_model_availability(fallback_model)
                if fallback_status["available"]:
                    logger.warning(f"使用備用模型: {fallback_model} (原因: {fallback['reason']})")
                    return True, fallback_model, fallback_status["path"]
            
            # 完全失敗
            logger.error(f"無法獲取模型 {requested_model}，也無可用備用方案")
            return False, requested_model, None
            
        except Exception as e:
            logger.error(f"獲取模型時發生錯誤: {e}")
            return False, requested_model, None
    
    def get_model_info_for_ui(self) -> Dict[str, Dict]:
        """為UI提供模型資訊"""
        model_info = {}
        
        for model_name, config in self.model_config.items():
            status = self.get_model_availability(model_name)
            
            model_info[model_name] = {
                "name": model_name.capitalize(),
                "size_mb": config["size_mb"],
                "description": config["description"],
                "available": status["available"],
                "source": status["source"],
                "bundled": config["bundled"],
                "downloadable": status["downloadable"],
                "status_text": self._get_status_text(status)
            }
        
        return model_info
    
    def _get_status_text(self, status: Dict) -> str:
        """獲取狀態顯示文字"""
        if status["available"]:
            if status["source"] == "bundled":
                return "✅ 已安裝"
            elif status["source"] == "cached":
                return "💾 已緩存"
            else:
                return "✅ 可用"
        elif status["downloadable"]:
            return "⬇️ 需要下載"
        else:
            return "❌ 不可用"
    
    def cleanup_cache(self, max_age_days: int = 30):
        """清理舊緩存"""
        try:
            if not self.cache_dir.exists():
                return
            
            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 3600
            cleaned_count = 0
            
            for item in self.cache_dir.iterdir():
                if item.is_dir() and "whisper" in item.name.lower():
                    # 檢查目錄修改時間
                    age = current_time - item.stat().st_mtime
                    if age > max_age_seconds:
                        try:
                            shutil.rmtree(item)
                            cleaned_count += 1
                            logger.info(f"清理舊緩存: {item.name}")
                        except Exception as e:
                            logger.warning(f"清理緩存失敗: {item.name}, {e}")
            
            if cleaned_count > 0:
                logger.info(f"清理了 {cleaned_count} 個舊緩存目錄")
                
        except Exception as e:
            logger.error(f"緩存清理失敗: {e}")


def test_smart_manager():
    """測試智能模型管理器"""
    manager = SmartModelManager()
    
    print("=== 智能模型管理器測試 ===")
    
    # 檢查網路連接
    network_ok = manager.check_network_connectivity()
    print(f"網路連接: {'✅ 正常' if network_ok else '❌ 不可用'}")
    
    # 檢查所有模型狀態
    print("\n--- 模型狀態檢查 ---")
    for model_name in ["base", "medium", "large"]:
        status = manager.get_model_availability(model_name)
        print(f"{model_name:6}: {manager._get_status_text(status):12} | 源: {status.get('source', 'none'):8} | 備用: {len(status['fallback_options'])}")
    
    # 測試最佳模型選擇
    print("\n--- 最佳模型選擇測試 ---")
    for model_name in ["base", "medium", "large"]:
        def progress(percent, message):
            print(f"  [{percent:3d}%] {message}")
        
        success, actual_model, path = manager.get_best_available_model(model_name, progress)
        result = f"✅ {actual_model}" if success else "❌ 失敗"
        print(f"{model_name} -> {result}")
    
    # UI 模型資訊
    print("\n--- UI 模型資訊 ---")
    ui_info = manager.get_model_info_for_ui()
    for model, info in ui_info.items():
        print(f"{model}: {info['status_text']} - {info['description']}")


if __name__ == "__main__":
    test_smart_manager()