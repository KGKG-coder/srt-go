#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動生成的性能測試腳本: quick_validation
快速驗證所有性能模式
預估執行時間: 5-10分鐘
"""

import sys
import os
import time
import subprocess
import json
from pathlib import Path

# 添加父目錄到路徑以便導入
sys.path.append(str(Path(__file__).parent.parent))

def run_performance_test():
    """執行性能測試"""
    print("=== quick_validation 性能測試 ===")
    print("描述: 快速驗證所有性能模式")
    print("預估時間: 5-10分鐘")
    print()
    
    test_files = [
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\SRTGO\\srt中文final_copy\\venv310\\Lib\\site-packages\\scipy\\io\\tests\\data\\test-44100Hz-le-1ch-4bytes-incomplete-chunk.wav",
        "name": "test-44100Hz-le-1ch-4bytes-incomplete-chunk.wav",
        "size": 13,
        "size_mb": 0.0,
        "estimated_duration": 9.918212890625e-05,
        "extension": ".wav"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\SRTGO\\srt_whisper_lite\\portable_python\\Lib\\site-packages\\scipy\\io\\tests\\data\\test-44100Hz-le-1ch-4bytes-incomplete-chunk.wav",
        "name": "test-44100Hz-le-1ch-4bytes-incomplete-chunk.wav",
        "size": 13,
        "size_mb": 0.0,
        "estimated_duration": 9.918212890625e-05,
        "extension": ".wav"
    }
]
    performance_modes = ['auto', 'gpu', 'cpu']
    
    results = []
    
    for file_info in test_files:
        file_path = file_info['path']
        if not Path(file_path).exists():
            print(f"警告: 檔案不存在 {file_path}")
            continue
            
        print(f"測試檔案: {file_info['name']} ({file_info['estimated_duration']:.1f}s)")
        
        for mode in performance_modes:
            print(f"  測試模式: {mode}")
            
            # 構建測試命令
            # 構建設定JSON
            enable_gpu_str = "true" if mode == "gpu" else "false"
            settings_json = '{"model":"large","language":"auto","performanceMode":"' + mode + '","outputFormat":"srt","customDir":"C:/temp/test_results","enable_gpu":' + enable_gpu_str + '}'
            
            cmd = [
                "python",
                str(Path(__file__).parent.parent / "electron_backend.py"),
                "--files", f'["{file_path}"]',
                "--settings", settings_json,
                "--corrections", "[]"
            ]
            
            # 執行測試
            start_time = time.time()
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                end_time = time.time()
                
                processing_time = end_time - start_time
                rtf = processing_time / file_info['estimated_duration']
                
                test_result = {
                    'file': file_info['name'],
                    'mode': mode,
                    'processing_time': processing_time,
                    'audio_duration': file_info['estimated_duration'],
                    'rtf': rtf,
                    'success': result.returncode == 0,
                    'stdout': result.stdout[:500],  # 前500字符
                    'stderr': result.stderr[:500] if result.stderr else None
                }
                
                results.append(test_result)
                
                print(f"    處理時間: {processing_time:.1f}s")
                print(f"    RTF: {rtf:.3f}")
                print(f"    狀態: {'成功' if test_result['success'] else '失敗'}")
                
                if not test_result['success']:
                    print(f"    錯誤: {result.stderr[:200]}")
                
            except subprocess.TimeoutExpired:
                print(f"    超時 (>10分鐘)")
                results.append({'file': file_info['name'], 'mode': mode, 'status': 'timeout'})
            except Exception as e:
                print(f"    異常: {e}")
                results.append({'file': file_info['name'], 'mode': mode, 'status': 'error', 'error': str(e)})
            
            print()
    
    # 保存結果
    result_file = Path(__file__).parent / "quick_validation_results.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({'test_name': 'quick_validation', 'results': results, 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')}, f, ensure_ascii=False, indent=2)
    
    print(f"測試結果已保存至: {result_file}")
    return results

if __name__ == "__main__":
    results = run_performance_test()
    print(f"\nquick_validation 測試完成，共執行 {len(results)} 個測試案例")
