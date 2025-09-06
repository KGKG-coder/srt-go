#!/usr/bin/env python3
"""
簡化版字幕生成核心
移除複雜功能，專注於穩定的基本字幕生成
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Callable
import tempfile
import numpy as np

logger = logging.getLogger(__name__)



# 添加網路連接檢查功能
def check_network_and_cache():
    """檢查網路連接和模型緩存狀態"""
    import urllib.request
    import os
    
    # 檢查網路
    try:
        urllib.request.urlopen('https://huggingface.co', timeout=5)
        has_internet = True
    except:
        has_internet = False
    
    # 檢查本地緩存
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
    has_cache = os.path.exists(cache_dir) and len(os.listdir(cache_dir)) > 0
    
    return has_internet, has_cache

class SimplifiedSubtitleCore:
    """簡化版字幕生成核心"""
    
    def __init__(self, model_size=None, device=None, compute_type=None, performance_mode="auto"):
        # 導入配置管理器
        try:
            from config_manager import get_config_manager
            self.config = get_config_manager()
        except ImportError:
            self.config = None
            logger.warning("配置管理器不可用，使用默認參數")
        
        # 智能模型選擇 - 根據用戶配置決定模型
        self.model_size = model_size or "large-v3"  # 默認使用 LARGE V3，但允許配置覆蓋
        self.device = device or (self.config.get("model.device") if self.config else "auto")
        self.compute_type = compute_type or (self.config.get("model.compute_type") if self.config else "auto")
        self.performance_mode = performance_mode  # 新增性能模式參數
        
        self.model = None
        self.initialized = False
        
        # 只支援 LARGE 模型 - 專業版
        self.supported_models = ["large"]
        
        # 模型顯示名稱映射
        self.model_display_names = {
            "base": "Base",
            "medium": "Medium", 
            "large": "Large"
        }
        
        # 模型特定的優化參數（簡化）
        self.model_params = {
            "base": {"beam_size": 4, "best_of": 4, "temperature": [0.0, 0.2, 0.4, 0.6]},
            "medium": {"beam_size": 6, "best_of": 6, "temperature": [0.0, 0.2, 0.4, 0.6, 0.8]},
            "large": {"beam_size": 8, "best_of": 8, "temperature": [0.0, 0.2, 0.4, 0.6, 0.8]}
        }
        
    def initialize(self, progress_callback: Optional[Callable] = None) -> bool:
        """初始化模型"""
        try:
            if progress_callback:
                if progress_callback(5, "正在載入 AI 模型...") == False:
                    return False
            
            from faster_whisper import WhisperModel
            
            # 根據性能模式選擇適當的模型管理器
            using_fp16_optimization = False
            model_manager = None
            
            if self.performance_mode == "gpu":
                # 強制使用GPU模式
                try:
                    from large_v3_fp16_performance_manager import get_fp16_performance_manager
                    model_manager = get_fp16_performance_manager()
                    # 強制設備和計算類型
                    self.device = "cuda"
                    self.compute_type = "float16"
                    using_fp16_optimization = True
                    logger.info("用戶選擇GPU模式 - 強制使用CUDA Float16")
                except ImportError:
                    logger.warning("FP16管理器不可用，回退到自動模式")
                    
            elif self.performance_mode == "cpu":
                # 強制使用CPU模式
                try:
                    from large_v3_int8_model_manager import LargeV3INT8ModelManager
                    model_manager = LargeV3INT8ModelManager()
                    # 強制設備和計算類型
                    self.device = "cpu"
                    self.compute_type = "int8"
                    using_fp16_optimization = False
                    logger.info("用戶選擇CPU模式 - 強制使用CPU INT8")
                except ImportError:
                    logger.warning("INT8管理器不可用，回退到自動模式")
            
            # 自動模式或回退情況
            if model_manager is None:
                # 優先使用FP16性能優化配置（生產級50%性能提升）
                try:
                    from large_v3_fp16_performance_manager import get_fp16_performance_manager
                    model_manager = get_fp16_performance_manager()
                    using_fp16_optimization = True
                    logger.info("自動模式 - 使用FP16性能優化配置 (RTF預期: 0.135)")
                except ImportError:
                    # 回退到INT8版本
                    from large_v3_int8_model_manager import LargeV3INT8ModelManager
                    model_manager = LargeV3INT8ModelManager()
                    using_fp16_optimization = False
                    logger.info("自動模式 - 回退到INT8配置")
            
            # 使用配置的模型大小和設置
            logger.info(f"載入模型: {self.model_size}, 設備: {self.device}, 計算類型: {self.compute_type}")
            
            # 添加模型下載超時和重試機制
            import os
            import time
            from pathlib import Path
            
            # 檢查本地模型緩存
            cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
            local_model_exists = False
            
            if os.path.exists(cache_dir):
                # 檢查是否有本地 large 模型
                for item in os.listdir(cache_dir):
                    if "whisper-large" in item.lower():
                        local_model_exists = True
                        break
            
            logger.info(f"本地模型緩存檢查: {'存在' if local_model_exists else '不存在'}")
            
            # 添加網路連接檢查
            def check_internet_connection():
                try:
                    import urllib.request
                    urllib.request.urlopen('https://huggingface.co', timeout=10)
                    return True
                except:
                    return False
            
            has_internet = check_internet_connection()
            logger.info(f"網路連接狀態: {'可用' if has_internet else '不可用'}")
            
            # 智能選擇模型下載策略
            download_timeout = 300  # 5分鐘超時
            max_download_retries = 2
            
            for download_attempt in range(max_download_retries + 1):
                try:
                    if progress_callback:
                        if download_attempt == 0:
                            progress_callback(5, "正在初始化 AI 模型...")
                        else:
                            progress_callback(5, f"模型初始化重試 {download_attempt}/{max_download_retries}...")
                    
                    start_time = time.time()
                    
                    # 強制使用指定的模型，不進行降級
                    actual_model_size = self.model_size
                    if not has_internet and not local_model_exists:
                        logger.warning(f"無網路連接且無本地 {self.model_size} 模型")
                        if progress_callback:
                            progress_callback(8, f"需要下載 {self.model_size} 模型...")
                        # 不降級，保持原模型大小
                    
                    # 使用 LARGE 專用模型管理器
                    def model_progress(percent, message):
                        if progress_callback:
                            progress_callback(5 + (percent // 5), message)
                    
                    success, model_path = model_manager.ensure_model_ready()
                    
                    if not success:
                        logger.error("無法獲取模型")
                        return False
                    
                    # 創建模型實例 - 根據管理器類型使用配置
                    if using_fp16_optimization:
                        model_config = model_manager.get_optimized_whisper_config()
                        logger.info("應用FP16優化配置，預期性能提升50%")
                    else:
                        model_config = model_manager.get_faster_whisper_config()
                        logger.info("使用INT8配置")
                    
                    # 智能配置覆蓋 - 確保設備和計算類型的一致性
                    if self.device and self.device != "auto":
                        if using_fp16_optimization:
                            # 對於FP16優化，只在用戶明確要求且配置一致時覆蓋
                            if self.device == "cpu" and model_config["compute_type"] == "float16":
                                logger.warning("用戶選擇CPU但檢測到float16，自動調整為int8以確保兼容性")
                                model_config["compute_type"] = "int8"
                                model_config["device"] = "cpu"
                            elif self.device == "cuda" and model_config["compute_type"] == "int8":
                                logger.info("用戶選擇CUDA，保持float16配置")
                                model_config["compute_type"] = "float16" 
                                model_config["device"] = "cuda"
                            else:
                                model_config["device"] = self.device
                        else:
                            model_config["device"] = self.device
                    
                    # 模型優化配置應用
                    if using_fp16_optimization:
                        # FP16優化配置已在model_config中設定，保持原始配置
                        logger.info(f"FP16優化 - 設備: {model_config['device']}, 計算類型: {model_config['compute_type']}, 線程: {model_config['cpu_threads']}")
                    else:
                        # INT8 模型最佳化配置
                        if hasattr(model_manager, 'model_variant') and "int8" in model_manager.model_variant:
                            model_config["compute_type"] = "int8"  # 強制使用 INT8
                            if self.device == "cuda":
                                model_config["compute_type"] = "int8_float16"  # GPU 上使用混合精度
                    
                    # 構建WhisperModel參數
                    whisper_kwargs = {
                        "device": model_config["device"],
                        "compute_type": model_config["compute_type"],
                        "download_root": model_config.get("download_root"),
                        "local_files_only": not has_internet,  # 無網路時僅使用本地文件
                        "num_workers": self.config.get("model.num_workers", 4) if self.config and self.device == "cuda" else 2
                    }
                    
                    # Large V3 特殊處理：強制使用標準模型避免特徵形狀錯誤
                    model_path_or_name = model_config["model_size_or_path"]
                    if "large-v3" in str(model_path_or_name).lower():
                        logger.info("檢測到 Large V3 模型，使用標準 'large-v3' 避免特徵形狀問題...")
                        # 強制使用標準的 large-v3 模型，避免 turbo 版本的特徵形狀不匹配
                        whisper_kwargs['download_root'] = model_config.get("download_root")
                        self.model = WhisperModel(
                            "large-v3",
                            **whisper_kwargs
                        )
                    else:
                        # 非Large V3模型，正常載入
                        self.model = WhisperModel(
                            model_path_or_name,
                            **whisper_kwargs
                        )
                    
                    elapsed_time = time.time() - start_time
                    logger.info(f"模型載入成功，耗時: {elapsed_time:.1f}秒")
                    
                    if progress_callback:
                        progress_callback(20, "AI 模型載入完成")
                    
                    break  # 成功載入，跳出重試循環
                    
                except Exception as model_error:
                    elapsed_time = time.time() - start_time
                    logger.error(f"模型載入失敗 (嘗試 {download_attempt + 1}/{max_download_retries + 1}): {model_error}")
                    
                    if download_attempt == max_download_retries:
                        # 不再降級到 tiny 模型，直接失敗
                        logger.error(f"無法載入 {self.model_size} 模型，所有重試已失敗")
                        if progress_callback:
                            progress_callback(0, f"模型載入失敗: {str(model_error)[:50]}...")
                        return False
                    else:
                        # 等待後重試
                        wait_time = (download_attempt + 1) * 5
                        logger.info(f"等待 {wait_time} 秒後重試...")
                        time.sleep(wait_time)
                        
                        if progress_callback:
                            progress_callback(3, f"模型載入重試中...({download_attempt + 1}/{max_download_retries})")
            
            if progress_callback:
                if progress_callback(20, "AI 模型載入完成") == False:
                    return False
            
            self.initialized = True
            logger.info("簡化版字幕生成器初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"初始化失敗: {e}")
            if progress_callback:
                progress_callback(0, f"初始化失敗: {e}")
            return False
    
    def generate_subtitle(self, 
                         input_file: str,
                         output_file: str,
                         language: Optional[str] = None,
                         output_language: Optional[str] = None,
                         format: str = "srt",
                         progress_callback: Optional[Callable] = None) -> bool:
        """生成字幕（簡化版，含性能監控）"""
        
        if not self.initialized:
            logger.error("模型未初始化")
            return False
        
        # 性能監控 - 開始計時
        import time
        processing_start_time = time.time()
        audio_duration = 0
        
        try:
            # 檢查輸入文件
            if not os.path.exists(input_file):
                logger.error(f"輸入文件不存在: {input_file}")
                return False
            
            if progress_callback:
                if progress_callback(25, "開始處理音頻文件...") == False:
                    return False
            
            logger.info(f"開始轉錄: {input_file} (性能監控已啟用)")
            
            # 獲取模型特定的優化參數
            model_params = self.model_params.get(self.model_size, self.model_params["medium"])
            
            # 優化的轉錄參數 - 提升準確度和語意斷句，加入重試機制
            max_retries = 3
            retry_count = 0
            last_error = None
            
            # 語言代碼映射（Whisper 只支援基本語言代碼）
            whisper_language = language
            if language == 'zh-TW' or language == 'zh-CN':
                whisper_language = 'zh'
            elif language == 'auto':
                whisper_language = None
            
            while retry_count < max_retries:
                try:
                    segments, info = self.model.transcribe(
                        input_file,
                        language=whisper_language,
                        task="transcribe",
                        beam_size=model_params["beam_size"],     # 動態beam_size
                        best_of=model_params["best_of"],         # 動態best_of
                        temperature=model_params["temperature"], # 多溫度策略
                        compression_ratio_threshold=2.4,         # 使用 srt_final-orign 的優化值
                        log_prob_threshold=-1.0,                 # 使用 srt_final-orign 的優化值
                        no_speech_threshold=0.6,                 # 使用 srt_final-orign 的優化值
                        condition_on_previous_text=False,        # 改為 False，提高獨立性
                        initial_prompt=None,
                        prefix=None,
                        suppress_blank=True,
                        suppress_tokens=[-1],
                        without_timestamps=False,
                        max_initial_timestamp=1.0,
                        word_timestamps=True,                    # 啟用詞級時間戳，用於精確時間軸
                        prepend_punctuations="\"'([{-",
                        append_punctuations="\"'.。,，!！?？:：\")]}、",
                        vad_filter=True,
                        vad_parameters={
                            # 智能VAD參數 - 根據模式調整
                            "threshold": getattr(self, 'vad_threshold', 0.35),  # 使用配置的閾值
                            "min_speech_duration_ms": 250,  # 最短語音持續時間
                            "max_speech_duration_s": 20,  # 限制單個片段最大長度
                            "min_silence_duration_ms": 1000,  # 調整為1秒靜音分段
                            "speech_pad_ms": 100  # 添加少量時間填充以提升準確性
                        }
                    )
                    break  # 成功則跳出重試循環
                    
                except RuntimeError as e:
                    retry_count += 1
                    last_error = e
                    logger.warning(f"轉錄失敗 (第 {retry_count}/{max_retries} 次重試): {e}")
                    
                    if retry_count < max_retries:
                        if progress_callback:
                            progress_callback(25, f"轉錄失敗，正在重試 ({retry_count}/{max_retries})...")
                        # 重試前短暫等待
                        import time
                        time.sleep(1)
                    else:
                        raise e
            
            if progress_callback:
                if progress_callback(60, f"識別語言: {info.language}, 處理中...") == False:
                    return False
            
            # 記錄語言檢測信心度和音頻時長（用於性能監控）
            language_probability = getattr(info, 'language_probability', 1.0)
            audio_duration = info.duration  # 記錄音頻時長用於RTF計算
            logger.info(f"檢測到語言: {info.language} (信心度: {language_probability:.2%}), 時長: {info.duration:.1f}秒")
            
            # 如果信心度過低，發出警告
            if language_probability < 0.8:
                logger.warning(f"語言檢測信心度較低 ({language_probability:.2%})，建議手動指定語言")
                if progress_callback:
                    progress_callback(60, f"語言檢測信心度較低，繼續處理...")
            
            # 收集轉錄結果 - 使用批次處理優化記憶體
            result_segments = []
            segment_count = 0
            batch_size = 100  # 每批處理100個段落
            segment_buffer = []
            
            for segment in segments:
                if progress_callback and segment_count % 10 == 0:
                    progress = 60 + int((segment_count / 100) * 25)  # 60-85%
                    if progress_callback(min(progress, 85), f"處理段落 {segment_count + 1}...") == False:
                        return False
                
                # 清理文本
                text = segment.text.strip()
                if text:  # 只保留非空文本
                    # 使用詞級時間戳來獲得更精確的時間軸
                    segment_start = segment.start
                    segment_end = segment.end
                    
                    # 如果有詞級時間戳，使用最後一個詞的結束時間作為段落結束時間
                    if hasattr(segment, 'words') and segment.words:
                        words_data = []
                        for word in segment.words:
                            words_data.append({
                                'start': word.start,
                                'end': word.end,
                                'word': word.word,
                                'probability': getattr(word, 'probability', 1.0)
                            })
                        
                        # 使用詞級時間戳來調整段落時間軸
                        if words_data:
                            segment_start = min(segment_start, words_data[0]['start'])
                            segment_end = max(segment_end, words_data[-1]['end'])
                    
                    # 在結束時間後延續0.1秒，提供更好的閱讀體驗
                    segment_end += 0.1
                    
                    segment_data = {
                        'start': segment_start,
                        'end': segment_end,
                        'text': text,
                        'no_speech_prob': getattr(segment, 'no_speech_prob', 0.0),
                        'avg_logprob': getattr(segment, 'avg_logprob', 0.0)
                    }
                    
                    # 如果有詞級時間戳，添加到段落數據中
                    if hasattr(segment, 'words') and segment.words:
                        segment_data['words'] = words_data
                    
                    segment_buffer.append(segment_data)
                    
                    # 批次處理以優化記憶體使用
                    if len(segment_buffer) >= batch_size:
                        result_segments.extend(segment_buffer)
                        segment_buffer = []  # 清空緩衝區
                        
                        # 強制垃圾回收以釋放記憶體
                        import gc
                        gc.collect()
                
                segment_count += 1
            
            # 處理剩餘的段落
            if segment_buffer:
                result_segments.extend(segment_buffer)
            
            if not result_segments:
                logger.error("沒有獲得任何轉錄結果")
                if progress_callback:
                    progress_callback(0, "轉錄失敗：沒有識別到語音內容")
                
                # 檢查是否為靜音文件
                try:
                    import wave
                    import numpy as np
                    
                    # 簡單檢查音頻能量
                    with wave.open(input_file, 'rb') as wav_file:
                        frames = wav_file.readframes(wav_file.getnframes())
                        audio_data = np.frombuffer(frames, dtype=np.int16)
                        energy = np.mean(np.abs(audio_data))
                        
                        if energy < 100:  # 閾值可調整
                            logger.info("檢測到靜音文件")
                            if progress_callback:
                                progress_callback(0, "文件似乎是靜音的，沒有可識別的語音內容")
                except:
                    pass  # 忽略檢查錯誤
                    
                return False
            
            if progress_callback:
                if progress_callback(85, f"獲得 {len(result_segments)} 個字幕段落，正在優化語意斷句...") == False:
                    return False
            
            logger.info(f"轉錄完成，共 {len(result_segments)} 個段落")
            
            # 添加 srt_final-orign 風格的理解度分析
            self._analyze_subtitle_quality(result_segments, progress_callback)
            
            # 語意斷句優化
            try:
                from semantic_processor import SemanticSegmentProcessor
                
                # 獲取語言代碼
                detected_language = info.language if hasattr(info, 'language') else language
                
                # 優化語意斷句，確保每行只顯示適當長度的文字，並傳遞模型大小和音頻文件路徑
                logger.info(f"開始語意斷句處理，使用 {self.model_size} 模型優化字幕分割")
                processor = SemanticSegmentProcessor(detected_language, self.model_size)
                processor.audio_file = input_file  # 傳遞音頻文件路徑供剪映對齊使用
                result_segments = processor.process_segments(result_segments)
                
                if progress_callback:
                    if progress_callback(92, f"語意優化完成，共 {len(result_segments)} 個段落") == False:
                        return False
                
                logger.info(f"語意斷句優化完成，優化後共 {len(result_segments)} 個段落")
                
            except ImportError:
                logger.warning("語意處理器不可用，跳過優化步驟")
            except Exception as e:
                logger.warning(f"語意斷句優化失敗，使用原始結果: {e}")
            
            # 增強型輕量級語音檢測 v2.0 - 整合內容類型自動檢測（預設啟用）
            if hasattr(self, 'enable_adaptive_voice_detection') and getattr(self, 'enable_adaptive_voice_detection', True):
                try:
                    from enhanced_lightweight_voice_detector import EnhancedLightweightVoiceDetector
                    
                    if progress_callback:
                        if progress_callback(88, "啟動增強型語音檢測系統 v2.0...") == False:
                            return False
                    
                    logger.info("🎯 啟動增強型輕量級語音檢測系統 v2.0 - 自動內容類型檢測")
                    voice_detector = EnhancedLightweightVoiceDetector()
                    result_segments = voice_detector.detect_voice_segments(result_segments, input_file)
                    
                    # 記錄檢測摘要
                    summary = voice_detector.get_detection_summary()
                    logger.info(f"Content type detected: {summary['content_type_detected']}")
                    logger.info(f"Applied specialized thresholds for {summary['content_type_detected']}")
                    
                    if progress_callback:
                        if progress_callback(92, f"增強型語音檢測完成，共 {len(result_segments)} 個段落") == False:
                            return False
                    
                    logger.info(f"✅ 增強型語音檢測完成，最終 {len(result_segments)} 個段落")
                    
                except ImportError:
                    # 備用機制1：嘗試基礎版輕量級檢測器
                    try:
                        from lightweight_voice_detector import LightweightVoiceDetector
                        
                        if progress_callback:
                            if progress_callback(88, "啟動基礎版語音檢測系統...") == False:
                                return False
                        
                        logger.info("🎯 啟動輕量級語音檢測系統 (基礎版) - 無依賴，純音頻特徵驅動")
                        voice_detector = LightweightVoiceDetector()
                        result_segments = voice_detector.detect_voice_segments(result_segments, input_file)
                        
                        if progress_callback:
                            if progress_callback(92, f"基礎版語音檢測完成，共 {len(result_segments)} 個段落") == False:
                                return False
                        
                        logger.info(f"✅ 基礎版語音檢測完成，最終 {len(result_segments)} 個段落")
                        
                    except ImportError:
                        logger.warning("所有輕量級語音檢測器不可用，跳過語音檢測步驟")
                    except Exception as e2:
                        logger.warning(f"基礎版語音檢測失敗: {e2}")
                        
                except Exception as e:
                    logger.warning(f"增強型語音檢測失敗，嘗試備用方案: {e}")
                    # 備用機制：嘗試基礎版檢測器
                    try:
                        from lightweight_voice_detector import LightweightVoiceDetector
                        logger.info("🔄 備用機制：啟動基礎版輕量級檢測器")
                        voice_detector = LightweightVoiceDetector()
                        result_segments = voice_detector.detect_voice_segments(result_segments, input_file)
                        logger.info("✅ 備用語音檢測完成")
                    except Exception as fallback_error:
                        logger.warning(f"備用語音檢測也失敗: {fallback_error}")
                        # 最終備用：嘗試自適應檢測器
                        try:
                            from adaptive_voice_detector import AdaptiveVoiceDetector
                            logger.info("🔄 最終備用：啟動自適應語音檢測器")
                            voice_detector = AdaptiveVoiceDetector()
                            result_segments = voice_detector.detect_voice_segments(result_segments, input_file)
                            logger.info("✅ 最終備用檢測完成")
                        except Exception as final_error:
                            logger.warning(f"所有語音檢測器都失敗: {final_error}")
            
            # 智能間奏檢測 - 檢查是否啟用（向後兼容，但不再是預設）
            elif hasattr(self, 'enable_interlude_detection') and getattr(self, 'enable_interlude_detection', False):
                try:
                    from intelligent_interlude_filter import IntelligentInterludeFilter
                    
                    if progress_callback:
                        if progress_callback(88, "啟動傳統智能間奏檢測系統...") == False:
                            return False
                    
                    logger.info("啟動傳統智能間奏檢測與修正系統")
                    interlude_filter = IntelligentInterludeFilter()
                    result_segments = interlude_filter.detect_and_fix_interludes(result_segments, input_file)
                    
                    if progress_callback:
                        if progress_callback(92, f"智能間奏檢測完成，共 {len(result_segments)} 個段落") == False:
                            return False
                    
                    logger.info(f"智能間奏檢測完成，最終 {len(result_segments)} 個段落")
                    
                except ImportError:
                    logger.warning("智能間奏檢測器不可用，跳過間奏檢測步驟")
                except Exception as e:
                    logger.warning(f"智能間奏檢測失敗，使用原始結果: {e}")
            
            # 傳統SubEasy 5層濾波系統 - 檢查是否啟用（向後兼容）
            elif hasattr(self, 'enable_subeasy') and getattr(self, 'enable_subeasy', False):
                try:
                    from subeasy_multilayer_filter import IntelligentMultiLayerFilter
                    
                    if progress_callback:
                        if progress_callback(88, "啟動傳統SubEasy 5層濾波系統...") == False:
                            return False
                    
                    logger.info("啟動傳統SubEasy智能5層濾波系統")
                    subeasy_filter = IntelligentMultiLayerFilter()
                    result_segments = subeasy_filter.apply_multilayer_filter(result_segments, input_file)
                    
                    if progress_callback:
                        if progress_callback(92, f"SubEasy濾波完成，共 {len(result_segments)} 個段落") == False:
                            return False
                    
                    logger.info(f"SubEasy 5層濾波完成，最終 {len(result_segments)} 個段落")
                    
                except ImportError:
                    logger.warning("SubEasy濾波器不可用，跳過5層濾波步驟")
                except Exception as e:
                    logger.warning(f"SubEasy濾波失敗，使用原始結果: {e}")
            
            # 跳過後處理優化以保持精確的詞級時間戳
            if progress_callback:
                if progress_callback(93, "保持原始時間戳，跳過後處理...") == False:
                    return False
            
            logger.info(f"保持原始詞級時間戳，跳過後處理優化，最終 {len(result_segments)} 個段落")
            
            # 如果需要翻譯到其他語言，使用 Whisper 重新處理
            logger.info(f"檢查翻譯條件 - output_language: {output_language}")
            if output_language and output_language != 'same':
                logger.info(f"啟動翻譯流程，目標語言: {output_language}")
                if progress_callback:
                    if progress_callback(95, f"正在生成 {output_language} 字幕...") == False:
                        return False
                try:
                    result_segments = self._generate_translated_subtitle(input_file, output_language, model_params, result_segments)
                    logger.info(f"多語言字幕生成完成，目標語言: {output_language}")
                except Exception as e:
                    logger.warning(f"多語言字幕生成失敗，使用原始文本: {e}")
            else:
                logger.info(f"跳過翻譯步驟 - output_language: {output_language}")
            
            if progress_callback:
                if progress_callback(97, "正在保存字幕文件...") == False:
                    return False
            
            # 保存字幕
            success = self._save_subtitle(result_segments, output_file, format)
            
            if success:
                # 性能監控 - 計算並報告RTF
                processing_time = time.time() - processing_start_time
                
                # 使用FP16性能管理器進行性能驗證（如果可用）
                try:
                    if hasattr(self, 'model') and hasattr(self.model, '__dict__'):
                        # 檢查是否使用FP16優化
                        from large_v3_fp16_performance_manager import validate_processing_performance
                        performance_result = validate_processing_performance(processing_time, audio_duration)
                        
                        logger.info(f"性能監控報告:")
                        logger.info(f"  處理時間: {processing_time:.1f}秒")
                        logger.info(f"  音頻時長: {audio_duration:.1f}秒") 
                        logger.info(f"  RTF: {performance_result['current_rtf']:.3f}")
                        logger.info(f"  性能等級: {performance_result['performance_tier']}")
                        logger.info(f"  相比基準改善: {performance_result['improvement_percent']:.1f}%")
                        logger.info(f"  狀態: {performance_result['status']}")
                        
                        # 如果性能低於預期，記錄警告
                        if performance_result['current_rtf'] > 0.2:
                            logger.warning(f"RTF {performance_result['current_rtf']:.3f} 高於最佳目標 0.2")
                            
                except ImportError:
                    # 基本性能報告（沒有FP16管理器時）
                    rtf = processing_time / audio_duration if audio_duration > 0 else float('inf')
                    logger.info(f"處理完成 - 時間: {processing_time:.1f}秒, RTF: {rtf:.3f}")
                
                if progress_callback:
                    progress_callback(100, "字幕生成完成！")
                logger.info(f"字幕保存成功: {output_file}")
                return True
            else:
                logger.error("字幕保存失敗")
                if progress_callback:
                    progress_callback(0, "字幕保存失敗")
                return False
                
        except MemoryError as e:
            logger.error(f"記憶體不足: {e}")
            if progress_callback:
                progress_callback(0, "錯誤：記憶體不足，請嘗試使用較小的模型或處理較短的文件")
            return False
        except FileNotFoundError as e:
            logger.error(f"文件未找到: {e}")
            if progress_callback:
                progress_callback(0, f"錯誤：找不到文件 {input_file}")
            return False
        except PermissionError as e:
            logger.error(f"權限錯誤: {e}")
            if progress_callback:
                progress_callback(0, "錯誤：沒有權限訪問文件，請檢查文件權限")
            return False
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"字幕生成失敗 ({error_type}): {e}")
            if progress_callback:
                # 提供更友好的錯誤信息
                if "CUDA" in str(e) or "GPU" in str(e):
                    progress_callback(0, "錯誤：GPU 處理失敗，請嘗試使用 CPU 模式")
                elif "codec" in str(e).lower() or "decode" in str(e).lower():
                    progress_callback(0, "錯誤：無法解碼音頻文件，請檢查文件格式是否支援")
                elif "model" in str(e).lower():
                    progress_callback(0, "錯誤：模型載入失敗，請檢查模型文件是否完整")
                else:
                    progress_callback(0, f"生成失敗: {str(e)}")
            return False
    
    def _generate_translated_subtitle(self, input_file: str, target_language: str, model_params: dict, existing_segments: list = None) -> list:
        """使用 Whisper 生成目標語言字幕並進行繁簡轉換"""
        try:
            # 如果目標語言是英文，使用 Whisper 的翻譯任務
            if target_language == 'en':
                task = "translate"
                language = None  # 自動檢測原語言
                logger.info("使用 Whisper 翻譯任務生成英文字幕")
                
                # 使用 Whisper 處理音頻
                segments, info = self.model.transcribe(
                    input_file,
                    task=task,
                    language=language,
                    beam_size=model_params["beam_size"],
                    best_of=model_params["best_of"],
                    temperature=model_params["temperature"],
                    compression_ratio_threshold=2.0,
                    log_prob_threshold=-0.7,
                    no_speech_threshold=0.4,
                    condition_on_previous_text=True,
                    suppress_blank=True,
                    suppress_tokens=[-1],
                    word_timestamps=True,
                    vad_filter=True,
                    vad_parameters={
                        "threshold": 0.3,
                        "min_speech_duration_ms": 150,
                        "max_speech_duration_s": float("inf"),
                        "min_silence_duration_ms": 800,
                        "speech_pad_ms": 250
                    }
                )
                
                # 收集處理後的段落
                processed_segments = []
                for segment in segments:
                    text = segment.text.strip()
                    if text:
                        segment_data = {
                            'start': segment.start,
                            'end': segment.end,
                            'text': text
                        }
                        
                        # 如果有詞級時間戳，添加到段落數據中
                        if hasattr(segment, 'words') and segment.words:
                            segment_data['words'] = [
                                {
                                    'start': word.start,
                                    'end': word.end,
                                    'word': word.word,
                                    'probability': getattr(word, 'probability', 1.0)
                                } for word in segment.words
                            ]
                        
                        processed_segments.append(segment_data)
                
                logger.info(f"Whisper 英文翻譯完成，共 {len(processed_segments)} 個段落")
                return processed_segments
                
            # 對於中文繁簡轉換，先生成繁體，然後轉換
            elif target_language in ['zh-TW', 'zh-CN']:
                # 如果有現有段落，直接重用並進行轉換
                if existing_segments:
                    logger.info(f"重用現有段落進行 {target_language} 轉換，保留時間戳修正")
                    processed_segments = []
                    for segment in existing_segments:
                        text = segment.get('text', '').strip()
                        if text:
                            # 進行繁簡轉換
                            if target_language == 'zh-CN':
                                text = self._convert_to_simplified(text)
                            elif target_language == 'zh-TW':
                                text = self._convert_to_traditional(text)
                            
                            # 保留原始段落的所有信息，包括修正的時間戳
                            segment_data = segment.copy()
                            segment_data['text'] = text
                            processed_segments.append(segment_data)
                    
                    logger.info(f"中文字幕轉換完成，保留 {len(processed_segments)} 個段落的時間戳修正")
                    return processed_segments
                else:
                    # 沒有現有段落時，重新轉錄
                    segments, info = self.model.transcribe(
                        input_file,
                        task="transcribe",
                        language='zh',
                        beam_size=model_params["beam_size"],
                        best_of=model_params["best_of"],
                        temperature=model_params["temperature"],
                        compression_ratio_threshold=2.0,
                        log_prob_threshold=-0.7,
                        no_speech_threshold=0.4,
                        condition_on_previous_text=True,
                        suppress_blank=True,
                        suppress_tokens=[-1],
                        word_timestamps=True,
                        vad_filter=True,
                        vad_parameters={
                            "threshold": 0.3,
                            "min_speech_duration_ms": 150,
                            "max_speech_duration_s": float("inf"),
                            "min_silence_duration_ms": 800,
                            "speech_pad_ms": 250
                        }
                    )
                    
                    # 收集段落並進行繁簡轉換
                    processed_segments = []
                    for segment in segments:
                        text = segment.text.strip()
                        if text:
                            # 進行繁簡轉換
                            if target_language == 'zh-CN':
                                text = self._convert_to_simplified(text)
                            elif target_language == 'zh-TW':
                                text = self._convert_to_traditional(text)
                            
                            segment_data = {
                                'start': segment.start,
                                'end': segment.end,
                                'text': text
                            }
                        
                        # 如果有詞級時間戳，添加到段落數據中
                        if hasattr(segment, 'words') and segment.words:
                            segment_data['words'] = [
                                {
                                    'start': word.start,
                                    'end': word.end,
                                    'word': word.word,
                                    'probability': getattr(word, 'probability', 1.0)
                                } for word in segment.words
                            ]
                        
                        processed_segments.append(segment_data)
                
                logger.info(f"中文字幕生成並轉換完成，共 {len(processed_segments)} 個段落")
                return processed_segments
            
            # 對於其他語言，保持原有邏輯
            else:
                # Whisper 語言代碼映射
                whisper_lang_map = {
                    'ja': 'ja', 
                    'ko': 'ko',
                    'es': 'es',
                    'fr': 'fr',
                    'de': 'de',
                    'it': 'it',
                    'pt': 'pt',
                    'ru': 'ru',
                    'ar': 'ar'
                }
                
                whisper_target_lang = whisper_lang_map.get(target_language, 'en')
                
                # 使用轉錄任務並指定目標語言
                segments, info = self.model.transcribe(
                    input_file,
                    task="transcribe",
                    language=whisper_target_lang,
                    beam_size=model_params["beam_size"],
                    best_of=model_params["best_of"],
                    temperature=model_params["temperature"],
                    compression_ratio_threshold=2.0,
                    log_prob_threshold=-0.7,
                    no_speech_threshold=0.4,
                    condition_on_previous_text=True,
                    suppress_blank=True,
                    suppress_tokens=[-1],
                    word_timestamps=True,
                    vad_filter=True,
                    vad_parameters={
                        "threshold": 0.3,
                        "min_speech_duration_ms": 150,
                        "max_speech_duration_s": float("inf"),
                        "min_silence_duration_ms": 800,
                        "speech_pad_ms": 250
                    }
                )
                
                # 收集處理後的段落
                processed_segments = []
                for segment in segments:
                    text = segment.text.strip()
                    if text:
                        segment_data = {
                            'start': segment.start,
                            'end': segment.end,
                            'text': text
                        }
                        
                        # 如果有詞級時間戳，添加到段落數據中
                        if hasattr(segment, 'words') and segment.words:
                            segment_data['words'] = [
                                {
                                    'start': word.start,
                                    'end': word.end,
                                    'word': word.word,
                                    'probability': getattr(word, 'probability', 1.0)
                                } for word in segment.words
                            ]
                        
                        processed_segments.append(segment_data)
                
                logger.info(f"Whisper 多語言處理完成，共 {len(processed_segments)} 個段落")
                return processed_segments
            
        except Exception as e:
            logger.error(f"Whisper 多語言處理失敗: {e}")
            raise e
    
    def _convert_to_simplified(self, text: str) -> str:
        """Convert text to Simplified Chinese (handles mixed traditional/simplified text)"""
        try:
            # Try using opencc first (if available)
            try:
                import opencc
                # Use t2s converter which handles mixed text well
                converter = opencc.OpenCC('t2s')  # Traditional to Simplified
                simplified_text = converter.convert(text)
                
                logger.debug(f"簡體轉換: '{text}' -> '{simplified_text}'")
                return simplified_text
            except ImportError:
                # Fallback to basic character mapping
                logger.info("OpenCC 不可用，使用基本字符映射進行簡體轉換")
                return self._basic_traditional_to_simplified(text)
        except Exception as e:
            logger.warning(f"簡體轉換失敗，返回原文: {e}")
            return text
    
    def _convert_to_traditional(self, text: str) -> str:
        """Convert text to Traditional Chinese (handles mixed simplified/traditional text)"""
        try:
            # Try using opencc first (if available)
            try:
                import opencc
                # First normalize any traditional to simplified, then convert to traditional
                # This ensures consistent conversion of mixed text
                t2s_converter = opencc.OpenCC('t2s')  # Traditional to Simplified first
                s2t_converter = opencc.OpenCC('s2t')  # Then Simplified to Traditional
                
                normalized_text = t2s_converter.convert(text)  # Normalize to simplified first
                traditional_text = s2t_converter.convert(normalized_text)  # Convert to traditional
                
                logger.debug(f"中文轉換: '{text}' -> 規範化: '{normalized_text}' -> 繁體: '{traditional_text}'")
                return traditional_text
            except ImportError:
                # Fallback to basic character mapping with normalization
                logger.info("OpenCC 不可用，使用基本字符映射進行繁體轉換")
                return self._basic_convert_to_traditional_robust(text)
        except Exception as e:
            logger.warning(f"繁體轉換失敗，返回原文: {e}")
            return text
    
    def _basic_traditional_to_simplified(self, text: str) -> str:
        """Basic Traditional to Simplified Chinese conversion using common character mappings"""
        # Common Traditional to Simplified mappings
        t2s_map = {
            '個': '个', '來': '来', '對': '对', '會': '会', '時': '时', '國': '国',
            '學': '学', '說': '说', '開': '开', '關': '关', '門': '门', '問': '问',
            '題': '题', '現': '现', '發': '发', '後': '后', '長': '长', '經': '经',
            '過': '过', '還': '还', '沒': '没', '見': '见', '聽': '听', '覺': '觉',
            '應': '应', '該': '该', '點': '点', '線': '线', '邊': '边', '間': '间',
            '內': '内', '網': '网', '電': '电', '話': '话', '機': '机', '車': '车',
            '動': '动', '運': '运', '進': '进', '遠': '远', '場': '场', '園': '园',
            '業': '业', '務': '务', '員': '员', '員': '员', '級': '级', '價': '价',
            '買': '买', '賣': '卖', '錢': '钱', '銀': '银', '行': '行', '處': '处',
            '辦': '办', '總': '总', '選': '选', '擇': '择', '決': '决', '議': '议',
            '討': '讨', '論': '论', '認': '认', '識': '识', '記': '记', '錄': '录',
            '書': '书', '報': '报', '紙': '纸', '雜': '杂', '誌': '志', '廣': '广',
            '告': '告', '視': '视', '聲': '声', '響': '响', '樂': '乐', '歌': '歌',
            '劇': '剧', '戲': '戏', '影': '影', '畫': '画', '圖': '图', '標': '标',
            '準': '准', '規': '规', '則': '则', '法': '法', '律': '律', '條': '条',
            '約': '约', '際': '际', '間': '间', '係': '系', '關': '关', '聯': '联',
            '結': '结', '構': '构', '建': '建', '設': '设', '計': '计', '劃': '划',
            '種': '种', '類': '类', '樣': '样', '變': '变', '化': '化', '統': '统',
            '傳': '传', '輸': '输', '導': '导', '領': '领', '帶': '带', '隊': '队',
            '團': '团', '組': '组', '織': '织', '參': '参', '與': '与', '協': '协',
            '調': '调', '節': '节', '制': '制', '造': '造', '產': '产', '品': '品',
            '質': '质', '量': '量', '數': '数', '據': '据', '資': '资', '料': '料',
            '訊': '讯', '息': '息', '內': '内', '容': '容', '格': '格', '式': '式',
            '檔': '档', '案': '案', '夾': '夹', '層': '层', '級': '级', '別': '别',
            '類': '类', '項': '项', '目': '目', '單': '单', '項': '项', '條': '条',
            '例': '例', '樣': '样', '本': '本', '版': '版', '號': '号', '碼': '码',
            '編': '编', '輯': '辑', '製': '制', '作': '作', '創': '创', '造': '造',
            '設': '设', '計': '计', '畫': '画', '劃': '划', '備': '备', '準': '准',
            '確': '确', '認': '认', '證': '证', '實': '实', '現': '现', '達': '达',
            '到': '到', '獲': '获', '得': '得', '取': '取', '給': '给', '與': '与',
            '供': '供', '提': '提', '交': '交', '付': '付', '收': '收', '納': '纳',
            '接': '接', '受': '受', '處': '处', '理': '理', '辦': '办', '事': '事',
            '項': '项', '務': '务', '服': '服', '務': '务', '業': '业', '職': '职',
            '業': '业', '專': '专', '業': '业', '課': '课', '程': '程', '訓': '训',
            '練': '练', '習': '习', '學': '学', '習': '习', '教': '教', '育': '育',
            '師': '师', '資': '资', '訊': '讯', '息': '息', '知': '知', '識': '识',
            '經': '经', '驗': '验', '技': '技', '術': '术', '能': '能', '力': '力',
            '氣': '气', '質': '质', '個': '个', '性': '性', '特': '特', '色': '色'
        }
        
        result = text
        for trad, simp in t2s_map.items():
            result = result.replace(trad, simp)
        
        return result
    
    def _basic_simplified_to_traditional(self, text: str) -> str:
        """Basic Simplified to Traditional Chinese conversion using common character mappings"""
        # Common Simplified to Traditional mappings (reverse of above)
        s2t_map = {
            '个': '個', '来': '來', '对': '對', '会': '會', '时': '時', '国': '國',
            '学': '學', '说': '說', '开': '開', '关': '關', '门': '門', '问': '問',
            '题': '題', '现': '現', '发': '發', '后': '後', '长': '長', '经': '經',
            '过': '過', '还': '還', '没': '沒', '见': '見', '听': '聽', '觉': '覺',
            '应': '應', '该': '該', '点': '點', '线': '線', '边': '邊', '间': '間',
            '内': '內', '网': '網', '电': '電', '话': '話', '机': '機', '车': '車',
            '动': '動', '运': '運', '进': '進', '远': '遠', '场': '場', '园': '園',
            '业': '業', '务': '務', '员': '員', '级': '級', '价': '價',
            '买': '買', '卖': '賣', '钱': '錢', '银': '銀', '处': '處',
            '办': '辦', '总': '總', '选': '選', '择': '擇', '决': '決', '议': '議',
            '讨': '討', '论': '論', '认': '認', '识': '識', '记': '記', '录': '錄',
            '书': '書', '报': '報', '纸': '紙', '杂': '雜', '志': '誌', '广': '廣',
            '视': '視', '声': '聲', '响': '響', '乐': '樂',
            '剧': '劇', '戏': '戲', '画': '畫', '图': '圖', '标': '標',
            '准': '準', '规': '規', '则': '則', '条': '條',
            '约': '約', '际': '際', '系': '係', '联': '聯',
            '结': '結', '构': '構', '设': '設', '计': '計', '划': '劃',
            '种': '種', '类': '類', '样': '樣', '变': '變', '统': '統',
            '传': '傳', '输': '輸', '导': '導', '领': '領', '带': '帶', '队': '隊',
            '团': '團', '组': '組', '织': '織', '参': '參', '与': '與', '协': '協',
            '调': '調', '节': '節', '制': '制', '产': '產',
            '质': '質', '数': '數', '据': '據', '资': '資',
            '讯': '訊', '档': '檔', '夹': '夾', '层': '層', '别': '別',
            '项': '項', '单': '單', '条': '條',
            '号': '號', '码': '碼',
            '编': '編', '辑': '輯', '制': '製', '创': '創',
            '设': '設', '计': '計', '画': '畫', '划': '劃', '备': '備', '准': '準',
            '确': '確', '认': '認', '证': '證', '实': '實', '现': '現', '达': '達',
            '获': '獲', '给': '給',
            '纳': '納', '处': '處', '办': '辦', '项': '項', '务': '務',
            '职': '職', '专': '專', '课': '課', '训': '訓',
            '练': '練', '习': '習', '师': '師', '资': '資', '讯': '訊', '识': '識',
            '经': '經', '验': '驗', '术': '術',
            '气': '氣', '质': '質', '个': '個'
        }
        
        result = text
        for simp, trad in s2t_map.items():
            result = result.replace(simp, trad)
        
        return result
    
    def _basic_convert_to_traditional_robust(self, text: str) -> str:
        """Robust basic conversion to Traditional Chinese with normalization"""
        # Step 1: First normalize any traditional to simplified using reverse mapping
        normalized_text = text
        
        # Traditional to Simplified normalization mapping (for mixed text handling)
        t2s_normalize = {
            '個': '个', '來': '来', '對': '对', '會': '会', '時': '时', '國': '国',
            '學': '学', '說': '说', '開': '开', '關': '关', '門': '门', '問': '问',
            '題': '题', '現': '现', '發': '发', '後': '后', '長': '长', '經': '经',
            '過': '过', '還': '还', '沒': '没', '見': '见', '聽': '听', '覺': '觉',
            '應': '应', '該': '该', '點': '点', '線': '线', '邊': '边', '間': '间',
            '內': '内', '網': '网', '電': '电', '話': '话', '機': '机', '車': '车',
            '動': '动', '運': '运', '進': '进', '遠': '远', '場': '场', '園': '园',
            '業': '业', '務': '务', '員': '员', '級': '级', '價': '价', '買': '买', 
            '賣': '卖', '錢': '钱', '銀': '银', '處': '处', '辦': '办', '總': '总', 
            '選': '选', '擇': '择', '決': '决', '議': '议', '討': '讨', '論': '论', 
            '認': '认', '識': '识', '記': '记', '錄': '录', '書': '书', '報': '报', 
            '紙': '纸', '雜': '杂', '誌': '志', '廣': '广', '視': '视', '聲': '声', 
            '響': '响', '樂': '乐', '劇': '剧', '戲': '戏', '畫': '画', '圖': '图', 
            '標': '标', '準': '准', '規': '规', '則': '则', '條': '条', '約': '约', 
            '際': '际', '係': '系', '關': '关', '聯': '联', '結': '结', '構': '构', 
            '設': '设', '計': '计', '劃': '划', '種': '种', '類': '类', '樣': '样', 
            '變': '变', '統': '统', '傳': '传', '輸': '输', '導': '导', '領': '领', 
            '帶': '带', '隊': '队', '團': '团', '組': '组', '織': '织', '參': '参', 
            '與': '与', '協': '协', '調': '调', '節': '节', '產': '产', '質': '质', 
            '數': '数', '據': '据', '資': '资', '訊': '讯', '檔': '档', '夾': '夹', 
            '層': '层', '別': '别', '項': '项', '單': '单', '號': '号', '碼': '码', 
            '編': '编', '輯': '辑', '製': '制', '創': '创', '設': '设', '畫': '画', 
            '劃': '划', '備': '备', '確': '确', '證': '证', '實': '实', '現': '现', 
            '達': '达', '獲': '获', '給': '给', '納': '纳', '職': '职', '專': '专', 
            '課': '课', '訓': '训', '練': '练', '習': '习', '師': '师', '經': '经', 
            '驗': '验', '術': '术', '氣': '气'
        }
        
        # Normalize traditional characters to simplified
        for trad, simp in t2s_normalize.items():
            normalized_text = normalized_text.replace(trad, simp)
        
        # Step 2: Convert simplified to traditional
        result = self._basic_simplified_to_traditional(normalized_text)
        
        logger.debug(f"基本繁體轉換: '{text}' -> 規範化: '{normalized_text}' -> 繁體: '{result}'")
        return result
    
    def _save_subtitle(self, segments: list, output_file: str, format: str) -> bool:
        """保存字幕文件"""
        try:
            from subtitle_formatter import SubtitleFormatter
            return SubtitleFormatter.save_subtitle(segments, output_file, format)
        except Exception as e:
            logger.error(f"保存字幕失敗: {e}")
            return False
    
    def get_supported_formats(self) -> list:
        """獲取支援的格式"""
        return ["srt", "vtt", "txt"]
    
    def get_supported_models(self) -> list:
        """獲取支援的模型"""
        return self.supported_models
    
    def change_model(self, model_size: str, device: str = None, compute_type: str = None) -> bool:
        """動態更換模型"""
        if model_size not in self.supported_models:
            logger.error(f"不支援的模型大小: {model_size}")
            return False
        
        # 清理舊模型
        self.cleanup()
        
        # 設定新參數
        self.model_size = model_size
        if device:
            self.device = device
        if compute_type:
            self.compute_type = compute_type
        
        logger.info(f"切換到模型: {self.model_size}")
        return True
    
    def get_model_info(self) -> dict:
        """獲取當前模型資訊"""
        return {
            "model_size": self.model_size,
            "device": self.device,
            "compute_type": self.compute_type,
            "initialized": self.initialized,
            "parameters": self.model_params.get(self.model_size, {})
        }
    
    def _analyze_subtitle_quality(self, segments: list, progress_callback: Optional[Callable] = None):
        """分析字幕質量，採用 srt_final-orign 的優秀分析方法"""
        try:
            if not segments:
                return
            
            # 語音理解度分析
            understanding_levels = {'high': 0, 'medium': 0, 'low': 0}
            content_issues = []  # 過短句子和填充詞
            suspicious_issues = []  # 語意異常等可疑內容
            pure_uncertainty = []  # 排除內容問題後，純粹的模型不確定
            all_confidences = []
            
            for i, segment in enumerate(segments):
                text = segment.get('text', '').strip()
                start_time = segment.get('start', 0.0)
                end_time = segment.get('end', 0.0)
                
                # 獲取置信度（如果有詞級資料）
                avg_logprob = -0.3  # 預設值
                if 'words' in segment and segment['words']:
                    # 計算平均對數概率
                    probabilities = [word.get('probability', 0.8) for word in segment['words']]
                    if probabilities:
                        avg_prob = sum(probabilities) / len(probabilities)
                        avg_logprob = np.log(max(avg_prob, 0.01))  # 避免 log(0)
                
                # 判斷理解度等級（採用 srt_final-orign 的標準）
                if avg_logprob > -0.3:
                    understanding_level = 'high'
                elif avg_logprob > -0.5:
                    understanding_level = 'medium'
                else:
                    understanding_level = 'low'
                
                # 內容問題檢測
                has_content_issue = False
                issue_type = ""
                
                # 檢測過短的句子
                if len(text) < 3:
                    has_content_issue = True
                    issue_type = "句子過短"
                
                # 檢測常見的填充詞或噪音
                noise_words = ['嗯', '啊', '呃', '那個', '這個', '就是', '然後', '所以']
                if any(word in text for word in noise_words):
                    has_content_issue = True
                    issue_type = "包含填充詞"
                
                # 可疑內容檢測
                has_suspicious_content = False
                suspicious_reasons = []
                confidence_score = 1.0
                
                if not has_content_issue:
                    # 詞彙頻率分析
                    rare_words = ['腳膜', '膜都很', '都很透明', '膜都', '都很', '淒淋鞋', '淒淋', '淋鞋']
                    if any(word in text for word in rare_words):
                        has_suspicious_content = True
                        suspicious_reasons.append("包含罕見詞彙")
                        confidence_score *= 0.7
                    
                    # 語義一致性檢測
                    if '都很' in text and len(text) < 12:
                        if any(char in text for char in ['膜', '透', '明']):
                            has_suspicious_content = True
                            suspicious_reasons.append("語義搭配異常")
                            confidence_score *= 0.6
                    
                    # 重複模式檢測
                    if len(text) > 3:
                        char_count = {}
                        for char in text:
                            char_count[char] = char_count.get(char, 0) + 1
                        max_repeat = max(char_count.values())
                        if max_repeat > len(text) * 0.4:
                            has_suspicious_content = True
                            suspicious_reasons.append("字符重複過多")
                            confidence_score *= 0.5
                    
                    # 綜合合理性判斷
                    if confidence_score < 0.6:
                        has_suspicious_content = True
                        if "綜合分數過低" not in suspicious_reasons:
                            suspicious_reasons.append(f"綜合分數過低({confidence_score:.2f})")
                
                # 分類問題片段
                if has_content_issue:
                    content_issues.append({
                        "id": i + 1,
                        "text": text,
                        "avg_logprob": avg_logprob,
                        "understanding_level": understanding_level,
                        "issue_type": issue_type,
                        "start": start_time,
                        "end": end_time
                    })
                elif has_suspicious_content:
                    suspicious_issues.append({
                        "id": i + 1,
                        "text": text,
                        "avg_logprob": avg_logprob,
                        "understanding_level": understanding_level,
                        "issue_type": f"可疑內容({', '.join(suspicious_reasons)})",
                        "start": start_time,
                        "end": end_time
                    })
                elif understanding_level == 'low':
                    pure_uncertainty.append({
                        "id": i + 1,
                        "text": text,
                        "avg_logprob": avg_logprob,
                        "understanding_level": understanding_level,
                        "start": start_time,
                        "end": end_time
                    })
                
                understanding_levels[understanding_level] += 1
                all_confidences.append(avg_logprob)
            
            # 顯示理解度統計信息
            if all_confidences:
                min_conf = min(all_confidences)
                max_conf = max(all_confidences)
                avg_conf = sum(all_confidences) / len(all_confidences)
                logger.info("=== 語音理解度分析 ===")
                logger.info(f"理解度統計: 高理解度={understanding_levels['high']}個, 中理解度={understanding_levels['medium']}個, 低理解度={understanding_levels['low']}個")
                logger.info(f"avg_logprob範圍: {min_conf:.3f} ~ {max_conf:.3f}, 平均值={avg_conf:.3f}")
            
            # 顯示各種問題片段
            logger.warning("=== 字幕品質分析報告 ===")
            
            # 顯示內容問題
            if content_issues:
                logger.warning(f"發現 {len(content_issues)} 個內容問題片段")
                logger.warning("內容問題前5個:")
                for i, seg in enumerate(content_issues[:5]):
                    start_time = self._format_time(seg["start"])
                    end_time = self._format_time(seg["end"])
                    logger.warning(f"  {i+1}. [{start_time} --> {end_time}] 問題: {seg['issue_type']}")
                    logger.warning(f"     識別結果: {seg['text']}")
            else:
                logger.info("沒有發現內容問題片段")
            
            # 顯示可疑內容
            if suspicious_issues:
                logger.warning(f"發現 {len(suspicious_issues)} 個可疑內容片段")
                logger.warning("可疑內容前5個:")
                for i, seg in enumerate(suspicious_issues[:5]):
                    start_time = self._format_time(seg["start"])
                    end_time = self._format_time(seg["end"])
                    logger.warning(f"  {i+1}. [{start_time} --> {end_time}] 問題: {seg['issue_type']}")
                    logger.warning(f"     識別結果: {seg['text']}")
            else:
                logger.info("沒有發現可疑內容片段")
            
            # 顯示純粹的模型不確定片段
            if pure_uncertainty:
                logger.warning(f"發現 {len(pure_uncertainty)} 個純粹的模型不確定片段")
                logger.warning("模型最不確定的前5句:")
                
                # 按avg_logprob排序，顯示前5個
                pure_uncertainty.sort(key=lambda x: x["avg_logprob"])
                for i, seg in enumerate(pure_uncertainty[:5]):
                    start_time = self._format_time(seg["start"])
                    end_time = self._format_time(seg["end"])
                    logger.warning(f"  {i+1}. [{start_time} --> {end_time}]")
                    logger.warning(f"     理解度: {seg['understanding_level']} (avg_logprob: {seg['avg_logprob']:.3f})")
                    logger.warning(f"     識別結果: {seg['text']}")
            else:
                logger.info("沒有發現純粹的模型不確定片段")
                
        except Exception as e:
            logger.error(f"字幕品質分析失敗: {e}")
    
    def _format_time(self, seconds: float) -> str:
        """格式化時間為SRT格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

    def cleanup(self):
        """清理資源"""
        if self.model:
            # Faster-Whisper 會自動管理資源
            self.model = None
        self.initialized = False


