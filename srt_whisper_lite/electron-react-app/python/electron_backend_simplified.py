#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版 Electron 後端處理腳本
直接使用嵌入式 Python，移除智能選擇邏輯
版本：v2.2.1-simplified
"""

import sys
import json
import logging
import argparse
from pathlib import Path
import os

# 設定控制台編碼為UTF-8
if sys.platform.startswith('win'):
    os.system('chcp 65001 > NUL')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('electron_backend.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# 添加當前目錄到路徑
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    logger.info(f"當前工作目錄: {os.getcwd()}")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"腳本目錄: {current_dir}")
    
    from simplified_subtitle_core import SimplifiedSubtitleCore
    from subtitle_formatter import SubtitleFormatter
    from subeasy_multilayer_filter import IntelligentMultiLayerFilter
    logger.info("核心模組導入成功")
except ImportError as e:
    logger.error(f"模組導入失敗: {e}")
    logger.error(f"當前目錄內容: {list(current_dir.iterdir()) if current_dir.exists() else '目錄不存在'}")
    sys.exit(1)

def progress_callback(progress, message):
    """進度回調函數，輸出 JSON 格式給 Electron"""
    progress_data = {
        "type": "progress",
        "percent": progress,
        "filename": message,
        "message": message
    }
    output = f"PROGRESS:{json.dumps(progress_data, ensure_ascii=False)}"
    print(output)
    sys.stdout.flush()
    return True

def process_subtitle_files(files, settings, corrections):
    """處理字幕文件"""
    try:
        # 解析設置
        model_size = settings.get('model', 'large')
        language = settings.get('language', None)
        output_language = settings.get('outputLanguage', None)
        
        if language == 'auto':
            language = None
        elif language == 'zh-TW' or language == 'zh-CN':
            language = 'zh'
            
        if output_language == 'same':
            output_language = None
        output_format = settings.get('outputFormat', 'srt')
        output_dir = settings.get('customDir', str(current_dir))
        
        if not output_dir and files:
            output_dir = str(Path(files[0]).parent)
        
        logger.info(f"開始處理 {len(files)} 個文件")
        logger.info(f"設置: 模型={model_size}, 語言={language}, 格式={output_format}")
        
        # 初始化核心
        core = SimplifiedSubtitleCore(
            model_size=model_size,
            debug_mode=False
        )
        
        # 設置純人聲模式（預設啟用）
        if settings.get('enablePureVoiceMode', True):
            core.enable_pure_voice_mode = True
            logger.info("已啟用純人聲模式（自適應語音檢測）")
        
        # 傳遞VAD閾值
        core.vad_threshold = settings.get('vad_threshold', 0.35)
        logger.info(f"設置VAD閾值: {core.vad_threshold}")
        
        # 初始化模型
        if not core.initialize(progress_callback):
            logger.error("模型初始化失敗")
            return False
        
        results = []
        
        for i, file_path in enumerate(files):
            logger.info(f"處理文件 {i+1}/{len(files)}: {file_path}")
            
            # 構建輸出文件路徑
            input_path = Path(file_path)
            output_filename = f"{input_path.stem}.{output_format}"
            output_file = Path(output_dir) / output_filename
            
            # 創建專門的進度回調
            def file_progress_callback(progress, message):
                file_progress = 10 + (i * 80) // len(files) + (progress * 80) // (len(files) * 100)
                return progress_callback(file_progress, f"{input_path.name}: {message}")
            
            progress_callback(10 + (i * 80) // len(files), f"開始處理: {input_path.name}")
            
            # 生成字幕
            success = core.generate_subtitle(
                file_path,
                str(output_file),
                language=language,
                output_language=output_language,
                format=output_format,
                progress_callback=file_progress_callback
            )
            
            if success:
                results.append({
                    "input": file_path,
                    "output": str(output_file),
                    "success": True
                })
                logger.info(f"成功生成字幕: {output_file}")
            else:
                results.append({
                    "input": file_path,
                    "output": None,
                    "success": False
                })
                logger.error(f"字幕生成失敗: {file_path}")
        
        progress_callback(100, "處理完成")
        
        return results
        
    except Exception as e:
        logger.error(f"處理過程中出錯: {e}", exc_info=True)
        return False

def main():
    """主函數 - 直接處理，不再使用智能選擇"""
    parser = argparse.ArgumentParser(description='簡化版字幕生成後端')
    parser.add_argument('--files', type=str, required=True, help='要處理的文件列表（JSON格式）')
    parser.add_argument('--settings', type=str, required=True, help='處理設置（JSON格式）')
    parser.add_argument('--corrections', type=str, default='[]', help='自定義校正（JSON格式）')
    
    args = parser.parse_args()
    
    try:
        # 解析參數
        files = json.loads(args.files)
        settings = json.loads(args.settings)
        corrections = json.loads(args.corrections)
        
        logger.info("="*50)
        logger.info("簡化版後端啟動")
        logger.info(f"Python版本: {sys.version}")
        logger.info(f"執行路徑: {sys.executable}")
        logger.info("="*50)
        
        # 直接處理文件，不再進行環境選擇
        result = process_subtitle_files(files, settings, corrections)
        
        if result:
            # 發送成功結果
            success_data = {
                "type": "result",
                "data": {
                    "success": True,
                    "results": result,
                    "message": "所有文件處理完成"
                }
            }
            print(f"RESULT:{json.dumps(success_data, ensure_ascii=False)}")
        else:
            # 發送失敗結果
            error_data = {
                "type": "error",
                "data": {
                    "success": False,
                    "message": "處理失敗",
                    "code": "PROCESSING_ERROR"
                }
            }
            print(f"ERROR:{json.dumps(error_data, ensure_ascii=False)}")
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析錯誤: {e}")
        error_data = {
            "type": "error",
            "data": {
                "success": False,
                "message": f"參數解析錯誤: {str(e)}",
                "code": "JSON_PARSE_ERROR"
            }
        }
        print(f"ERROR:{json.dumps(error_data, ensure_ascii=False)}")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"未預期的錯誤: {e}", exc_info=True)
        error_data = {
            "type": "error",
            "data": {
                "success": False,
                "message": f"系統錯誤: {str(e)}",
                "code": "SYSTEM_ERROR"
            }
        }
        print(f"ERROR:{json.dumps(error_data, ensure_ascii=False)}")
        sys.exit(1)

if __name__ == "__main__":
    main()