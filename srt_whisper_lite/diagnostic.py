#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""診斷腳本 - 檢查Python環境和依賴"""

import sys
import json
import os

def check_environment():
    """檢查Python環境"""
    result = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "python_path": sys.path[:3],
        "working_dir": os.getcwd(),
        "encoding": sys.stdout.encoding
    }
    
    # 檢查必要模組
    modules_to_check = [
        'simplified_subtitle_core',
        'subtitle_formatter',
        'audio_processor',
        'semantic_processor',
        'config_manager'
    ]
    
    result["modules"] = {}
    for module in modules_to_check:
        try:
            __import__(module)
            result["modules"][module] = "✓ OK"
        except ImportError as e:
            result["modules"][module] = f"✗ Error: {str(e)}"
    
    # 檢查依賴套件
    packages = [
        'faster_whisper',
        'numpy',
        'av'
    ]
    
    result["packages"] = {}
    for package in packages:
        try:
            __import__(package)
            result["packages"][package] = "✓ Installed"
        except ImportError:
            result["packages"][package] = "✗ Not installed"
    
    return result

if __name__ == "__main__":
    try:
        result = check_environment()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0)
    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "type": type(e).__name__
        }, ensure_ascii=False))
        sys.exit(1)
