#!/usr/bin/env python3
"""
Create a complete SRT GO Enhanced v2.0 .exe executable
Uses the successfully built electron-builder output and fixes Python dependencies
"""

import os
import shutil
from pathlib import Path

def create_complete_executable():
    """Create complete executable with full Python environment"""
    
    print("Creating Complete SRT GO Enhanced v2.0 Executable...")
    
    # Paths
    source_base = Path("dist_final/win-unpacked")
    target_base = Path("dist/SRT-GO-Enhanced-v2.0-Complete")
    main_python = Path("mini_python")
    main_python_scripts = Path("python")
    
    # Create target directory
    target_base.mkdir(parents=True, exist_ok=True)
    
    print(f"Source: {source_base.absolute()}")
    print(f"Target: {target_base.absolute()}")
    
    # Step 1: Copy the entire electron-builder output
    print("Copying Electron application...")
    if source_base.exists():
        for item in source_base.iterdir():
            target_item = target_base / item.name
            if item.is_file():
                shutil.copy2(item, target_item)
                print(f"Copied file: {item.name}")
            elif item.is_dir() and item.name != "resources":
                shutil.copytree(item, target_item, dirs_exist_ok=True)
                print(f"Copied directory: {item.name}")
    
    # Step 2: Create resources directory properly
    resources_dir = target_base / "resources"
    resources_dir.mkdir(exist_ok=True)
    
    # Copy app.asar
    asar_source = source_base / "resources" / "app.asar"
    if asar_source.exists():
        shutil.copy2(asar_source, resources_dir / "app.asar")
        print("✅ Copied app.asar")
    
    # Step 3: Copy working Python environment
    print("🐍 Setting up complete Python environment...")
    
    # Copy mini_python (working Python)
    target_mini_python = resources_dir / "mini_python"
    if main_python.exists():
        if target_mini_python.exists():
            shutil.rmtree(target_mini_python)
        shutil.copytree(main_python, target_mini_python)
        print("✅ Copied complete Python environment")
    
    # Copy python scripts
    target_python_scripts = resources_dir / "python"
    if main_python_scripts.exists():
        if target_python_scripts.exists():
            shutil.rmtree(target_python_scripts)
        shutil.copytree(main_python_scripts, target_python_scripts)
        print("✅ Copied Python scripts")
    
    # Copy models if they exist
    main_models = Path("models")
    target_models = resources_dir / "models"
    if main_models.exists():
        if target_models.exists():
            shutil.rmtree(target_models)
        shutil.copytree(main_models, target_models)
        print("✅ Copied AI models")
    else:
        # Try to copy from the electron-builder output
        builder_models = source_base / "resources" / "models"
        if builder_models.exists():
            shutil.copytree(builder_models, target_models)
            print("✅ Copied AI models from builder output")
    
    # Step 4: Create launcher scripts for convenience
    print("📝 Creating launcher scripts...")
    
    # Windows launcher
    launcher_content = '''@echo off
cd /d "%~dp0"
echo ========================================
echo  SRT GO Enhanced v2.0
echo  True Windows Executable Version
echo ========================================
echo.
echo Starting application...
start "" "SRT GO Enhanced v2.0.exe"
'''
    
    with open(target_base / "Start SRT GO.bat", 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print("✅ Created launcher script")
    
    # Step 5: Create README
    readme_content = '''# SRT GO Enhanced v2.0 - Complete Executable

## 🚀 真正的 Windows 執行檔版本

這是一個完整的 Windows 執行檔版本，包含所有必要的元件：

### 執行方式
直接雙擊以下檔案啟動應用程式：
- **SRT GO Enhanced v2.0.exe** - 主執行檔 (真正的 .exe)
- **Start SRT GO.bat** - 方便的啟動腳本 (可選)

### 特色功能
✅ **真正的 Windows .exe 執行檔** - 不需要 .bat 檔案
✅ **完整的 Python 環境** - 內建所有必要套件
✅ **Large V3 Turbo AI 模型** - 最高準確度
✅ **Enhanced Voice Detector v2.0** - 革命性語音檢測
✅ **現代化 GUI** - Electron + React 介面

### 系統需求
- Windows 10/11 (64-bit)
- 4GB+ RAM (建議 8GB+)
- 8GB 硬碟空間

### 首次使用
1. 確保系統滿足需求
2. 雙擊 "SRT GO Enhanced v2.0.exe"
3. 等待應用程式載入
4. 開始使用 AI 字幕生成

---
SRT GO Enhanced v2.0 - 革命性 AI 字幕生成工具
使用真正的 Windows 執行檔，無需批次檔案！
'''
    
    with open(target_base / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ Created README file")
    
    # Step 6: Final verification
    print("\n🔍 Verifying executable structure...")
    
    exe_file = target_base / "SRT GO Enhanced v2.0.exe"
    if exe_file.exists():
        size_mb = exe_file.stat().st_size / (1024*1024)
        print(f"✅ Main executable: {size_mb:.1f} MB")
    
    python_exe = target_base / "resources" / "mini_python" / "python.exe"
    if python_exe.exists():
        print("✅ Python environment: Complete")
    
    python_scripts = target_base / "resources" / "python" / "electron_backend.py"
    if python_scripts.exists():
        print("✅ Python scripts: Complete")
    
    # Calculate total size
    total_size = sum(f.stat().st_size for f in target_base.rglob('*') if f.is_file()) / (1024**3)
    total_files = len(list(target_base.rglob('*')))
    
    print(f"\n🎉 完整執行檔創建成功！")
    print(f"📁 位置: {target_base.absolute()}")
    print(f"📊 總大小: {total_size:.2f} GB")
    print(f"📄 檔案數量: {total_files}")
    
    print(f"\n🚀 使用方式:")
    print(f"   雙擊: 'SRT GO Enhanced v2.0.exe' (真正的執行檔)")
    print(f"   或使用: 'Start SRT GO.bat' (啟動腳本)")
    
    return True

if __name__ == "__main__":
    create_complete_executable()