#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Electron 後端處理腳本
處理從 Electron 應用傳來的字幕生成請求
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

# 如果在打包環境中，確保能找到所有模組
script_dir = Path(__file__).parent.absolute()
if script_dir not in [Path(p) for p in sys.path]:
    sys.path.insert(0, str(script_dir))

try:
    logger.info(f"當前工作目錄: {os.getcwd()}")
    logger.info(f"Python路徑: {sys.path[:3]}")
    logger.info(f"腳本目錄: {script_dir}")
    
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
    # 前端期望的格式：percent 和 filename
    progress_data = {
        "type": "progress",
        "percent": progress,
        "filename": message,
        "message": message
    }
    # 明確設定UTF-8編碼輸出
    output = f"PROGRESS:{json.dumps(progress_data, ensure_ascii=False)}"
    print(output.encode('utf-8').decode('utf-8'))
    sys.stdout.flush()
    return True

def process_subtitle_files(files, settings, corrections):
    """處理字幕文件"""
    try:
        # 解析設置
        model_size = settings.get('model', 'medium')
        language = settings.get('language', None)
        output_language = settings.get('outputLanguage', None)
        
        if language == 'auto':
            language = None
        # 語言代碼映射（Whisper 只支援基本語言代碼）
        elif language == 'zh-TW' or language == 'zh-CN':
            language = 'zh'
            
        # 處理輸出語言設置
        if output_language == 'same':
            output_language = None
        output_format = settings.get('outputFormat', 'srt')
        output_dir = settings.get('customDir', str(current_dir))
        
        # 如果沒有指定輸出目錄，使用第一個文件的目錄
        if not output_dir:
            if files:
                output_dir = str(Path(files[0]).parent)
            else:
                output_dir = str(current_dir)
        
        logger.info(f"開始處理 {len(files)} 個文件")
        logger.info(f"設置: 模型={model_size}, 語言={language}, 格式={output_format}")
        
        # 智能設備選擇 - 使用ctranslate2內建的GPU檢測
        def detect_gpu_support():
            """智能檢測GPU支援"""
            try:
                # 第一步：檢測ctranslate2是否支援CUDA
                import ctranslate2
                cuda_types = ctranslate2.get_supported_compute_types("cuda")
                if not cuda_types:
                    logger.info("ctranslate2不支援CUDA，使用CPU模式")
                    return False, "int8"
                
                logger.info(f"基礎GPU檢測通過，可用計算類型: {cuda_types}")
                
                # 第二步：嘗試實際創建GPU設備來測試庫完整性
                try:
                    # 創建一個簡單的測試來驗證GPU庫
                    test_translator = ctranslate2.Translator("", device="cuda")
                    logger.info("GPU庫完整性測試通過")
                    return True, "float16"
                except Exception as gpu_test_error:
                    # GPU基礎支援但庫不完整，降級到CPU
                    logger.warning(f"GPU庫不完整，降級到CPU模式: {gpu_test_error}")
                    return False, "int8"
                    
            except Exception as e:
                logger.info(f"GPU檢測失敗，使用CPU模式: {e}")
                return False, "int8"
        
        # 讀取用戶設定（如果有的話）
        enable_gpu = settings.get('enable_gpu', True)  # 默認啟用GPU
        
        if enable_gpu:
            gpu_available, gpu_compute_type = detect_gpu_support()
            if gpu_available:
                device = "cuda"
                compute_type = gpu_compute_type
                logger.info("使用GPU加速模式")
            else:
                device = "cpu"
                compute_type = "int8"
                logger.info("GPU不可用，使用CPU模式")
        else:
            device = "cpu"
            compute_type = "int8"
            logger.info("用戶選擇CPU模式")
        
        # 初始化字幕生成器
        core = SimplifiedSubtitleCore(
            model_size=model_size,
            device=device,
            compute_type=compute_type
        )
        
        # 傳遞SubEasy設置和VAD參數到core
        if settings.get('enable_subeasy_mode', False):
            core.enable_subeasy = True
            logger.info("已啟用SubEasy 5層濾波系統")
        
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
            
            # 創建專門的進度回調，包含當前文件信息
            def file_progress_callback(progress, message):
                # 調整進度範圍，每個文件佔用 80% / 文件數量
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
                # 報告文件完成狀態
                progress_callback(10 + ((i + 1) * 80) // len(files), f"完成: {input_path.name}")
                logger.info(f"成功生成字幕: {output_file}")
            else:
                results.append({
                    "input": file_path,
                    "output": str(output_file),
                    "success": False,
                    "error": "字幕生成失敗"
                })
                progress_callback(10 + ((i + 1) * 80) // len(files), f"失敗: {input_path.name}")
                logger.error(f"字幕生成失敗: {file_path}")
        
        # 輸出完成結果
        completion_data = {
            "type": "complete",
            "results": results,
            "total": len(files),
            "successful": sum(1 for r in results if r["success"])
        }
        output = f"COMPLETE:{json.dumps(completion_data, ensure_ascii=False)}"
        print(output.encode('utf-8').decode('utf-8'))
        
        return True
        
    except Exception as e:
        logger.error(f"處理過程中發生錯誤: {e}")
        error_data = {
            "type": "error",
            "error": str(e)
        }
        output = f"ERROR:{json.dumps(error_data, ensure_ascii=False)}"
        print(output.encode('utf-8').decode('utf-8'))
        return False

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="Electron 字幕生成後端")
    parser.add_argument('--files', required=True, help='要處理的文件列表 (JSON)')
    parser.add_argument('--settings', required=True, help='處理設置 (JSON)')
    parser.add_argument('--corrections', help='自定義修正 (JSON)')
    
    args = parser.parse_args()
    
    try:
        # 解析參數 - 加強JSON解析錯誤處理  
        try:
            files = json.loads(args.files)
        except json.JSONDecodeError as e:
            logger.error(f"文件列表 JSON 解析錯誤: {e}")
            # 嘗試修復常見的反斜線問題
            fixed_files_json = args.files.replace('\\', '\\\\')
            try:
                files = json.loads(fixed_files_json)
                logger.info("已修復文件路徑的反斜線問題")
            except json.JSONDecodeError:
                logger.error("無法修復 JSON 格式，請檢查文件路徑")
                sys.exit(1)
        
        settings = json.loads(args.settings)
        
        # 測試配置：創建多種VAD參數測試
        original_model = settings.get('model', 'medium')
        
        # 檢查是否有特殊測試參數
        vad_threshold = settings.get('vad_threshold', 0.35)  # 調整到更合理的閾值
        enable_ultra_sensitive = settings.get('enableUltraSensitive', False)  # 默認關閉超敏感模式
        
        # 檢查是否啟用SubEasy模式
        enable_subeasy = settings.get('enableSubEasy', True)
        
        if enable_subeasy:
            settings['model'] = 'large-v3'
            settings['enable_subeasy_mode'] = True
            settings['vad_threshold'] = vad_threshold
            logger.info(f"[SubEasy] 啟用SubEasy模式 - VAD: {vad_threshold}, 模型: Large V3 (原設定: {original_model})")
        elif enable_ultra_sensitive:
            settings['model'] = 'large-v3'
            settings['enable_ultra_sensitive_mode'] = True
            logger.info(f"[TEST] 超敏感模式測試 - VAD: {vad_threshold}, 模型: Large V3 (原設定: {original_model})")
        else:
            settings['model'] = original_model
            logger.info(f"[TEST] 標準模式測試 - 模型: {original_model}")

        corrections = json.loads(args.corrections) if args.corrections else []
        
        logger.info("Electron 後端啟動")
        logger.info(f"接收到 {len(files)} 個文件")
        
        # 處理文件
        success = process_subtitle_files(files, settings, corrections)
        
        if success:
            logger.info("所有文件處理完成")
            sys.exit(0)
        else:
            logger.error("處理過程中發生錯誤")
            sys.exit(1)
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析錯誤: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"未知錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()