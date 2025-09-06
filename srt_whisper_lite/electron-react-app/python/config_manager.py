#!/usr/bin/env python3
"""
配置管理器
統一管理應用設置和用戶配置
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
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """載入配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"載入配置失敗: {e}")
        
        return self.get_default_config()
    
    def save_config(self) -> bool:
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存配置失敗: {e}")
            return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            "model": "medium",
            "language": "auto",
            "output_format": "srt",
            "enable_gpu": True,
            "vad_threshold": 0.35,
            "enable_subeasy": True,
            "audio_enhancement": True,
            "semantic_segmentation": True,
            "output_language": "same"
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """獲取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """設置配置值"""
        self.config[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """批量更新配置"""
        self.config.update(updates)
    
    def reset_to_default(self) -> None:
        """重置為默認配置"""
        self.config = self.get_default_config()

# 全局配置實例
global_config = ConfigManager()