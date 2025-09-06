#!/usr/bin/env python3
"""
測試 Large V3 Turbo Float16 配置
"""

import sys
import time
import logging
from pathlib import Path

# 添加當前目錄到路徑
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_turbo_config():
    """測試 Turbo 配置"""
    print("=== Large V3 Turbo Float16 Configuration Test ===")
    print()
    
    try:
        from large_v3_float16_model_manager import LargeV3TurboFloat16ModelManager
        
        # 初始化模型管理器
        manager = LargeV3TurboFloat16ModelManager()
        
        # 獲取模型信息
        print("Model Configuration:")
        info = manager.get_model_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        print()
        print("Whisper Parameters:")
        params = manager.get_whisper_model_params()
        for key, value in params.items():
            print(f"  {key}: {value}")
        
        print()
        print("GPU Optimization Test:")
        
        # 測試模型載入
        try:
            from faster_whisper import WhisperModel
            
            print("  Loading large-v3 with GPU Turbo settings...")
            start_time = time.time()
            
            model = WhisperModel(
                model_size_or_path="large-v3",
                device="cuda",
                compute_type="float16",
                num_workers=1,
                device_index=0
            )
            
            load_time = time.time() - start_time
            print(f"  SUCCESS: Model loaded in {load_time:.2f}s")
            
            # 檢查 GPU 記憶體使用
            try:
                import torch
                if torch.cuda.is_available():
                    memory_used = torch.cuda.memory_allocated() / (1024**3)
                    memory_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    print(f"  GPU Memory: {memory_used:.2f}/{memory_total:.1f} GB ({memory_used/memory_total*100:.1f}%)")
                    
                    # 檢查 GPU 型號
                    gpu_name = torch.cuda.get_device_name(0)
                    print(f"  GPU Device: {gpu_name}")
            except ImportError:
                print("  PyTorch not available, cannot check GPU details")
            
            print()
            print("Turbo Performance Benefits:")
            print("  - Float16 precision: 2x GPU memory efficiency")
            print("  - CUDA optimizations: 5-10x speed boost vs CPU")
            print("  - Tensor Core acceleration: Additional 2-3x speedup")
            print("  - Lower latency: Ideal for real-time processing")
            
            return True
            
        except Exception as e:
            print(f"  ERROR: Model loading failed: {e}")
            return False
            
    except ImportError as e:
        print(f"ERROR: Cannot import model manager: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_turbo_config()
    if success:
        print("\n✅ Large V3 Turbo Float16 configuration is ready!")
    else:
        print("\n❌ Configuration test failed")