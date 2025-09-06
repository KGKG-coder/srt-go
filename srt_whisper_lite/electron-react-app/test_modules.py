#!/usr/bin/env python3
"""
快速測試嵌入式 Python 模組
"""

import sys
import os

def test_module(module_name, display_name=None):
    """測試模組導入"""
    if display_name is None:
        display_name = module_name
    
    try:
        module = __import__(module_name)
        version = getattr(module, '__version__', 'Unknown')
        print(f"[OK] {display_name}: {version}")
        return True
    except ImportError as e:
        print(f"[NO] {display_name}: {e}")
        return False

def main():
    """主函數"""
    print(f"Python: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Executable: {sys.executable}")
    print("-" * 50)
    
    # 測試基本模組
    modules = [
        ("json", "JSON"),
        ("pathlib", "PathLib"),
        ("requests", "Requests"),
        ("tqdm", "TQDM"),
        ("soundfile", "SoundFile"),
        ("ctranslate2", "CTranslate2"),
        ("huggingface_hub", "HuggingFace Hub"),
        ("tokenizers", "Tokenizers"),
    ]
    
    available = 0
    total = len(modules)
    
    for module_name, display_name in modules:
        if test_module(module_name, display_name):
            available += 1
    
    print("-" * 50)
    print(f"可用模組: {available}/{total}")
    
    if available >= total * 0.7:
        print("[成功] 嵌入式環境基本可用")
        return True
    else:
        print("[失敗] 嵌入式環境需要設置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)