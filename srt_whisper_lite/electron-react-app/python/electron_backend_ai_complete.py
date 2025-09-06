#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整 AI 功能簡化版後端 - 使用 Faster-Whisper 進行真實語音轉錄
"""

import sys
import json
import argparse
from pathlib import Path
import os
import time

# 設定編碼
if sys.platform.startswith('win'):
    os.system('chcp 65001 > NUL 2>&1')

def send_progress(percent, filename="", message=""):
    """發送進度更新"""
    progress_data = {
        "type": "progress",
        "percent": percent,
        "filename": filename,
        "message": message
    }
    print(f"PROGRESS:{json.dumps(progress_data, ensure_ascii=False)}")
    sys.stdout.flush()

def send_result(data):
    """發送結果數據"""
    result_data = {
        "type": "result", 
        "data": data
    }
    print(f"RESULT:{json.dumps(result_data, ensure_ascii=False)}")
    sys.stdout.flush()

def send_error(message, code="UNKNOWN_ERROR"):
    """發送錯誤信息"""
    error_data = {
        "type": "error",
        "data": {
            "success": False,
            "message": message,
            "code": code
        }
    }
    print(f"ERROR:{json.dumps(error_data, ensure_ascii=False)}")
    sys.stdout.flush()

def check_dependencies():
    """檢查依賴是否可用"""
    missing_deps = []
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import soundfile
    except ImportError:
        missing_deps.append("soundfile")
    
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        missing_deps.append("faster-whisper")
    
    return missing_deps

def process_audio_file(file_path, model, language="auto"):
    """處理單個音頻檔案"""
    try:
        from faster_whisper import WhisperModel
        import soundfile as sf
        import os
        
        # 檢查檔案是否存在
        if not os.path.exists(file_path):
            return {
                "input": file_path,
                "output": None,
                "success": False,
                "error": f"檔案不存在: {file_path}"
            }
        
        # 嘗試載入音頻檔案（測試格式）
        try:
            data, samplerate = sf.read(file_path)
            send_progress(10, os.path.basename(file_path), "音頻檔案讀取成功")
        except Exception as e:
            return {
                "input": file_path,
                "output": None,  
                "success": False,
                "error": f"無法讀取音頻檔案: {e}"
            }
        
        # 初始化 Whisper 模型
        try:
            if model == "large":
                model_name = "large-v3"
            elif model == "medium":
                model_name = "medium"
            else:
                model_name = "base"
            
            whisper_model = WhisperModel(model_name, device="cpu", compute_type="int8")
            send_progress(30, os.path.basename(file_path), f"載入 {model_name} 模型")
        except Exception as e:
            return {
                "input": file_path,
                "output": None,
                "success": False,
                "error": f"模型載入失敗: {e}"
            }
        
        # 執行語音轉錄
        try:
            send_progress(50, os.path.basename(file_path), "開始 AI 語音轉錄...")
            
            segments, info = whisper_model.transcribe(
                file_path, 
                language=None if language == "auto" else language,
                beam_size=5,
                word_timestamps=False
            )
            
            send_progress(80, os.path.basename(file_path), "處理轉錄結果...")
            
            # 生成字幕內容
            srt_content = ""
            segment_count = 0
            
            for segment in segments:
                segment_count += 1
                start_time = segment.start
                end_time = segment.end
                text = segment.text.strip()
                
                # 轉換時間格式 (秒 -> SRT 時間格式)
                start_h = int(start_time // 3600)
                start_m = int((start_time % 3600) // 60)
                start_s = int(start_time % 60)
                start_ms = int((start_time % 1) * 1000)
                
                end_h = int(end_time // 3600)
                end_m = int((end_time % 3600) // 60)
                end_s = int(end_time % 60)
                end_ms = int((end_time % 1) * 1000)
                
                srt_content += f"{segment_count}\n"
                srt_content += f"{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms:03d} --> {end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms:03d}\n"
                srt_content += f"{text}\n\n"
            
            # 生成輸出檔案名
            input_path = Path(file_path)
            output_path = input_path.with_suffix('.srt')
            
            # 寫入字幕檔案
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            send_progress(100, os.path.basename(file_path), "轉錄完成")
            
            return {
                "input": file_path,
                "output": str(output_path),
                "success": True,
                "segments": segment_count,
                "language": info.language if hasattr(info, 'language') else language,
                "duration": info.duration if hasattr(info, 'duration') else "unknown"
            }
            
        except Exception as e:
            return {
                "input": file_path,
                "output": None,
                "success": False,
                "error": f"轉錄失敗: {e}"
            }
    
    except Exception as e:
        return {
            "input": file_path,
            "output": None,
            "success": False,
            "error": f"處理異常: {e}"
        }

def main():
    """主函數 - 完整 AI 轉錄功能"""
    parser = argparse.ArgumentParser(description='完整 AI 字幕生成後端')
    parser.add_argument('--files', type=str, required=True, help='要處理的文件列表（JSON格式）')
    parser.add_argument('--settings', type=str, required=True, help='處理設置（JSON格式）')
    parser.add_argument('--corrections', type=str, default='[]', help='自定義校正（JSON格式）')
    
    args = parser.parse_args()
    
    try:
        # 解析參數
        files = json.loads(args.files)
        settings = json.loads(args.settings)
        corrections = json.loads(args.corrections)
        
        print("=" * 50)
        print("完整 AI 字幕生成後端")
        print(f"Python 版本: {sys.version}")
        print(f"執行路徑: {sys.executable}")
        print("=" * 50)
        
        print(f"文件數量: {len(files)}")
        print(f"設置: {settings}")
        print(f"校正數量: {len(corrections)}")
        
        # 檢查依賴
        send_progress(5, "", "檢查 AI 依賴...")
        missing_deps = check_dependencies()
        
        if missing_deps:
            error_msg = f"缺少依賴: {', '.join(missing_deps)}"
            send_error(error_msg, "MISSING_DEPENDENCIES")
            return False
        
        # 處理每個檔案
        results = []
        total_files = len(files)
        
        for i, file_path in enumerate(files):
            send_progress(10 + (i * 80 // total_files), 
                         os.path.basename(file_path), 
                         f"處理檔案 {i+1}/{total_files}")
            
            result = process_audio_file(
                file_path,
                settings.get("model", "base"),
                settings.get("language", "auto")
            )
            results.append(result)
            
            # 如果某個檔案失敗，記錄但繼續處理其他檔案
            if not result["success"]:
                print(f"檔案處理失敗: {file_path} - {result.get('error', 'Unknown error')}")
        
        # 統計結果
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        # 發送最終結果
        final_result = {
            "success": successful > 0,
            "results": results,
            "summary": {
                "total": len(files),
                "successful": successful,
                "failed": failed
            },
            "message": f"處理完成：{successful}/{len(files)} 成功"
        }
        
        send_result(final_result)
        return successful > 0
        
    except json.JSONDecodeError as e:
        send_error(f"參數解析錯誤: {str(e)}", "JSON_PARSE_ERROR")
        return False
        
    except Exception as e:
        send_error(f"處理錯誤: {str(e)}", "PROCESSING_ERROR")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)