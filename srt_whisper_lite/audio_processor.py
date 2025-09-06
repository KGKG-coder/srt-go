#!/usr/bin/env python3
"""
音頻預處理模組（簡化版）
專注於核心功能，確保打包穩定性
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import tempfile

logger = logging.getLogger(__name__)


class AudioProcessor:
    """音頻預處理器（簡化版）"""
    
    def __init__(self, 
                 target_sample_rate: int = 16000,
                 enable_normalize: bool = True,
                 enable_denoise: bool = True,
                 enable_enhancement: bool = True,
                 noise_reduce_strength: float = 0.6):
        """
        初始化音頻處理器
        
        Args:
            target_sample_rate: 目標採樣率
            enable_normalize: 是否啟用音量標準化
            enable_denoise: 是否啟用降噪
            enable_enhancement: 是否啟用音頻增強
            noise_reduce_strength: 降噪強度 (0-1)
        """
        self.target_sample_rate = target_sample_rate
        self.enable_normalize = enable_normalize
        self.enable_denoise = enable_denoise
        self.enable_enhancement = enable_enhancement
        self.noise_reduce_strength = noise_reduce_strength
        
        # 檢查可選依賴
        self.librosa = self._load_librosa()
        self.soundfile = self._load_soundfile()
        self.noisereduce = self._load_noisereduce() if enable_denoise else None
        self.scipy_signal = self._load_scipy_signal() if enable_enhancement else None
        
        # 音頻增強參數
        self.enhancement_params = {
            'dynamic_range_ratio': 0.3,      # 動態範圍壓縮比率
            'speech_freq_boost': 2.0,        # 語音頻率增強倍數
            'high_freq_cut': 8000,           # 高頻截止頻率
            'low_freq_cut': 80,              # 低頻截止頻率
            'compressor_threshold': -20,     # 壓縮器闾值 (dB)
            'compressor_ratio': 4.0,         # 壓縮比率
            'limiter_threshold': 0.95        # 限制器闾值
        }
        
    def _load_librosa(self):
        """載入 librosa（可選依賴）"""
        try:
            import librosa
            return librosa
        except ImportError:
            logger.warning("librosa 未安裝，將使用基本音頻處理")
            return None
    
    def _load_soundfile(self):
        """載入 soundfile（可選依賴）"""
        try:
            import soundfile as sf
            return sf
        except ImportError:
            logger.warning("soundfile 未安裝，將使用基本音頻處理")
            return None
    
    def _load_noisereduce(self):
        """載入 noisereduce（可選依賴）"""
        try:
            import noisereduce as nr
            return nr
        except ImportError:
            logger.warning("noisereduce 未安裝，跳過降噪功能")
            return None
    
    def _load_scipy_signal(self):
        """載入 scipy.signal（用於音頻增強）"""
        try:
            from scipy import signal
            return signal
        except ImportError:
            logger.warning("scipy 未安裝，跳過音頻增強功能")
            return None
    
    def process_audio(self, audio_path: str, 
                     progress_callback: Optional[callable] = None) -> str:
        """
        處理音頻文件
        
        Args:
            audio_path: 輸入音頻路徑
            progress_callback: 進度回調
            
        Returns:
            str: 處理後的音頻路徑
        """
        try:
            # 檢查輸入文件
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"音頻文件不存在: {audio_path}")
            
            if progress_callback:
                progress_callback(5, "開始音頻預處理...")
            
            # 如果沒有音頻處理庫，直接返回原文件
            if not self.librosa or not self.soundfile:
                logger.info("音頻處理庫不可用，使用原始文件")
                return audio_path
            
            # 載入音頻
            if progress_callback:
                progress_callback(10, "載入音頻文件...")
            
            try:
                audio_data, sample_rate = self.librosa.load(
                    audio_path, 
                    sr=self.target_sample_rate,
                    mono=True
                )
            except Exception as e:
                logger.warning(f"音頻載入失敗，使用原始文件: {e}")
                return audio_path
            
            # 音量標準化
            if self.enable_normalize and progress_callback:
                progress_callback(15, "標準化音量...")
                audio_data = self._normalize_audio(audio_data)
            
            # 降噪處理（如果啟用）
            if self.enable_denoise:
                if progress_callback:
                    progress_callback(16, "降噪處理...")
                audio_data = self._denoise_audio(audio_data, sample_rate)
            
            # 音頻增強處理（如果啟用）
            if self.enable_enhancement:
                if progress_callback:
                    progress_callback(18, "音頻增強處理...")
                audio_data = self._enhance_audio(audio_data, sample_rate)
            
            # 保存處理後的音頻
            if progress_callback:
                progress_callback(20, "保存處理結果...")
            
            output_path = self._save_processed_audio(audio_data, sample_rate)
            
            logger.info(f"音頻預處理完成: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"音頻預處理失敗: {e}")
            # 失敗時返回原始文件
            return audio_path
    
    def _normalize_audio(self, audio_data) -> any:
        """增強的音量標準化和語音增強"""
        try:
            import numpy as np
            
            # 1. 動態範圍壓縮
            audio_data = self._dynamic_range_compression(audio_data)
            
            # 2. 高頻增強（提升語音清晰度）
            audio_data = self._enhance_speech_frequencies(audio_data)
            
            # 3. RMS標準化
            rms = np.sqrt(np.mean(audio_data ** 2))
            
            # 避免除零
            if rms > 0:
                # 標準化到 -18dB（稍微提高音量）
                target_rms = 0.125
                audio_data = audio_data * (target_rms / rms)
            
            # 4. 軟限制防止削波
            audio_data = self._soft_limiter(audio_data)
            
            return audio_data
        
        except ImportError:
            logger.warning("numpy 不可用，使用基本標準化")
            return audio_data
        except Exception as e:
            logger.warning(f"音量標準化失敗: {e}")
            return audio_data
    
    def _dynamic_range_compression(self, audio_data) -> any:
        """動態範圍壓縮，提升小音量部分"""
        try:
            import numpy as np
            
            # 計算音頻的絕對值
            abs_audio = np.abs(audio_data)
            
            # 設定壓縮參數
            threshold = 0.3  # 壓縮閾值
            ratio = 3.0      # 壓縮比
            
            # 對超過閾值的部分進行壓縮
            compressed = np.where(
                abs_audio > threshold,
                np.sign(audio_data) * (threshold + (abs_audio - threshold) / ratio),
                audio_data
            )
            
            return compressed
            
        except Exception as e:
            logger.warning(f"動態範圍壓縮失敗: {e}")
            return audio_data
    
    def _enhance_speech_frequencies(self, audio_data) -> any:
        """增強語音頻率範圍（1kHz-4kHz）"""
        try:
            import numpy as np
            
            # 簡化的高頻增強（使用時域方法避免FFT依賴）
            # 實現一個簡單的高通濾波器效果
            if len(audio_data) < 3:
                return audio_data
            
            # 計算差分來增強高頻內容
            diff = np.diff(audio_data, prepend=audio_data[0])
            
            # 將差分與原信號混合，增強高頻
            enhanced = audio_data + diff * 0.2
            
            # 限制幅度
            max_val = np.max(np.abs(enhanced))
            if max_val > 1.0:
                enhanced = enhanced / max_val
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"語音頻率增強失敗: {e}")
            return audio_data
    
    def _soft_limiter(self, audio_data, threshold: float = 0.95) -> any:
        """軟限制器，防止削波"""
        try:
            import numpy as np
            
            # 對超過閾值的部分進行軟限制
            abs_audio = np.abs(audio_data)
            
            # 使用tanh函數進行軟限制
            limited = np.where(
                abs_audio > threshold,
                np.sign(audio_data) * threshold * np.tanh(abs_audio / threshold),
                audio_data
            )
            
            return limited
            
        except Exception as e:
            logger.warning(f"軟限制處理失敗: {e}")
            return audio_data
    
    def _denoise_audio(self, audio_data, sample_rate: int) -> any:
        """輕量級降噪處理"""
        try:
            import numpy as np
            
            # 如果有 noisereduce，優先使用
            if self.noisereduce:
                try:
                    denoised = self.noisereduce.reduce_noise(
                        y=audio_data,
                        sr=sample_rate,
                        stationary=True,
                        prop_decrease=0.6  # 降低強度避免失真
                    )
                    return denoised
                except Exception as e:
                    logger.warning(f"noisereduce 降噪失敗，使用內建算法: {e}")
            
            # 內建輕量級降噪算法
            return self._lightweight_denoise(audio_data)
            
        except Exception as e:
            logger.warning(f"降噪處理失敗: {e}")
            return audio_data
    
    def _lightweight_denoise(self, audio_data) -> any:
        """輕量級降噪算法"""
        try:
            import numpy as np
            
            # 1. 簡單的靜音部分降噪
            audio_data = self._reduce_silence_noise(audio_data)
            
            # 2. 平滑濾波減少高頻噪聲
            audio_data = self._smooth_filter(audio_data)
            
            # 3. 動態門限降噪
            audio_data = self._gate_noise(audio_data)
            
            return audio_data
            
        except Exception as e:
            logger.warning(f"輕量級降噪失敗: {e}")
            return audio_data
    
    def _reduce_silence_noise(self, audio_data) -> any:
        """減少靜音部分的噪聲"""
        try:
            import numpy as np
            
            # 計算移動平均來檢測靜音部分
            window_size = min(512, len(audio_data) // 10)
            if window_size < 10:
                return audio_data
            
            # 計算音頻能量
            energy = np.abs(audio_data)
            
            # 移動平均平滑
            padded_energy = np.pad(energy, window_size//2, mode='edge')
            smooth_energy = np.convolve(padded_energy, np.ones(window_size)/window_size, mode='valid')
            
            # 檢測靜音閾值
            noise_threshold = np.percentile(smooth_energy, 25)  # 前25%作為噪聲水平
            
            # 對靜音部分進行降噪
            noise_mask = smooth_energy < noise_threshold
            reduction_factor = 0.3  # 降噪係數
            
            denoised = audio_data.copy()
            denoised[noise_mask] *= reduction_factor
            
            return denoised
            
        except Exception as e:
            logger.warning(f"靜音降噪失敗: {e}")
            return audio_data
    
    def _smooth_filter(self, audio_data) -> any:
        """平滑濾波器"""
        try:
            import numpy as np
            
            if len(audio_data) < 5:
                return audio_data
            
            # 使用3點移動平均進行輕度平滑
            kernel = np.array([0.25, 0.5, 0.25])
            
            # 對音頻進行卷積平滑
            smoothed = np.convolve(audio_data, kernel, mode='same')
            
            # 混合原始信號和平滑信號
            mix_ratio = 0.7  # 70%原始信號，30%平滑信號
            result = audio_data * mix_ratio + smoothed * (1 - mix_ratio)
            
            return result
            
        except Exception as e:
            logger.warning(f"平滑濾波失敗: {e}")
            return audio_data
    
    def _gate_noise(self, audio_data) -> any:
        """動態門限降噪"""
        try:
            import numpy as np
            
            # 計算音頻的RMS能量
            window_size = min(1024, len(audio_data) // 20)
            if window_size < 10:
                return audio_data
            
            # 滑動窗口RMS計算
            rms_values = []
            for i in range(0, len(audio_data) - window_size, window_size // 2):
                window = audio_data[i:i + window_size]
                rms = np.sqrt(np.mean(window ** 2))
                rms_values.append(rms)
            
            if not rms_values:
                return audio_data
            
            # 設定門限
            noise_floor = np.percentile(rms_values, 30)
            gate_threshold = noise_floor * 2.0
            
            # 應用門限
            gated = audio_data.copy()
            
            # 計算每個樣本的局部RMS
            for i in range(len(audio_data)):
                start = max(0, i - window_size // 2)
                end = min(len(audio_data), i + window_size // 2)
                local_rms = np.sqrt(np.mean(audio_data[start:end] ** 2))
                
                if local_rms < gate_threshold:
                    # 對低於門限的部分進行衰減
                    gated[i] *= 0.4
                    
            return gated
            
        except Exception as e:
            logger.warning(f"門限降噪失敗: {e}")
            return audio_data
    
    def _save_processed_audio(self, audio_data, sample_rate: int) -> str:
        """保存處理後的音頻"""
        try:
            # 創建臨時文件
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "processed_audio.wav")
            
            # 保存音頻
            self.soundfile.write(
                temp_path,
                audio_data,
                sample_rate,
                format='WAV',
                subtype='PCM_16'
            )
            
            return temp_path
            
        except Exception as e:
            logger.error(f"保存音頻失敗: {e}")
            raise
    
    def cleanup_temp_files(self):
        """清理臨時文件"""
        try:
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "processed_audio.wav")
            
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info("臨時音頻文件已清理")
                
        except Exception as e:
            logger.warning(f"清理臨時文件失敗: {e}")
    
    def get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        """獲取音頻信息"""
        try:
            if not self.librosa:
                return {"error": "音頻處理庫不可用"}
            
            # 載入音頻（只載入前10秒用於分析）
            y, sr = self.librosa.load(audio_path, duration=10.0)
            
            # 獲取完整時長
            duration = self.librosa.get_duration(path=audio_path)
            
            return {
                "duration": duration,
                "sample_rate": sr,
                "channels": 1,  # librosa 默認轉為單聲道
                "format": Path(audio_path).suffix.lower()
            }
            
        except Exception as e:
            logger.error(f"獲取音頻信息失敗: {e}")
            return {"error": str(e)}
    
    def _enhance_audio(self, audio_data, sample_rate):
        """
        音頻增強處理 - 提升語音識別準確度
        """
        try:
            import numpy as np
            
            # 1. 頻率域濾波 - 保留語音頻段
            audio_data = self._frequency_filter(audio_data, sample_rate)
            
            # 2. 動態範圍壓縮 - 平衡音量
            audio_data = self._advanced_compression(audio_data)
            
            # 3. 語音頻率增強 - 突出人聲特徵
            audio_data = self._speech_enhancement(audio_data, sample_rate)
            
            # 4. 軟限制器 - 防止削峰
            audio_data = self._soft_limiter(audio_data)
            
            logger.info("音頻增強處理完成")
            return audio_data
            
        except Exception as e:
            logger.warning(f"音頻增強失敗，使用原始音頻: {e}")
            return audio_data
    
    def _frequency_filter(self, audio_data, sample_rate):
        """頻率域濾波 - 保留語音重要頻段"""
        try:
            if not self.scipy_signal:
                return audio_data
                
            import numpy as np
            
            # 設計帶通濾波器保留語音頻段 (80Hz - 8000Hz)
            nyquist = sample_rate / 2
            low_freq = self.enhancement_params['low_freq_cut'] / nyquist
            high_freq = self.enhancement_params['high_freq_cut'] / nyquist
            
            # 使用巴特沃斯濾波器
            b, a = self.scipy_signal.butter(4, [low_freq, high_freq], btype='band')
            filtered_audio = self.scipy_signal.filtfilt(b, a, audio_data)
            
            return filtered_audio
            
        except Exception as e:
            logger.warning(f"頻率濾波失敗: {e}")
            return audio_data
    
    def _advanced_compression(self, audio_data):
        """高級動態範圍壓縮"""
        try:
            import numpy as np
            
            # 轉換為dB
            audio_db = 20 * np.log10(np.abs(audio_data) + 1e-10)
            
            # 壓縮器參數
            threshold = self.enhancement_params['compressor_threshold']
            ratio = self.enhancement_params['compressor_ratio']
            
            # 計算增益縮減
            gain_reduction = np.where(
                audio_db > threshold,
                (audio_db - threshold) / ratio + threshold - audio_db,
                0
            )
            
            # 應用壓縮
            compressed_db = audio_db + gain_reduction
            compressed_audio = np.sign(audio_data) * np.power(10, compressed_db / 20)
            
            return compressed_audio
            
        except Exception as e:
            logger.warning(f"動態壓縮失敗: {e}")
            return audio_data
    
    def _speech_enhancement(self, audio_data, sample_rate):
        """語音頻率增強"""
        try:
            if not self.scipy_signal:
                return audio_data
                
            import numpy as np
            
            # 設計語音頻率增強濾波器 (1kHz - 4kHz)
            nyquist = sample_rate / 2
            center_freq = 2500 / nyquist  # 語音核心頻率
            Q = 2.0  # 品質因子
            
            # 創建峰值濾波器
            w0 = 2 * np.pi * center_freq
            alpha = np.sin(w0) / (2 * Q)
            
            # 峰值濾波器係數
            gain_db = 3  # 增益3dB
            A = np.power(10, gain_db / 40)
            
            b0 = 1 + alpha * A
            b1 = -2 * np.cos(w0)
            b2 = 1 - alpha * A
            a0 = 1 + alpha / A
            a1 = -2 * np.cos(w0)
            a2 = 1 - alpha / A
            
            b = np.array([b0, b1, b2]) / a0
            a = np.array([1, a1/a0, a2/a0])
            
            enhanced_audio = self.scipy_signal.filtfilt(b, a, audio_data)
            
            return enhanced_audio
            
        except Exception as e:
            logger.warning(f"語音增強失敗: {e}")
            return audio_data
    
    def _soft_limiter(self, audio_data):
        """軟限制器 - 防止削峰並保持動態"""
        try:
            import numpy as np
            
            threshold = self.enhancement_params['limiter_threshold']
            
            # 軟限制函數（雙曲正切）
            limited_audio = np.tanh(audio_data / threshold) * threshold
            
            return limited_audio
            
        except Exception as e:
            logger.warning(f"軟限制失敗: {e}")
            return audio_data