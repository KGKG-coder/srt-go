#!/usr/bin/env python3
"""
國際化支援模組
支援多語言界面和訊息
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class I18n:
    """國際化管理器"""
    
    def __init__(self, default_language: str = 'zh-TW'):
        self.current_language = default_language
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """載入翻譯字典"""
        return {
            'zh-TW': {
                'processing': '處理中...',
                'completed': '完成',
                'failed': '失敗',
                'initializing': '初始化中...',
                'loading_model': '載入模型...',
                'generating_subtitle': '生成字幕中...',
                'audio_processing': '音頻預處理...',
                'saving_file': '保存文件中...',
                'error_occurred': '發生錯誤',
                'file_not_found': '文件未找到',
                'invalid_format': '無效格式',
                'success': '成功'
            },
            'zh-CN': {
                'processing': '处理中...',
                'completed': '完成',
                'failed': '失败',
                'initializing': '初始化中...',
                'loading_model': '加载模型...',
                'generating_subtitle': '生成字幕中...',
                'audio_processing': '音频预处理...',
                'saving_file': '保存文件中...',
                'error_occurred': '发生错误',
                'file_not_found': '文件未找到',
                'invalid_format': '无效格式',
                'success': '成功'
            },
            'en': {
                'processing': 'Processing...',
                'completed': 'Completed',
                'failed': 'Failed',
                'initializing': 'Initializing...',
                'loading_model': 'Loading model...',
                'generating_subtitle': 'Generating subtitle...',
                'audio_processing': 'Audio preprocessing...',
                'saving_file': 'Saving file...',
                'error_occurred': 'Error occurred',
                'file_not_found': 'File not found',
                'invalid_format': 'Invalid format',
                'success': 'Success'
            }
        }
    
    def set_language(self, language: str) -> None:
        """設置語言"""
        if language in self.translations:
            self.current_language = language
        else:
            logger.warning(f"不支援的語言: {language}")
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """獲取翻譯文本"""
        current_dict = self.translations.get(self.current_language, {})
        return current_dict.get(key, default or key)
    
    def get_supported_languages(self) -> list:
        """獲取支援的語言列表"""
        return list(self.translations.keys())

# 全局國際化實例
i18n = I18n()