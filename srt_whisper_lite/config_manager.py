#!/usr/bin/env python3
"""
配置管理器
管理用戶設置和參數配置
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "user_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_default_config()
        self.load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """載入默認配置
        
        模型配置決策記錄 (2025-08-12):
        - 主要模型: Large-v3 預設參數 (生產版本)
        - 備用模型: Medium 優化配置 (未來免費版本，95.4%手動編輯匹配度)
        - 選擇理由: Large-v3預設參數無需調教即達最佳性能
        """
        return {
            # 模型配置 - 主要模型：Large-v3 預設參數
            "model": {
                "primary_model": "large-v3",      # 主要生產模型
                "backup_model": "medium",         # 備用免費版模型
                "size": "large-v3",               # 當前使用模型 (2025-08-12決定)
                "use_default_params": True,       # 使用預設參數 (Large-v3最優)
                "device": "auto",
                "compute_type": "auto",
                "num_workers": 4
            },
            
            # Medium 優化配置 (保留作為免費版備用)
            "medium_optimized_config": {
                "status": "backup_for_free_version",
                "achievement": "95.4%_manual_editing_match",
                "vad_parameters": {
                    "threshold": 0.05,
                    "min_speech_duration_ms": 50,
                    "min_silence_duration_ms": 100,
                    "speech_pad_ms": 50
                },
                "whisper_params": {
                    "beam_size": 3,
                    "condition_on_previous_text": False,
                    "compression_ratio_threshold": 1.8,
                    "log_prob_threshold": -1.5,
                    "no_speech_threshold": 0.4
                }
            },
            
            # Whisper 轉錄參數
            "transcription": {
                "beam_size": 6,
                "best_of": 6,
                "temperature": [0.0, 0.2, 0.4, 0.6, 0.8],
                "compression_ratio_threshold": 2.0,
                "log_prob_threshold": -0.7,
                "no_speech_threshold": 0.4,
                "condition_on_previous_text": True,
                "word_timestamps": True
            },
            
            # VAD 參數
            "vad": {
                "enabled": True,
                "threshold": 0.3,
                "min_speech_duration_ms": 150,
                "max_speech_duration_s": float("inf"),
                "min_silence_duration_ms": 800,
                "speech_pad_ms": 250
            },
            
            # 音頻預處理
            "audio_processing": {
                "target_sample_rate": 16000,
                "enable_normalize": True,
                "enable_denoise": True,
                "enable_enhancement": True,
                "noise_reduce_strength": 0.6,
                "dynamic_range_ratio": 0.3,
                "speech_freq_boost": 2.0,
                "high_freq_cut": 8000,
                "low_freq_cut": 80,
                "compressor_threshold": -20,
                "compressor_ratio": 4.0,
                "limiter_threshold": 0.95
            },
            
            # 語意處理
            "semantic": {
                "enabled": True,
                "auto_detect_language": True,
                "sentence_min_length": 3,
                "sentence_max_length": 100,
                "merge_short_segments": True,
                "split_long_segments": True
            },
            
            # 後處理優化
            "post_processing": {
                "remove_duplicates": True,
                "clean_filler_words": True,
                "smooth_timestamps": True,
                "adjust_reading_speed": True,
                "apply_custom_corrections": True,
                "similarity_threshold": 0.7,
                "min_segment_duration": 0.5,
                "max_segment_duration": 10.0,
                "min_chars_per_second": 8,
                "max_chars_per_second": 20
            },
            
            # 輸出設置
            "output": {
                "default_format": "srt",
                "max_line_length": 42,
                "max_lines_per_subtitle": 2,
                "include_timestamps_in_txt": False,
                "custom_output_directory": None
            },
            
            # 界面設置
            "ui": {
                "theme": "light",
                "language": "zh-TW",
                "auto_save_settings": True,
                "show_advanced_options": False,
                "remember_last_directory": True,
                "last_input_directory": None,
                "last_output_directory": None
            },
            
            # 性能設置
            "performance": {
                "enable_gpu": True,
                "max_memory_usage": "auto",
                "enable_parallel_processing": True,
                "cache_models": True,
                "cleanup_temp_files": True
            }
        }
    
    def load_config(self) -> bool:
        """載入配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # 遞歸合併配置
                self.config = self._merge_configs(self.config, user_config)
                logger.info(f"配置文件載入成功: {self.config_file}")
                return True
            else:
                logger.info("配置文件不存在，使用默認配置")
                self.save_config()  # 創建默認配置文件
                return True
                
        except Exception as e:
            logger.error(f"載入配置文件失敗: {e}")
            return False
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置文件保存成功: {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存配置文件失敗: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        獲取配置值
        
        Args:
            key_path: 配置鍵路徑，如 "model.size" 或 "transcription.beam_size"
            default: 默認值
            
        Returns:
            配置值
        """
        try:
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                value = value[key]
            
            return value
            
        except (KeyError, TypeError):
            logger.warning(f"配置鍵不存在: {key_path}")
            return default
    
    def set(self, key_path: str, value: Any) -> bool:
        """
        設置配置值
        
        Args:
            key_path: 配置鍵路徑
            value: 要設置的值
            
        Returns:
            是否成功
        """
        try:
            keys = key_path.split('.')
            config = self.config
            
            # 導航到最後一層
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            # 設置值
            config[keys[-1]] = value
            
            # 自動保存（如果啟用）
            if self.get("ui.auto_save_settings", True):
                self.save_config()
            
            logger.debug(f"配置已更新: {key_path} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"設置配置失敗: {e}")
            return False
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """遞歸合併配置"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_model_config(self) -> Dict[str, Any]:
        """獲取模型配置"""
        return {
            "model_size": self.get("model.size"),
            "device": self.get("model.device"),
            "compute_type": self.get("model.compute_type"),
            "num_workers": self.get("model.num_workers")
        }
    
    def get_transcription_config(self) -> Dict[str, Any]:
        """獲取轉錄配置"""
        config = {}
        for key in ["beam_size", "best_of", "temperature", "compression_ratio_threshold",
                   "log_prob_threshold", "no_speech_threshold", "condition_on_previous_text",
                   "word_timestamps"]:
            config[key] = self.get(f"transcription.{key}")
        return config
    
    def get_vad_config(self) -> Dict[str, Any]:
        """獲取VAD配置"""
        if not self.get("vad.enabled"):
            return None
            
        return {
            "threshold": self.get("vad.threshold"),
            "min_speech_duration_ms": self.get("vad.min_speech_duration_ms"),
            "max_speech_duration_s": self.get("vad.max_speech_duration_s"),
            "min_silence_duration_ms": self.get("vad.min_silence_duration_ms"),
            "speech_pad_ms": self.get("vad.speech_pad_ms")
        }
    
    def get_audio_processing_config(self) -> Dict[str, Any]:
        """獲取音頻處理配置"""
        return {
            "target_sample_rate": self.get("audio_processing.target_sample_rate"),
            "enable_normalize": self.get("audio_processing.enable_normalize"),
            "enable_denoise": self.get("audio_processing.enable_denoise"),
            "enable_enhancement": self.get("audio_processing.enable_enhancement"),
            "noise_reduce_strength": self.get("audio_processing.noise_reduce_strength"),
            "enhancement_params": {
                "dynamic_range_ratio": self.get("audio_processing.dynamic_range_ratio"),
                "speech_freq_boost": self.get("audio_processing.speech_freq_boost"),
                "high_freq_cut": self.get("audio_processing.high_freq_cut"),
                "low_freq_cut": self.get("audio_processing.low_freq_cut"),
                "compressor_threshold": self.get("audio_processing.compressor_threshold"),
                "compressor_ratio": self.get("audio_processing.compressor_ratio"),
                "limiter_threshold": self.get("audio_processing.limiter_threshold")
            }
        }
    
    def reset_to_defaults(self) -> bool:
        """重置為默認配置"""
        try:
            self.config = self._load_default_config()
            self.save_config()
            logger.info("配置已重置為默認值")
            return True
        except Exception as e:
            logger.error(f"重置配置失敗: {e}")
            return False
    
    def export_config(self, file_path: str) -> bool:
        """導出配置到指定文件"""
        try:
            export_path = Path(file_path)
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置已導出到: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"導出配置失敗: {e}")
            return False
    
    def import_config(self, file_path: str) -> bool:
        """從指定文件導入配置"""
        try:
            import_path = Path(file_path)
            if not import_path.exists():
                logger.error(f"配置文件不存在: {import_path}")
                return False
            
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # 合併導入的配置
            self.config = self._merge_configs(self.config, imported_config)
            self.save_config()
            
            logger.info(f"配置已從 {import_path} 導入")
            return True
            
        except Exception as e:
            logger.error(f"導入配置失敗: {e}")
            return False


# 全局配置實例
_config_manager = None

def get_config_manager() -> ConfigManager:
    """獲取全局配置管理器實例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_config(key_path: str, default: Any = None) -> Any:
    """快捷方法：獲取配置值"""
    return get_config_manager().get(key_path, default)

def set_config(key_path: str, value: Any) -> bool:
    """快捷方法：設置配置值"""
    return get_config_manager().set(key_path, value)