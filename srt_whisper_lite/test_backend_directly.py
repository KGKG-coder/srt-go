#!/usr/bin/env python3
"""
直接測試 electron_backend.py 的功能
"""

import subprocess
import json
import sys
from pathlib import Path
import os

def test_backend():
    print("直接測試 Electron Backend")
    print("=" * 50)
    
    # 測試參數
    test_files = ["C:\\Users\\USER-ART0\\Desktop\\test.mp4"]  # 假設的測試文件
    test_settings = {
        "model": "tiny",
        "language": "auto", 
        "outputFormat": "srt",
        "customDir": ""
    }
    test_corrections = []
    
    # 準備命令
    current_dir = Path(__file__).parent
    
    # 檢查在打包環境還是開發環境
    packaged_backend = current_dir / "dist" / "SRT_Whisper_Lite" / "_internal" / "electron_backend.py"
    packaged_python = current_dir / "dist" / "SRT_Whisper_Lite" / "_internal" / "portable_python" / "python.exe"
    dev_backend = current_dir / "electron_backend.py"
    
    if packaged_backend.exists() and packaged_python.exists():
        print("使用打包版本進行測試")
        command = str(packaged_python)
        script = str(packaged_backend)
        working_dir = str(packaged_backend.parent)
        print(f"Python: {command}")
        print(f"Script: {script}")
        print(f"Working Dir: {working_dir}")
    elif dev_backend.exists():
        print("使用開發版本進行測試")
        command = "python"
        script = str(dev_backend)
        working_dir = str(current_dir)
        print(f"Python: {command}")
        print(f"Script: {script}")
        print(f"Working Dir: {working_dir}")
    else:
        print("找不到 electron_backend.py")
        return False
    
    # 構建參數
    args = [
        command,
        script,
        '--files', json.dumps(test_files),
        '--settings', json.dumps(test_settings),
        '--corrections', json.dumps(test_corrections)
    ]
    
    print("\n執行命令:")
    print(" ".join(args))
    print("\n" + "=" * 50)
    
    try:
        # 執行命令
        result = subprocess.run(
            args,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8'
        )
        
        print(f"退出碼: {result.returncode}")
        print(f"標準輸出:\n{result.stdout}")
        print(f"錯誤輸出:\n{result.stderr}")
        
        if result.returncode == 0:
            print("Backend 執行成功!")
            return True
        else:
            print("Backend 執行失敗!")
            return False
            
    except subprocess.TimeoutExpired:
        print("Backend 執行超時!")
        return False
    except Exception as e:
        print(f"執行時發生異常: {e}")
        return False

if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1)