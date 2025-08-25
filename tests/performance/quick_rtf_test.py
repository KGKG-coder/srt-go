#!/usr/bin/env python3
"""
快速RTF測試 - 使用系統Python和現有測試音頻
"""

import time
import json
import subprocess
import sys
from pathlib import Path

def quick_rtf_benchmark():
    """執行快速RTF測試"""
    
    print("=== Quick RTF Performance Test ===")
    
    # 使用系統Python和主開發路徑
    backend_script = Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "python" / "electron_backend.py"
    test_audio = Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "test_VIDEO" / "hutest.mp4"
    
    print(f"Backend script: {backend_script}")
    print(f"Test audio: {test_audio}")
    print(f"Backend exists: {backend_script.exists()}")
    print(f"Audio exists: {test_audio.exists()}")
    
    if not backend_script.exists() or not test_audio.exists():
        print("ERROR: Required files not found")
        return
    
    # 創建輸出目錄
    output_dir = Path("rtf_test_output")
    output_dir.mkdir(exist_ok=True)
    
    print()
    print("=== Test Configurations ===")
    
    # 測試配置 - 簡化版本，只測試核心功能
    test_configs = [
        {"model": "medium", "gpu": False, "name": "Medium_CPU"},
        {"model": "small", "gpu": False, "name": "Small_CPU"},
        # {"model": "large", "gpu": False, "name": "Large_CPU"},  # 註釋掉以節省時間
        {"model": "medium", "gpu": True, "name": "Medium_GPU"},  # 會自動降級到CPU如果GPU不可用
    ]
    
    results = []
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n[{i}/{len(test_configs)}] Testing: {config['name']}")
        print(f"  Model: {config['model']}")
        print(f"  GPU: {'Enabled' if config['gpu'] else 'Disabled'}")
        
        # 設置
        settings = {
            "model": config["model"],
            "language": "auto",
            "outputFormat": "srt",
            "customDir": str(output_dir),
            "enable_gpu": config["gpu"],
            "enablePureVoiceMode": True,  # 使用預設的adaptive voice detection
            "vad_threshold": 0.35
        }
        
        # 命令
        cmd = [
            sys.executable,  # 使用系統Python
            str(backend_script),
            "--files", json.dumps([str(test_audio)]),
            "--settings", json.dumps(settings),
            "--corrections", json.dumps([])
        ]
        
        print(f"  Running test...")
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=120  # 2分鐘超時
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # 檢查結果
            success = result.returncode == 0
            output_files = list(output_dir.glob("*.srt"))
            
            if success and output_files:
                srt_file = output_files[-1]  # 使用最新的文件
                file_size = srt_file.stat().st_size
                
                if file_size > 0:
                    # 估算RTF（假設音頻約11.3秒，基於之前的測試）
                    estimated_duration = 11.3
                    rtf = processing_time / estimated_duration
                    
                    print(f"  [+] SUCCESS: {processing_time:.1f}s")
                    print(f"  [+] RTF: {rtf:.3f}")
                    
                    # 性能評級
                    if rtf <= 0.2:
                        rating = "Excellent"
                    elif rtf <= 0.5:
                        rating = "Good"
                    elif rtf <= 1.0:
                        rating = "Acceptable"
                    else:
                        rating = "Needs Improvement"
                    
                    print(f"  [+] Rating: {rating}")
                    
                    # 檢查字幕內容
                    try:
                        content = srt_file.read_text(encoding='utf-8')
                        subtitle_count = content.count('-->')
                        print(f"  [+] Subtitles: {subtitle_count} segments")
                    except:
                        pass
                    
                    results.append({
                        "name": config["name"],
                        "model": config["model"],
                        "gpu": config["gpu"],
                        "processing_time": processing_time,
                        "rtf": rtf,
                        "rating": rating,
                        "success": True
                    })
                    
                else:
                    print(f"  [-] FAILED: Empty output file")
                    results.append({
                        "name": config["name"],
                        "success": False,
                        "error": "Empty output"
                    })
            else:
                print(f"  [-] FAILED: Processing error")
                if result.stderr:
                    print(f"  [-] Error: {result.stderr[:200]}...")
                results.append({
                    "name": config["name"],
                    "success": False,
                    "error": "Processing failed"
                })
                
        except subprocess.TimeoutExpired:
            print(f"  [-] TIMEOUT: Exceeded 2 minutes")
            results.append({
                "name": config["name"],
                "success": False,
                "error": "Timeout"
            })
        except Exception as e:
            print(f"  [-] ERROR: {e}")
            results.append({
                "name": config["name"],
                "success": False,
                "error": str(e)
            })
    
    print()
    print("=== RTF Performance Summary ===")
    
    successful_tests = [r for r in results if r.get("success", False)]
    
    if successful_tests:
        print("Successful Tests:")
        for result in successful_tests:
            print(f"  {result['name']}: RTF {result['rtf']:.3f} ({result['rating']})")
        
        print()
        print("Performance Analysis:")
        
        # 計算平均RTF
        avg_rtf = sum(r["rtf"] for r in successful_tests) / len(successful_tests)
        print(f"  Average RTF: {avg_rtf:.3f}")
        
        # 最佳性能
        best_test = min(successful_tests, key=lambda x: x["rtf"])
        print(f"  Best Performance: {best_test['name']} (RTF: {best_test['rtf']:.3f})")
        
        # GPU vs CPU比較（如果有）
        cpu_tests = [r for r in successful_tests if not r["gpu"]]
        gpu_tests = [r for r in successful_tests if r["gpu"]]
        
        if cpu_tests:
            cpu_avg = sum(r["rtf"] for r in cpu_tests) / len(cpu_tests)
            print(f"  CPU Average RTF: {cpu_avg:.3f}")
        
        if gpu_tests:
            gpu_avg = sum(r["rtf"] for r in gpu_tests) / len(gpu_tests)
            print(f"  GPU Average RTF: {gpu_avg:.3f}")
            
            if cpu_tests and gpu_tests:
                speedup = cpu_avg / gpu_avg
                print(f"  GPU Speedup: {speedup:.1f}x")
        
        print()
        print("RTF Performance Targets:")
        print("  RTF <= 0.2: Excellent (Real-time capable)")
        print("  RTF <= 0.5: Good (Batch processing suitable)")  
        print("  RTF <= 1.0: Acceptable (Basic requirement)")
        print("  RTF > 1.0: Needs Improvement")
        
    else:
        print("No successful tests - system may need configuration")
        
    failed_tests = [r for r in results if not r.get("success", False)]
    if failed_tests:
        print()
        print("Failed Tests:")
        for result in failed_tests:
            print(f"  {result['name']}: {result.get('error', 'Unknown error')}")
    
    print()
    print("=== RTF Benchmark Complete ===")

if __name__ == "__main__":
    quick_rtf_benchmark()