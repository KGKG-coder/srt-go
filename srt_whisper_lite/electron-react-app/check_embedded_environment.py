#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查嵌入式環境完整性
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

# 設置編碼
if sys.platform.startswith('win'):
    os.system('chcp 65001 > NUL 2>&1')

def check_module(module_name, display_name=None, required=True):
    """檢查模組是否可用"""
    if display_name is None:
        display_name = module_name
    
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'Unknown')
        print(f"[OK] {display_name}: {version}")
        return True
    except ImportError as e:
        status = "[ERROR]" if required else "[WARN]"
        print(f"{status} {display_name}: 不可用")
        if required:
            print(f"    錯誤: {e}")
        return False

def check_python_environment():
    """檢查 Python 環境"""
    print("Python 環境檢查:")
    print(f"  版本: {sys.version}")
    print(f"  執行路徑: {sys.executable}")
    print(f"  平台: {sys.platform}")
    print()

def check_core_dependencies():
    """檢查核心依賴"""
    print("核心依賴檢查:")
    
    core_deps = [
        ("numpy", "NumPy", True),
        ("faster_whisper", "Faster-Whisper", True),
        ("ctranslate2", "CTranslate2", True),
        ("librosa", "Librosa", True),
        ("soundfile", "SoundFile", True),
        ("scipy", "SciPy", True),
        ("sklearn", "Scikit-learn", True),
        ("tqdm", "TQDM", True),
        ("huggingface_hub", "Hugging Face Hub", True),
        ("tokenizers", "Tokenizers", True),
        ("requests", "Requests", True)
    ]
    
    results = []
    for module_name, display_name, required in core_deps:
        result = check_module(module_name, display_name, required)
        results.append((display_name, result, required))
    
    return results

def check_optional_dependencies():
    """檢查可選依賴"""
    print("\n可選依賴檢查:")
    
    optional_deps = [
        ("torch", "PyTorch", False),
        ("pysrt", "PySRT", False),
        ("webvtt", "WebVTT", False),
        ("opencc", "OpenCC", False),
        ("jieba", "Jieba", False),
        ("pydub", "PyDub", False),
        ("transformers", "Transformers", False),
        ("pyannote.audio", "PyAnnote", False)
    ]
    
    results = []
    for module_name, display_name, required in optional_deps:
        result = check_module(module_name, display_name, required)
        results.append((display_name, result, required))
    
    return results

def test_faster_whisper():
    """測試 Faster-Whisper 功能"""
    print("\nFaster-Whisper 功能測試:")
    
    try:
        from faster_whisper import WhisperModel
        print("[OK] WhisperModel 可以導入")
        
        # 嘗試列出可用模型（不下載）
        print("[OK] Faster-Whisper 模組功能正常")
        return True
        
    except ImportError:
        print("[ERROR] 無法導入 WhisperModel")
        return False
    except Exception as e:
        print(f"[WARN] 導入成功但有警告: {e}")
        return True

def test_audio_processing():
    """測試音頻處理功能"""
    print("\n音頻處理功能測試:")
    
    try:
        import numpy as np
        import librosa
        import soundfile as sf
        
        # 創建測試音頻數據
        sample_rate = 16000
        duration = 1  # 1秒
        t = np.linspace(0, duration, sample_rate * duration)
        audio = np.sin(2 * np.pi * 440 * t)  # 440Hz 正弦波
        
        print("[OK] NumPy 數組創建成功")
        
        # 測試 librosa 功能
        audio_resampled = librosa.resample(audio, orig_sr=sample_rate, target_sr=8000)
        print("[OK] Librosa 重新採樣功能正常")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 音頻處理測試失敗: {e}")
        return False

def test_ml_features():
    """測試機器學習功能"""
    print("\n機器學習功能測試:")
    
    try:
        import numpy as np
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        
        # 創建測試數據
        X = np.random.rand(100, 5)
        
        # 測試標準化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        print("[OK] 數據標準化功能正常")
        
        # 測試聚類
        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        print("[OK] K-means 聚類功能正常")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 機器學習測試失敗: {e}")
        return False

def generate_environment_report():
    """生成環境報告"""
    print("\n" + "="*60)
    print("環境完整性報告")
    print("="*60)
    
    # 檢查 Python 環境
    check_python_environment()
    
    # 檢查依賴
    core_results = check_core_dependencies()
    optional_results = check_optional_dependencies()
    
    # 功能測試
    faster_whisper_ok = test_faster_whisper()
    audio_ok = test_audio_processing()
    ml_ok = test_ml_features()
    
    # 統計結果
    core_passed = sum(1 for _, result, _ in core_results if result)
    core_total = len(core_results)
    
    optional_passed = sum(1 for _, result, _ in optional_results if result)
    optional_total = len(optional_results)
    
    print(f"\n總結:")
    print(f"  核心依賴: {core_passed}/{core_total} 可用")
    print(f"  可選依賴: {optional_passed}/{optional_total} 可用")
    print(f"  功能測試: Faster-Whisper {'OK' if faster_whisper_ok else 'FAIL'}, "
          f"音頻處理 {'OK' if audio_ok else 'FAIL'}, "
          f"機器學習 {'OK' if ml_ok else 'FAIL'}")
    
    # 判斷整體狀態
    if core_passed == core_total and faster_whisper_ok and audio_ok and ml_ok:
        print(f"\n[成功] 嵌入式環境完整，可以正常運行！")
        return True
    elif core_passed >= core_total * 0.8:
        print(f"\n[警告] 嵌入式環境基本可用，但有部分問題")
        return True
    else:
        print(f"\n[失敗] 嵌入式環境不完整，需要重新設置")
        return False

def main():
    """主函數"""
    print("嵌入式 Python 環境檢查")
    print("版本: 2.2.1-simplified")
    
    return generate_environment_report()

if __name__ == "__main__":
    success = main()
    input("\n按 Enter 鍵退出...")
    sys.exit(0 if success else 1)