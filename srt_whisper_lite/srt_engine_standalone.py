#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SRT GO 獨立 AI 引擎
專為 PyInstaller 打包設計的獨立執行檔
"""

import sys
import os
import json
import logging
import argparse
from pathlib import Path
import tempfile

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
        logging.FileHandler('srt_engine.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# 動態添加路徑
if getattr(sys, 'frozen', False):
    # PyInstaller 打包環境
    base_path = Path(sys.executable).parent
    sys.path.insert(0, str(base_path))
else:
    # 開發環境
    base_path = Path(__file__).parent
    sys.path.insert(0, str(base_path))

try:
    from simplified_subtitle_core import SimplifiedSubtitleCore
    from model_manager import ModelManager
    logger.info("核心模組導入成功")
except ImportError as e:
    logger.error(f"核心模組導入失敗: {e}")
    sys.exit(1)

class SRTEngineStandalone:
    """獨立的 SRT 引擎"""
    
    def __init__(self):
        self.model_manager = ModelManager()
        self.core = None
        
    def initialize_engine(self, model_size="medium", enable_gpu=True):
        """初始化引擎"""
        try:
            logger.info(f"初始化引擎，模型: {model_size}")
            
            # 智能模型選擇
            success, model_path, source = self.model_manager.download_model_if_needed(
                model_size, 
                progress_callback=self._progress_callback
            )
            
            if not success:
                logger.error(f"模型獲取失敗: {model_path}")
                return False, f"模型載入失敗: {model_path}"
                
            logger.info(f"使用模型: {model_size} (來源: {source})")
            
            # 創建字幕生成器
            self.core = SimplifiedSubtitleCore(
                model_size=model_size,
                device="cuda" if enable_gpu else "cpu",
                compute_type="auto"
            )
            
            # 初始化
            if not self.core.initialize(self._progress_callback):
                return False, "引擎初始化失敗"
                
            logger.info("SRT引擎初始化完成")
            return True, "引擎就緒"
            
        except Exception as e:
            logger.error(f"引擎初始化失敗: {e}")
            return False, str(e)
            
    def _progress_callback(self, percent, message):
        """進度回調"""
        progress_data = {
            "type": "progress", 
            "percent": percent,
            "message": message
        }
        print(f"PROGRESS:{json.dumps(progress_data, ensure_ascii=False)}")
        sys.stdout.flush()
        return True
        
    def process_files(self, files, settings, corrections=None):
        """處理檔案"""
        try:
            if not self.core:
                return {"success": False, "error": "引擎未初始化"}
                
            results = []
            
            for i, file_path in enumerate(files):
                logger.info(f"處理文件 {i+1}/{len(files)}: {file_path}")
                
                # 構建輸出路徑
                input_path = Path(file_path)
                output_dir = settings.get('customDir', str(input_path.parent))
                output_format = settings.get('outputFormat', 'srt')
                output_file = Path(output_dir) / f"{input_path.stem}.{output_format}"
                
                # 生成字幕
                def file_progress_callback(progress, message):
                    overall_progress = 10 + (i * 80) // len(files) + (progress * 80) // (len(files) * 100)
                    return self._progress_callback(overall_progress, f"{input_path.name}: {message}")
                
                # 處理語言設置
                input_language = settings.get('language', 'auto')
                output_language = settings.get('outputLanguage', 'same')
                
                # 如果輸入語言是 auto，傳遞 None 給 Whisper
                whisper_language = None if input_language == 'auto' else input_language
                
                # 如果輸出語言是 same，設為 None 表示不轉換
                target_output_language = None if output_language == 'same' else output_language
                
                logger.info(f"語言設置 - 輸入: {input_language}, 輸出: {output_language}")
                logger.info(f"Whisper參數 - 語言: {whisper_language}, 目標輸出: {target_output_language}")
                
                success = self.core.generate_subtitle(
                    str(input_path),
                    str(output_file),
                    language=whisper_language,
                    output_language=target_output_language,
                    format=output_format,
                    progress_callback=file_progress_callback
                )
                
                if success:
                    results.append({
                        "input": str(input_path),
                        "output": str(output_file),
                        "success": True
                    })
                    logger.info(f"成功生成: {output_file}")
                else:
                    results.append({
                        "input": str(input_path),
                        "output": str(output_file),
                        "success": False,
                        "error": "字幕生成失敗"
                    })
                    
            # 輸出完成結果
            completion_data = {
                "type": "complete",
                "results": results,
                "total": len(files),
                "successful": sum(1 for r in results if r["success"])
            }
            
            print(f"COMPLETE:{json.dumps(completion_data, ensure_ascii=False)}")
            return completion_data
            
        except Exception as e:
            logger.error(f"處理過程中發生錯誤: {e}")
            error_data = {
                "type": "error",
                "error": str(e)
            }
            print(f"ERROR:{json.dumps(error_data, ensure_ascii=False)}")
            return error_data

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='SRT GO 獨立 AI 引擎')
    parser.add_argument('--init', help='初始化引擎，指定模型大小 (base/medium/large)')
    parser.add_argument('--process', help='處理檔案，提供 JSON 配置')
    parser.add_argument('--enable-gpu', action='store_true', default=True, help='啟用GPU加速')
    parser.add_argument('--test', action='store_true', help='執行測試')
    
    args = parser.parse_args()
    
    if args.test:
        # 測試模式
        print("=== SRT GO 獨立引擎測試 ===")
        engine = SRTEngineStandalone()
        
        # 測試初始化
        success, message = engine.initialize_engine("base", args.enable_gpu)
        if success:
            print(f"✅ 測試通過: {message}")
            return 0
        else:
            print(f"❌ 測試失敗: {message}")
            return 1
            
    elif args.init:
        # 初始化模式
        engine = SRTEngineStandalone()
        success, message = engine.initialize_engine(args.init, args.enable_gpu)
        
        result = {
            "success": success,
            "message": message,
            "model": args.init
        }
        print(f"INIT:{json.dumps(result, ensure_ascii=False)}")
        return 0 if success else 1
        
    elif args.process:
        # 處理模式
        try:
            config = json.loads(args.process)
            files = config.get('files', [])
            settings = config.get('settings', {})
            corrections = config.get('corrections', [])
            
            engine = SRTEngineStandalone()
            
            # 自動初始化
            model_size = settings.get('model', 'medium')
            success, message = engine.initialize_engine(model_size, args.enable_gpu)
            
            if not success:
                error_result = {"success": False, "error": message}
                print(f"ERROR:{json.dumps(error_result, ensure_ascii=False)}")
                return 1
                
            # 處理檔案
            result = engine.process_files(files, settings, corrections)
            return 0 if result.get('type') == 'complete' else 1
            
        except Exception as e:
            error_result = {"success": False, "error": str(e)}
            print(f"ERROR:{json.dumps(error_result, ensure_ascii=False)}")
            return 1
    else:
        print("使用方法:")
        print("  --init <model>     初始化指定模型 (base/medium/large)")
        print("  --process <json>   處理檔案，提供JSON配置")
        print("  --test             執行測試")
        print("  --enable-gpu       啟用GPU加速")
        return 1

if __name__ == "__main__":
    sys.exit(main())