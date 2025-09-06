import os
import shutil
from pathlib import Path

def create_exe_launcher():
    """創建一個 EXE 啟動器包裝便攜版"""
    
    print("🚀 Creating EXE launcher for SRT GO Enhanced v2.0...")
    
    # 源目錄和目標目錄
    source_dir = Path("dist/SRT-GO-Enhanced-v2.0-Portable")
    target_dir = Path("dist/SRT-GO-Enhanced-v2.0-EXE")
    
    # 確保目標目錄存在
    target_dir.mkdir(exist_ok=True)
    
    print(f"📁 Source: {source_dir}")
    print(f"📁 Target: {target_dir}")
    
    # 複製所有檔案到目標目錄
    if source_dir.exists():
        print("📋 Copying files...")
        
        # 複製所有內容
        for item in source_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, target_dir / item.name)
                print(f"✅ Copied: {item.name}")
            elif item.is_dir():
                shutil.copytree(item, target_dir / item.name, dirs_exist_ok=True)
                print(f"✅ Copied directory: {item.name}")
    
    # 創建 EXE 啟動器腳本
    exe_launcher_content = '''@echo off
cd /d "%~dp0"
echo 🚀 Starting SRT GO Enhanced v2.0...
start "" /min cmd /c "SRT GO Enhanced v2.0.bat"
'''
    
    with open(target_dir / "SRT GO Enhanced v2.0 Launcher.bat", 'w', encoding='utf-8') as f:
        f.write(exe_launcher_content)
    
    print("✅ Created launcher batch file")
    
    # 創建說明檔案
    readme_content = '''# SRT GO Enhanced v2.0 EXE版本

## 🚀 執行方式

雙擊以下任一檔案啟動應用程式：

1. **SRT GO Enhanced v2.0.bat** - 顯示啟動過程
2. **SRT GO Enhanced v2.0 Launcher.bat** - 最小化啟動

## 📋 檔案說明

這是一個包含所有必要檔案的完整版本：
- 內建 Python 3.11 環境
- 包含 Large V3 Turbo AI 模型
- Enhanced Voice Detector v2.0 技術
- 現代化 Electron + React GUI

## 💻 系統需求

- Windows 10/11 (64-bit)
- 4GB+ RAM (建議 8GB+)
- Node.js 16+ (首次運行時自動安裝 Electron)

## 🔧 首次使用

1. 確保已安裝 Node.js
2. 雙擊啟動檔案
3. 等待 Electron 環境安裝完成
4. 開始使用 AI 字幕生成功能

---
SRT GO Enhanced v2.0 - 革命性 AI 字幕生成工具
'''
    
    with open(target_dir / "README_EXE.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ Created README file")
    
    # 檢查結果
    total_files = len(list(target_dir.rglob('*')))
    total_size = sum(f.stat().st_size for f in target_dir.rglob('*') if f.is_file()) / (1024**3)
    
    print("\n🎉 EXE版本創建完成！")
    print(f"📁 位置: {target_dir.absolute()}")
    print(f"📊 包含檔案: {total_files} 個")
    print(f"📏 總大小: {total_size:.2f} GB")
    print("\n💡 啟動方式:")
    print("   - 雙擊 'SRT GO Enhanced v2.0.bat'")
    print("   - 或雙擊 'SRT GO Enhanced v2.0 Launcher.bat'")

if __name__ == "__main__":
    create_exe_launcher()