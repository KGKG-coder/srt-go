#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SRT GO 完整版後端 - 商業級 AI 字幕生成
版本: v2.2.1 完整版
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

def check_ai_dependencies():
    """檢查 AI 依賴是否完整可用"""
    missing_deps = []
    optional_deps = []
    
    # 核心依賴檢查
    core_deps = [
        ('faster_whisper', 'Faster-Whisper'),
        ('numpy', 'NumPy'),
        ('soundfile', 'SoundFile')
    ]
    
    for module, name in core_deps:
        try:
            __import__(module)
        except ImportError:
            missing_deps.append(name)
    
    # 可選依賴檢查
    optional_deps_list = [
        ('ctranslate2', 'CTranslate2'),
        ('sklearn', 'Scikit-learn'),
        ('librosa', 'Librosa')
    ]
    
    for module, name in optional_deps_list:
        try:
            __import__(module)
        except ImportError:
            optional_deps.append(name)
    
    return missing_deps, optional_deps

def get_available_models():
    """獲取可用的模型列表"""
    try:
        from faster_whisper import WhisperModel
        
        # 標準模型列表
        models = [
            ("large-v3", "最高精度 (推薦)"),
            ("large-v2", "高精度"),
            ("medium", "平衡性能"),
            ("base", "快速處理"),
            ("small", "輕量級"),
            ("tiny", "極速模式")
        ]
        
        return models
    except ImportError:
        return []

def process_audio_with_whisper(file_path, model_size="base", language="auto", progress_callback=None):
    """使用 Whisper 處理音頻檔案"""
    try:
        from faster_whisper import WhisperModel
        import soundfile as sf
        
        # 檢查檔案存在
        if not os.path.exists(file_path):
            return {"success": False, "error": f"檔案不存在: {file_path}"}
        
        if progress_callback:
            progress_callback(10, os.path.basename(file_path), "檢查音頻檔案...")
        
        # 檢查音頻格式
        try:
            data, samplerate = sf.read(file_path)
            if progress_callback:
                progress_callback(20, os.path.basename(file_path), "音頻檔案驗證通過")
        except Exception as e:
            return {"success": False, "error": f"音頻檔案格式錯誤: {e}"}
        
        # 模型名稱映射
        model_map = {
            "large": "large-v3",
            "medium": "medium", 
            "small": "small",
            "base": "base",
            "tiny": "tiny"
        }
        
        model_name = model_map.get(model_size, "base")
        
        if progress_callback:
            progress_callback(30, os.path.basename(file_path), f"載入 {model_name} 模型...")
        
        # 初始化模型
        model = WhisperModel(
            model_name, 
            device="cpu", 
            compute_type="int8"
        )
        
        if progress_callback:
            progress_callback(50, os.path.basename(file_path), "開始 AI 語音轉錄...")
        
        # 執行轉錄
        segments, info = model.transcribe(
            file_path,
            language=None if language == "auto" else language,
            beam_size=5,
            word_timestamps=False,
            vad_filter=True
        )
        
        if progress_callback:
            progress_callback(80, os.path.basename(file_path), "處理轉錄結果...")
        
        # 生成 SRT 內容
        srt_content = ""
        segment_count = 0
        
        for segment in segments:
            segment_count += 1
            start = segment.start
            end = segment.end
            text = segment.text.strip()
            
            # 時間格式轉換
            start_h = int(start // 3600)
            start_m = int((start % 3600) // 60)
            start_s = int(start % 60)
            start_ms = int((start % 1) * 1000)
            
            end_h = int(end // 3600)
            end_m = int((end % 3600) // 60)
            end_s = int(end % 60)
            end_ms = int((end % 1) * 1000)
            
            srt_content += f"{segment_count}\n"
            srt_content += f"{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms:03d} --> {end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms:03d}\n"
            srt_content += f"{text}\n\n"
        
        # 儲存檔案
        input_path = Path(file_path)
        output_path = input_path.with_suffix('.srt')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        if progress_callback:
            progress_callback(100, os.path.basename(file_path), "轉錄完成")
        
        return {
            "success": True,
            "input": file_path,
            "output": str(output_path),
            "segments": segment_count,
            "language": info.language if hasattr(info, 'language') else language,
            "duration": info.duration if hasattr(info, 'duration') else "unknown"
        }
        
    except Exception as e:
        return {"success": False, "error": f"轉錄過程發生錯誤: {e}"}

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='SRT GO 完整版 AI 字幕生成後端')
    parser.add_argument('--files', type=str, required=True, help='要處理的文件列表（JSON格式）')
    parser.add_argument('--settings', type=str, required=True, help='處理設置（JSON格式）')
    parser.add_argument('--corrections', type=str, default='[]', help='自定義校正（JSON格式）')
    
    args = parser.parse_args()
    
    try:
        # 解析參數
        files = json.loads(args.files)
        settings = json.loads(args.settings)
        corrections = json.loads(args.corrections)
        
        print("=" * 60)
        print("SRT GO 完整版 AI 字幕生成後端")
        print(f"Python 版本: {sys.version}")
        print(f"執行路徑: {sys.executable}")
        print("=" * 60)
        
        print(f"處理檔案: {len(files)} 個")
        print(f"模型設置: {settings.get('model', 'base')}")
        print(f"語言設置: {settings.get('language', 'auto')}")
        
        # 環境檢查
        send_progress(5, "", "檢查 AI 環境...")
        missing_deps, optional_deps = check_ai_dependencies()
        
        if missing_deps:
            error_msg = f"缺少核心依賴: {', '.join(missing_deps)}"
            send_error(error_msg, "MISSING_CORE_DEPENDENCIES")
            return False
        
        if optional_deps:
            print(f"注意: 缺少可選依賴: {', '.join(optional_deps)}")
        
        print("✅ AI 環境檢查通過")
        
        # 處理每個檔案
        results = []
        total_files = len(files)
        
        for i, file_path in enumerate(files):
            print(f"\n處理檔案 {i+1}/{total_files}: {file_path}")
            
            def file_progress_callback(progress, filename, message):
                overall_progress = 10 + (i * 80 // total_files) + (progress * 80 // (total_files * 100))
                send_progress(overall_progress, filename, message)
            
            result = process_audio_with_whisper(
                file_path,
                settings.get("model", "base"),
                settings.get("language", "auto"),
                file_progress_callback
            )
            
            results.append(result)
            
            if result["success"]:
                print(f"✅ 成功: {result['output']}")
            else:
                print(f"❌ 失敗: {result['error']}")
        
        # 統計結果
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        final_result = {
            "success": successful > 0,
            "results": results,
            "summary": {
                "total": len(files),
                "successful": successful,
                "failed": failed,
                "success_rate": f"{successful/len(files)*100:.1f}%" if files else "0%"
            },
            "message": f"完整版 AI 轉錄完成：{successful}/{len(files)} 成功",
            "version": "SRT GO v2.2.1 完整版"
        }
        
        send_result(final_result)
        
        print(f"\n=== 處理完成 ===")
        print(f"成功: {successful}/{len(files)}")
        print(f"成功率: {successful/len(files)*100:.1f}%" if files else "0%")
        
        return successful > 0
        
    except json.JSONDecodeError as e:
        send_error(f"參數解析錯誤: {str(e)}", "JSON_PARSE_ERROR")
        return False
        
    except Exception as e:
        send_error(f"系統錯誤: {str(e)}", "SYSTEM_ERROR")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)