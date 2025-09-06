#!/usr/bin/env python3
"""
剪映風格的雙重時間對齊技術
基於頻域和時域分析的智能字幕時間戳校正器
"""

import numpy as np
import logging
from typing import List, Dict, Any, Tuple, Optional
import librosa
from pathlib import Path

logger = logging.getLogger(__name__)

class JianyingInspiredAligner:
    """
    基於剪映技術的雙重對齊引擎
    
    模擬剪映的 time_align_freq_domain 和 time_align_time_domain 技術
    """
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.hop_length = 512
        self.frame_length = 2048
        
        # 語音 vs 音樂的頻域特徵閾值
        self.speech_freq_range = (85, 4000)  # 人聲主要頻率範圍
        self.music_freq_range = (20, 20000)  # 音樂頻率範圍
        
        logger.info("剪映風格雙重對齊引擎初始化完成")
    
    def dual_alignment_correction(self, segments: List[Dict], audio_file: str) -> List[Dict]:
        """
        雙重對齊主流程：頻域 + 時域分析
        
        Args:
            segments: 原始字幕段落
            audio_file: 音頻文件路徑
            
        Returns:
            List[Dict]: 校正後的段落
        """
        try:
            logger.info("開始剪映風格雙重對齊校正")
            
            # 載入音頻
            audio_data, sr = librosa.load(audio_file, sr=self.sample_rate)
            
            # 階段1：頻域分析 - 檢測語音/間奏區間
            freq_analysis = self._frequency_domain_analysis(audio_data, segments)
            
            # 階段2：時域分析 - 精確語音邊界定位
            time_analysis = self._time_domain_analysis(audio_data, segments)
            
            # 階段3：雙重融合決策
            aligned_segments = self._dual_fusion_decision(segments, freq_analysis, time_analysis)
            
            logger.info(f"雙重對齊完成，處理 {len(aligned_segments)} 個段落")
            return aligned_segments
            
        except Exception as e:
            logger.error(f"雙重對齊失敗: {e}")
            return segments  # 失敗時返回原始段落
    
    def _frequency_domain_analysis(self, audio_data: np.ndarray, segments: List[Dict]) -> Dict:
        """
        頻域分析：模擬剪映的 time_align_freq_domain_v2.0.model
        
        檢測每個段落的頻域特徵，識別語音 vs 間奏/音樂
        """
        logger.debug("執行頻域分析...")
        
        # 計算短時傅立葉變換 (STFT)
        stft = librosa.stft(audio_data, 
                           hop_length=self.hop_length, 
                           n_fft=self.frame_length)
        magnitude = np.abs(stft)
        
        # 轉換為頻率-時間的能量譜
        freqs = librosa.fft_frequencies(sr=self.sample_rate, n_fft=self.frame_length)
        times = librosa.frames_to_time(np.arange(magnitude.shape[1]), 
                                      sr=self.sample_rate, 
                                      hop_length=self.hop_length)
        
        freq_analysis = {}
        
        for i, segment in enumerate(segments):
            start_time = segment.get('start', 0.0)
            end_time = segment.get('end', start_time + 1.0)
            
            # 找到對應的時間範圍
            start_frame = int(start_time * self.sample_rate / self.hop_length)
            end_frame = int(end_time * self.sample_rate / self.hop_length)
            
            if start_frame >= magnitude.shape[1] or end_frame <= start_frame:
                continue
            
            # 提取該段落的頻域特徵
            segment_magnitude = magnitude[:, start_frame:end_frame]
            
            # 語音頻段能量 (85Hz - 4kHz)
            speech_freq_indices = np.where((freqs >= self.speech_freq_range[0]) & 
                                         (freqs <= self.speech_freq_range[1]))[0]
            speech_energy = np.mean(segment_magnitude[speech_freq_indices, :])
            
            # 全頻段能量
            total_energy = np.mean(segment_magnitude)
            
            # 低頻能量 (可能的背景音樂)
            low_freq_indices = np.where((freqs >= 20) & (freqs <= 200))[0]
            low_freq_energy = np.mean(segment_magnitude[low_freq_indices, :])
            
            # 計算語音純度比例
            speech_purity = speech_energy / (total_energy + 1e-8)
            music_indicator = low_freq_energy / (total_energy + 1e-8)
            
            # 檢測間奏模式
            is_interlude = self._detect_interlude_pattern(segment_magnitude, freqs)
            
            freq_analysis[i] = {
                'speech_energy': speech_energy,
                'total_energy': total_energy,
                'speech_purity': speech_purity,
                'music_indicator': music_indicator,
                'is_interlude': is_interlude,
                'confidence': speech_purity * (1 - music_indicator)
            }
            
            logger.debug(f"段落 {i+1}: 語音純度={speech_purity:.3f}, 音樂指標={music_indicator:.3f}")
        
        return freq_analysis
    
    def _time_domain_analysis(self, audio_data: np.ndarray, segments: List[Dict]) -> Dict:
        """
        時域分析：模擬剪映的 time_align_time_domain_v1.0.model
        
        精確檢測語音的起始和結束邊界
        """
        logger.debug("執行時域分析...")
        
        # 計算音頻包絡
        envelope = librosa.onset.onset_strength(y=audio_data, sr=self.sample_rate)
        envelope_times = librosa.frames_to_time(np.arange(len(envelope)), sr=self.sample_rate)
        
        # 計算RMS能量
        rms = librosa.feature.rms(y=audio_data, hop_length=self.hop_length)[0]
        rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=self.sample_rate, hop_length=self.hop_length)
        
        time_analysis = {}
        
        for i, segment in enumerate(segments):
            start_time = segment.get('start', 0.0)
            end_time = segment.get('end', start_time + 1.0)
            
            # 獲取該段落的RMS能量
            start_idx = np.argmin(np.abs(rms_times - start_time))
            end_idx = np.argmin(np.abs(rms_times - end_time))
            
            if end_idx <= start_idx:
                continue
            
            segment_rms = rms[start_idx:end_idx]
            segment_times = rms_times[start_idx:end_idx]
            
            # 檢測真正的語音起始點
            speech_threshold = np.max(segment_rms) * 0.3  # 30%峰值作為語音閾值
            speech_indices = np.where(segment_rms > speech_threshold)[0]
            
            if len(speech_indices) > 0:
                # 找到第一個和最後一個語音點
                first_speech_idx = speech_indices[0]
                last_speech_idx = speech_indices[-1]
                
                precise_start = segment_times[first_speech_idx]
                precise_end = segment_times[last_speech_idx]
                
                # 計算時間戳修正量
                start_correction = precise_start - start_time
                end_correction = precise_end - end_time
                
            else:
                # 沒有檢測到明顯語音
                start_correction = 0.0
                end_correction = 0.0
                precise_start = start_time
                precise_end = end_time
            
            time_analysis[i] = {
                'precise_start': precise_start,
                'precise_end': precise_end,
                'start_correction': start_correction,
                'end_correction': end_correction,
                'speech_detected': len(speech_indices) > 0,
                'speech_ratio': len(speech_indices) / len(segment_rms)
            }
            
            logger.debug(f"段落 {i+1}: 時域修正 start={start_correction:.3f}s, end={end_correction:.3f}s")
        
        return time_analysis
    
    def _detect_interlude_pattern(self, magnitude: np.ndarray, freqs: np.ndarray) -> bool:
        """
        檢測間奏模式：持續的低頻能量 + 缺乏語音頻段變化
        """
        # 檢查是否有持續的低頻背景音樂
        low_freq_indices = np.where((freqs >= 20) & (freqs <= 300))[0]
        low_freq_power = magnitude[low_freq_indices, :]
        low_freq_stability = np.std(np.mean(low_freq_power, axis=0))
        
        # 檢查語音頻段的變化
        speech_freq_indices = np.where((freqs >= 200) & (freqs <= 4000))[0]
        speech_power = magnitude[speech_freq_indices, :]
        speech_variation = np.std(np.mean(speech_power, axis=0))
        
        # 間奏特徵：低頻穩定 + 語音頻段變化小
        is_interlude = (low_freq_stability < speech_variation * 0.5) and (speech_variation < 0.1)
        
        return is_interlude
    
    def _dual_fusion_decision(self, segments: List[Dict], freq_analysis: Dict, time_analysis: Dict) -> List[Dict]:
        """
        雙重融合決策：結合頻域和時域分析結果
        """
        logger.debug("執行雙重融合決策...")
        
        corrected_segments = []
        
        for i, segment in enumerate(segments):
            # 獲取分析結果
            freq_result = freq_analysis.get(i, {})
            time_result = time_analysis.get(i, {})
            
            # 原始時間戳
            original_start = segment.get('start', 0.0)
            original_end = segment.get('end', original_start + 1.0)
            
            # 決策邏輯
            corrected_start = original_start
            corrected_end = original_end
            correction_applied = False
            
            # 規則1：如果頻域檢測到間奏，使用時域的精確邊界
            if freq_result.get('is_interlude', False) or freq_result.get('speech_purity', 1.0) < 0.3:
                if time_result.get('speech_detected', False):
                    corrected_start = time_result['precise_start']
                    corrected_end = time_result['precise_end']
                    correction_applied = True
                    logger.info(f"段落 {i+1}: 檢測到間奏，應用時域修正 {original_start:.3f}s -> {corrected_start:.3f}s")
            
            # 規則2：如果時域檢測到顯著修正且頻域置信度高，應用修正
            elif (abs(time_result.get('start_correction', 0.0)) > 1.0 and 
                  freq_result.get('confidence', 0.0) > 0.7):
                corrected_start = time_result['precise_start']
                correction_applied = True
                logger.info(f"段落 {i+1}: 高置信度時域修正 {original_start:.3f}s -> {corrected_start:.3f}s")
            
            # 規則3：如果兩者都檢測到異常，使用加權平均
            elif (freq_result.get('speech_purity', 1.0) < 0.5 and 
                  time_result.get('speech_ratio', 1.0) < 0.5):
                # 加權融合：頻域置信度高時更信任時域結果
                weight = freq_result.get('confidence', 0.5)
                if weight > 0.6:
                    corrected_start = time_result.get('precise_start', original_start)
                    correction_applied = True
                    logger.info(f"段落 {i+1}: 加權融合修正 {original_start:.3f}s -> {corrected_start:.3f}s")
            
            # 保存結果
            corrected_segment = segment.copy()
            corrected_segment['start'] = corrected_start
            corrected_segment['end'] = corrected_end
            
            # 添加診斷信息
            if correction_applied:
                corrected_segment['alignment_correction'] = {
                    'freq_purity': freq_result.get('speech_purity', 1.0),
                    'time_correction': time_result.get('start_correction', 0.0),
                    'method': 'jianying_dual_alignment'
                }
            
            corrected_segments.append(corrected_segment)
        
        return corrected_segments


def apply_jianying_alignment(segments: List[Dict], audio_file: str) -> List[Dict]:
    """
    便利函數：對段落應用剪映風格的對齊校正
    
    Args:
        segments: 字幕段落列表
        audio_file: 音頻文件路徑
        
    Returns:
        List[Dict]: 校正後的段落
    """
    try:
        aligner = JianyingInspiredAligner()
        return aligner.dual_alignment_correction(segments, audio_file)
    except Exception as e:
        logger.error(f"剪映風格對齊失敗: {e}")
        return segments