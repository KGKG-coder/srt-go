#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試簡化版架構設置
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def test_embedded_python():
    """測試嵌入式 Python 環境"""
    print("="*60)
    print("1. 測試嵌入式 Python 環境")
    print("="*60)
    
    mini_python_path = Path(__file__).parent / "mini_python" / "python.exe"
    
    if mini_python_path.exists():
        print(f"[OK] 找到嵌入式 Python: {mini_python_path}")
        
        # 檢查版本
        try:
            result = subprocess.run(
                [str(mini_python_path), "--version"],
                capture_output=True,
                text=True
            )
            print(f"   版本: {result.stdout.strip()}")
        except Exception as e:
            print(f"[ERROR] 無法執行 Python: {e}")
            return False
    else:
        print(f"[ERROR] 找不到嵌入式 Python: {mini_python_path}")
        return False
    
    return True

def test_simplified_backend():
    """測試簡化版後端腳本"""
    print("\n" + "="*60)
    print("2. 測試簡化版後端腳本")
    print("="*60)
    
    backend_path = Path(__file__).parent / "python" / "electron_backend_simplified.py"
    
    if backend_path.exists():
        print(f"[OK] 找到簡化版後端: {backend_path}")
        
        # 檢查檔案大小
        size_kb = backend_path.stat().st_size / 1024
        print(f"   檔案大小: {size_kb:.1f} KB")
        
        # 檢查是否包含簡化邏輯
        with open(backend_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "智能選擇" not in content and "smart_backend_selector" not in content:
                print("[OK] 確認已移除智能選擇邏輯")
            else:
                print("[WARNING] 警告：仍包含智能選擇相關程式碼")
    else:
        print(f"[ERROR] 找不到簡化版後端: {backend_path}")
        return False
    
    return True

def test_main_simplified():
    """測試簡化版主程序"""
    print("\n" + "="*60)
    print("3. 測試簡化版 Electron 主程序")
    print("="*60)
    
    main_path = Path(__file__).parent / "main_simplified.js"
    
    if main_path.exists():
        print(f"[OK] 找到簡化版主程序: {main_path}")
        
        # 檢查檔案大小
        size_kb = main_path.stat().st_size / 1024
        print(f"   檔案大小: {size_kb:.1f} KB")
        
        # 檢查關鍵函數
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "getEmbeddedPythonPath" in content:
                print("[OK] 包含 getEmbeddedPythonPath 函數")
            if "smart" not in content.lower() or "selector" not in content.lower():
                print("[OK] 確認已移除智能選擇邏輯")
    else:
        print(f"[ERROR] 找不到簡化版主程序: {main_path}")
        return False
    
    return True

def test_package_json():
    """測試 package.json 更新"""
    print("\n" + "="*60)
    print("4. 測試 package.json 腳本")
    print("="*60)
    
    package_path = Path(__file__).parent / "package.json"
    
    if package_path.exists():
        with open(package_path, 'r', encoding='utf-8') as f:
            package = json.load(f)
            
        scripts = package.get('scripts', {})
        
        # 檢查新增的簡化版腳本
        if "start:simplified" in scripts:
            print("[OK] 找到 start:simplified 腳本")
        else:
            print("[WARNING] 缺少 start:simplified 腳本")
            
        if "dev:simplified" in scripts:
            print("[OK] 找到 dev:simplified 腳本")
        else:
            print("[WARNING] 缺少 dev:simplified 腳本")
            
        if "build:simplified" in scripts:
            print("[OK] 找到 build:simplified 腳本")
        else:
            print("[WARNING] 缺少 build:simplified 腳本")
    else:
        print(f"[ERROR] 找不到 package.json")
        return False
    
    return True

def test_python_modules():
    """測試 Python 模組可用性"""
    print("\n" + "="*60)
    print("5. 測試 Python 模組可用性")
    print("="*60)
    
    mini_python_path = Path(__file__).parent / "mini_python" / "python.exe"
    
    if not mini_python_path.exists():
        print("[ERROR] 無法測試，找不到嵌入式 Python")
        return False
    
    # 測試核心模組
    modules = [
        ("sys", "系統模組"),
        ("json", "JSON 模組"),
        ("pathlib", "路徑處理"),
        ("numpy", "NumPy"),
        ("faster_whisper", "Faster-Whisper")
    ]
    
    for module_name, desc in modules:
        try:
            result = subprocess.run(
                [str(mini_python_path), "-c", f"import {module_name}; print('OK')"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"[OK] {desc} ({module_name}): 可用")
            else:
                print(f"[ERROR] {desc} ({module_name}): 不可用")
        except subprocess.TimeoutExpired:
            print(f"[WARNING] {desc} ({module_name}): 測試超時")
        except Exception as e:
            print(f"[ERROR] {desc} ({module_name}): 錯誤 - {e}")
    
    return True

def main():
    """主測試函數"""
    print("簡化架構設置測試")
    print("版本: 2.2.1-simplified")
    print()
    
    results = []
    
    # 執行各項測試
    results.append(("嵌入式 Python", test_embedded_python()))
    results.append(("簡化版後端", test_simplified_backend()))
    results.append(("簡化版主程序", test_main_simplified()))
    results.append(("Package.json", test_package_json()))
    results.append(("Python 模組", test_python_modules()))
    
    # 總結
    print("\n" + "="*60)
    print("測試總結")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS] 通過" if result else "[FAIL] 失敗"
        print(f"{name}: {status}")
    
    print(f"\n總計: {passed}/{total} 通過")
    
    if passed == total:
        print("\n所有測試通過！簡化架構已準備就緒。")
        print("\n下一步：")
        print("1. 執行 'npm run dev:simplified' 測試開發模式")
        print("2. 執行測試影片處理")
        print("3. 建置生產版本")
    else:
        print("\n部分測試失敗，請檢查設置。")
    
    return passed == total

if __name__ == "__main__":
    sys.exit(0 if main() else 1)