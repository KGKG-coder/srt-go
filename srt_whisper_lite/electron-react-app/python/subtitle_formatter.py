#!/usr/bin/env python3
"""
字幕格式化工具
支援 SRT、VTT 等格式輸出
增強的智能後處理系統
"""

import re
import json
import logging
from typing import List, Dict, Optional, Set
from datetime import timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class SubtitleFormatter:
    """字幕格式化器"""
    
    @staticmethod
    def format_timestamp_srt(seconds: float) -> str:
        """格式化時間戳為 SRT 格式 (HH:MM:SS,mmm) - 修復負數時間戳問題"""
        # 確保不會有負數時間戳
        if seconds < 0:
            logger.warning(f"發現負數時間戳: {seconds}, 修正為 0.000")
            seconds = 0.0
        
        # 確保時間戳不會超出合理範圍 (24小時)
        if seconds > 86400:  # 24小時 = 86400秒
            logger.warning(f"時間戳過大: {seconds}, 修正為最大值")
            seconds = 86399.999  # 23:59:59,999
        
        td = timedelta(seconds=seconds)
        total_seconds = td.total_seconds()
        
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60) 
        secs = int(total_seconds % 60)
        milliseconds = int((total_seconds % 1) * 1000)
        
        # 確保各部分都在有效範圍內
        hours = max(0, min(23, hours))
        minutes = max(0, min(59, minutes)) 
        secs = max(0, min(59, secs))
        milliseconds = max(0, min(999, milliseconds))
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
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
        """將段落轉換為 SRT 格式 - 增強兼容性版本"""
        # 首先優化時間戳以確保適當間隙
        optimized_segments = SubtitleFormatter._optimize_for_premiere(segments)
        
        srt_content = []
        valid_segment_count = 0
        
        for segment in optimized_segments:
            # 驗證時間戳有效性
            start = float(segment.get('start', 0))
            end = float(segment.get('end', 0))
            text = segment.get('text', '').strip()
            
            # 修復無效時間戳
            if start < 0:
                logger.warning(f"修復負數開始時間: {start} -> 0.0")
                start = 0.0
            if end < 0:
                logger.warning(f"修復負數結束時間: {end} -> {start + 1.0}")
                end = start + 1.0
            if end <= start:
                logger.warning(f"修復無效時間範圍: {start}-{end} -> {start}-{start + 1.0}")
                end = start + 1.0
            
            # 清理和標準化文字
            if text:
                # 移除控制字符和非打印字符
                text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', text)
                
                # 標準化換行符（某些編輯軟體對此敏感）
                text = re.sub(r'\r\n|\r|\n', '\n', text)
                
                # 移除前後空白，但保留內部格式
                text = text.strip()
                
                if text:  # 再次檢查清理後是否還有內容
                    valid_segment_count += 1
                    start_time = SubtitleFormatter.format_timestamp_srt(start)
                    end_time = SubtitleFormatter.format_timestamp_srt(end)
                    
                    srt_content.append(f"{valid_segment_count}")
                    srt_content.append(f"{start_time} --> {end_time}")
                    srt_content.append(text)
                    srt_content.append("")  # 空行分隔
        
        # 確保文件以換行符結尾
        result = "\n".join(srt_content)
        if result and not result.endswith('\n'):
            result += '\n'
            
        return result
    
    @staticmethod
    def segments_to_vtt(segments: List[Dict[str, any]]) -> str:
        """將段落轉換為 VTT 格式"""
        vtt_content = ["WEBVTT", ""]
        
        for segment in segments:
            start_time = SubtitleFormatter.format_timestamp_vtt(segment['start'])
            end_time = SubtitleFormatter.format_timestamp_vtt(segment['end'])
            text = segment.get('text', '').strip()
            
            if text:
                vtt_content.append(f"{start_time} --> {end_time}")
                vtt_content.append(text)
                vtt_content.append("")  # 空行分隔
        
        return "\n".join(vtt_content)
    
    @staticmethod
    def segments_to_txt(segments: List[Dict[str, any]]) -> str:
        """將段落轉換為純文本格式"""
        txt_content = []
        
        for segment in segments:
            text = segment.get('text', '').strip()
            if text:
                txt_content.append(text)
        
        return "\n".join(txt_content)
    
    @staticmethod
    def clean_subtitle_text(text: str, language: str = 'auto') -> str:
        """清理字幕文本"""
        if not text:
            return ""
        
        # 移除多餘空白
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 根據語言進行特定清理
        if language in ['zh', 'zh-CN', 'zh-TW']:
            # 中文標點符號標準化
            punctuation_map = {
                '，': ',', '。': '.', '！': '!', '？': '?',
                '；': ';', '：': ':', ''': "'", ''': "'",
                '"': '"', '"': '"', '（': '(', '）': ')',
                '【': '[', '】': ']', '《': '<', '》': '>'
            }
            for chinese_punct, english_punct in punctuation_map.items():
                text = text.replace(chinese_punct, english_punct)
        
        return text
    
    @staticmethod
    def post_process_segments(segments: List[Dict], language: str = 'auto') -> List[Dict]:
        """後處理字幕段落"""
        if not segments:
            return []
        
        processed_segments = []
        
        for segment in segments:
            # 清理文本
            text = SubtitleFormatter.clean_subtitle_text(
                segment.get('text', ''), language
            )
            
            if text:  # 只保留有文本的段落
                processed_segment = segment.copy()
                processed_segment['text'] = text
                processed_segments.append(processed_segment)
        
        # 移除重複段落
        processed_segments = SubtitleFormatter._remove_duplicate_segments(processed_segments)
        
        return processed_segments
    
    @staticmethod
    def _remove_duplicate_segments(segments: List[Dict]) -> List[Dict]:
        """移除重複的字幕段落"""
        if len(segments) <= 1:
            return segments
        
        unique_segments = []
        seen_texts = set()
        
        for segment in segments:
            text = segment.get('text', '').strip()
            if text and text not in seen_texts:
                unique_segments.append(segment)
                seen_texts.add(text)
            elif not text:  # 保留空文本段落（如果有的話）
                unique_segments.append(segment)
        
        return unique_segments
    
    @staticmethod
    def _optimize_for_premiere(segments: List[Dict]) -> List[Dict]:
        """優化字幕以兼容 Premiere Pro - 確保適當的時間戳間隙"""
        if len(segments) <= 1:
            return segments
        
        optimized = segments.copy()
        
        for i in range(len(optimized) - 1):
            current = optimized[i]
            next_seg = optimized[i + 1]
            
            # 計算當前間隙
            gap = next_seg['start'] - current['end']
            
            # 如果重疊或間隙太小（< 0.1秒），調整時間戳
            if gap < 0.1:
                # 在中點創建0.1秒的間隙
                midpoint = (current['end'] + next_seg['start']) / 2
                current['end'] = midpoint - 0.05  # 前段結束時間
                next_seg['start'] = midpoint + 0.05  # 後段開始時間
                
                logger.debug(f"調整段落 {i+1}-{i+2} 間隙: {gap:.3f}s -> 0.1s")
                
                # 確保最小持續時間0.3秒
                if current['end'] - current['start'] < 0.3:
                    current['start'] = current['end'] - 0.3
                if next_seg['end'] - next_seg['start'] < 0.3:
                    next_seg['end'] = next_seg['start'] + 0.3
        
        return optimized
    
    @staticmethod
    def save_subtitle(segments: List[Dict], output_file: str, format: str = 'srt') -> bool:
        """保存字幕文件"""
        try:
            if not segments:
                logger.warning("沒有字幕段落要保存")
                return False
            
            # 根據格式選擇轉換方法
            if format.lower() == 'srt':
                content = SubtitleFormatter.segments_to_srt(segments)
            elif format.lower() == 'vtt':
                content = SubtitleFormatter.segments_to_vtt(segments)
            elif format.lower() == 'txt':
                content = SubtitleFormatter.segments_to_txt(segments)
            else:
                logger.error(f"不支援的格式: {format}")
                return False
            
            # 寫入文件 - 使用適當的編碼和換行符
            # 對於SRT文件，使用UTF-8 BOM以增加兼容性
            if format.lower() == 'srt':
                with open(output_file, 'w', encoding='utf-8-sig', newline='\r\n') as f:
                    f.write(content)
            else:
                with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(content)
            
            logger.info(f"字幕保存成功: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存字幕失敗: {e}")
            return False