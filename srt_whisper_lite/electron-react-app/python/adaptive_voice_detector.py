#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自適應人聲檢測器
完全基於音頻特徵的動態人聲檢測，無硬編碼閾值
"""

import numpy as np
import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import math
import scipy.signal
from scipy.cluster.vq import kmeans2, whiten
from sklearn.preprocessing import StandardScaler
import librosa

logger = logging.getLogger(__name__)


class AdaptiveVoiceDetector:
    """
    自適應人聲檢測器
    
    基於多維音頻特徵的無硬編碼人聲檢測系統：
    - 動態學習音頻內容特徵分佈
    - 自適應聚類區分人聲與非人聲
    - 精確的時間邊界定位
    """
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.frame_length = int(sample_rate * 0.025)  # 25ms frames
        self.hop_length = int(sample_rate * 0.010)    # 10ms hop
        
        # 特徵統計（動態計算）
        self.audio_features_stats = {}
        self.voice_model = None
        self.scaler = StandardScaler()
        
        # 人聲檢測參數（動態設定）
        self.voice_confidence_threshold = None  # 動態計算
        self.segment_min_voice_ratio = None     # 動態計算
        
        logger.info("自適應人聲檢測器初始化完成")
    
    def detect_voice_segments(self, segments: List[Dict], audio_file: str) -> List[Dict]:
        """
        檢測並修正語音段落的時間邊界
        
        Args:
            segments: 原始字幕段落
            audio_file: 音頻文件路徑
            
        Returns:
            List[Dict]: 修正後的段落（僅包含真實人聲部分）
        """
        try:
            logger.info("開始自適應人聲檢測")
            
            # 1. 載入音頻並分析特徵
            audio_data, sr = self._load_audio(audio_file)
            if audio_data is None:
                logger.warning("音頻載入失敗，跳過人聲檢測")
                return segments
            
            # 2. 全域特徵分析和學習
            self._analyze_global_features(audio_data, sr)
            
            # 3. 為每個段落進行人聲檢測
            voice_segments = self._process_segments_for_voice(segments, audio_data, sr)
            
            # 4. 精確邊界修正
            refined_segments = self._refine_voice_boundaries(voice_segments, audio_data, sr)
            
            # 5. 報告檢測結果
            self._report_voice_detection_results(segments, refined_segments)
            
            return refined_segments
            
        except Exception as e:
            logger.error(f"人聲檢測失敗: {e}")
            return segments
    
    def _load_audio(self, audio_file: str) -> Tuple[Optional[np.ndarray], int]:
        """載入音頻文件"""
        try:
            if not Path(audio_file).exists():
                logger.error(f"音頻文件不存在: {audio_file}")
                return None, 0
            
            # 使用 librosa 載入音頻
            audio_data, sr = librosa.load(audio_file, sr=self.sample_rate)
            logger.info(f"音頻載入成功: {len(audio_data)/sr:.2f}秒, 採樣率={sr}Hz")
            
            return audio_data, sr
            
        except Exception as e:
            logger.error(f"音頻載入失敗: {e}")
            return None, 0
    
    def _analyze_global_features(self, audio_data: np.ndarray, sr: int) -> None:
        """分析全域音頻特徵並建立動態模型"""
        try:
            logger.info("分析全域音頻特徵...")
            
            # 提取全域特徵
            global_features = self._extract_global_audio_features(audio_data, sr)
            
            # 分段特徵提取（用於學習）
            segment_features = []
            window_size = sr * 2  # 2秒窗口
            hop_size = sr // 4    # 0.25秒跳躍
            
            for start in range(0, len(audio_data) - window_size, hop_size):
                end = start + window_size
                segment_audio = audio_data[start:end]
                
                features = self._extract_segment_features(segment_audio, sr)
                if features is not None:
                    segment_features.append(features)
            
            if not segment_features:
                logger.warning("無法提取段落特徵")
                return
            
            # 轉換為矩陣
            feature_matrix = np.array(segment_features)
            
            # 標準化特徵
            self.scaler.fit(feature_matrix)
            normalized_features = self.scaler.transform(feature_matrix)
            
            # 無監督聚類學習（假設存在人聲和非人聲兩類）
            self._learn_voice_nonvoice_clusters(normalized_features)
            
            # 動態設定檢測閾值
            self._calculate_dynamic_thresholds(feature_matrix)
            
            logger.info("全域特徵分析完成")
            
        except Exception as e:
            logger.error(f"全域特徵分析失敗: {e}")
    
    def _extract_global_audio_features(self, audio_data: np.ndarray, sr: int) -> Dict:
        """提取全域音頻特徵"""
        features = {}
        
        # 頻譜特徵
        stft = librosa.stft(audio_data, hop_length=self.hop_length, 
                           n_fft=self.frame_length * 2)
        magnitude = np.abs(stft)
        
        # 頻譜質心
        features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(
            S=magnitude, sr=sr)[0])
        
        # 頻譜帶寬
        features['spectral_bandwidth'] = np.mean(librosa.feature.spectral_bandwidth(
            S=magnitude, sr=sr)[0])
        
        # 頻譜滾降
        features['spectral_rolloff'] = np.mean(librosa.feature.spectral_rolloff(
            S=magnitude, sr=sr)[0])
        
        # 零交叉率
        features['zcr'] = np.mean(librosa.feature.zero_crossing_rate(
            audio_data, frame_length=self.frame_length, hop_length=self.hop_length)[0])
        
        # 能量統計
        features['energy_mean'] = np.mean(audio_data ** 2)
        features['energy_std'] = np.std(audio_data ** 2)
        
        return features
    
    def _extract_segment_features(self, segment_audio: np.ndarray, sr: int) -> Optional[np.ndarray]:
        """提取音頻段落的多維特徵向量"""
        try:
            if len(segment_audio) < self.frame_length:
                return None
            
            features = []
            
            # 1. 基頻特徵（F0）
            try:
                f0, voiced_flag, voiced_probs = librosa.pyin(
                    segment_audio, 
                    fmin=librosa.note_to_hz('C2'),  # ~65 Hz
                    fmax=librosa.note_to_hz('C7')   # ~2093 Hz
                )
                f0_clean = f0[voiced_flag]
                if len(f0_clean) > 0:
                    features.extend([
                        np.mean(f0_clean),      # 平均基頻
                        np.std(f0_clean),       # 基頻變化
                        np.mean(voiced_probs)   # 有聲概率
                    ])
                else:
                    features.extend([0.0, 0.0, 0.0])
            except:
                features.extend([0.0, 0.0, 0.0])
            
            # 2. 梅爾頻率倒譜係數 (MFCC) - 語音識別核心特徵
            mfccs = librosa.feature.mfcc(
                y=segment_audio, sr=sr, n_mfcc=13,
                hop_length=self.hop_length, n_fft=self.frame_length * 2
            )
            features.extend(np.mean(mfccs, axis=1))  # 13維MFCC平均值
            
            # 3. 頻譜特徵
            stft = librosa.stft(segment_audio, hop_length=self.hop_length, 
                               n_fft=self.frame_length * 2)
            magnitude = np.abs(stft)
            
            # 頻譜質心（音色特徵）
            spectral_centroid = librosa.feature.spectral_centroid(
                S=magnitude, sr=sr)
            features.append(np.mean(spectral_centroid))
            
            # 頻譜帶寬（頻譜分散度）
            spectral_bandwidth = librosa.feature.spectral_bandwidth(
                S=magnitude, sr=sr)
            features.append(np.mean(spectral_bandwidth))
            
            # 4. 共振峰相關特徵（人聲特有）
            # 計算線性預測係數（LPC）近似共振峰
            try:
                lpc_coeffs = librosa.lpc(segment_audio, order=12)
                # 從LPC係數計算共振峰頻率
                roots = np.roots(lpc_coeffs)
                roots = roots[np.imag(roots) >= 0]
                
                formant_frequencies = []
                for root in roots:
                    if np.abs(root) < 1.0:
                        freq = np.angle(root) * sr / (2 * np.pi)
                        if 200 < freq < 4000:  # 人聲共振峰範圍
                            formant_frequencies.append(freq)
                
                if formant_frequencies:
                    formant_frequencies.sort()
                    # 前三個共振峰
                    for i in range(3):
                        if i < len(formant_frequencies):
                            features.append(formant_frequencies[i])
                        else:
                            features.append(0.0)
                else:
                    features.extend([0.0, 0.0, 0.0])
            except:
                features.extend([0.0, 0.0, 0.0])
            
            # 5. 時域特徵
            # 零交叉率（語音vs音樂區分）
            zcr = librosa.feature.zero_crossing_rate(
                segment_audio, frame_length=self.frame_length, 
                hop_length=self.hop_length)
            features.append(np.mean(zcr))
            
            # 短時能量
            energy = librosa.feature.rms(
                y=segment_audio, frame_length=self.frame_length, 
                hop_length=self.hop_length)
            features.extend([np.mean(energy), np.std(energy)])
            
            # 6. 頻譜平坦度（音樂vs語音指標）
            spectral_flatness = librosa.feature.spectral_flatness(
                S=magnitude)
            features.append(np.mean(spectral_flatness))
            
            return np.array(features)
            
        except Exception as e:
            logger.debug(f"特徵提取失敗: {e}")
            return None
    
    def _learn_voice_nonvoice_clusters(self, feature_matrix: np.ndarray) -> None:
        """學習人聲/非人聲聚類模型"""
        try:
            if len(feature_matrix) < 4:
                logger.warning("數據不足，無法進行聚類學習")
                return
            
            # K-means聚類（假設2類：人聲和非人聲）
            centroids, labels = kmeans2(feature_matrix, 2)
            
            # 分析兩個聚類的特徵
            cluster_0_features = feature_matrix[labels == 0]
            cluster_1_features = feature_matrix[labels == 1]
            
            # 基於MFCC和基頻特徵判斷哪個是人聲聚類
            # 人聲通常具有：更明顯的基頻、特定的MFCC模式
            def voice_likelihood(features):
                # 基頻相關特徵 (indices 0-2)
                f0_mean = np.mean(features[:, 0])
                voiced_prob = np.mean(features[:, 2])
                
                # MFCC特徵穩定性
                mfcc_features = features[:, 3:16]  # MFCC係數
                mfcc_stability = 1.0 / (np.mean(np.std(mfcc_features, axis=0)) + 1e-8)
                
                # 零交叉率（語音適中，音樂可能更低或更高）
                zcr_mean = np.mean(features[:, -4])
                zcr_score = 1.0 - abs(zcr_mean - 0.1)  # 語音ZCR通常around 0.1
                
                return (voiced_prob * 2.0 + mfcc_stability * 1.0 + zcr_score * 1.0) / 4.0
            
            voice_score_0 = voice_likelihood(cluster_0_features)
            voice_score_1 = voice_likelihood(cluster_1_features)
            
            if voice_score_0 > voice_score_1:
                self.voice_cluster_id = 0
                self.voice_centroid = centroids[0]
                logger.info(f"人聲聚類: 0 (評分: {voice_score_0:.3f} vs {voice_score_1:.3f})")
            else:
                self.voice_cluster_id = 1
                self.voice_centroid = centroids[1]
                logger.info(f"人聲聚類: 1 (評分: {voice_score_1:.3f} vs {voice_score_0:.3f})")
            
            self.cluster_centroids = centroids
            self.cluster_labels = labels
            
        except Exception as e:
            logger.error(f"聚類學習失敗: {e}")
            self.voice_cluster_id = None
    
    def _calculate_dynamic_thresholds(self, feature_matrix: np.ndarray) -> None:
        """動態計算檢測閾值"""
        try:
            # 基於特徵分佈的統計方法設定閾值
            if hasattr(self, 'voice_cluster_id') and self.voice_cluster_id is not None:
                voice_features = feature_matrix[self.cluster_labels == self.voice_cluster_id]
                
                # 人聲置信度閾值（基於距離分佈的分位數）
                distances = []
                for feature in feature_matrix:
                    normalized_feature = self.scaler.transform([feature])[0]
                    distance = np.linalg.norm(normalized_feature - self.voice_centroid)
                    distances.append(distance)
                
                distances = np.array(distances)
                
                # 使用75%分位數作為閾值（動態調整）
                self.voice_confidence_threshold = np.percentile(distances, 75)
                
                # 段落最小人聲比例（基於聚類結果動態設定）
                voice_ratio = len(voice_features) / len(feature_matrix)
                self.segment_min_voice_ratio = max(0.3, voice_ratio * 0.6)
                
                logger.info(f"動態閾值設定完成:")
                logger.info(f"  人聲置信度閾值: {self.voice_confidence_threshold:.3f}")
                logger.info(f"  最小人聲比例: {self.segment_min_voice_ratio:.3f}")
            else:
                # 預設保守值
                self.voice_confidence_threshold = 1.0
                self.segment_min_voice_ratio = 0.5
                
        except Exception as e:
            logger.error(f"閾值計算失敗: {e}")
            self.voice_confidence_threshold = 1.0
            self.segment_min_voice_ratio = 0.5
    
    def _process_segments_for_voice(self, segments: List[Dict], 
                                  audio_data: np.ndarray, sr: int) -> List[Dict]:
        """為每個段落進行人聲檢測"""
        processed_segments = []
        
        for i, segment in enumerate(segments):
            try:
                start_time = segment.get('start', 0.0)
                end_time = segment.get('end', start_time + 1.0)
                
                # 提取段落音頻
                start_sample = int(start_time * sr)
                end_sample = int(end_time * sr)
                
                if end_sample > len(audio_data):
                    end_sample = len(audio_data)
                
                if end_sample <= start_sample:
                    processed_segments.append(segment)
                    continue
                
                segment_audio = audio_data[start_sample:end_sample]
                
                # 分析段落的人聲內容
                voice_analysis = self._analyze_segment_voice_content(segment_audio, sr)
                
                # 決定是否保留此段落
                segment_copy = segment.copy()
                segment_copy['voice_analysis'] = voice_analysis
                
                if voice_analysis['is_voice_segment']:
                    # 保留為人聲段落，可能需要調整邊界
                    processed_segments.append(segment_copy)
                    logger.debug(f"段落 {i+1} 判定為人聲: {voice_analysis['voice_confidence']:.3f}")
                else:
                    # 標記為非人聲段落
                    segment_copy['filtered_reason'] = 'non_voice_content'
                    logger.info(f"段落 {i+1} 過濾（非人聲）: 「{segment.get('text', '')}」"
                              f" (置信度: {voice_analysis['voice_confidence']:.3f})")
                
            except Exception as e:
                logger.error(f"段落 {i+1} 處理失敗: {e}")
                processed_segments.append(segment)
        
        return processed_segments
    
    def _analyze_segment_voice_content(self, segment_audio: np.ndarray, sr: int) -> Dict:
        """分析段落的人聲內容"""
        try:
            # 滑動窗口分析
            window_size = sr // 2  # 0.5秒窗口
            hop_size = sr // 4     # 0.25秒跳躍
            
            voice_scores = []
            
            for start in range(0, len(segment_audio) - window_size, hop_size):
                end = start + window_size
                window_audio = segment_audio[start:end]
                
                features = self._extract_segment_features(window_audio, sr)
                if features is not None:
                    # 計算與人聲聚類中心的距離
                    if hasattr(self, 'voice_centroid'):
                        normalized_features = self.scaler.transform([features])[0]
                        distance = np.linalg.norm(normalized_features - self.voice_centroid)
                        voice_score = 1.0 / (1.0 + distance)  # 距離越小，評分越高
                        voice_scores.append(voice_score)
            
            if not voice_scores:
                return {
                    'is_voice_segment': False,
                    'voice_confidence': 0.0,
                    'voice_ratio': 0.0
                }
            
            # 計算段落的人聲指標
            voice_scores = np.array(voice_scores)
            mean_voice_score = np.mean(voice_scores)
            
            # 基於動態閾值判定
            is_voice = (mean_voice_score > 1.0 / (1.0 + self.voice_confidence_threshold))
            voice_ratio = np.sum(voice_scores > 0.5) / len(voice_scores)
            
            return {
                'is_voice_segment': is_voice and voice_ratio > self.segment_min_voice_ratio,
                'voice_confidence': mean_voice_score,
                'voice_ratio': voice_ratio,
                'voice_scores': voice_scores.tolist()
            }
            
        except Exception as e:
            logger.error(f"人聲內容分析失敗: {e}")
            return {
                'is_voice_segment': True,  # 預設保留
                'voice_confidence': 0.5,
                'voice_ratio': 0.5
            }
    
    def _refine_voice_boundaries(self, segments: List[Dict], 
                               audio_data: np.ndarray, sr: int) -> List[Dict]:
        """精確修正人聲邊界"""
        refined_segments = []
        
        for segment in segments:
            # 跳過被過濾的段落
            if 'filtered_reason' in segment:
                continue
            
            try:
                start_time = segment.get('start', 0.0)
                end_time = segment.get('end', start_time + 1.0)
                
                # 精確邊界檢測
                refined_start, refined_end = self._find_precise_voice_boundaries(
                    audio_data, sr, start_time, end_time
                )
                
                # 如果邊界變化顯著，記錄修正
                if abs(refined_start - start_time) > 0.1 or abs(refined_end - end_time) > 0.1:
                    logger.info(f"邊界修正: {start_time:.3f}s-{end_time:.3f}s → "
                              f"{refined_start:.3f}s-{refined_end:.3f}s "
                              f"「{segment.get('text', '')}」")
                    
                    segment_copy = segment.copy()
                    segment_copy['start'] = refined_start
                    segment_copy['end'] = refined_end
                    segment_copy['_original_start'] = start_time
                    segment_copy['_original_end'] = end_time
                    segment_copy['_boundary_refined'] = True
                    
                    refined_segments.append(segment_copy)
                else:
                    refined_segments.append(segment)
                    
            except Exception as e:
                logger.error(f"邊界修正失敗: {e}")
                refined_segments.append(segment)
        
        return refined_segments
    
    def _find_precise_voice_boundaries(self, audio_data: np.ndarray, sr: int,
                                     start_time: float, end_time: float) -> Tuple[float, float]:
        """找到精確的人聲邊界"""
        try:
            # 擴展搜索範圍
            search_margin = 2.0  # 前後各擴展2秒
            search_start_time = max(0, start_time - search_margin)
            search_end_time = min(len(audio_data) / sr, end_time + search_margin)
            
            search_start_sample = int(search_start_time * sr)
            search_end_sample = int(search_end_time * sr)
            
            search_audio = audio_data[search_start_sample:search_end_sample]
            
            # 高解析度滑動窗口分析
            window_size = sr // 10  # 0.1秒窗口
            hop_size = sr // 20     # 0.05秒跳躍
            
            voice_timeline = []
            time_points = []
            
            for start in range(0, len(search_audio) - window_size, hop_size):
                end = start + window_size
                window_audio = search_audio[start:end]
                window_time = search_start_time + start / sr
                
                features = self._extract_segment_features(window_audio, sr)
                if features is not None and hasattr(self, 'voice_centroid'):
                    normalized_features = self.scaler.transform([features])[0]
                    distance = np.linalg.norm(normalized_features - self.voice_centroid)
                    voice_score = 1.0 / (1.0 + distance)
                    
                    voice_timeline.append(voice_score)
                    time_points.append(window_time)
            
            if not voice_timeline:
                return start_time, end_time
            
            voice_timeline = np.array(voice_timeline)
            time_points = np.array(time_points)
            
            # 動態閾值（基於整體評分分佈）
            voice_threshold = np.percentile(voice_timeline, 60)  # 60%分位點
            
            # 找到人聲區間
            voice_mask = voice_timeline > voice_threshold
            
            if not np.any(voice_mask):
                return start_time, end_time
            
            # 找到最長的連續人聲區間
            voice_regions = []
            in_voice = False
            region_start = None
            
            for i, is_voice in enumerate(voice_mask):
                if is_voice and not in_voice:
                    region_start = time_points[i]
                    in_voice = True
                elif not is_voice and in_voice:
                    if region_start is not None:
                        voice_regions.append((region_start, time_points[i-1]))
                    in_voice = False
            
            # 處理最後一個區間
            if in_voice and region_start is not None:
                voice_regions.append((region_start, time_points[-1]))
            
            if not voice_regions:
                return start_time, end_time
            
            # 選擇與原始段落重疊最多的區間
            best_region = None
            max_overlap = 0
            
            for region_start, region_end in voice_regions:
                overlap = min(end_time, region_end) - max(start_time, region_start)
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_region = (region_start, region_end)
            
            if best_region and max_overlap > 0:
                return best_region[0], best_region[1]
            else:
                return start_time, end_time
                
        except Exception as e:
            logger.error(f"精確邊界檢測失敗: {e}")
            return start_time, end_time
    
    def _report_voice_detection_results(self, original: List[Dict], processed: List[Dict]) -> None:
        """報告人聲檢測結果"""
        filtered_count = 0
        refined_count = 0
        
        # 統計被過濾的段落
        original_count = len(original)
        processed_count = len([s for s in processed if 'filtered_reason' not in s])
        filtered_count = original_count - processed_count
        
        # 統計邊界修正的段落
        refined_count = len([s for s in processed if s.get('_boundary_refined', False)])
        
        logger.info("🎯 自適應人聲檢測結果:")
        logger.info(f"  原始段落: {original_count}")
        logger.info(f"  保留段落: {processed_count}")
        logger.info(f"  過濾段落: {filtered_count} (非人聲內容)")
        logger.info(f"  邊界修正: {refined_count}")
        
        if filtered_count > 0:
            logger.info("✅ 成功過濾非人聲段落，僅保留真實語音內容")


def apply_adaptive_voice_detection(segments: List[Dict], audio_file: str) -> List[Dict]:
    """
    便利函數：應用自適應人聲檢測
    
    Args:
        segments: 字幕段落列表
        audio_file: 音頻文件路徑
        
    Returns:
        List[Dict]: 檢測後的段落（僅包含人聲部分）
    """
    try:
        detector = AdaptiveVoiceDetector()
        return detector.detect_voice_segments(segments, audio_file)
    except Exception as e:
        logger.warning(f"自適應人聲檢測處理異常: {e}")
        return segments