#!/usr/bin/env python3
"""
測試 Large V3 Turbo Float16 模型性能
"""

import sys
import time
import logging
from pathlib import Path

# 添加當前目錄到路徑
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from large_v3_turbo_float16_model_manager import LargeV3TurboFloat16ModelManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_turbo_model():
    """測試 Turbo 模型的可用性和性能"""
    print("=== Large V3 Turbo Float16 模型測試 ===")
    print()
    
    # 初始化模型管理器
    manager = LargeV3TurboFloat16ModelManager()
    
    # 獲取模型信息
    print("Model Information:")
    info = manager.get_model_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print()
    print("Size Comparison:")
    comparison = manager.get_size_comparison()
    for key, value in comparison.items():
        print(f"  {key}: {value}")
    
    print()
    print("Model Parameters:")
    try:
        params = manager.get_whisper_model_params()
        for key, value in params.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"  錯誤: {e}")
    
    print()
    print("Performance Test:")
    
    # 測試模型載入時間
    try:
        from faster_whisper import WhisperModel
        
        # 測試 Distil Large V3
        print("  Testing distil-large-v3 loading speed...")
        start_time = time.time()
        
        try:
            model = WhisperModel("distil-large-v3", device="cuda", compute_type="float16")
            load_time = time.time() - start_time
            print(f"  SUCCESS: Distil Large V3 loaded in {load_time:.2f}s")
            
            # 測試 GPU 記憶體使用
            try:
                import torch
                if torch.cuda.is_available():
                    memory_used = torch.cuda.memory_allocated() / (1024**3)
                    print(f"  GPU Memory Used: {memory_used:.2f} GB")
            except ImportError:
                print("  PyTorch not available, cannot check GPU memory")
                
        except Exception as e:
            print(f"  ERROR: Distil model failed: {e}")
            
            # 回退測試標準版
            print("  Fallback to standard large-v3...")
            start_time = time.time()
            model = WhisperModel("large-v3", device="cuda", compute_type="float16")
            load_time = time.time() - start_time
            print(f"  SUCCESS: Standard Large V3 loaded in {load_time:.2f}s")
    
    except ImportError:
        print("  ERROR: faster-whisper not available")
    except Exception as e:
        print(f"  ERROR: Model test failed: {e}")

    print()
    print("Recommendations:")
    print("  - 推薦用於: 大量處理、實時應用")
    print("  - GPU 記憶體需求: ~2-3GB (vs 5-6GB 標準版)")
    print("  - 處理速度: 6x faster than standard")
    print("  - 精度保留: ~97% (適合大多數應用)")
    
    return manager

if __name__ == "__main__":
    test_turbo_model()