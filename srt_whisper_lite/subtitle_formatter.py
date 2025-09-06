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
    def _optimize_for_premiere(segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """為Premiere Pro優化字幕段落"""
        if not segments:
            return segments
            
        optimized = []
        for i, segment in enumerate(segments):
            seg_copy = segment.copy()
            
            # 確保最小顯示時間（PR需要至少0.5秒）
            duration = seg_copy['end'] - seg_copy['start']
            if duration < 0.5:
                seg_copy['end'] = seg_copy['start'] + 0.5
            
            # 確保段落間有合理間隔（避免合併）
            if i > 0:
                prev_end = optimized[-1]['end']
                if seg_copy['start'] - prev_end < 0.1:
                    seg_copy['start'] = prev_end + 0.1
                    # 重新檢查最小顯示時間
                    if seg_copy['end'] - seg_copy['start'] < 0.5:
                        seg_copy['end'] = seg_copy['start'] + 0.5
            
            optimized.append(seg_copy)
        
        logger.debug(f"PR優化完成：{len(segments)} -> {len(optimized)} 個段落")
        return optimized
    
    @staticmethod
    def segments_to_srt_pr_compatible(segments: List[Dict[str, any]]) -> str:
        """將段落轉換為PR兼容的SRT格式"""
        srt_content = []
        
        for i, segment in enumerate(segments, 1):
            start_time = SubtitleFormatter.format_timestamp_srt(segment['start'])
            end_time = SubtitleFormatter.format_timestamp_srt(segment['end'])
            text = segment['text'].strip()
            
            # 確保文本不為空
            if not text:
                continue
                
            # PR兼容的格式：序號、時間戳、文本、空行
            srt_content.extend([
                str(i),
                f"{start_time} --> {end_time}",
                text,
                ""  # 空行分隔，對PR很重要
            ])
        
        # 移除最後的空行並確保以單一換行符結尾
        result = "\n".join(srt_content).rstrip() + "\n"
        return result
    
    @staticmethod
    def save_subtitle(segments: List[Dict[str, any]], 
                     output_path: str,
                     format: str = "srt") -> bool:
        """保存字幕文件（PR兼容版）"""
        try:
            output_path = Path(output_path)
            
            # 為PR優化：確保字幕間隔和格式正確
            pr_optimized_segments = SubtitleFormatter._optimize_for_premiere(segments)
            
            # 根據格式生成內容
            if format.lower() == "srt":
                content = SubtitleFormatter.segments_to_srt_pr_compatible(pr_optimized_segments)
            elif format.lower() == "vtt":
                content = SubtitleFormatter.segments_to_vtt(pr_optimized_segments)
            elif format.lower() == "txt":
                content = SubtitleFormatter.segments_to_txt(pr_optimized_segments)
            else:
                raise ValueError(f"不支援的格式: {format}")
            
            # 確保目錄存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 寫入文件（強制UTF-8，Unix換行符）
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            
            file_size = output_path.stat().st_size
            logger.info(f"字幕文件保存成功: {output_path} ({file_size} bytes)")
            
            return True
            
        except Exception as e:
            print(f"保存字幕失敗: {e}")
            return False
    
    @staticmethod
    def post_process_optimize(segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """後處理優化"""
        try:
            if not segments:
                return segments
            
            # 1. 清理重複內容
            segments = SubtitleFormatter.remove_duplicates(segments)
            
            # 2. 清理填詞語
            segments = SubtitleFormatter.clean_filler_words(segments)
            
            # 3. 時間軸平滑處理
            segments = SubtitleFormatter.smooth_timestamps(segments)
            
            # 4. 檢測和修復重疊
            segments = SubtitleFormatter.fix_overlaps(segments)
            
            # 5. 語速適配
            segments = SubtitleFormatter.adapt_reading_speed(segments)
            
            return segments
            
        except Exception as e:
            print(f"後處理優化失敗: {e}")
            return segments
    
    @staticmethod
    def remove_duplicates(segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """移除重複內容"""
        if not segments:
            return segments
        
        cleaned = []
        prev_text = ""
        
        for segment in segments:
            text = segment['text'].strip().lower()
            
            # 檢查是否與前一個相似（考慮小變化）
            if not SubtitleFormatter._is_similar_text(text, prev_text):
                cleaned.append(segment)
                prev_text = text
        
        return cleaned
    
    @staticmethod
    def _is_similar_text(text1: str, text2: str, threshold: float = 0.8) -> bool:
        """檢查兩個文本是否相似"""
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
    def clean_filler_words(segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """清理填詞語"""
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
                segment['text'] = text
                cleaned.append(segment)
        
        return cleaned
    
    @staticmethod
    def smooth_timestamps(segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """平滑時間戳"""
        if len(segments) < 2:
            return segments
        
        smoothed = []
        
        for i, segment in enumerate(segments):
            current = segment.copy()
            
            # 檢查與前一個片段的間隔
            if i > 0:
                prev_end = smoothed[-1]['end']
                gap = current['start'] - prev_end
                
                # 如果間隔太小，調整開始時間
                if 0 < gap < 0.2:  # 小於200ms的間隔
                    current['start'] = prev_end + 0.1
                
                # 如果重疊，調整開始時間
                elif gap < 0:
                    current['start'] = prev_end + 0.05
            
            # 檢查與下一個片段的關係
            if i < len(segments) - 1:
                next_start = segments[i + 1]['start']
                
                # 確保不會超過下一個片段的開始時間
                if current['end'] > next_start:
                    current['end'] = next_start - 0.05
            
            # 確保最小時長
            min_duration = 0.5
            if current['end'] - current['start'] < min_duration:
                current['end'] = current['start'] + min_duration
            
            smoothed.append(current)
        
        return smoothed
    
    @staticmethod
    def fix_overlaps(segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """修復時間重疊"""
        if len(segments) < 2:
            return segments
        
        fixed = [segments[0].copy()]
        
        for i in range(1, len(segments)):
            current = segments[i].copy()
            previous = fixed[-1]
            
            # 檢查重疊
            if current['start'] < previous['end']:
                # 調整當前片段的開始時間
                current['start'] = previous['end'] + 0.05
                
                # 確保調整後仍有有效時長
                if current['end'] <= current['start']:
                    current['end'] = current['start'] + 0.5
            
            fixed.append(current)
        
        return fixed
    
    @staticmethod
    def adapt_reading_speed(segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """適配閱讀速度"""
        adapted = []
        
        for i, segment in enumerate(segments):
            text = segment['text']
            char_count = len(text)
            duration = segment['end'] - segment['start']
            
            # 計算當前閱讀速度（字符/秒）
            current_speed = char_count / duration if duration > 0 else 0
            
            # 設定理想閱讀速度範圍（根據語言調整）
            # 中文字符較密集，速度較慢；英文單詞較長，速度較快
            is_chinese = any('\u4e00' <= c <= '\u9fff' for c in text)
            
            if is_chinese:
                min_speed = 2.0   # 最慢 2 字符/秒
                max_speed = 8.0   # 最快 8 字符/秒
                ideal_speed = 4.0 # 理想 4 字符/秒
            else:
                min_speed = 10.0  # 最慢 10 字符/秒（約2詞/秒）
                max_speed = 30.0  # 最快 30 字符/秒（約6詞/秒）
                ideal_speed = 20.0 # 理想 20 字符/秒（約4詞/秒）
            
            new_segment = segment.copy()
            
            # 如果速度超出範圍，調整顯示時長
            if current_speed > max_speed:
                # 太快，延長顯示時間
                new_duration = char_count / ideal_speed
                new_segment['end'] = new_segment['start'] + new_duration
            elif current_speed < min_speed and duration > 1.0:
                # 太慢且時長合理，縮短顯示時間
                new_duration = max(1.0, char_count / ideal_speed)
                new_segment['end'] = new_segment['start'] + new_duration
            
            adapted.append(new_segment)
        
        return adapted
    
    @staticmethod
    def use_word_timestamps(segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """使用詞級時間戳來獲得更準確的結束時間
        
        Args:
            segments: 字幕段落列表
            
        Returns:
            調整後的字幕段落列表
        """
        adjusted = []
        
        for segment in segments:
            new_segment = segment.copy()
            
            # 如果有詞級時間戳，使用最後一個詞的結束時間
            if 'words' in segment and segment['words']:
                last_word = segment['words'][-1]
                if 'end' in last_word:
                    # 使用最後一個詞的結束時間，加上小的緩衝
                    new_segment['end'] = last_word['end'] + 0.2
            
            adjusted.append(new_segment)
        
        return adjusted
    
    @staticmethod
    def extend_subtitle_duration(segments: List[Dict[str, any]], min_display_time: float = 1.5) -> List[Dict[str, any]]:
        """延長字幕顯示時間，確保字幕顯示到句子講完
        
        Args:
            segments: 字幕段落列表
            min_display_time: 最小顯示時間（秒）
            
        Returns:
            調整後的字幕段落列表
        """
        extended = []
        
        for i, segment in enumerate(segments):
            new_segment = segment.copy()
            
            # 計算當前時長
            current_duration = segment['end'] - segment['start']
            
            # 確保最小顯示時間
            if current_duration < min_display_time:
                # 檢查是否會與下一個字幕重疊
                if i < len(segments) - 1:
                    next_start = segments[i + 1]['start']
                    # 延長到下一個字幕開始前，留小間隔
                    max_end_time = next_start - 0.05
                    new_segment['end'] = min(segment['start'] + min_display_time, max_end_time)
                else:
                    # 最後一個字幕，延長到最小顯示時間
                    new_segment['end'] = segment['start'] + min_display_time
            
            # 如果有下一個字幕且間隔很小，延長當前字幕
            if i < len(segments) - 1:
                next_start = segments[i + 1]['start']
                gap = next_start - new_segment['end']
                
                # 如果間隔小於 0.3 秒，延長當前字幕填補間隙
                if 0 < gap < 0.3:
                    new_segment['end'] = next_start - 0.05
            
            extended.append(new_segment)
        
        return extended
    
    @staticmethod
    def post_process_optimize(segments: List[Dict[str, any]], language: str = None) -> List[Dict[str, any]]:
        """完整的後處理優化流程
        
        Args:
            segments: 原始字幕段落
            language: 語言代碼
            
        Returns:
            優化後的字幕段落
        """
        if not segments:
            return segments
        
        logger.info(f"開始後處理優化，共 {len(segments)} 個段落")
        
        # 1. 使用詞級時間戳優化結束時間
        segments = SubtitleFormatter.use_word_timestamps(segments)
        logger.info("已使用詞級時間戳優化")
        
        # 2. 清理重複內容
        segments = SubtitleFormatter.remove_duplicates(segments)
        logger.info(f"清理重複後: {len(segments)} 個段落")
        
        # 3. 清理填詞語（可選）
        # segments = SubtitleFormatter.clean_filler_words(segments)
        
        # 4. 延長字幕顯示時間
        segments = SubtitleFormatter.extend_subtitle_duration(segments)
        logger.info("字幕顯示時間已優化")
        
        # 5. 平滑時間戳
        segments = SubtitleFormatter.smooth_timestamps(segments)
        logger.info("時間戳已平滑")
        
        # 6. 修復重疊
        segments = SubtitleFormatter.fix_overlaps(segments)
        logger.info("時間重疊已修復")
        
        logger.info(f"後處理優化完成，最終 {len(segments)} 個段落")
        return segments
    
    @staticmethod
    def save_subtitle(segments: List[Dict[str, any]], output_file: str, format: str) -> bool:
        """保存字幕文件到指定路徑
        
        Args:
            segments: 字幕段落列表
            output_file: 輸出文件路徑
            format: 輸出格式 (srt, vtt, txt)
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 確保輸出目錄存在
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"正在保存字幕到: {output_file}")
            
            # 根據格式生成內容
            if format.lower() == "srt":
                content = SubtitleFormatter.segments_to_srt(segments)
            elif format.lower() == "vtt":
                content = SubtitleFormatter.segments_to_vtt(segments)
            elif format.lower() == "txt":
                content = SubtitleFormatter.segments_to_txt(segments)
            else:
                logger.error(f"不支援的格式: {format}")
                return False
            
            # 寫入文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 檢驗文件是否成功寫入
            if output_path.exists() and output_path.stat().st_size > 0:
                logger.info(f"字幕文件保存成功: {output_file} ({output_path.stat().st_size} bytes)")
                return True
            else:
                logger.error(f"字幕文件保存失敗，文件不存在或為空: {output_file}")
                return False
                
        except PermissionError as e:
            logger.error(f"沒有權限寫入文件 {output_file}: {e}")
            return False
        except Exception as e:
            logger.error(f"保存字幕文件時發生錯誤: {e}")
            return False
    
    @staticmethod
    def merge_short_segments(segments: List[Dict[str, any]], 
                           min_duration: float = 2.0) -> List[Dict[str, any]]:
        """合併過短的段落"""
        if not segments:
            return segments
        
        merged = []
        current = None
        
        for segment in segments:
            duration = segment['end'] - segment['start']
            
            if current is None:
                current = segment.copy()
            elif duration < min_duration and (current['end'] - current['start']) < min_duration * 2:
                # 合併到當前段落
                current['end'] = segment['end']
                current['text'] = f"{current['text']} {segment['text']}"
            else:
                merged.append(current)
                current = segment.copy()
        
        if current:
            merged.append(current)
        
        return merged
    
    @staticmethod
    def split_long_segments(segments: List[Dict[str, any]], 
                          max_duration: float = 5.0) -> List[Dict[str, any]]:
        """分割過長的段落"""
        split_segments = []
        
        for segment in segments:
            duration = segment['end'] - segment['start']
            
            if duration <= max_duration:
                split_segments.append(segment)
            else:
                # 需要分割
                text = segment['text']
                words = text.split()
                
                if len(words) > 1:
                    mid_point = len(words) // 2
                    first_text = ' '.join(words[:mid_point])
                    second_text = ' '.join(words[mid_point:])
                    
                    mid_time = segment['start'] + duration / 2
                    
                    split_segments.append({
                        'start': segment['start'],
                        'end': mid_time,
                        'text': first_text
                    })
                    split_segments.append({
                        'start': mid_time,
                        'end': segment['end'],
                        'text': second_text
                    })
                else:
                    split_segments.append(segment)
        
        return split_segments

    @staticmethod
    def post_process_optimize(segments: List[Dict[str, any]], language: str = "auto") -> List[Dict[str, any]]:
        """
        智能後處理優化系統
        
        Args:
            segments: 原始字幕段落
            language: 語言代碼
            
        Returns:
            優化後的字幕段落
        """
        try:
            logger.info(f"開始智能後處理優化，共 {len(segments)} 個段落")
            
            # 1. 移除重複內容
            segments = SubtitleFormatter.remove_duplicates(segments)
            logger.info(f"移除重複後：{len(segments)} 個段落")
            
            # 2. 清理填充詞
            segments = SubtitleFormatter.clean_filler_words(segments, language)
            
            # 3. 平滑時間戳
            segments = SubtitleFormatter.smooth_timestamps(segments)
            
            # 4. 調整閱讀速度
            segments = SubtitleFormatter.adjust_reading_speed(segments)
            
            # 5. 應用自定義修正
            segments = SubtitleFormatter.apply_custom_corrections(segments)
            
            # 6. 最終品質檢查
            segments = SubtitleFormatter.final_quality_check(segments)
            
            logger.info(f"後處理完成，最終 {len(segments)} 個段落")
            return segments
            
        except Exception as e:
            logger.error(f"後處理優化失敗: {e}")
            return segments

    @staticmethod
    def remove_duplicates(segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """移除重複的字幕段落"""
        if not segments:
            return segments
            
        cleaned_segments = []
        prev_text = ""
        similarity_threshold = 0.7
        
        for segment in segments:
            current_text = segment['text'].strip().lower()
            
            # 計算與前一個文本的相似度
            if current_text and current_text != prev_text:
                similarity = SubtitleFormatter._calculate_similarity(current_text, prev_text)
                
                if similarity < similarity_threshold:
                    cleaned_segments.append(segment)
                    prev_text = current_text
                    
        return cleaned_segments

    @staticmethod
    def clean_filler_words(segments: List[Dict[str, any]], language: str = "auto") -> List[Dict[str, any]]:
        """清理填充詞和無意義內容"""
        
        # 多語言填充詞詞典
        filler_patterns = {
            'zh': [
                r'\b(呃|額|嗯|啊|唔|那個|這個|就是說|然後呢)\b',
                r'\.{3,}',  # 多個省略號
                r'\s+嗯\s*',
                r'嗯嗯'
            ],
            'en': [
                r'\b(um|uh|er|ah|like|you know|sort of|kind of)\b',
                r'\b(well|so|basically|actually|literally)\b',
                r'\.{3,}'
            ],
            'auto': [
                r'\b(呃|額|嗯|啊|唔|那個|這個|就是說|然後呢)\b',
                r'\b(um|uh|er|ah|like|you know|sort of|kind of)\b',
                r'\.{3,}',
                r'\s+嗯\s*'
            ]
        }
        
        patterns = filler_patterns.get(language, filler_patterns['auto'])
        
        cleaned_segments = []
        for segment in segments:
            text = segment['text']
            
            # 應用清理模式
            for pattern in patterns:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
            # 清理多餘空格
            text = re.sub(r'\s+', ' ', text).strip()
            
            # 只保留有意義的內容
            if text and len(text) > 1:
                segment_copy = segment.copy()
                segment_copy['text'] = text
                cleaned_segments.append(segment_copy)
                
        return cleaned_segments

    @staticmethod
    def smooth_timestamps(segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """平滑時間戳，消除不合理的跳躍"""
        if len(segments) < 2:
            return segments
            
        smoothed_segments = []
        
        for i, segment in enumerate(segments):
            smoothed_segment = segment.copy()
            
            # 確保最小時長（避免閃現）
            min_duration = 0.5  # 最小0.5秒
            if segment['end'] - segment['start'] < min_duration:
                smoothed_segment['end'] = segment['start'] + min_duration
            
            # 與下一個段落的間隔調整
            if i < len(segments) - 1:
                next_segment = segments[i + 1]
                gap = next_segment['start'] - smoothed_segment['end']
                
                # 如果間隔太小（<0.1秒），調整結束時間
                if 0 < gap < 0.1:
                    smoothed_segment['end'] = next_segment['start'] - 0.05
                
                # 如果有重疊，調整時間
                elif gap < 0:
                    mid_time = (smoothed_segment['end'] + next_segment['start']) / 2
                    smoothed_segment['end'] = mid_time
                    
            smoothed_segments.append(smoothed_segment)
            
        return smoothed_segments

    @staticmethod
    def adjust_reading_speed(segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """調整閱讀速度，確保合理的字幕顯示時間"""
        
        # 閱讀速度參數（字符/秒）
        min_chars_per_second = 8   # 最慢閱讀速度
        max_chars_per_second = 20  # 最快閱讀速度
        
        adjusted_segments = []
        
        for i, segment in enumerate(segments):
            text_length = len(segment['text'])
            current_duration = segment['end'] - segment['start']
            
            if text_length == 0:
                continue
                
            current_speed = text_length / current_duration
            
            # 計算理想時長
            if current_speed > max_chars_per_second:
                # 太快，延長時間
                ideal_duration = text_length / max_chars_per_second
            elif current_speed < min_chars_per_second:
                # 太慢，縮短時間
                ideal_duration = text_length / min_chars_per_second
            else:
                # 速度合適
                ideal_duration = current_duration
            
            # 創建調整後的段落
            adjusted_segment = segment.copy()
            
            # 保持開始時間，調整結束時間
            adjusted_segment['end'] = segment['start'] + ideal_duration
            
            # 確保不與下一個段落重疊
            if i < len(segments) - 1:
                next_start = segments[i + 1]['start']
                if adjusted_segment['end'] > next_start - 0.1:
                    adjusted_segment['end'] = next_start - 0.1
                    
            adjusted_segments.append(adjusted_segment)
            
        return adjusted_segments

    @staticmethod
    def apply_custom_corrections(segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """應用自定義修正規則"""
        try:
            corrections_file = Path("custom_corrections.json")
            if not corrections_file.exists():
                return segments
                
            with open(corrections_file, 'r', encoding='utf-8') as f:
                corrections = json.load(f)
                
            corrected_segments = []
            
            for segment in segments:
                text = segment['text']
                
                # 應用修正規則
                for wrong, correct in corrections.items():
                    text = text.replace(wrong, correct)
                    
                segment_copy = segment.copy()
                segment_copy['text'] = text
                corrected_segments.append(segment_copy)
                
            return corrected_segments
            
        except Exception as e:
            logger.warning(f"應用自定義修正失敗: {e}")
            return segments

    @staticmethod
    def final_quality_check(segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """最終品質檢查和清理"""
        quality_segments = []
        
        for segment in segments:
            text = segment['text'].strip()
            
            # 過濾品質檢查
            if (len(text) > 0 and                    # 非空
                len(text) < 500 and                  # 不過長
                segment['end'] > segment['start'] and # 時間有效
                not re.match(r'^[^\w\s]*$', text)):  # 不只是標點符號
                
                quality_segments.append(segment)
                
        return quality_segments

    @staticmethod
    def _calculate_similarity(text1: str, text2: str) -> float:
        """計算兩個文本的相似度"""
        if not text1 or not text2:
            return 0.0
            
        # 簡單的基於字符集合的相似度計算
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0