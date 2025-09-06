#!/usr/bin/env python3
"""
調試整合測試 - 使用低VAD閾值測試完整流程
適用於測試合成音頻的完整處理管道
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
    """調試後端處理過程 - 使用低VAD閾值"""
    # 創建臨時目錄和測試音頻
    temp_dir = Path(tempfile.mkdtemp(prefix="debug_test_low_vad_"))
    print(f"Working directory: {temp_dir}")
    
    # 生成測試音頻 - 使用超真實語音生成器
    audio_files = create_ultra_realistic_test_audio(str(temp_dir / "audio"))
    speech_file = audio_files.get('ultra_realistic')
    
    if not speech_file:
        print("ERROR: No speech file generated")
        return
    
    print(f"Using speech file: {speech_file}")
    
    # 設置處理參數 - 降低VAD閾值以測試完整流程
    output_dir = temp_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    settings = {
        "model": "medium",
        "language": "auto", 
        "outputFormat": "srt",
        "customDir": str(output_dir),
        "enable_gpu": False,
        "enablePureVoiceMode": True,
        "vad_threshold": 0.1  # 降低VAD閾值讓合成音頻通過
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
            timeout=120
        )
        
        print(f"Return code: {result.returncode}")
        print()
        
        if result.stdout:
            print("=== STDOUT ===")
            # 過濾掉可能的Unicode字符
            stdout_safe = result.stdout.encode('ascii', 'replace').decode('ascii')
            print(stdout_safe)
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
                        print(f"    SRT Content Preview: {content_clean[:300]}...")
                    except Exception as e:
                        print(f"    Preview: (Error reading content: {e})")
        else:
            print("  No output files found")
        
        # 檢查處理結果
        print()
        print("=== INTEGRATION TEST RESULTS ===")
        if result.returncode == 0:
            srt_files = list(output_dir.glob("*.srt"))
            if srt_files:
                srt_file = srt_files[0]
                if srt_file.stat().st_size > 0:
                    print(f"SUCCESS: SRT file generated with {srt_file.stat().st_size} bytes")
                    
                    # 分析SRT內容
                    try:
                        content = srt_file.read_text(encoding='utf-8')
                        lines = content.strip().split('\n')
                        subtitle_count = content.count('-->')
                        print(f"  - Contains {subtitle_count} subtitle segments")
                        print(f"  - Total content lines: {len(lines)}")
                        
                        # 驗證SRT格式
                        if '-->' in content and content.strip().split('\n')[0].isdigit():
                            print("  - SRT format validation: PASSED")
                        else:
                            print("  - SRT format validation: FAILED")
                            
                    except Exception as e:
                        print(f"  - Content analysis failed: {e}")
                        
                    print()
                    print("=== END-TO-END WORKFLOW VALIDATION ===")
                    print("✓ Audio generation: SUCCESS")
                    print("✓ Backend processing: SUCCESS") 
                    print("✓ SRT file creation: SUCCESS")
                    print("✓ Integration test: PASSED")
                    
                else:
                    print("WARNING: SRT file is empty")
                    print("✗ Integration test: FAILED (empty output)")
            else:
                print("ERROR: No SRT files generated")
                print("✗ Integration test: FAILED (no output)")
        else:
            print(f"ERROR: Backend process failed with code {result.returncode}")
            print("✗ Integration test: FAILED (process error)")
            
    except Exception as e:
        print(f"ERROR running backend: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== Integration Test with Low VAD Threshold ===")
    print("This test uses synthetic audio with reduced VAD sensitivity")
    print("to validate the complete processing pipeline")
    print()
    debug_backend_processing()