#!/usr/bin/env python3
"""
字幕格式化工具（修復版）
修復時間軸問題，移除重複函數定義
"""

import re
import json
import logging
from typing import List, Dict, Optional, Set
from datetime import timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class SubtitleFormatter:
    """字幕格式化器（修復版）"""
    
    @staticmethod
    def format_timestamp_srt(seconds: float) -> str:
        """格式化時間戳為 SRT 格式 (HH:MM:SS,mmm)"""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        seconds = int(td.total_seconds() % 60)
        milliseconds = int((td.total_seconds() % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
    @staticmethod
    def format_timestamp_vtt(seconds: float) -> str:
        """格式化時間戳為 VTT 格式 (HH:MM:SS.mmm)"""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        seconds = int(td.total_seconds() % 60)
        milliseconds = int((td.total_seconds() % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    
    @staticmethod
    def segments_to_srt(segments: List[Dict[str, any]]) -> str:
        """將段落轉換為 SRT 格式"""
        srt_content = []
        
        for i, segment in enumerate(segments, 1):
            start_time = SubtitleFormatter.format_timestamp_srt(segment['start'])
            end_time = SubtitleFormatter.format_timestamp_srt(segment['end'])
            text = segment['text'].strip()
            
            # 處理長文本換行
            text = SubtitleFormatter._wrap_text(text, max_chars=42)
            
            srt_content.append(f"{i}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(text)
            srt_content.append("")  # 空行分隔
        
        return "\n".join(srt_content).strip()
    
    @staticmethod
    def segments_to_vtt(segments: List[Dict[str, any]]) -> str:
        """將段落轉換為 VTT 格式"""
        vtt_content = ["WEBVTT", ""]
        
        for segment in segments:
            start_time = SubtitleFormatter.format_timestamp_vtt(segment['start'])
            end_time = SubtitleFormatter.format_timestamp_vtt(segment['end'])
            text = segment['text'].strip()
            
            # 處理長文本換行
            text = SubtitleFormatter._wrap_text(text, max_chars=42)
            
            vtt_content.append(f"{start_time} --> {end_time}")
            vtt_content.append(text)
            vtt_content.append("")  # 空行分隔
        
        return "\n".join(vtt_content).strip()
    
    @staticmethod
    def segments_to_txt(segments: List[Dict[str, any]], 
                       include_timestamps: bool = False) -> str:
        """將段落轉換為純文本格式"""
        txt_content = []
        
        for segment in segments:
            if include_timestamps:
                start_time = SubtitleFormatter.format_timestamp_srt(segment['start'])
                txt_content.append(f"[{start_time}] {segment['text'].strip()}")
            else:
                txt_content.append(segment['text'].strip())
        
        return "\n".join(txt_content)
    
    @staticmethod
    def _wrap_text(text: str, max_chars: int = 42) -> str:
        """智能換行處理"""
        if len(text) <= max_chars:
            return text
        
        # 尋找合適的斷點
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + (1 if current_line else 0)
            
            if current_length + word_length <= max_chars:
                current_line.append(word)
                current_length += word_length
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # 最多顯示兩行
        if len(lines) > 2:
            lines = lines[:2]
            lines[1] = lines[1][:max_chars-3] + "..."
        
        return '\n'.join(lines)
    
    @staticmethod
    def save_subtitle(segments: List[Dict[str, any]], 
                     output_path: str,
                     format: str = "srt") -> bool:
        """保存字幕文件"""
        try:
            output_path = Path(output_path)
            
            # 輕量級後處理優化
            optimized_segments = SubtitleFormatter.post_process_optimize(segments)
            
            # 根據格式生成內容
            if format.lower() == "srt":
                content = SubtitleFormatter.segments_to_srt(optimized_segments)
            elif format.lower() == "vtt":
                content = SubtitleFormatter.segments_to_vtt(optimized_segments)
            elif format.lower() == "txt":
                content = SubtitleFormatter.segments_to_txt(optimized_segments)
            else:
                raise ValueError(f"不支援的格式: {format}")
            
            # 確保目錄存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 寫入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            logger.error(f"保存字幕失敗: {e}")
            return False
    
    @staticmethod
    def post_process_optimize(segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        統一的後處理優化函數（修復版）
        保持原始 Whisper 時間軸的準確性，僅進行必要調整
        """
        try:
            if not segments:
                return segments
            
            logger.info(f"開始後處理優化，共 {len(segments)} 個段落")
            
            # 1. 清理重複內容（保持原始時間軸）
            segments = SubtitleFormatter.remove_duplicates(segments)
            logger.info(f"清理重複後: {len(segments)} 個段落")
            
            # 2. 修復嚴重的時間重疊（僅修復明顯錯誤）
            segments = SubtitleFormatter.fix_critical_overlaps(segments)
            logger.info("修復嚴重重疊完成")
            
            # 3. 確保最小可讀性（非常保守的調整）
            segments = SubtitleFormatter.ensure_minimal_readability(segments)
            logger.info("確保最小可讀性完成")
            
            logger.info(f"後處理優化完成，最終 {len(segments)} 個段落")
            return segments
            
        except Exception as e:
            logger.error(f"後處理優化失敗: {e}")
            return segments
    
    @staticmethod
    def remove_duplicates(segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """移除重複內容（保持時間軸不變）"""
        if not segments:
            return segments
        
        cleaned = []
        prev_text = ""
        
        for segment in segments:
            text = segment['text'].strip().lower()
            
            # 檢查是否與前一個完全相同或高度相似
            if text and text != prev_text and not SubtitleFormatter._is_highly_similar(text, prev_text):
                cleaned.append(segment)
                prev_text = text
        
        return cleaned
    
    @staticmethod
    def _is_highly_similar(text1: str, text2: str, threshold: float = 0.85) -> bool:
        """檢查兩個文本是否高度相似（設定更高閾值）"""
        if not text1 or not text2:
            return False
        
        # 簡單的相似度計算
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return text1 == text2
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        similarity = intersection / union if union > 0 else 0
        return similarity >= threshold
    
    @staticmethod
    def fix_critical_overlaps(segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """僅修復嚴重的時間重疊（> 0.5秒重疊）"""
        if len(segments) < 2:
            return segments
        
        fixed = [segments[0].copy()]
        
        for i in range(1, len(segments)):
            current = segments[i].copy()
            previous = fixed[-1]
            
            # 僅修復嚴重重疊（> 0.5秒）
            overlap = previous['end'] - current['start']
            if overlap > 0.5:
                # 在重疊中點進行切分
                split_time = current['start'] + overlap / 2
                previous['end'] = split_time - 0.05
                current['start'] = split_time + 0.05
                
                # 更新前一個段落
                fixed[-1] = previous
            
            fixed.append(current)
        
        return fixed
    
    @staticmethod
    def ensure_minimal_readability(segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """確保最基本的可讀性（非常保守）"""
        adjusted = []
        
        for segment in segments:
            new_segment = segment.copy()
            duration = segment['end'] - segment['start']
            text_length = len(segment['text'])
            
            # 僅對極端情況進行調整
            # 1. 時長小於0.3秒的片段適當延長
            if duration < 0.3 and text_length > 0:
                new_segment['end'] = segment['start'] + max(0.5, duration * 1.5)
            
            # 2. 對於長文本但時間太短的情況
            elif text_length > 20 and duration < 1.0:
                # 計算基於字符數的最小時長（保守估算）
                min_duration = text_length * 0.08  # 每字符 80ms（很快的閱讀速度）
                if min_duration > duration:
                    new_segment['end'] = segment['start'] + min_duration
            
            adjusted.append(new_segment)
        
        return adjusted
    
    @staticmethod
    def clean_filler_words(segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """清理填詞語（可選功能）"""
        filler_patterns = [
            r'\b(um|uh|er|ah|like|you know)\b',  # 英文
            r'\b(呃|嗯|啊|那個|這個|就是說|然後)\b',      # 中文
        ]
        
        cleaned = []
        for segment in segments:
            text = segment['text']
            
            # 清理填詞語
            for pattern in filler_patterns:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
            # 清理多餘空格
            text = re.sub(r'\s+', ' ', text).strip()
            
            if text:  # 只保留非空內容
                segment_copy = segment.copy()
                segment_copy['text'] = text
                cleaned.append(segment_copy)
        
        return cleaned