#!/usr/bin/env python3
"""
官方 Large V3 Turbo Float16 模型管理器
正確使用官方 openai/whisper-large-v3-turbo 模型 (809M 參數, ~1.6GB)
支援 Float16 精度，提供最佳速度與品質平衡
"""

import os
import logging
import requests
import shutil
import hashlib
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
from tqdm import tqdm
import time

logger = logging.getLogger(__name__)

class OfficialLargeV3TurboFloat16Manager:
    """官方 Large V3 Turbo Float16 模型管理器"""
    
    def __init__(self):
        # 官方模型信息
        self.model_name = "openai/whisper-large-v3-turbo"
        self.model_variant = "float16"
        self.model_full_name = "official-large-v3-turbo-float16"
        
        # 模型規格（官方數據）
        self.model_specs = {
            "parameters": "809M",
            "decoder_layers": 4,  # 從 32 層減少到 4 層
            "expected_size_gb": 1.6,  # 約 1.6GB
            "model_bin_size_mb": 1550,  # model.bin 約 1.55GB
            "speed_improvement": "8x faster than large-v3",
            "accuracy": "Similar to large-v2",
            "precision": "float16",
            "compute_optimized": True
        }
        
        # 路徑設定
        self.app_models_dir = Path(__file__).parent / "models"
        self.model_dir = self.app_models_dir / self.model_full_name
        self.cache_dir = Path.home() / ".cache" / "whisper" / self.model_full_name
        
        # HuggingFace 緩存路徑
        self.hf_cache_dir = Path.home() / ".cache" / "huggingface" / "hub" / "models--openai--whisper-large-v3-turbo"
        
        # 確保目錄存在
        self.app_models_dir.mkdir(parents=True, exist_ok=True)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"官方 Large V3 Turbo Float16 模型管理器初始化:")
        logger.info(f"  - 模型: {self.model_name}")
        logger.info(f"  - 參數數量: {self.model_specs['parameters']}")
        logger.info(f"  - 解碼層: {self.model_specs['decoder_layers']} (vs 32 in standard)")
        logger.info(f"  - 預期大小: {self.model_specs['expected_size_gb']} GB")
        logger.info(f"  - 速度提升: {self.model_specs['speed_improvement']}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """獲取模型信息"""
        available = self.check_model_availability()
        
        return {
            "name": "Official Large V3 Turbo",
            "repository": self.model_name,
            "variant": "Float16 官方版",
            "available": available,
            "status_text": "已安裝" if available else "需要下載",
            "parameters": self.model_specs["parameters"],
            "decoder_layers": self.model_specs["decoder_layers"],
            "expected_size": f"{self.model_specs['expected_size_gb']} GB",
            "actual_size": self._format_size(self._get_model_size()) if available else "0 MB",
            "path": str(self.model_dir) if available else None,
            "performance": self.model_specs["speed_improvement"],
            "accuracy": self.model_specs["accuracy"],
            "precision": self.model_specs["precision"],
            "model_type": "openai/whisper-large-v3-turbo",
            "compute_type": "float16",
            "device": "cuda",
            "download_source": "Official OpenAI Repository"
        }
    
    def check_model_availability(self) -> bool:
        """檢查模型是否可用"""
        # 檢查 HuggingFace 緩存
        if self._check_hf_cache():
            logger.info("✅ 找到 HuggingFace 緩存中的官方 Turbo 模型")
            return True
        
        # 檢查本地模型目錄
        if self._validate_local_model():
            logger.info("✅ 找到本地官方 Turbo 模型")
            return True
        
        logger.info("❌ 未找到官方 Large V3 Turbo 模型")
        return False
    
    def _check_hf_cache(self) -> bool:
        """檢查 HuggingFace 緩存"""
        if not self.hf_cache_dir.exists():
            return False
        
        snapshots_dir = self.hf_cache_dir / "snapshots"
        if not snapshots_dir.exists():
            return False
        
        # 檢查最新的 snapshot
        for snapshot_dir in snapshots_dir.iterdir():
            if snapshot_dir.is_dir() and self._validate_model_files(snapshot_dir):
                return True
        
        return False
    
    def _validate_local_model(self) -> bool:
        """驗證本地模型"""
        return self._validate_model_files(self.model_dir)
    
    def _validate_model_files(self, model_path: Path) -> bool:
        """驗證模型文件是否完整且符合 Turbo 規格"""
        if not model_path.exists():
            return False
        
        # 檢查必要文件
        essential_files = ["model.bin", "config.json", "tokenizer.json"]
        for file_name in essential_files:
            file_path = model_path / file_name
            if not file_path.exists():
                logger.debug(f"缺失文件: {file_name}")
                return False
        
        # 檢查 model.bin 大小（關鍵：Turbo 版本應該更小）
        model_bin = model_path / "model.bin"
        if model_bin.exists():
            size_bytes = model_bin.stat().st_size
            size_gb = size_bytes / (1024**3)
            
            # Turbo 版本應該約 1.5-1.7GB，不應該接近 3GB
            if size_gb > 2.5:
                logger.warning(f"模型過大 ({size_gb:.2f}GB)，可能是標準版而非 Turbo 版")
                return False
            
            if size_gb < 1.0:
                logger.warning(f"模型過小 ({size_gb:.2f}GB)，可能不完整")
                return False
            
            logger.info(f"模型大小驗證通過: {size_gb:.2f}GB (符合 Turbo 規格)")
        
        # 檢查 config.json 中的架構信息
        config_file = model_path / "config.json"
        if config_file.exists():
            try:
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 檢查解碼層數量
                decoder_layers = config.get("decoder_layers", 32)
                if decoder_layers != 4:
                    logger.warning(f"解碼層數量 ({decoder_layers}) 不符合 Turbo 規格 (應為 4)")
                    return False
                
                logger.info(f"架構驗證通過: {decoder_layers} 解碼層 (Turbo 規格)")
            except Exception as e:
                logger.debug(f"無法讀取配置文件: {e}")
        
        return True
    
    def download_official_model(self) -> bool:
        """下載官方 Large V3 Turbo 模型"""
        try:
            logger.info("開始下載官方 Large V3 Turbo 模型...")
            logger.info(f"來源: {self.model_name}")
            logger.info(f"預期大小: ~{self.model_specs['expected_size_gb']} GB")
            
            # 使用 HuggingFace 下載
            from huggingface_hub import snapshot_download
            
            local_dir = snapshot_download(
                repo_id=self.model_name,
                cache_dir=Path.home() / ".cache" / "huggingface",
                resume_download=True,
                local_files_only=False
            )
            
            logger.info(f"✅ 官方模型下載完成: {local_dir}")
            
            # 驗證下載的模型
            if self._validate_model_files(Path(local_dir)):
                logger.info("✅ 模型驗證通過")
                return True
            else:
                logger.error("❌ 下載的模型驗證失敗")
                return False
            
        except ImportError:
            logger.error("❌ 需要安裝 huggingface_hub: pip install huggingface_hub")
            return False
        except Exception as e:
            logger.error(f"❌ 模型下載失敗: {e}")
            return False
    
    def ensure_model_ready(self) -> Tuple[bool, str]:
        """確保官方模型準備就緒"""
        if self.check_model_availability():
            logger.info("官方 Large V3 Turbo 模型已可用")
            return True, "openai/whisper-large-v3-turbo"
        
        logger.info("正在下載官方 Large V3 Turbo 模型...")
        if self.download_official_model():
            return True, "openai/whisper-large-v3-turbo"
        else:
            logger.error("無法獲取官方模型")
            return False, ""
    
    def get_whisper_model_params(self) -> Dict[str, Any]:
        """獲取 Whisper 模型參數"""
        success, model_name = self.ensure_model_ready()
        
        if not success:
            raise RuntimeError("官方 Large V3 Turbo 模型不可用")
        
        return {
            "model_size_or_path": model_name,  # 使用官方模型名稱
            "device": "cuda" if self._check_cuda_available() else "cpu",
            "compute_type": "float16" if self._check_cuda_available() else "int8",
            "num_workers": 1,
            "device_index": 0 if self._check_cuda_available() else None
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
            "Official Large V3 Turbo": f"{self.model_specs['expected_size_gb']} GB (4 decoder layers)",
            "Size Reduction": "48% smaller",
            "Parameter Reduction": f"809M vs 1550M ({round(809/1550*100)}% of original)",
            "Speed Improvement": self.model_specs["speed_improvement"],
            "Accuracy": self.model_specs["accuracy"],
            "GPU Memory Saving": "~1.5 GB saved",
            "Architecture": "Pruned from 32 to 4 decoder layers"
        }
    
    def _get_model_size(self) -> int:
        """獲取模型總大小（字節）"""
        try:
            # 檢查 HF 緩存
            if self.hf_cache_dir.exists():
                snapshots = self.hf_cache_dir / "snapshots"
                if snapshots.exists():
                    for snapshot_dir in snapshots.iterdir():
                        if snapshot_dir.is_dir():
                            total_size = sum(f.stat().st_size for f in snapshot_dir.rglob('*') if f.is_file())
                            return total_size
            
            # 檢查本地目錄
            if self.model_dir.exists():
                total_size = sum(f.stat().st_size for f in self.model_dir.glob('*') if f.is_file())
                return total_size
        except Exception as e:
            logger.debug(f"無法獲取模型大小: {e}")
        
        return 0
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def clean_fake_turbo_models(self) -> Dict[str, bool]:
        """清理偽造的 Turbo 模型（實際是標準版的錯誤標記）"""
        results = {}
        
        # 檢查本地的偽造 Turbo 模型
        fake_turbo_dirs = [
            self.app_models_dir / "large-v3-turbo-float16",
            self.app_models_dir / "large-v3-turbo-int8"
        ]
        
        for fake_dir in fake_turbo_dirs:
            if fake_dir.exists():
                try:
                    # 檢查是否為偽造（大小過大）
                    model_bin = fake_dir / "model.bin"
                    if model_bin.exists():
                        size_gb = model_bin.stat().st_size / (1024**3)
                        if size_gb > 2.5:  # 明顯是標準版
                            logger.info(f"發現偽造 Turbo 模型: {fake_dir.name} ({size_gb:.2f}GB)")
                            logger.info(f"重新命名為標準版...")
                            
                            new_name = fake_dir.name.replace("-turbo", "-standard")
                            new_path = fake_dir.parent / new_name
                            
                            if not new_path.exists():
                                fake_dir.rename(new_path)
                                results[fake_dir.name] = True
                                logger.info(f"✅ 已重新命名: {new_name}")
                            else:
                                results[fake_dir.name] = False
                                logger.warning(f"目標路徑已存在: {new_name}")
                        else:
                            results[fake_dir.name] = True  # 大小正確，保留
                    else:
                        results[fake_dir.name] = False
                except Exception as e:
                    logger.error(f"處理 {fake_dir.name} 時出錯: {e}")
                    results[fake_dir.name] = False
            else:
                results[fake_dir.name] = True  # 不存在，無需處理
        
        return results


def get_official_turbo_manager() -> OfficialLargeV3TurboFloat16Manager:
    """便利函數：獲取官方 Turbo 模型管理器實例"""
    return OfficialLargeV3TurboFloat16Manager()


if __name__ == "__main__":
    # 測試官方管理器
    manager = OfficialLargeV3TurboFloat16Manager()
    
    print("=== 官方 Large V3 Turbo Float16 管理器測試 ===")
    print()
    
    # 獲取模型信息
    print("模型信息:")
    info = manager.get_model_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print()
    print("大小對比:")
    comparison = manager.get_size_comparison()
    for key, value in comparison.items():
        print(f"  {key}: {value}")
    
    print()
    print("清理偽造模型:")
    cleanup_results = manager.clean_fake_turbo_models()
    for model_name, success in cleanup_results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {model_name}")
    
    print()
    print("模型可用性檢查:")
    available = manager.check_model_availability()
    if available:
        print("✅ 官方 Large V3 Turbo 模型可用")
        params = manager.get_whisper_model_params()
        print("模型參數:")
        for key, value in params.items():
            print(f"  {key}: {value}")
    else:
        print("❌ 需要下載官方模型")
        print("執行下載...")
        if manager.download_official_model():
            print("✅ 下載成功")
        else:
            print("❌ 下載失敗")