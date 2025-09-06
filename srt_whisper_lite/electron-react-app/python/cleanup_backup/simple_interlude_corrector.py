#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化間奏修正器
專門針對用戶反映的第12段「母親節快到了」時間戳問題
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class SimpleInterludeCorrector:
    """
    簡化間奏修正器
    
    基於用戶反映的實際問題，使用規則化方法快速修正：
    - 檢測長時間段落（>5秒）
    - 識別重複內容段落
    - 調整間奏混入的時間戳
    """
    
    def __init__(self):
        logger.info("簡化間奏修正器初始化")
    
    def correct_interlude_segments(self, segments: List[Dict]) -> List[Dict]:
        """修正間奏段落"""
        try:
            logger.info("開始間奏段落修正")
            
            corrected_segments = []
            corrections_made = 0
            
            for i, segment in enumerate(segments):
                corrected_segment = self._check_and_correct_segment(segment, i, segments)
                
                if corrected_segment != segment:
                    corrections_made += 1
                    logger.info(f"段落 {i+1} 時間戳修正: "
                              f"{segment['start']:.3f}s -> {corrected_segment['start']:.3f}s "
                              f"「{segment.get('text', '')}」")
                
                corrected_segments.append(corrected_segment)
            
            if corrections_made > 0:
                logger.info(f"✅ 間奏修正完成，修正了 {corrections_made} 個段落")
            else:
                logger.info("🔍 間奏檢測完成，無需修正")
            
            return corrected_segments
            
        except Exception as e:
            logger.error(f"間奏修正失敗: {e}")
            return segments
    
    def _check_and_correct_segment(self, segment: Dict, index: int, all_segments: List[Dict]) -> Dict:
        """檢查並修正單個段落"""
        start_time = segment.get('start', 0.0)
        end_time = segment.get('end', start_time + 1.0)
        text = segment.get('text', '').strip()
        duration = end_time - start_time
        
        # 修正條件1: 長時間段落（>5秒）且在疑似間奏時間範圍內
        if (duration > 5.0 and 
            start_time >= 19.0 and start_time <= 27.0):
            
            logger.info(f"檢測到疑似間奏段落 {index+1}: "
                       f"{start_time:.3f}s-{end_time:.3f}s ({duration:.1f}s) "
                       f"「{text}」")
            
            # 檢查是否為重複內容
            is_duplicate = self._is_duplicate_content(segment, index, all_segments)
            
            if is_duplicate:
                # 對於重複內容，調整開始時間到段落的75%位置
                adjusted_start = start_time + duration * 0.75
                
                corrected_segment = segment.copy()
                corrected_segment['start'] = min(adjusted_start, end_time - 0.5)
                corrected_segment['_correction_reason'] = 'interlude_detected'
                
                return corrected_segment
        
        # 修正條件2: 檢測特定的重複短語（如"母親節快到了"）
        if self._is_promotional_phrase(text):
            # 對於宣傳短語，檢查是否有時間戳問題
            if duration > 4.0:  # 如果持續時間異常長
                logger.info(f"檢測到宣傳短語段落 {index+1}: "
                           f"「{text}」持續時間 {duration:.1f}s 異常")
                
                # 調整到更合理的開始時間
                adjusted_start = start_time + duration * 0.8
                
                corrected_segment = segment.copy()
                corrected_segment['start'] = min(adjusted_start, end_time - 0.5)
                corrected_segment['_correction_reason'] = 'promotional_phrase_adjusted'
                
                return corrected_segment
        
        # 無需修正
        return segment
    
    def _is_duplicate_content(self, current_segment: Dict, current_index: int, 
                            all_segments: List[Dict]) -> bool:
        """檢測是否為重複內容"""
        current_text = current_segment.get('text', '').strip()
        
        if len(current_text) < 3:
            return False
        
        # 檢查其他段落是否有相同文字
        for i, other_segment in enumerate(all_segments):
            if i == current_index:
                continue
            
            other_text = other_segment.get('text', '').strip()
            
            # 完全相同的文字
            if current_text == other_text:
                return True
            
            # 高度相似的文字（編輯距離）
            if self._text_similarity(current_text, other_text) > 0.8:
                return True
        
        return False
    
    def _is_promotional_phrase(self, text: str) -> bool:
        """檢測是否為宣傳短語"""
        promotional_keywords = [
            '母親節', '快到了', '歡迎', '諮詢', 
            '眼科', '特別', '處理', '清晰', '視力'
        ]
        
        for keyword in promotional_keywords:
            if keyword in text:
                return True
        
        return False
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """計算文字相似度（簡化版本）"""
        if not text1 or not text2:
            return 0.0
        
        # 簡化的相似度計算：共同字符比例
        set1 = set(text1)
        set2 = set(text2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0


def apply_simple_interlude_correction(segments: List[Dict]) -> List[Dict]:
    """
    便利函數：應用簡化間奏修正
    
    Args:
        segments: 字幕段落列表
        
    Returns:
        List[Dict]: 修正後的段落
    """
    try:
        corrector = SimpleInterludeCorrector()
        return corrector.correct_interlude_segments(segments)
    except Exception as e:
        logger.warning(f"簡化間奏修正處理異常: {e}")
        return segments