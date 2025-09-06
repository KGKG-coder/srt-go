#!/usr/bin/env python3
"""
調試整合測試 - 直接運行後端看看發生什麼
"""

import tempfile
import sys
import subprocess
from pathlib import Path
import json

# 設置路徑
sys.path.insert(0, str(Path(__file__).parent.parent / "srt_whisper_lite" / "electron-react-app" / "python"))
sys.path.insert(0, str(Path(__file__).parent))

from utils.ultra_realistic_speech_generator import create_ultra_realistic_test_audio

def debug_backend_processing():
    """調試後端處理過程"""
    # 創建臨時目錄和測試音頻
    temp_dir = Path(tempfile.mkdtemp(prefix="debug_test_"))
    print(f"Working directory: {temp_dir}")
    
    # 生成測試音頻 - 使用超真實語音生成器
    audio_files = create_ultra_realistic_test_audio(str(temp_dir / "audio"))
    speech_file = audio_files.get('ultra_realistic')
    
    if not speech_file:
        print("ERROR: No speech file generated")
        return
    
    print(f"Using speech file: {speech_file}")
    
    # 設置處理參數
    output_dir = temp_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    settings = {
        "model": "medium",
        "language": "auto",
        "outputFormat": "srt", 
        "customDir": str(output_dir),
        "enable_gpu": False,
        "enablePureVoiceMode": True
    }
    
    # 直接調用後端腳本
    python_script = Path(__file__).parent.parent / "srt_whisper_lite" / "electron-react-app" / "python" / "electron_backend.py"
    
    cmd = [
        sys.executable,
        str(python_script),
        "--files", json.dumps([speech_file]),
        "--settings", json.dumps(settings),
        "--corrections", json.dumps([])
    ]
    
    print("Running command:", " ".join(str(x) for x in cmd))
    print()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=120  # 增加超時時間
        )
        
        print(f"Return code: {result.returncode}")
        print()
        
        if result.stdout:
            print("=== STDOUT ===")
            # 過濾掉可能的Unicode字符
            stdout_safe = result.stdout.encode('ascii', 'replace').decode('ascii')
            print(stdout_safe)  # 顯示全部stdout
            print()
        
        if result.stderr:
            print("=== STDERR ===")
            stderr_safe = result.stderr.encode('ascii', 'replace').decode('ascii')
            print(stderr_safe[:1000])
            print()
        
        # 檢查輸出目錄
        print("=== OUTPUT DIRECTORY CONTENTS ===")
        output_files = list(output_dir.iterdir())
        if output_files:
            for file in output_files:
                size = file.stat().st_size if file.is_file() else "DIR"
                print(f"  {file.name}: {size} bytes")
                
                # 如果是SRT文件，顯示內容預覽
                if file.suffix == '.srt' and file.stat().st_size > 0:
                    try:
                        content = file.read_text(encoding='utf-8', errors='replace')
                        # 清理Unicode字符用於安全顯示
                        content_clean = content.encode('ascii', 'replace').decode('ascii')
                        print(f"    Preview: {content_clean[:200]}...")
                    except Exception as e:
                        print(f"    Preview: (Error reading content: {e})")
        else:
            print("  No output files found")
        
        # 檢查是否有其他位置的輸出文件
        print()
        print("=== SEARCHING ALL .srt FILES IN TEMP DIR ===")
        all_srt_files = list(temp_dir.rglob("*.srt"))
        if all_srt_files:
            for srt_file in all_srt_files:
                size = srt_file.stat().st_size
                print(f"  Found: {srt_file} ({size} bytes)")
                if size > 0:
                    try:
                        content = srt_file.read_text(encoding='utf-8', errors='replace')
                        content_clean = content.encode('ascii', 'replace').decode('ascii')
                        print(f"    Preview: {content_clean[:200]}...")
                    except Exception as e:
                        print(f"    Preview: (Error reading: {e})")
        else:
            print("  No .srt files found anywhere in temp directory")
        
    except Exception as e:
        print(f"ERROR running backend: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_backend_processing()