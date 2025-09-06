#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 模型下載腳本 - 為完整版打包準備
"""

import os
import sys
from pathlib import Path

def download_models():
    """下載 AI 模型到 models 目錄"""
    print("=== SRT GO 完整版模型下載 ===")
    
    models_dir = Path(__file__).parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    print(f"模型目錄: {models_dir}")
    
    # 導入並使用 Faster-Whisper 下載模型
    try:
        from faster_whisper import WhisperModel
        
        models_to_download = [
            ("large-v3", "主要模型 - 最高精度"),
            ("medium", "備用模型 - 平衡性能"),
            ("base", "基礎模型 - 快速處理")
        ]
        
        for model_name, description in models_to_download:
            print(f"\n下載 {model_name} 模型 ({description})...")
            try:
                # 初始化模型會自動下載到快取
                model = WhisperModel(model_name, device="cpu", compute_type="int8")
                print(f"✅ {model_name} 模型下載完成")
            except Exception as e:
                print(f"❌ {model_name} 模型下載失敗: {e}")
        
        print("\n=== 模型下載完成 ===")
        print("模型已快取到系統目錄，打包時會包含到 models/ 目錄")
        
        # 檢查模型快取位置
        import os
        home_dir = os.path.expanduser("~")
        cache_dir = os.path.join(home_dir, ".cache", "huggingface", "hub")
        
        if os.path.exists(cache_dir):
            print(f"\n模型快取位置: {cache_dir}")
            
            # 列出已下載的模型
            import glob
            whisper_models = glob.glob(os.path.join(cache_dir, "*whisper*"))
            print(f"發現 {len(whisper_models)} 個 Whisper 模型快取")
            
            for model_path in whisper_models:
                model_name = os.path.basename(model_path)
                print(f"  - {model_name}")
        
        return True
        
    except ImportError:
        print("錯誤: faster-whisper 未安裝")
        print("請執行: pip install faster-whisper")
        return False
    except Exception as e:
        print(f"下載過程發生錯誤: {e}")
        return False

if __name__ == "__main__":
    success = download_models()
    input("\n按 Enter 鍵退出...")
    sys.exit(0 if success else 1)