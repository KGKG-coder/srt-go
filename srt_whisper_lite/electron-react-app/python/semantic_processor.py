#!/usr/bin/env python3
"""
語義分割處理器
智能句子邊界檢測和語義分割
"""

import re
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class SemanticSegmentProcessor:
    """語義分割處理器"""
    
    def __init__(self):
        """初始化語義處理器"""
        # 中文句子結束符
        self.chinese_endings = ['。', '！', '？', '；', '：', '，']
        
        # 英文句子結束符
        self.english_endings = ['.', '!', '?', ';', ':']
        
        # 語言檢測模式
        self.language_patterns = {
            'zh': re.compile(r'[\u4e00-\u9fff]'),
            'en': re.compile(r'[a-zA-Z]'),
            'ja': re.compile(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]'),
            'ko': re.compile(r'[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f]')
        }
    
    def detect_language(self, text: str) -> str:
        """檢測文本主要語言"""
        if not text:
            return 'auto'
        
        # 計算各語言字符比例
        total_chars = len(text)
        language_counts = {}
        
        for lang, pattern in self.language_patterns.items():
            matches = pattern.findall(text)
            language_counts[lang] = len(matches) / total_chars if total_chars > 0 else 0
        
        # 返回比例最高的語言
        max_lang = max(language_counts, key=language_counts.get)
        if language_counts[max_lang] > 0.3:  # 至少30%的字符符合該語言
            return max_lang
        
        return 'auto'
    
    def segment_by_semantic(self, segments: List[Dict], target_language: str = 'auto') -> List[Dict]:
        """基於語義進行智能分割"""
        if not segments:
            return []
        
        # 檢測語言
        if target_language == 'auto':
            all_text = ' '.join([seg.get('text', '') for seg in segments])
            target_language = self.detect_language(all_text)
        
        logger.info(f"使用語言模式: {target_language}")
        
        if target_language == 'zh':
            return self._segment_chinese(segments)
        elif target_language == 'en':
            return self._segment_english(segments)
        else:
            return self._segment_universal(segments)
    
    def _segment_chinese(self, segments: List[Dict]) -> List[Dict]:
        """中文語義分割"""
        processed_segments = []
        
        for segment in segments:
            text = segment.get('text', '').strip()
            if not text:
                continue
            
            # 檢測是否有完整句子結構
            has_complete_sentence = any(ending in text for ending in self.chinese_endings)
            
            if has_complete_sentence:
                # 按句號等分割
                sentences = re.split(r'[。！？；]', text)
                sentences = [s.strip() for s in sentences if s.strip()]
                
                if len(sentences) > 1:
                    # 多個句子，需要分割
                    duration = segment['end'] - segment['start']
                    sentence_duration = duration / len(sentences)
                    
                    for i, sentence in enumerate(sentences):
                        new_segment = segment.copy()
                        new_segment['text'] = sentence
                        new_segment['start'] = segment['start'] + i * sentence_duration
                        new_segment['end'] = segment['start'] + (i + 1) * sentence_duration
                        processed_segments.append(new_segment)
                else:
                    processed_segments.append(segment)
            else:
                processed_segments.append(segment)
        
        return processed_segments
    
    def _segment_english(self, segments: List[Dict]) -> List[Dict]:
        """英文語義分割"""
        processed_segments = []
        
        for segment in segments:
            text = segment.get('text', '').strip()
            if not text:
                continue
            
            # 按句號分割
            sentences = re.split(r'[.!?;]', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) > 1:
                # 多個句子
                duration = segment['end'] - segment['start']
                sentence_duration = duration / len(sentences)
                
                for i, sentence in enumerate(sentences):
                    new_segment = segment.copy()
                    new_segment['text'] = sentence
                    new_segment['start'] = segment['start'] + i * sentence_duration
                    new_segment['end'] = segment['start'] + (i + 1) * sentence_duration
                    processed_segments.append(new_segment)
            else:
                processed_segments.append(segment)
        
        return processed_segments
    
    def _segment_universal(self, segments: List[Dict]) -> List[Dict]:
        """通用語義分割"""
        processed_segments = []
        
        for segment in segments:
            text = segment.get('text', '').strip()
            if text:
                processed_segments.append(segment)
        
        return processed_segments
    
    def optimize_segment_timing(self, segments: List[Dict]) -> List[Dict]:
        """優化段落時間戳"""
        if len(segments) <= 1:
            return segments
        
        optimized = segments.copy()
        
        # 確保時間戳連續性
        for i in range(len(optimized) - 1):
            current = optimized[i]
            next_seg = optimized[i + 1]
            
            # 修正重疊
            if current['end'] > next_seg['start']:
                mid_point = (current['end'] + next_seg['start']) / 2
                current['end'] = mid_point - 0.01
                next_seg['start'] = mid_point
        
        return optimized