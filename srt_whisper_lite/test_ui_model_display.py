#!/usr/bin/env python3
"""
測試 UI 模型顯示和實際執行模型的一致性
"""

import json
import subprocess
import sys
from pathlib import Path

def test_backend_model():
    """測試後端是否確實使用 LARGE 模型"""
    print("測試後端模型設定...")
    
    # 測試設定
    test_settings = {
        "model": "medium",  # 故意設定為 medium 來測試強制修正
        "language": "auto",
        "outputFormat": "srt",
        "customDir": "C:/Users/USER-ART0/Desktop/test_model_force",
        "enable_gpu": False
    }
    
    test_files = ["C:/Users/USER-ART0/Desktop/hutest.mp3"]
    test_corrections = []
    
    # 建立輸出目錄
    Path(test_settings["customDir"]).mkdir(exist_ok=True)
    
    # 呼叫後端測試
    try:
        cmd = [
            "C:/Users/USER-ART0/Desktop/SRTGO/srt_whisper_lite/mini_python/python.exe",
            "electron_backend.py",
            "--files", json.dumps(test_files),
            "--settings", json.dumps(test_settings),
            "--corrections", json.dumps(test_corrections)
        ]
        
        print(f"執行命令: {' '.join(cmd)}")
        print(f"測試設定: {test_settings}")
        print("預期結果: 後端應自動將 medium 強制修正為 large")
        
        # 注意: 這裡只是展示命令，實際執行會需要音檔
        # result = subprocess.run(cmd, capture_output=True, text=True, cwd="C:/Users/USER-ART0/Desktop/SRTGO/srt_whisper_lite")
        print("[INFO] 命令已準備好，可以手動執行來測試強制修正功能")
        
    except Exception as e:
        print(f"測試時發生錯誤: {e}")

def check_localStorage_script():
    """檢查 localStorage 清除腳本內容"""
    script_path = Path("electron-react-app/clear_cache.js")
    
    if script_path.exists():
        print(f"\n清除緩存腳本內容 ({script_path}):")
        print("-" * 40)
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(content)
        print("-" * 40)
        print("請在應用程式的開發者工具 Console 中執行此腳本")
        return True
    else:
        print(f"[ERROR] 清除緩存腳本不存在: {script_path}")
        return False

def main():
    """主函數"""
    print("=" * 60)
    print("測試 UI 模型顯示和實際執行模型的一致性")
    print("=" * 60)
    
    print("1. 後端強制修正測試:")
    test_backend_model()
    
    print("\n2. 清除緩存腳本檢查:")
    check_localStorage_script()
    
    print("\n" + "=" * 60)
    print("測試步驟:")
    print("1. 啟動 SRT GO 應用程式")
    print("2. 檢查設定頁面是否顯示 'Large (專業版)' 模型")
    print("3. 如果顯示不正確，按 F12 開啟開發者工具")
    print("4. 在 Console 中貼上清除緩存腳本的內容並執行")
    print("5. 確認頁面重新載入後顯示正確")
    print("6. 執行實際的字幕生成測試來驗證使用 LARGE 模型")
    print("=" * 60)

if __name__ == "__main__":
    main()