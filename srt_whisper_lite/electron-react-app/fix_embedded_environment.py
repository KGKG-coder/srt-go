#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復嵌入式Python環境
Fix Embedded Python Environment
"""

import sys
import os
import subprocess
from pathlib import Path

def fix_embedded_python():
    """修復嵌入式Python環境中的模組問題"""
    
    print("=== 修復嵌入式Python環境 ===")
    
    # 設定路徑
    current_dir = Path(__file__).parent
    mini_python_dir = current_dir / "mini_python"
    python_exe = mini_python_dir / "python.exe"
    
    if not python_exe.exists():
        print(f"ERROR: 嵌入式Python不存在: {python_exe}")
        return False
    
    print(f"Python路徑: {python_exe}")
    
    # 檢查Python版本
    try:
        result = subprocess.run([str(python_exe), "--version"], 
                              capture_output=True, text=True, timeout=10)
        print(f"Python版本: {result.stdout.strip()}")
    except Exception as e:
        print(f"無法檢查Python版本: {e}")
        return False
    
    # 核心依賴列表
    core_packages = [
        "numpy>=1.21.0",
        "torch>=1.10.0",
        "ctranslate2>=3.0.0", 
        "faster-whisper>=1.1.0",
        "soundfile>=0.12.1",
        "librosa>=0.9.0"
    ]
    
    print("\n=== 安裝核心依賴 ===")
    
    for package in core_packages:
        print(f"安裝 {package}...")
        try:
            # 使用系統級安裝，強制重新安裝
            cmd = [
                str(python_exe), "-m", "pip", "install", 
                "--upgrade", "--force-reinstall", "--no-deps",
                package
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"[OK] {package} 安裝成功")
            else:
                print(f"[ERROR] {package} 安裝失敗: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] {package} 安裝超時，跳過")
        except Exception as e:
            print(f"[ERROR] {package} 安裝異常: {e}")
    
    print("\n=== 測試模組導入 ===")
    
    # 測試關鍵模組
    test_modules = ["numpy", "torch", "ctranslate2", "faster_whisper"]
    
    for module in test_modules:
        try:
            cmd = [str(python_exe), "-c", f"import {module}; print('[OK] {module}: SUCCESS')"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(result.stdout.strip())
            else:
                print(f"[ERROR] {module}: 導入失敗")
                
        except Exception as e:
            print(f"[ERROR] {module}: 測試異常 - {e}")
    
    return True

if __name__ == "__main__":
    fix_embedded_python()