#!/usr/bin/env python3
"""
最終版 Large V3 Turbo Float16 模型管理器
使用經過 CTranslate2 轉換的真正 Turbo 模型
支援多個來源，確保獲得真正的 Float16 Turbo 性能
"""

import os
import logging
import time
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class FinalLargeV3TurboFloat16Manager:
    """最終版 Large V3 Turbo Float16 模型管理器"""
    
    def __init__(self):
        # 可用的 CTranslate2 格式 Turbo 模型（按優先順序）
        self.turbo_model_candidates = [
            {
                "repo": "deepdml/faster-whisper-large-v3-turbo-ct2",
                "name": "DeepDML Large V3 Turbo CT2",
                "description": "CTranslate2 格式的官方轉換版",
                "expected_size_gb": 1.5,
                "precision": "float16",
                "speed_boost": "8x faster",
                "accuracy": "Similar to large-v2",
                "priority": 1
            },
            {
                "repo": "mobiuslabsgmbh/faster-whisper-large-v3-turbo",
                "name": "Mobius Labs Large V3 Turbo",
                "description": "Mobius Labs 優化版本",
                "expected_size_gb": 1.6,
                "precision": "float16",
                "speed_boost": "7x faster", 
                "accuracy": "Similar to large-v2",
                "priority": 2
            },
            {
                "repo": "h2oai/faster-whisper-large-v3-turbo",
                "name": "H2O.ai Large V3 Turbo",
                "description": "H2O.ai 轉換版本",
                "expected_size_gb": 1.5,
                "precision": "float16",
                "speed_boost": "8x faster",
                "accuracy": "Similar to large-v2", 
                "priority": 3
            },
            {
                "repo": "Infomaniak-AI/faster-whisper-large-v3-turbo",
                "name": "Infomaniak AI Large V3 Turbo",
                "description": "Infomaniak AI 轉換版本",
                "expected_size_gb": 1.6,
                "precision": "float16",
                "speed_boost": "7x faster",
                "accuracy": "Similar to large-v2",
                "priority": 4
            }
        ]
        
        # 後備選項：Distil 模型（如果 Turbo 不可用）
        self.fallback_models = [
            {
                "repo": "distil-whisper/distil-large-v3",
                "name": "Distil Large V3",
                "description": "蒸餾版本（後備）",
                "expected_size_gb": 0.8,
                "precision": "float16",
                "speed_boost": "6x faster",
                "accuracy": "97% of original",
                "priority": 5
            }
        ]
        
        # 模型配置
        self.model_name = "large-v3-turbo-float16"
        self.selected_model = None
        self.model_status = "not_checked"
        
        # 路徑設定
        self.cache_base = Path.home() / ".cache" / "huggingface" / "hub"
        
        logger.info(f"最終版 Large V3 Turbo Float16 模型管理器初始化")
        logger.info(f"可用候選模型: {len(self.turbo_model_candidates)} 個")
    
    def get_model_info(self) -> Dict[str, Any]:
        """獲取模型信息"""
        available, selected_model = self.check_model_availability()
        
        if available and selected_model:
            return {
                "name": selected_model["name"],
                "repository": selected_model["repo"],
                "variant": "Float16 Turbo 真正版",
                "available": True,
                "status_text": "已安裝並可用",
                "expected_size": f"{selected_model['expected_size_gb']} GB",
                "actual_size": self._get_model_actual_size(selected_model["repo"]),
                "precision": selected_model["precision"],
                "performance": selected_model["speed_boost"],
                "accuracy": selected_model["accuracy"],
                "description": selected_model["description"],
                "model_type": "CTranslate2 Turbo",
                "compute_type": "float16",
                "device": "cuda/cpu",
                "priority": selected_model["priority"]
            }
        else:
            return {
                "name": "Large V3 Turbo Float16",
                "repository": "未選定",
                "variant": "Float16 Turbo",
                "available": False,
                "status_text": "需要下載",
                "expected_size": "~1.5 GB",
                "actual_size": "0 MB",
                "precision": "float16",
                "performance": "8x faster",
                "accuracy": "Similar to large-v2",
                "description": "正在選擇最佳可用模型",
                "model_type": "CTranslate2 Turbo",
                "compute_type": "float16",
                "device": "cuda/cpu",
                "priority": "待定"
            }
    
    def check_model_availability(self) -> Tuple[bool, Optional[Dict]]:
        """檢查模型可用性並選擇最佳模型"""
        if self.selected_model and self.model_status == "available":
            return True, self.selected_model
        
        logger.info("檢查可用的 Turbo 模型...")
        
        # 檢查所有候選模型
        all_candidates = self.turbo_model_candidates + self.fallback_models
        sorted_candidates = sorted(all_candidates, key=lambda x: x["priority"])
        
        for candidate in sorted_candidates:
            if self._is_model_downloaded(candidate["repo"]):
                logger.info(f"✅ 找到可用模型: {candidate['name']}")
                self.selected_model = candidate
                self.model_status = "available"
                return True, candidate
        
        logger.info("❌ 沒有找到可用的 Turbo 模型")
        self.model_status = "not_available"
        return False, None
    
    def _is_model_downloaded(self, repo: str) -> bool:
        """檢查模型是否已下載並完整"""
        cache_name = f"models--{repo.replace('/', '--')}"
        cache_path = self.cache_base / cache_name
        
        if not cache_path.exists():
            return False
        
        # 檢查 snapshots
        snapshots_dir = cache_path / "snapshots"
        if not snapshots_dir.exists():
            return False
        
        # 檢查最新 snapshot 中的關鍵文件
        for snapshot_dir in snapshots_dir.iterdir():
            if snapshot_dir.is_dir():
                required_files = ["model.bin", "config.json"]
                
                all_present = True
                for req_file in required_files:
                    file_path = snapshot_dir / req_file
                    if not file_path.exists():
                        all_present = False
                        break
                    
                    # 檢查 model.bin 大小（Turbo 應該較小）
                    if req_file == "model.bin":
                        size_gb = file_path.stat().st_size / (1024**3)
                        if size_gb > 2.5:  # 太大，可能是標準版
                            logger.warning(f"模型 {repo} 大小異常: {size_gb:.2f}GB")
                            all_present = False
                
                return all_present
        
        return False
    
    def _get_model_actual_size(self, repo: str) -> str:
        """獲取模型實際大小"""
        try:
            cache_name = f"models--{repo.replace('/', '--')}"
            cache_path = self.cache_base / cache_name / "snapshots"
            
            if cache_path.exists():
                for snapshot_dir in cache_path.iterdir():
                    if snapshot_dir.is_dir():
                        total_size = sum(f.stat().st_size for f in snapshot_dir.rglob('*') if f.is_file())
                        size_gb = total_size / (1024**3)
                        return f"{size_gb:.2f} GB"
        except Exception:
            pass
        
        return "未知大小"
    
    def ensure_model_ready(self) -> Tuple[bool, str]:
        """確保模型準備就緒"""
        available, selected_model = self.check_model_availability()
        
        if available and selected_model:
            logger.info(f"使用 Large V3 Turbo 模型: {selected_model['name']}")
            return True, selected_model["repo"]
        
        # 嘗試下載第一個候選模型
        first_candidate = self.turbo_model_candidates[0]
        logger.info(f"開始下載推薦模型: {first_candidate['name']}")
        
        success = self._download_model(first_candidate["repo"])
        if success:
            self.selected_model = first_candidate
            self.model_status = "available"
            return True, first_candidate["repo"]
        else:
            logger.error("模型下載失敗")
            return False, ""
    
    def _download_model(self, repo: str) -> bool:
        """下載指定模型"""
        try:
            from faster_whisper import WhisperModel
            
            logger.info(f"正在下載模型: {repo}")
            logger.info("這可能需要幾分鐘時間...")
            
            # 使用 faster-whisper 自動下載機制
            model = WhisperModel(repo, device="cpu", compute_type="int8")
            
            logger.info(f"✅ 模型 {repo} 下載完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 模型 {repo} 下載失敗: {e}")
            return False
    
    def get_whisper_model_params(self) -> Dict[str, Any]:
        """獲取 Whisper 模型參數"""
        success, model_repo = self.ensure_model_ready()
        
        if not success:
            raise RuntimeError("Large V3 Turbo 模型不可用")
        
        # 設備檢測
        device = "cuda" if self._check_cuda_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        
        return {
            "model_size_or_path": model_repo,
            "device": device,
            "compute_type": compute_type,
            "num_workers": 1,
            "device_index": 0 if device == "cuda" else None
        }
    
    def _check_cuda_available(self) -> bool:
        """檢查 CUDA 是否可用"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def get_size_comparison(self) -> Dict[str, str]:
        """獲取大小對比信息"""
        return {
            "Standard Large V3": "3.1 GB (32 decoder layers)",
            "Large V3 Turbo (Real)": "1.5 GB (4 decoder layers)",
            "Size Reduction": "52% smaller",
            "Parameter Count": "809M (vs 1550M standard)",
            "Speed Improvement": "6-8x faster",
            "Accuracy": "Similar to large-v2 (minimal loss)",
            "GPU Memory Saving": "~1.6 GB saved",
            "Precision": "Float16 for optimal GPU performance",
            "Format": "CTranslate2 optimized"
        }
    
    def test_model_performance(self) -> Dict[str, Any]:
        """測試模型性能"""
        try:
            success, model_repo = self.ensure_model_ready()
            if not success:
                return {"error": "模型不可用"}
            
            from faster_whisper import WhisperModel
            
            logger.info("開始性能測試...")
            start_time = time.time()
            
            # 載入模型
            params = self.get_whisper_model_params()
            model = WhisperModel(**params)
            
            load_time = time.time() - start_time
            
            # 檢查模型屬性
            result = {
                "model_repo": model_repo,
                "load_time": f"{load_time:.2f} seconds",
                "device": params["device"],
                "compute_type": params["compute_type"],
                "model_loaded": True,
                "memory_efficient": params["device"] == "cuda" and params["compute_type"] == "float16",
                "status": "SUCCESS"
            }
            
            logger.info(f"✅ 性能測試完成: {load_time:.2f}s 載入時間")
            return result
            
        except Exception as e:
            logger.error(f"❌ 性能測試失敗: {e}")
            return {"error": str(e), "status": "FAILED"}
    
    def get_model_candidates_status(self) -> List[Dict]:
        """獲取所有候選模型狀態"""
        candidates_status = []
        
        all_candidates = self.turbo_model_candidates + self.fallback_models
        
        for candidate in all_candidates:
            is_downloaded = self._is_model_downloaded(candidate["repo"])
            actual_size = self._get_model_actual_size(candidate["repo"]) if is_downloaded else "未下載"
            
            status = {
                "name": candidate["name"],
                "repo": candidate["repo"],
                "priority": candidate["priority"],
                "expected_size": f"{candidate['expected_size_gb']} GB",
                "actual_size": actual_size,
                "available": is_downloaded,
                "performance": candidate["speed_boost"],
                "accuracy": candidate["accuracy"],
                "description": candidate["description"]
            }
            
            candidates_status.append(status)
        
        return sorted(candidates_status, key=lambda x: x["priority"])


def get_final_turbo_manager() -> FinalLargeV3TurboFloat16Manager:
    """便利函數：獲取最終版 Turbo 模型管理器實例"""
    return FinalLargeV3TurboFloat16Manager()


if __name__ == "__main__":
    # 測試最終版管理器
    manager = FinalLargeV3TurboFloat16Manager()
    
    print("=== 最終版 Large V3 Turbo Float16 管理器測試 ===")
    print()
    
    # 檢查候選模型狀態
    print("候選模型狀態:")
    candidates = manager.get_model_candidates_status()
    for candidate in candidates:
        status_icon = "✅" if candidate["available"] else "❌"
        print(f"  {status_icon} {candidate['name']}")
        print(f"     倉庫: {candidate['repo']}")
        print(f"     大小: {candidate['actual_size']} (預期: {candidate['expected_size']})")
        print(f"     性能: {candidate['performance']}")
        print()
    
    # 獲取模型信息
    print("當前模型信息:")
    info = manager.get_model_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print()
    print("大小對比:")
    comparison = manager.get_size_comparison()
    for key, value in comparison.items():
        print(f"  {key}: {value}")
    
    # 性能測試
    print()
    print("性能測試:")
    perf_result = manager.test_model_performance()
    for key, value in perf_result.items():
        print(f"  {key}: {value}")