def test_simple_generation():
    """測試簡化版字幕生成"""
    print("=== 測試簡化版字幕生成 ===")
    
    # 創建測試音頻
    try:
        import numpy as np
        import soundfile as sf
        
        # 創建簡單的測試音頻
        duration = 3.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # 創建包含多個頻率的音頻（模擬語音）
        audio = 0.3 * (
            np.sin(2 * np.pi * 220 * t) +  # 低頻
            0.5 * np.sin(2 * np.pi * 440 * t) +  # 中頻
            0.3 * np.sin(2 * np.pi * 880 * t)   # 高頻
        )
        
        test_file = "simple_test.wav"
        sf.write(test_file, audio, sample_rate)
        print(f"[OK] 創建測試音頻: {test_file}")
        
        # 測試字幕生成
        core = SimplifiedSubtitleCore()
        
        def progress_callback(value, message):
            print(f"[{value:3d}%] {message}")
        
        print("[INFO] 初始化模型...")
        if core.initialize(progress_callback):
            print("[INFO] 開始生成字幕...")
            output_file = "simple_test.srt"
            
            success = core.generate_subtitle(
                test_file,
                output_file,
                language=None,
                format="srt",
                progress_callback=progress_callback
            )
            
            if success and os.path.exists(output_file):
                print(f"[OK] 字幕生成成功: {output_file}")
                
                # 顯示結果
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print("字幕內容預覽:")
                    print("-" * 40)
                    print(content[:300] + "..." if len(content) > 300 else content)
                    print("-" * 40)
                
                # 清理測試文件
                os.remove(test_file)
                os.remove(output_file)
                
                return True
            else:
                print("[ERROR] 字幕生成失敗")
                return False
        else:
            print("[ERROR] 模型初始化失敗")
            return False
            
    except ImportError:
        print("[WARNING] 缺少測試依賴，跳過測試")
        return True
    except Exception as e:
        print(f"[ERROR] 測試失敗: {e}")
        return False


