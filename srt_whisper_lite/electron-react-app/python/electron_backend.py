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
                
                # 第二步：檢查PyTorch CUDA支持作為額外驗證
                try:
                    import torch
                    if torch.cuda.is_available() and torch.cuda.device_count() > 0:
                        device_name = torch.cuda.get_device_name(0)
                        logger.info(f"GPU庫完整性測試通過: {device_name}")
                        return True, "float16"
                    else:
                        logger.info("PyTorch未檢測到可用GPU，使用CPU模式")
                        return False, "int8"
                except Exception as gpu_test_error:
                    logger.warning(f"GPU完整性測試失敗: {gpu_test_error}")
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
        
        # 初始化字幕生成器 - 智能模型選擇
        # 檢查是否有INT8模型管理器
        actual_model = model_size
        model_manager_used = None
        
        try:
            if model_size in ['large', 'large-v2', 'large-v3']:
                # 嘗試使用INT8模型管理器
                from large_v3_int8_model_manager import LargeV3INT8ModelManager
                model_manager = LargeV3INT8ModelManager()
                if model_manager.check_model_availability():
                    actual_model = model_manager.get_faster_whisper_config()['model_size_or_path']
                    model_manager_used = "Large V3 Turbo INT8"
                    logger.info(f"使用 Large V3 Turbo INT8 模型管理器")
                else:
                    logger.info(f"INT8模型不可用，使用標準 {model_size} 模型")
            else:
                logger.info(f"使用指定的 {model_size} 模型")
        except ImportError:
            logger.info(f"INT8模型管理器不可用，使用標準 {model_size} 模型")
        
        # 獲取性能模式設置
        performance_mode = settings.get('performanceMode', 'auto')
        logger.info(f"性能模式設置: {performance_mode}")
        
        # 如果有模型管理器，使用其配置
        if model_manager_used:
            model_config = model_manager.get_faster_whisper_config()
            core = SimplifiedSubtitleCore(
                model_size=model_config['model_size_or_path'],
                device=model_config['device'],
                compute_type=model_config['compute_type'],
                performance_mode=performance_mode
            )
            logger.info(f"模型配置: {model_manager_used} - 設備: {model_config['device']}, 計算類型: {model_config['compute_type']}, 性能模式: {performance_mode}")
        else:
            core = SimplifiedSubtitleCore(
                model_size=actual_model,
                device=device,
                compute_type=compute_type,
                performance_mode=performance_mode
            )
            logger.info(f"模型配置: {actual_model} - 設備: {device}, 計算類型: {compute_type}, 性能模式: {performance_mode}")
        
        # 傳遞自適應人聲檢測設置到core（新的預設選項）
        if settings.get('enable_pure_voice_mode', True):
            core.enable_adaptive_voice_detection = True
            logger.info("已啟用自適應人聲檢測系統 - 純音頻特徵驅動，無硬編碼")
        
        # 傳遞智能間奏檢測設置到core（向後兼容，非預設）
        elif settings.get('enable_interlude_detection', False):
            core.enable_interlude_detection = True
            logger.info("已啟用傳統智能間奏檢測系統")
        
        # 傳遞傳統SubEasy設置到core（向後兼容）
        elif settings.get('enable_subeasy_mode', False):
            core.enable_subeasy = True
            logger.info("已啟用傳統SubEasy 5層濾波系統")
        
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
        
        # 純人聲模式（預設啟用，基於音頻特徵無硬編碼）
        enable_pure_voice_mode = settings.get('enablePureVoiceMode', True)
        
        # 智能間奏檢測（向後兼容，非預設）
        enable_interlude_detection = settings.get('enableInterludeDetection', False)
        
        # 檢查是否啟用傳統SubEasy模式（保留向後兼容）
        enable_subeasy = settings.get('enableSubEasy', False)
        
        if enable_pure_voice_mode:
            settings['enable_pure_voice_mode'] = True
            logger.info(f"[純人聲模式] 啟用自適應人聲檢測 - 純音頻特徵驅動，無硬編碼閾值")
        elif enable_interlude_detection:
            settings['enable_interlude_detection'] = True
            logger.info(f"[智能過濾] 啟用傳統智能間奏檢測 - 自動過濾非人聲段落")
        elif enable_subeasy:
            settings['model'] = 'large-v3'
            settings['enable_subeasy_mode'] = True
            settings['vad_threshold'] = vad_threshold
            logger.info(f"[SubEasy] 啟用傳統SubEasy模式 - VAD: {vad_threshold}, 模型: Large V3 (原設定: {original_model})")
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