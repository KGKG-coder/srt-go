#!/usr/bin/env python3
"""
修正的 Large V3 Turbo 模型管理器
解決模型大小不符和缺失檔案問題
"""

import os
import logging
import time
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)

class CorrectedLargeV3TurboManager:
    """修正的 Large V3 Turbo 模型管理器"""
    
    def __init__(self):
        # 修正的模型優先順序
        self.model_candidates = [
            {
                "name": "distil-whisper/distil-large-v3",
                "description": "Official Distilled Large V3",
                "expected_size_mb": 756,
                "model_bin_size_mb": 700,  # model.bin 應該約 700MB
                "speed_boost": "6x faster",
                "accuracy": "97% of original",
                "priority": 1
            },
            {
                "name": "Systran/faster-distil-whisper-large-v3", 
                "description": "Systran Distilled Version",
                "expected_size_mb": 800,
                "model_bin_size_mb": 750,
                "speed_boost": "5x faster", 
                "accuracy": "96% of original",
                "priority": 2
            },
            {
                "name": "Systran/faster-whisper-large-v3",
                "description": "Standard Large V3 (Fallback)",
                "expected_size_mb": 3100,
                "model_bin_size_mb": 2900,
                "speed_boost": "4x faster",
                "accuracy": "99.5% of original", 
                "priority": 3
            }
        ]
        
        # 路徑設定
        self.cache_base = Path.home() / ".cache" / "huggingface" / "hub"
        self.current_model = None
        self.model_status = "not_checked"
        
    def check_available_models(self) -> Dict[str, Dict]:
        """檢查所有可用的模型"""
        available_models = {}
        
        for candidate in self.model_candidates:
            model_name = candidate["name"]
            cache_dir_name = f"models--{model_name.replace('/', '--')}"
            cache_path = self.cache_base / cache_dir_name
            
            status = self._validate_model_cache(cache_path, candidate)
            available_models[model_name] = {
                **candidate,
                "cache_path": cache_path,
                "status": status["status"],
                "actual_size_mb": status["actual_size_mb"],
                "missing_files": status["missing_files"],
                "usable": status["usable"]
            }
            
        return available_models
    
    def _validate_model_cache(self, cache_path: Path, candidate: Dict) -> Dict:
        """驗證模型快取的完整性"""
        if not cache_path.exists():
            return {
                "status": "not_downloaded",
                "actual_size_mb": 0,
                "missing_files": ["entire_model"],
                "usable": False
            }
        
        # 尋找 snapshots 目錄
        snapshots_dir = cache_path / "snapshots"
        if not snapshots_dir.exists():
            return {
                "status": "incomplete_download",
                "actual_size_mb": 0,
                "missing_files": ["snapshots"],
                "usable": False
            }
        
        # 檢查最新的 snapshot
        snapshot_dirs = [d for d in snapshots_dir.iterdir() if d.is_dir()]
        if not snapshot_dirs:
            return {
                "status": "no_snapshots",
                "actual_size_mb": 0,
                "missing_files": ["snapshot_data"],
                "usable": False
            }
        
        # 使用最新的 snapshot
        latest_snapshot = max(snapshot_dirs, key=lambda d: d.stat().st_mtime)
        
        # 檢查必要檔案
        required_files = ["config.json", "model.bin", "tokenizer.json"]
        missing_files = []
        actual_size_bytes = 0
        
        for req_file in required_files:
            file_path = latest_snapshot / req_file
            if file_path.exists():
                actual_size_bytes += file_path.stat().st_size
            else:
                missing_files.append(req_file)
        
        actual_size_mb = actual_size_bytes / (1024 * 1024)
        expected_size_mb = candidate["expected_size_mb"]
        
        # 判斷狀態
        if missing_files:
            if "model.bin" in missing_files:
                status = "missing_model_bin"
            else:
                status = "missing_config_files"
            usable = False
        elif actual_size_mb < expected_size_mb * 0.8:  # 允許 20% 誤差
            status = "size_mismatch" 
            usable = False
        else:
            status = "complete"
            usable = True
            
        return {
            "status": status,
            "actual_size_mb": round(actual_size_mb, 1),
            "missing_files": missing_files,
            "usable": usable,
            "snapshot_path": latest_snapshot
        }
    
    def get_best_available_model(self) -> Tuple[str, Dict]:
        """獲取最佳可用模型"""
        available_models = self.check_available_models()
        
        # 按優先順序排序並尋找可用的模型
        sorted_models = sorted(
            available_models.items(),
            key=lambda item: item[1]["priority"]
        )
        
        for model_name, model_info in sorted_models:
            if model_info["usable"]:
                logger.info(f"✅ 選擇模型: {model_name} ({model_info['actual_size_mb']}MB)")
                return model_name, model_info
        
        # 如果沒有完全可用的模型，回報狀況
        logger.warning("⚠️ 沒有完全可用的模型，分析問題:")
        for model_name, model_info in sorted_models:
            logger.warning(f"  {model_name}: {model_info['status']} (缺失: {model_info['missing_files']})")
        
        # 返回最高優先級的模型（即使不完整）
        fallback_name, fallback_info = sorted_models[0]
        logger.info(f"🔄 使用後備模型: {fallback_name}")
        return fallback_name, fallback_info
    
    def ensure_model_ready(self) -> Tuple[bool, str, Dict]:
        """確保模型準備就緒"""
        model_name, model_info = self.get_best_available_model()
        
        if model_info["usable"]:
            # 轉換為 faster-whisper 可識別的名稱
            whisper_model_name = self._convert_to_whisper_name(model_name)
            return True, whisper_model_name, model_info
        else:
            # 模型不可用，需要處理
            return False, model_name, model_info
    
    def _convert_to_whisper_name(self, hf_model_name: str) -> str:
        """將 HuggingFace 模型名稱轉換為 faster-whisper 識別的名稱"""
        name_mapping = {
            "distil-whisper/distil-large-v3": "distil-large-v3",
            "Systran/faster-distil-whisper-large-v3": "distil-large-v3",  # 也使用 distil 名稱
            "Systran/faster-whisper-large-v3": "large-v3"
        }
        return name_mapping.get(hf_model_name, "large-v3")
    
    def get_model_info(self) -> Dict[str, Any]:
        """獲取模型詳細信息"""
        success, model_name, model_info = self.ensure_model_ready()
        
        return {
            "success": success,
            "model_name": model_name,
            "status": model_info["status"],
            "actual_size": f"{model_info['actual_size_mb']} MB",
            "expected_size": f"{model_info['expected_size_mb']} MB",
            "missing_files": model_info["missing_files"],
            "usable": model_info["usable"],
            "description": model_info["description"],
            "performance": model_info["speed_boost"],
            "accuracy": model_info["accuracy"]
        }
    
    def get_whisper_model_params(self) -> Dict[str, Any]:
        """獲取 faster-whisper 模型參數"""
        success, model_name, model_info = self.ensure_model_ready()
        
        if not success:
            logger.warning(f"模型不完整，使用標準 large-v3 作為後備")
            model_name = "large-v3"
        
        # 優化的參數配置
        params = {
            "model_size_or_path": model_name,
            "device": "cuda" if self._check_cuda_available() else "cpu",
            "compute_type": "float16" if self._check_cuda_available() else "int8",
            "num_workers": 1
        }
        
        if params["device"] == "cuda":
            params["device_index"] = 0
        
        return params
    
    def _check_cuda_available(self) -> bool:
        """檢查 CUDA 是否可用"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def download_missing_model(self, model_name: str) -> bool:
        """下載缺失的模型"""
        try:
            from huggingface_hub import snapshot_download
            
            logger.info(f"開始下載模型: {model_name}")
            
            # 下載到快取目錄
            local_dir = snapshot_download(
                repo_id=model_name,
                cache_dir=self.cache_base.parent,
                resume_download=True
            )
            
            logger.info(f"✅ 模型下載完成: {local_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 模型下載失敗: {e}")
            return False
    
    def fix_incomplete_models(self) -> Dict[str, bool]:
        """修復不完整的模型"""
        available_models = self.check_available_models()
        results = {}
        
        for model_name, model_info in available_models.items():
            if not model_info["usable"] and model_info["status"] != "not_downloaded":
                logger.info(f"嘗試修復模型: {model_name}")
                results[model_name] = self.download_missing_model(model_name)
            else:
                results[model_name] = model_info["usable"]
        
        return results

def get_corrected_turbo_manager() -> CorrectedLargeV3TurboManager:
    """便利函數：獲取修正的 Turbo 模型管理器"""
    return CorrectedLargeV3TurboManager()

if __name__ == "__main__":
    # 測試修正的管理器
    manager = CorrectedLargeV3TurboManager()
    
    print("=== 修正的 Large V3 Turbo 管理器測試 ===")
    print()
    
    # 檢查可用模型
    print("檢查可用模型:")
    available = manager.check_available_models()
    for name, info in available.items():
        status_icon = "✅" if info["usable"] else "❌"
        print(f"  {status_icon} {name}: {info['status']} ({info['actual_size_mb']}MB)")
        if info["missing_files"]:
            print(f"      缺失檔案: {info['missing_files']}")
    
    print()
    print("最佳模型選擇:")
    model_info = manager.get_model_info()
    for key, value in model_info.items():
        print(f"  {key}: {value}")
    
    print()
    print("Whisper 參數:")
    params = manager.get_whisper_model_params()
    for key, value in params.items():
        print(f"  {key}: {value}")