"""
測試程式功能
"""
import os
import sys

def test_basic_import():
    """測試基本模組匯入"""
    try:
        import faster_whisper
        print("[OK] faster_whisper 模組正常")
    except ImportError as e:
        print(f"[FAIL] faster_whisper: {e}")
        return False
    
    try:
        import torch
        print(f"[OK] torch 模組正常 (版本: {torch.__version__})")
        print(f"     CUDA 可用: {torch.cuda.is_available()}")
    except ImportError as e:
        print(f"[FAIL] torch: {e}")
    
    try:
        import av
        print("[OK] av 模組正常")
    except ImportError as e:
        print(f"[FAIL] av: {e}")
    
    try:
        import customtkinter
        print("[OK] customtkinter 模組正常")
    except ImportError as e:
        print(f"[FAIL] customtkinter: {e}")
    
    try:
        import onnxruntime
        print(f"[OK] onnxruntime 模組正常")
    except ImportError as e:
        print(f"[FAIL] onnxruntime: {e}")
    
    return True

def test_project_modules():
    """測試專案模組"""
    modules = [
        'simplified_subtitle_core',
        'audio_processor',
        'semantic_processor',
        'subtitle_formatter',
        'config_manager',
        'i18n'
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"[OK] {module} 模組正常")
        except ImportError as e:
            print(f"[FAIL] {module}: {e}")
            all_ok = False
    
    return all_ok

def test_file_exists():
    """測試必要文件是否存在"""
    files = [
        'main.py',
        'icon.ico',
        'logo.png',
        'custom_corrections.json',
        'user_config.json'
    ]
    
    all_ok = True
    for file in files:
        if os.path.exists(file):
            print(f"[OK] {file} 存在")
        else:
            print(f"[FAIL] {file} 不存在")
            all_ok = False
    
    return all_ok

def test_whisper_model():
    """測試 Whisper 模型載入"""
    try:
        from faster_whisper import WhisperModel
        print("\n正在測試 Whisper 模型載入...")
        # 只測試 tiny 模型以節省時間
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        print("[OK] Whisper 模型載入成功")
        return True
    except Exception as e:
        print(f"[FAIL] Whisper 模型載入失敗: {e}")
        return False

def main():
    print("=== SRT Whisper Lite 功能測試 ===")
    print(f"Python 版本: {sys.version}")
    print(f"工作目錄: {os.getcwd()}")
    print()
    
    print("1. 測試基本模組匯入:")
    test_basic_import()
    print()
    
    print("2. 測試專案模組:")
    test_project_modules()
    print()
    
    print("3. 測試文件存在:")
    test_file_exists()
    print()
    
    print("4. 測試 Whisper 模型:")
    test_whisper_model()
    print()
    
    print("=== 測試完成 ===")

if __name__ == "__main__":
    main()