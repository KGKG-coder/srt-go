#!/usr/bin/env python3
"""
智能語意斷句處理器
優化字幕斷句和語意連貫性，保持打包友好性
"""

import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TextSegment:
    """文本片段數據結構"""
    start: float
    end: float
    text: str
    confidence: float = 1.0
    words: List[Dict] = None
    
    def duration(self) -> float:
        return self.end - self.start
    
    def word_count(self) -> int:
        return len(self.text.split())


class SemanticSegmentProcessor:
    """智能語意斷句處理器"""
    
    def __init__(self, language: str = "auto", model_size: str = "medium"):
        self.language = language
        self.model_size = model_size
        
        # 語言特定規則
        self.sentence_endings = {
            "zh": ["。", "！", "？", "；", "…"],
            "en": [".", "!", "?", ";"],
            "ja": ["。", "！", "？", "～"],
            "ko": [".", "!", "?", "요", "다", "까"]
        }
        
        # 連接詞和語氣詞
        self.connectors = {
            "zh": ["但是", "然後", "而且", "不過", "所以", "因為", "雖然", "如果", "那麼"],
            "en": ["but", "then", "and", "however", "so", "because", "although", "if", "therefore"],
            "ja": ["でも", "そして", "しかし", "だから", "もし", "それで"],
            "ko": ["그러나", "그리고", "하지만", "그래서", "만약", "그러면"]
        }
        
        # 填詞語清理
        self.filler_words = {
            "zh": ["呃", "嗯", "啊", "那個", "這個", "就是"],
            "en": ["um", "uh", "er", "ah", "like", "you know"],
            "ja": ["えーと", "あの", "その", "まあ"],
            "ko": ["음", "어", "그", "뭐", "저기"]
        }
    
    def process_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        處理字幕片段，優化語意斷句並移除標點符號
        
        Args:
            segments: 原始字幕片段列表
            
        Returns:
            List[Dict]: 優化後的字幕片段
        """
        try:
            if not segments:
                return segments
            
            logger.info(f"開始語意斷句處理，原始片段數: {len(segments)}")
            
            # 轉換為內部數據結構
            text_segments = [
                TextSegment(
                    start=seg['start'],
                    end=seg['end'],
                    text=seg['text'],
                    words=seg.get('words', [])
                ) for seg in segments
            ]
            
            # 階段1：移除標點符號（在其他處理之前）
            text_segments = self._remove_punctuation(text_segments)
            
            # 階段2：清理填詞語和空段落
            text_segments = self._clean_filler_words(text_segments)
            text_segments = self._remove_empty_segments(text_segments)
            
            # 階段3：智能語意合併（避免詞彙被切開）
            text_segments = self._merge_broken_words(text_segments)
            
            # 階段4：智能語意分割（僅對過長的片段進行分割，確保不切斷詞彙）
            text_segments = self._semantic_split_improved(text_segments)
            
            # 階段5：時長平衡和時間軸修正
            text_segments = self._balance_duration(text_segments)
            text_segments = self._fix_time_overlaps(text_segments)
            
            # 階段6：修復短間隙閃動問題
            text_segments = self._fix_short_gaps(text_segments)
            
            # 階段7：詞級時間戳校正（修復間奏被誤包含問題）
            text_segments = self._fix_word_level_timestamps(text_segments)
            
            # 階段8：音訊同步調整（解決字幕提前問題）
            text_segments = self._adjust_audio_sync(text_segments)
            
            # 轉換回字典格式
            result = [
                {
                    'start': seg.start,
                    'end': seg.end,
                    'text': seg.text.strip()
                } for seg in text_segments if seg.text.strip()
            ]
            
            logger.info(f"語意斷句處理完成，優化後片段數: {len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"語意斷句處理失敗: {e}")
            return segments  # 失敗時返回原始片段
    
    def _remove_punctuation(self, segments: List[TextSegment]) -> List[TextSegment]:
        """移除標點符號（句號和句點直接移除，其餘替換為空格）"""
        try:
            for segment in segments:
                text = segment.text
                
                # 直接移除句號和句點
                text = re.sub(r'[。\.]', '', text)
                
                # 將其他中文標點符號替換為空格
                text = re.sub(r'[！？，、；：""''（）【】《》…—]', ' ', text)
                
                # 將其他英文標點符號替換為空格
                text = re.sub(r'[!?,;:()\[\]{}"\'-]', ' ', text)
                
                # 將其他特殊符號替換為空格
                text = re.sub(r'[~`@#$%^&*+=<>/\\|_]', ' ', text)
                
                # 清理多餘空格
                text = re.sub(r'\s+', ' ', text.strip())
                
                segment.text = text
            
            return segments
            
        except Exception as e:
            logger.warning(f"標點符號處理失敗: {e}")
            return segments

    def _merge_broken_words(self, segments: List[TextSegment]) -> List[TextSegment]:
        """合併被切開的詞彙"""
        try:
            if not segments:
                return segments
            
            merged_segments = []
            i = 0
            
            while i < len(segments):
                current_segment = segments[i]
                
                # 檢查當前片段是否可能是被切開的詞彙
                if (i < len(segments) - 1 and 
                    self._is_likely_broken_word(current_segment, segments[i + 1])):
                    
                    # 合併當前片段和下一片段
                    next_segment = segments[i + 1]
                    
                    # 對於 LARGE 模型，合併時保守處理結束時間
                    if self.model_size == "large":
                        # 合併後的結束時間：使用下一片段的結束時間
                        # 但如果存在第三個片段，確保留出間隙
                        if i + 2 < len(segments):
                            # 留出至少 100ms 的間隙到下一個片段
                            merged_end = min(next_segment.end, segments[i + 2].start - 0.1)
                        else:
                            merged_end = next_segment.end
                    else:
                        merged_end = next_segment.end
                    
                    merged_segment = TextSegment(
                        start=current_segment.start,
                        end=merged_end,
                        text=f"{current_segment.text} {next_segment.text}".strip(),
                        words=(current_segment.words or []) + (next_segment.words or [])
                    )
                    
                    merged_segments.append(merged_segment)
                    i += 2  # 跳過下一個片段，因為已經合併
                else:
                    merged_segments.append(current_segment)
                    i += 1
            
            return merged_segments
            
        except Exception as e:
            logger.warning(f"詞彙合併失敗: {e}")
            return segments

    def _is_likely_broken_word(self, current: TextSegment, next_segment: TextSegment) -> bool:
        """判斷兩個片段是否可能是被切開的詞彙"""
        try:
            current_text = current.text.strip()
            next_text = next_segment.text.strip()
            
            # 如果任一片段為空，不合併
            if not current_text or not next_text:
                return False
            
            # 如果時間間隔太大（超過0.5秒），不合併
            if next_segment.start - current.end > 0.5:
                return False
            
            # 如果當前片段太短（少於3個字符），可能是被切開的
            if len(current_text) <= 2:
                return True
            
            # 如果下一片段太短（少於3個字符），可能是被切開的
            if len(next_text) <= 2:
                return True
            
            # 檢查是否是常見的被切開模式
            broken_patterns = [
                # 語助詞被切開
                (r'^(就|那|這|然|所|因)$', r'^(是|個|麼|後|以|為)'),
                # 動詞被切開  
                (r'^(要|會|可|應)$', r'^(做|有|以|該)'),
                # 形容詞被切開
                (r'^(很|非|比|更)$', r'^(好|常|較|加)'),
            ]
            
            for current_pattern, next_pattern in broken_patterns:
                if (re.match(current_pattern, current_text) and 
                    re.match(next_pattern, next_text)):
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"詞彙切開判斷失敗: {e}")
            return False

    def _semantic_split_improved(self, segments: List[TextSegment]) -> List[TextSegment]:
        """改進的語意分割，避免切斷詞彙"""
        split_segments = []
        
        for segment in segments:
            # 如果文本很短（少於12個字），不分割
            if len(segment.text.strip()) <= 12:
                split_segments.append(segment)
                continue
            
            # 如果時長很短（少於3秒），也不分割
            if segment.duration() <= 3.0:
                split_segments.append(segment)
                continue
            
            # 尋找安全的分割點（不會切斷詞彙）
            split_points = self._find_safe_split_points(segment)
            
            if not split_points:
                split_segments.append(segment)
                continue
            
            # 執行分割
            text_parts = []
            last_pos = 0
            
            for split_point in split_points:
                part = segment.text[last_pos:split_point].strip()
                if part:
                    text_parts.append(part)
                last_pos = split_point
            
            # 添加最後一部分
            final_part = segment.text[last_pos:].strip()
            if final_part:
                text_parts.append(final_part)
            
            # 基於詞級時間戳計算更精確的時間分配
            if hasattr(segment, 'words') and segment.words:
                split_segments.extend(self._create_segments_with_word_timing(segment, text_parts))
            else:
                # 均勻分配時間
                duration_per_part = segment.duration() / len(text_parts)
                current_start = segment.start
                
                for text_part in text_parts:
                    if text_part.strip():
                        new_segment = TextSegment(
                            start=current_start,
                            end=current_start + duration_per_part,
                            text=text_part.strip()
                        )
                        split_segments.append(new_segment)
                        current_start += duration_per_part
        
        return split_segments

    def _find_safe_split_points(self, segment: TextSegment) -> List[int]:
        """尋找安全的分割點，避免切斷詞彙"""
        text = segment.text
        split_points = []
        max_line_length = 20  # 每行最多20個字符（無標點符號後可以稍長）
        
        # 尋找語意完整的分割點
        safe_split_patterns = [
            r'(然後|接著|所以|因此|但是|不過|而且|另外|還有|除了)',  # 連接詞後
            r'(的時候|的情況|的話|之後|之前|以後|以前)',  # 時間詞後
            r'(這樣|那樣|這種|那種|這個|那個)',  # 指示詞後
        ]
        
        for pattern in safe_split_patterns:
            matches = list(re.finditer(pattern, text))
            for match in matches:
                pos = match.end()
                # 確保分割點不會造成過短或過長的片段
                if 8 <= pos <= len(text) - 8:
                    split_points.append(pos)
        
        # 如果沒有找到語意分割點，在空格處分割（但避免切斷詞組）
        if not split_points and len(text) > max_line_length:
            # 在中間位置附近尋找空格
            mid_point = len(text) // 2
            for i in range(mid_point - 5, mid_point + 6):
                if i > 0 and i < len(text) and text[i] == ' ':
                    # 檢查分割後不會切斷常見詞組
                    if not self._would_break_common_phrase(text, i):
                        split_points.append(i)
                        break
        
        return sorted(split_points)

    def _would_break_common_phrase(self, text: str, split_pos: int) -> bool:
        """檢查分割是否會切斷常見詞組"""
        try:
            # 檢查分割位置前後的文本
            before = text[max(0, split_pos-10):split_pos].strip()
            after = text[split_pos:min(len(text), split_pos+10)].strip()
            
            # 常見不應被切斷的詞組
            protected_phrases = [
                '不太', '比較', '非常', '特別', '實在', '確實',
                '可能', '應該', '或許', '大概', '差不多',
                '自己', '朋友', '家人', '同事', '老師',
                '工作', '學習', '生活', '健康', '快樂'
            ]
            
            for phrase in protected_phrases:
                if (before.endswith(phrase[:len(phrase)//2]) and 
                    after.startswith(phrase[len(phrase)//2:])):
                    return True
            
            return False
            
        except Exception:
            return False

    def _clean_filler_words(self, segments: List[TextSegment]) -> List[TextSegment]:
        """清理填詞語"""
        try:
            lang_fillers = self.filler_words.get(self.language, self.filler_words["zh"])
            
            for segment in segments:
                # 創建填詞語的正則表達式
                filler_pattern = "|".join(re.escape(word) for word in lang_fillers)
                
                # 清理填詞語，但保留語意重要的部分
                text = segment.text
                
                # 移除開頭和結尾的填詞語
                text = re.sub(f"^({filler_pattern})\\s*", "", text)
                text = re.sub(f"\\s*({filler_pattern})$", "", text)
                
                # 移除重複的填詞語
                for filler in lang_fillers:
                    # 移除連續重複的填詞語
                    pattern = f"({re.escape(filler)}\\s*){{2,}}"
                    text = re.sub(pattern, filler + " ", text)
                
                segment.text = text.strip()
            
            return segments
            
        except Exception as e:
            logger.warning(f"填詞語清理失敗: {e}")
            return segments
    
    def _remove_empty_segments(self, segments: List[TextSegment]) -> List[TextSegment]:
        """移除空的或只有標點符號的段落"""
        filtered_segments = []
        
        for segment in segments:
            text = segment.text.strip()
            # 移除只有標點符號或過短的無意義段落
            if len(text) <= 1 or text in ['。', '，', '！', '？', '；', '.', ',', '!', '?', ';', '嗯', '啊', '呃']:
                continue
            filtered_segments.append(segment)
        
        return filtered_segments
    
    def _merge_short_segments(self, segments: List[TextSegment]) -> List[TextSegment]:
        """合併過短的片段"""
        if not segments:
            return segments
        
        merged = []
        current = None
        
        for segment in segments:
            if not segment.text.strip():
                continue
                
            # 如果當前片段太短，嘗試合併
            if (current is None or 
                segment.duration() < 1.5 or 
                segment.word_count() < 3):
                
                if current is None:
                    current = segment
                else:
                    # 檢查是否應該合併
                    if self._should_merge(current, segment):
                        current.end = segment.end
                        current.text = f"{current.text} {segment.text}"
                    else:
                        merged.append(current)
                        current = segment
            else:
                if current is not None:
                    merged.append(current)
                current = segment
        
        if current is not None:
            merged.append(current)
        
        return merged
    
    def _should_merge(self, seg1: TextSegment, seg2: TextSegment) -> bool:
        """判斷兩個片段是否應該合併"""
        # 時間間隔檢查
        if seg2.start - seg1.end > 1.0:  # 間隔超過1秒不合併
            return False
        
        # 語意完整性檢查
        combined_duration = seg2.end - seg1.start
        if combined_duration > 6.0:  # 合併後超過6秒不合併
            return False
        
        # 檢查是否有句子結束標記
        lang_endings = self.sentence_endings.get(self.language, self.sentence_endings["zh"])
        if any(ending in seg1.text for ending in lang_endings):
            return False
        
        return True
    
    def _semantic_split(self, segments: List[TextSegment]) -> List[TextSegment]:
        """智能語意分割 - 針對單行字幕優化"""
        split_segments = []
        
        for segment in segments:
            # 如果文本很短（少於8個字），不分割
            if len(segment.text.strip()) <= 8:
                split_segments.append(segment)
                continue
            
            # 如果時長很短（少於2秒），也不分割
            if segment.duration() <= 2.0:
                split_segments.append(segment)
                continue
            
            # 尋找合適的分割點，優先考慮語意完整性
            split_points = self._find_optimal_split_points(segment)
            
            if not split_points:
                split_segments.append(segment)
                continue
            
            # 執行分割
            text_parts = []
            last_pos = 0
            
            for split_point in split_points:
                part = segment.text[last_pos:split_point].strip()
                if part:
                    text_parts.append(part)
                last_pos = split_point
            
            # 添加最後一部分
            final_part = segment.text[last_pos:].strip()
            if final_part:
                text_parts.append(final_part)
            
            # 基於詞級時間戳計算更精確的時間分配
            if hasattr(segment, 'words') and segment.words:
                split_segments.extend(self._create_segments_with_word_timing(segment, text_parts))
            else:
                # 均勻分配時間
                duration_per_part = segment.duration() / len(text_parts)
                current_start = segment.start
                
                for text_part in text_parts:
                    if text_part.strip():
                        new_segment = TextSegment(
                            start=current_start,
                            end=current_start + duration_per_part,
                            text=text_part.strip()
                        )
                        split_segments.append(new_segment)
                        current_start += duration_per_part
        
        return split_segments
    
    def _find_optimal_split_points(self, segment: TextSegment) -> List[int]:
        """尋找最優分割點 - 針對單行字幕優化"""
        text = segment.text
        split_points = []
        max_line_length = 15  # 每行最多15個字符
        
        # 首先嘗試在句號、逗號等標點符號處分割
        punctuation_points = []
        for i, char in enumerate(text):
            if char in ['，', '。', '！', '？', '；', ',', '.', '!', '?', ';']:
                if i > 5 and i < len(text) - 2:  # 避免太短或太接近末尾
                    punctuation_points.append(i + 1)
        
        # 如果有標點符號分割點，優先使用
        if punctuation_points:
            current_pos = 0
            for punct_pos in punctuation_points:
                if punct_pos - current_pos >= 8:  # 確保每段至少8個字符
                    split_points.append(punct_pos)
                    current_pos = punct_pos
        
        # 如果沒有合適的標點符號，在連接詞處分割
        if not split_points:
            connectors = self.connectors.get(self.language, self.connectors.get("zh", []))
            for connector in connectors:
                pos = text.find(connector)
                if pos > 5 and pos < len(text) - len(connector) - 2:
                    split_points.append(pos)
                    break
        
        # 如果還是沒有分割點，按長度強制分割
        if not split_points and len(text) > max_line_length:
            # 在中間位置附近尋找空格或適合的分割點
            mid_point = len(text) // 2
            for i in range(mid_point - 3, mid_point + 4):
                if i > 0 and i < len(text) and text[i] == ' ':
                    split_points.append(i)
                    break
            else:
                # 強制在中間分割
                split_points.append(mid_point)
        
        return sorted(split_points)
    
    def _create_segments_with_word_timing(self, segment: TextSegment, text_parts: List[str]) -> List[TextSegment]:
        """基於詞級時間戳創建精確的分段"""
        if not segment.words:
            return []
        
        segments = []
        word_index = 0
        
        for text_part in text_parts:
            if not text_part.strip():
                continue
            
            # 計算這部分文本需要多少個詞
            part_words = []
            part_length = len(text_part.strip())
            covered_length = 0
            
            while word_index < len(segment.words) and covered_length < part_length:
                word = segment.words[word_index]
                part_words.append(word)
                covered_length += len(word.get('word', '').strip())
                word_index += 1
            
            if part_words:
                start_time = part_words[0].get('start', segment.start)
                end_time = part_words[-1].get('end', segment.end)
                
                new_segment = TextSegment(
                    start=start_time,
                    end=end_time + 0.1,  # 加上0.1秒延續時間
                    text=text_part.strip(),
                    words=part_words
                )
                segments.append(new_segment)
        
        return segments
    
    def _find_split_points(self, segment: TextSegment) -> List[int]:
        """尋找語意分割點（舊版本，保留兼容性）"""
        text = segment.text
        split_points = []
        
        # 語言特定的分割邏輯
        if self.language in ["zh", "ja", "ko"]:
            # 中日韓語言：尋找自然停頓點
            patterns = [
                r'[。！？；]',  # 句號等
                r'[，、](?=.{10,})',  # 逗號（後面至少還有10個字符）
                r'(?<=.{15,})[，、]',  # 逗號（前面至少有15個字符）
            ]
        else:
            # 英語等：基於語法結構
            patterns = [
                r'[.!?;]',  # 句子結束
                r'[,](?=\s+.{20,})',  # 逗號後有足夠內容
                r'(?<=.{20,})[,]',  # 逗號前有足夠內容
            ]
        
        for pattern in patterns:
            matches = list(re.finditer(pattern, text))
            for match in matches:
                pos = match.end()
                # 確保分割點不會造成過短的片段
                if 10 <= pos <= len(text) - 10:
                    split_points.append(pos)
        
        # 去重並排序
        split_points = sorted(list(set(split_points)))
        
        # 限制分割數量，避免過度分割
        if len(split_points) > 2:
            split_points = split_points[:2]
        
        return split_points
    
    def _optimize_punctuation(self, segments: List[TextSegment]) -> List[TextSegment]:
        """優化標點符號"""
        for segment in segments:
            text = segment.text
            
            # 移除開頭的標點符號
            text = re.sub(r'^[，,、。.!！?？;；]+\s*', '', text)
            
            # 確保句子結尾有適當的標點
            if self.language in ["zh", "ja", "ko"]:
                if not re.search(r'[。！？；…]$', text.strip()):
                    # 根據語氣添加標點
                    if re.search(r'[嗎呢吧啊]$', text.strip()):
                        text += "？"
                    elif re.search(r'[吧呀啦]$', text.strip()):
                        text += "！"
                    else:
                        text += "。"
            else:
                if not re.search(r'[.!?]$', text.strip()):
                    text += "."
            
            segment.text = text.strip()
        
        return segments
    
    def _balance_duration(self, segments: List[TextSegment]) -> List[TextSegment]:
        """平衡片段時長"""
        balanced = []
        
        for segment in segments:
            # 計算理想的顯示時長（基於字數）
            char_count = len(segment.text)
            ideal_duration = max(2.0, min(6.0, char_count * 0.15))  # 每字符0.15秒
            
            actual_duration = segment.duration()
            
            # 如果實際時長與理想時長差距太大，調整
            if actual_duration < ideal_duration * 0.5:
                # 太短，延長結束時間
                segment.end = segment.start + ideal_duration
            elif actual_duration > ideal_duration * 2:
                # 太長，但不縮短（保持語音同步）
                pass
            
            balanced.append(segment)
        
        return balanced
    
    def _fix_time_overlaps(self, segments: List[TextSegment]) -> List[TextSegment]:
        """修正時間軸重疊問題 - 語音起始者優先，重疊部分不延伸"""
        if not segments:
            return segments
        
        # 按開始時間排序
        segments.sort(key=lambda x: x.start)
        
        fixed_segments = []
        
        for i, segment in enumerate(segments):
            if i == 0:
                fixed_segments.append(segment)
                continue
            
            prev_segment = fixed_segments[-1]
            
            # 檢查是否與下一個段落的開始時間重疊
            if segment.start < prev_segment.end:
                # 語音起始者優先：將前一段落的結束時間縮短到當前段落開始前0.05秒
                prev_segment.end = segment.start - 0.05
                
                # 確保前一段落至少有最小時長
                min_duration = 0.3
                if prev_segment.duration() < min_duration:
                    prev_segment.end = prev_segment.start + min_duration
                    # 如果調整後仍然重疊，調整當前段落開始時間
                    if prev_segment.end > segment.start:
                        segment.start = prev_segment.end + 0.05
            
            fixed_segments.append(segment)
        
        return fixed_segments
    
    def _fix_short_gaps(self, segments: List[TextSegment]) -> List[TextSegment]:
        """
        修復短間隙閃動問題 - 消除字幕間極短的空白期
        
        Args:
            segments: 字幕片段列表
            
        Returns:
            List[TextSegment]: 修復後的字幕片段
        """
        if not segments or len(segments) < 2:
            return segments
        
        try:
            # 按開始時間排序
            segments.sort(key=lambda x: x.start)
            
            fixed_segments = []
            
            for i, segment in enumerate(segments):
                if i == 0:
                    fixed_segments.append(segment)
                    continue
                
                prev_segment = fixed_segments[-1]
                current_gap = segment.start - prev_segment.end
                
                # 對於 LARGE 模型，完全跳過間隙處理
                if self.model_size == "large":
                    # LARGE 模型：保持原始時間戳，不做任何間隙調整
                    # 這樣可以確保字幕時間與音訊精確對應
                    logger.debug(f"LARGE模型保持原始間隙: {current_gap:.3f}s")
                    # 直接添加片段，不做任何修改
                else:
                    # 其他模型：檢測短間隙（0.15秒以下）
                    if 0 < current_gap <= 0.15:
                        # 原有的分級處理
                        if current_gap <= 0.05:
                            # 極短間隙（≤0.05秒）：直接無縫連接
                            prev_segment.end = segment.start
                            logger.debug(f"無縫連接間隙: {current_gap:.3f}s")
                            
                        elif current_gap <= 0.1:
                            # 短間隙（0.05-0.1秒）：平滑延伸，留1-2ms緩衝
                            buffer = min(0.002, current_gap * 0.1)  # 1-2ms緩衝
                            prev_segment.end = segment.start - buffer
                            logger.debug(f"平滑延伸間隙: {current_gap:.3f}s -> {buffer:.3f}s")
                            
                        else:
                            # 中等間隙（0.1-0.15秒）：保守延伸，基於語意連續性
                            if self._should_bridge_gap(prev_segment, segment):
                                # 語意連續，延伸到一半位置
                                bridge_point = prev_segment.end + current_gap * 0.5
                                prev_segment.end = bridge_point
                                logger.debug(f"語意橋接間隙: {current_gap:.3f}s -> {current_gap*0.5:.3f}s")
                    
                    # 確保前一片段的最小顯示時間（至少0.3秒）- 只對非LARGE模型
                    min_duration = 0.3
                    if prev_segment.duration() < min_duration:
                        prev_segment.end = prev_segment.start + min_duration
                        # 如果延伸後與當前片段重疊，調整當前片段開始時間
                        if prev_segment.end > segment.start:
                            segment.start = prev_segment.end + 0.01
                
                fixed_segments.append(segment)
            
            logger.info(f"短間隙修復完成，處理了 {len([s for s in segments if s.start > 0])} 個片段")
            return fixed_segments
            
        except Exception as e:
            logger.error(f"短間隙修復失敗: {e}")
            return segments
    
    def _should_bridge_gap(self, prev_segment: TextSegment, current_segment: TextSegment) -> bool:
        """
        判斷是否應該橋接間隙（基於語意連續性）
        
        Args:
            prev_segment: 前一個片段
            current_segment: 當前片段
            
        Returns:
            bool: 是否應該橋接
        """
        try:
            prev_text = prev_segment.text.strip().lower()
            current_text = current_segment.text.strip().lower()
            
            # 如果任一片段為空，不橋接
            if not prev_text or not current_text:
                return False
            
            # 檢查語意連續性指標
            continuity_indicators = [
                # 前一句以連接詞結尾
                prev_text.endswith(('然後', '接著', '而且', '但是', '所以', '因為')),
                prev_text.endswith(('and', 'but', 'so', 'then', 'because', 'however')),
                
                # 當前句以連接詞開始
                current_text.startswith(('然後', '接著', '而且', '但是', '所以', '因為')),
                current_text.startswith(('and', 'but', 'so', 'then', 'because', 'however')),
                
                # 前一句是不完整的句子（沒有明確結束）
                not any(prev_text.endswith(end) for end in ['了', '的', '嗎', '吧', '呢', '啊']),
                not any(prev_text.endswith(end) for end in ['.', '!', '?', 'yes', 'no']),
                
                # 句子長度較短，可能是語音切斷
                len(prev_text) < 8 or len(current_text) < 8,
            ]
            
            # 如果有任何連續性指標，建議橋接
            return any(continuity_indicators)
            
        except Exception as e:
            logger.debug(f"語意連續性判斷失敗: {e}")
            return False
    
    def _adjust_audio_sync(self, segments: List[TextSegment], offset_seconds: float = 0.1) -> List[TextSegment]:
        """
        調整字幕與音訊同步 - 解決字幕提前問題
        
        Args:
            segments: 字幕片段列表
            offset_seconds: 偏移秒數，正值表示延後字幕（預設0.1秒）
            
        Returns:
            List[TextSegment]: 調整後的字幕片段
        """
        if not segments:
            return segments
        
        try:
            # 可從配置檔案讀取偏移量
            config_offset = self._get_sync_offset_from_config()
            if config_offset is not None:
                offset_seconds = config_offset
            
            adjusted_segments = []
            
            for segment in segments:
                adjusted_segment = TextSegment(
                    start=max(0, segment.start + offset_seconds),  # 確保不會小於0
                    end=segment.end + offset_seconds,
                    text=segment.text,
                    confidence=segment.confidence,
                    words=segment.words
                )
                adjusted_segments.append(adjusted_segment)
            
            logger.info(f"音訊同步調整完成，偏移量: {offset_seconds:.3f}秒")
            return adjusted_segments
            
        except Exception as e:
            logger.error(f"音訊同步調整失敗: {e}")
            return segments
    
    def _statistical_timing_correction(self, segments: List[TextSegment]) -> List[TextSegment]:
        """
        基於統計分析的最終時間戳校正，針對市場反饋問題的激進解決方案
        
        分析段落模式，識別並修正異常的時間包含問題
        """
        if len(segments) < 3:
            return segments
        
        try:
            # 計算段落間的正常間隔
            gaps = []
            for i in range(len(segments) - 1):
                gap = segments[i + 1].start - segments[i].end
                if 0 <= gap <= 10:  # 只考慮合理的間隔
                    gaps.append(gap)
            
            if not gaps:
                return segments
            
            # 計算平均間隔和標準差
            avg_gap = sum(gaps) / len(gaps)
            
            # 對異常段落進行激進修正
            corrected_segments = []
            for i, segment in enumerate(segments):
                if i > 0:  # 檢查與前一段落的關係
                    prev_segment = segments[i - 1]
                    gap = segment.start - prev_segment.end
                    
                    # 如果間隔為負值或異常大，且段落持續時間很長
                    if (gap < -1.0 or gap > avg_gap * 3) and segment.duration() > 4.0:
                        # 檢查是否有詞級數據可以修正
                        if hasattr(segment, 'words') and segment.words:
                            # 找到第一個有效詞，更激進的修正
                            for word in segment.words[:3]:  # 檢查前3個詞
                                word_text = word.get('word', '').strip()
                                if len(word_text) > 1 and word.get('start'):
                                    new_start = word['start']
                                    # 確保不會與前一段落重疊太多
                                    if new_start > prev_segment.end - 0.5:
                                        if new_start != segment.start:
                                            logger.info(f"統計修正段落 {i+1}: '{segment.text[:20]}...' {segment.start:.3f}s -> {new_start:.3f}s")
                                            segment.start = new_start
                                        break
                
                corrected_segments.append(segment)
            
            return corrected_segments
            
        except Exception as e:
            logger.error(f"統計時間戳校正失敗: {e}")
            return segments
    
    def _fix_word_level_timestamps(self, segments: List[TextSegment]) -> List[TextSegment]:
        """
        使用詞級時間戳校正段落邊界，修復間奏被誤包含問題
        
        Args:
            segments: 字幕片段列表
            
        Returns:
            List[TextSegment]: 校正後的字幕片段
        """
        if not segments:
            return segments
            
        try:
            fixed_segments = []
            
            for segment in segments:
                if hasattr(segment, 'words') and segment.words and len(segment.words) > 0:
                    # 使用第一個詞的時間作為真實開始時間
                    first_word_start = segment.words[0].get('start', segment.start)
                    last_word_end = segment.words[-1].get('end', segment.end)
                    
                    # 市場成功方案：激進的時間戳校正（降低閾值到0.2秒）
                    time_diff = first_word_start - segment.start
                    if time_diff > 0.2:  # 只要提前超過0.2秒就修正
                        logger.info(f"激進校正: '{segment.text[:15]}...' {segment.start:.3f}s -> {first_word_start:.3f}s (提前 {time_diff:.3f}s)")
                        segment.start = first_word_start
                        
                    # 檢查結束時間
                    if abs(last_word_end - segment.end) > 0.5:
                        segment.end = last_word_end
                        
                    # 檢查段落是否異常長但詞數少（典型的間奏包含症狀）
                    duration = segment.end - segment.start
                    word_count = len([w for w in segment.words if len(w.get('word', '').strip()) > 1])
                    if duration > 6.0 and word_count < 5:  # 6秒以上但少於5個有效詞
                        # 縮短到最後一個詞+緩衝時間
                        if segment.words:
                            last_word_end = segment.words[-1].get('end', segment.end)
                            new_end = last_word_end + 0.5
                            logger.info(f"修正長段落: '{segment.text[:15]}...' 結束時間 {segment.end:.3f}s -> {new_end:.3f}s")
                            segment.end = new_end
                
                fixed_segments.append(segment)
            
            # 檢測和處理大間隙（潛在間奏）
            fixed_segments = self._detect_and_fix_gaps(fixed_segments)
            
            # 最終的激進修正：基於統計分析調整異常段落
            fixed_segments = self._statistical_timing_correction(fixed_segments)
            
            # 應用智能時間戳優化系統
            try:
                from subeasy_multilayer_filter import apply_subeasy_filter
                
                # 將 TextSegment 轉換為字典格式
                segment_dicts = []
                for seg in fixed_segments:
                    segment_dicts.append({
                        'start': seg.start,
                        'end': seg.end,
                        'text': seg.text,
                        'words': getattr(seg, 'words', None),
                        'no_speech_prob': getattr(seg, 'no_speech_prob', 0.0),
                        'avg_logprob': getattr(seg, 'avg_logprob', 0.0)
                    })
                
                # 應用智能時間戳優化
                if hasattr(self, 'audio_file') and self.audio_file:
                    logger.info(f"應用時間戳優化處理，共 {len(segment_dicts)} 個段落")
                    
                    filtered_dicts = apply_subeasy_filter(segment_dicts, self.audio_file)
                    
                    # 將結果轉換回 TextSegment 格式
                    multilayer_fixed_segments = []
                    for i, filtered_dict in enumerate(filtered_dicts):
                        # 查找對應的原始段落
                        if i < len(fixed_segments):
                            seg = fixed_segments[i]
                            seg.start = filtered_dict['start']
                            seg.end = filtered_dict['end']
                            multilayer_fixed_segments.append(seg)
                        else:
                            # 創建新的 TextSegment
                            new_seg = TextSegment(
                                start=filtered_dict['start'],
                                end=filtered_dict['end'],
                                text=filtered_dict['text']
                            )
                            multilayer_fixed_segments.append(new_seg)
                    
                    fixed_segments = multilayer_fixed_segments
                    logger.info("時間戳智能優化完成")
                else:
                    logger.debug("未提供音頻文件路徑，跳過智能優化處理")
                
            except ImportError:
                logger.debug("智能優化模組未載入，使用標準處理")
            except Exception as e:
                logger.warning(f"智能優化處理異常: {e}")
                # 發生錯誤時繼續使用原始segments，不中斷流程
            
            logger.info(f"詞級時間戳校正完成，處理了 {len(fixed_segments)} 個片段")
            return fixed_segments
            
        except Exception as e:
            logger.error(f"詞級時間戳校正失敗: {e}")
            return segments
    
    def _detect_and_fix_gaps(self, segments: List[TextSegment]) -> List[TextSegment]:
        """
        檢測大間隙並修正可能的間奏包含問題
        """
        if len(segments) < 2:
            return segments
            
        try:
            for i in range(len(segments) - 1):
                current = segments[i]
                next_segment = segments[i + 1]
                
                gap = next_segment.start - current.end
                
                # 檢測大間隙（可能有間奏）
                if gap > 3.0:  # 間隙超過3秒
                    logger.debug(f"檢測到大間隙 {gap:.1f}秒 在片段 '{current.text[:15]}...' 和 '{next_segment.text[:15]}...' 之間")
                    
                    # 對於LARGE模型，更保守地縮短段落結束時間
                    if self.model_size == "large":
                        # 確保當前段落不會延伸太遠到間奏中
                        max_duration = min(current.duration(), 6.0)  # 限制最大時長6秒
                        current.end = min(current.end, current.start + max_duration)
                        logger.debug(f"縮短段落時長至 {current.duration():.1f}秒")
                        
            return segments
            
        except Exception as e:
            logger.error(f"間隙檢測處理失敗: {e}")
            return segments
    
    def _get_sync_offset_from_config(self) -> Optional[float]:
        """
        從配置檔案讀取同步偏移量，並根據模型大小進行調整
        
        Returns:
            Optional[float]: 偏移量（秒），如果沒有配置則返回模型特定的預設值
        """
        try:
            import json
            import os
            
            # 模型特定的預設偏移量
            model_default_offsets = {
                "base": 0.1,      # Base 模型，保持原始偏移
                "medium": 0.1,    # Medium 模型，保持原始偏移
                "large": 0.0      # Large 模型，不需要額外偏移（更精確）
            }
            
            config_files = [
                'user_config.json',
                'local_gui_config.json',
                'subtitle_config.json'
            ]
            
            base_offset = None
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    # 首先檢查嵌套結構中的配置
                    nested_paths = [
                        ['audio_processing', 'audio_sync_offset'],
                        ['post_processing', 'audio_sync_offset'],
                        ['output', 'audio_sync_offset']
                    ]
                    
                    for path in nested_paths:
                        current = config
                        try:
                            for key in path:
                                current = current[key]
                            base_offset = float(current)
                            logger.info(f"從 {config_file} 讀取基礎同步偏移量: {base_offset:.3f}秒")
                            break
                        except (KeyError, TypeError, ValueError):
                            continue
                    
                    if base_offset is not None:
                        break
                    
                    # 然後檢查頂層配置鍵名
                    offset_keys = [
                        'audio_sync_offset',
                        'subtitle_delay',
                        'sync_offset',
                        'time_offset'
                    ]
                    
                    for key in offset_keys:
                        if key in config:
                            base_offset = float(config[key])
                            logger.info(f"從 {config_file} 讀取基礎同步偏移量: {base_offset:.3f}秒")
                            break
            
            # 如果沒有從配置檔案讀取到偏移量，使用模型特定的預設值
            if base_offset is None:
                base_offset = model_default_offsets.get(self.model_size, 0.1)
                logger.info(f"使用 {self.model_size} 模型的預設偏移量: {base_offset:.3f}秒")
            
            # 根據模型大小調整偏移量
            if self.model_size == "large":
                # Large 模型：高精度，但需要小幅延遲以完美同步
                # 根據實測，0.15秒的延遲可以讓字幕與聲音更同步
                final_offset = 0.15
                logger.info(f"Large 模型：使用 {final_offset:.3f}秒延遲以優化同步 (原始: {base_offset:.3f}秒)")
            elif self.model_size == "medium":
                # Medium 模型保持配置的偏移量
                final_offset = base_offset
                logger.info(f"Medium 模型：使用配置偏移量 {final_offset:.3f}秒")
            else:
                # Base 模型可能需要稍多的偏移
                final_offset = base_offset
                logger.info(f"Base 模型：使用配置偏移量 {final_offset:.3f}秒")
            
            return final_offset
            
        except Exception as e:
            logger.debug(f"讀取同步偏移量配置失敗: {e}")
            return None


def optimize_subtitle_segments(segments: List[Dict[str, Any]], 
                             language: str = "auto",
                             model_size: str = "medium",
                             audio_file: str = None) -> List[Dict[str, Any]]:
    """
    優化字幕片段的便捷函數
    
    Args:
        segments: 原始字幕片段
        language: 語言代碼
        model_size: 模型大小（用於調整音頻同步偏移）
        
    Returns:
        List[Dict]: 優化後的字幕片段
    """
    processor = SemanticSegmentProcessor(language, model_size)
    processor.audio_file = audio_file  # 設置音頻文件路徑供剪映對齊使用
    return processor.process_segments(segments)


# 測試函數
def test_semantic_processor():
    """測試語意處理器"""
    print("=== 測試語意斷句處理器 ===")
    
    # 測試數據
    test_segments = [
        {"start": 0.0, "end": 1.5, "text": "嗯，你好"},
        {"start": 1.5, "end": 4.0, "text": "我是語音助手，今天天氣很好"},
        {"start": 4.0, "end": 8.0, "text": "我們可以聊聊天氣，也可以討論其他話題，比如說音樂或者電影"},
        {"start": 8.0, "end": 9.0, "text": "好的"},
    ]
    
    processor = SemanticSegmentProcessor("zh")
    result = processor.process_segments(test_segments)
    
    print(f"原始片段數: {len(test_segments)}")
    print(f"處理後片段數: {len(result)}")
    
    for i, seg in enumerate(result, 1):
        print(f"[{i}] {seg['start']:.1f}s-{seg['end']:.1f}s: {seg['text']}")


if __name__ == "__main__":
    test_semantic_processor()