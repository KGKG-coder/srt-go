#!/usr/bin/env python3
"""
簡化的 RTF 性能測試 - 基於實際可用的後端路徑
"""

import time
import json
import subprocess
import sys
from pathlib import Path

def find_working_backend():
    """尋找可用的後端腳本和Python解釋器"""
    
    # 可能的backend路徑
    backend_paths = [
        Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "dist" / "win-unpacked" / "resources" / "resources" / "python" / "electron_backend.py",
        Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "python" / "electron_backend.py"
    ]
    
    # 可能的Python解釋器
    python_paths = [
        Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "dist" / "win-unpacked" / "resources" / "resources" / "mini_python" / "python.exe",
        Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "mini_python" / "python.exe",
        Path(sys.executable)  # 系統Python
    ]
    
    print("=== Backend and Python Discovery ===")
    
    # 檢查backend腳本
    backend_script = None
    for path in backend_paths:
        print(f"Checking backend: {path}")
        if path.exists():
            backend_script = path
            print(f"[+] Found backend at: {path}")
            break
        else:
            print(f"[-] Not found: {path}")
    
    # 檢查Python解釋器
    python_exe = None
    for path in python_paths:
        print(f"Checking Python: {path}")
        if path.exists():
            python_exe = path
            print(f"[+] Found Python at: {path}")
            break
        else:
            print(f"[-] Not found: {path}")
    
    return backend_script, python_exe

def test_simple_rtf():
    """執行簡單的RTF測試"""
    
    backend_script, python_exe = find_working_backend()
    
    if not backend_script or not python_exe:
        print("ERROR: Required components not found")
        if not backend_script:
            print("  - Backend script not found")
        if not python_exe:
            print("  - Python interpreter not found")
        return
    
    print()
    print("=== Simple RTF Test ===")
    
    # 使用現有的測試音頻文件（如果有）
    test_audio_candidates = [
        Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "test_VIDEO" / "hutest.mp4",
        Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "test_VIDEO" / "C0485.MP4",
        Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "test_VIDEO" / "DRLIN.mp4"
    ]
    
    test_audio = None
    for audio_path in test_audio_candidates:
        if audio_path.exists():
            test_audio = str(audio_path)
            print(f"Using test audio: {audio_path.name}")
            break
    
    if not test_audio:
        print("ERROR: No test audio files found")
        print("Searched locations:")
        for path in test_audio_candidates:
            print(f"  - {path}")
        return
    
    # 測試設置
    settings = {
        "model": "medium",
        "language": "auto",
        "outputFormat": "srt",
        "customDir": str(Path.cwd() / "temp_rtf_test"),
        "enable_gpu": False,
        "enablePureVoiceMode": True
    }
    
    # 創建輸出目錄
    output_dir = Path(settings["customDir"])
    output_dir.mkdir(exist_ok=True)
    
    # 構建命令
    cmd = [
        str(python_exe),
        str(backend_script),
        "--files", json.dumps([test_audio]),
        "--settings", json.dumps(settings),
        "--corrections", json.dumps([])
    ]
    
    print(f"Command: {' '.join([str(x) for x in cmd[:2]])} [parameters...]")
    print()
    
    # 執行測試
    print("Starting RTF performance test...")
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=180  # 3分鐘超時
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"Processing completed in {processing_time:.1f} seconds")
        print(f"Return code: {result.returncode}")
        
        # 檢查輸出結果
        output_files = list(output_dir.glob("*.srt"))
        if output_files and result.returncode == 0:
            srt_file = output_files[0]
            file_size = srt_file.stat().st_size
            
            print(f"[+] SUCCESS: Generated {srt_file.name} ({file_size} bytes)")
            
            # 估算音頻長度（簡化）
            estimated_duration = 15.0  # 秒，基於測試文件的估計
            rtf = processing_time / estimated_duration
            
            print(f"[+] Estimated RTF: {rtf:.3f}")
            
            # RTF評級
            if rtf <= 0.2:
                rating = "Excellent"
            elif rtf <= 0.5:
                rating = "Good" 
            elif rtf <= 1.0:
                rating = "Acceptable"
            else:
                rating = "Needs Improvement"
            
            print(f"[+] Performance Rating: {rating}")
            
            # 顯示部分輸出內容
            try:
                content = srt_file.read_text(encoding='utf-8')
                subtitle_count = content.count('-->')
                print(f"[+] Generated {subtitle_count} subtitle segments")
            except:
                pass
                
        else:
            print("[-] FAILED: No output files generated or process failed")
            if result.stderr:
                print("Error output:")
                print(result.stderr[:500])
                
    except subprocess.TimeoutExpired:
        print("[-] TIMEOUT: Test took longer than 3 minutes")
    except Exception as e:
        print(f"[-] ERROR: {e}")
    
    print()
    print("=== RTF Test Complete ===")

if __name__ == "__main__":
    test_simple_rtf()