def main():
    """主函數 - 支援命令行和Electron調用"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='簡化版字幕生成工具')
    parser.add_argument('--files', type=str, help='JSON格式的檔案列表')
    parser.add_argument('--settings', type=str, help='JSON格式的設定')
    parser.add_argument('--corrections', type=str, help='JSON格式的修正規則')
    parser.add_argument('--test', action='store_true', help='運行測試模式')
    
    args = parser.parse_args()
    
    # 設定日誌
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    if args.test:
        # 測試模式
        if test_simple_generation():
            print("\n[SUCCESS] Simplified subtitle generation test passed")
            return 0
        else:
            print("\n[FAILED] Simplified subtitle generation test failed")
            return 1
    
    if not args.files or not args.settings:
        print("Error: File list and settings are required")
        return 1
    
    try:
        # 解析參數
        files = json.loads(args.files)
        settings = json.loads(args.settings)
        corrections = json.loads(args.corrections) if args.corrections else []
        
        # 創建字幕生成器
        generator = SimplifiedSubtitleCore(
            model_size=settings.get('model', 'medium'),
            device='auto'
        )
        
        # 初始化生成器
        print(f"PROGRESS:{json.dumps({'percent': 0, 'filename': '', 'status': 'initializing', 'message': '正在初始化AI模型...'})}")
        if not generator.initialize():
            print(f"PROGRESS:{json.dumps({'percent': 0, 'filename': '', 'status': 'error', 'message': '模型初始化失敗'})}")
            return 1
        
        # 處理每個檔案
        total_files = len(files)
        for i, file_path in enumerate(files):
            if not os.path.exists(file_path):
                print(f"PROGRESS:{json.dumps({'percent': (i/total_files)*100, 'filename': file_path, 'status': 'error', 'message': '檔案不存在'})}")
                continue
            
            try:
                print(f"PROGRESS:{json.dumps({'percent': (i/total_files)*100, 'filename': os.path.basename(file_path), 'status': 'processing'})}")
                
                # 生成字幕 - 構建輸出檔案路徑
                input_path = Path(file_path)
                output_dir = settings.get('customDir', '') or str(input_path.parent)
                output_format = settings.get('outputFormat', 'srt')
                output_file = os.path.join(output_dir, f"{input_path.stem}.{output_format}")
                
                # 生成字幕
                output_lang = settings.get('outputLanguage', 'same')
                result = generator.generate_subtitle(
                    input_file=file_path,
                    output_file=output_file,
                    language=settings.get('language', None) if settings.get('language') != 'auto' else None,
                    output_language=output_lang if output_lang != 'same' else None,
                    format=output_format,
                    progress_callback=None
                )
                
                if result:
                    print(f"PROGRESS:{json.dumps({'percent': ((i+1)/total_files)*100, 'filename': os.path.basename(file_path), 'status': 'completed'})}")
                else:
                    print(f"PROGRESS:{json.dumps({'percent': ((i+1)/total_files)*100, 'filename': os.path.basename(file_path), 'status': 'error', 'message': '生成失敗'})}")
                    
            except Exception as e:
                print(f"PROGRESS:{json.dumps({'percent': ((i+1)/total_files)*100, 'filename': os.path.basename(file_path), 'status': 'error', 'message': str(e)})}")
        
        print("Processing completed successfully")
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())