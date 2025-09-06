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
        self.target_sample_rate = target_sample_rate
        self.enable_normalize = enable_normalize
        self.enable_denoise = enable_denoise
        self.enable_enhancement = enable_enhancement
        self.noise_reduce_strength = noise_reduce_strength
        
        # 檢查可選依賴
        self.librosa = self._load_librosa()
        self.soundfile = self._load_soundfile()
    
    def _load_librosa(self):
        """嘗試載入librosa"""
        try:
            import librosa
            return librosa
        except ImportError:
            logger.info("librosa未安裝，使用基本音頻處理")
            return None
    
    def _load_soundfile(self):
        """嘗試載入soundfile"""
        try:
            import soundfile as sf
            return sf
        except ImportError:
            logger.info("soundfile未安裝，使用基本音頻處理")
            return None
    
    def process_audio(self, input_path: str, output_path: Optional[str] = None, 
                      progress_callback=None) -> Optional[str]:
        """處理音頻文件"""
        try:
            if not os.path.exists(input_path):
                logger.error(f"輸入文件不存在: {input_path}")
                return None
            
            # 如果沒有音頻處理庫，直接返回原文件
            if not self.librosa:
                logger.info("使用原始音頻文件（無預處理）")
                return input_path
            
            if progress_callback:
                progress_callback(10, "開始音頻預處理")
            
            # 載入音頻
            audio, sr = self.librosa.load(input_path, sr=self.target_sample_rate)
            
            if progress_callback:
                progress_callback(50, "音頻處理中")
            
            # 基本正規化
            if self.enable_normalize:
                max_val = max(abs(audio.max()), abs(audio.min()))
                if max_val > 0:
                    audio = audio / max_val * 0.95
            
            # 確定輸出路徑
            if not output_path:
                output_path = self._create_temp_audio_file()
            
            if progress_callback:
                progress_callback(80, "保存處理後的音頻")
            
            # 保存處理後的音頻
            if self.soundfile:
                self.soundfile.write(output_path, audio, self.target_sample_rate)
            else:
                # 備用保存方法
                import scipy.io.wavfile as wav
                wav.write(output_path, self.target_sample_rate, (audio * 32767).astype('int16'))
            
            if progress_callback:
                progress_callback(100, "音頻預處理完成")
            
            return output_path
            
        except Exception as e:
            logger.error(f"音頻處理失敗: {e}")
            return input_path  # 處理失敗時返回原文件
    
    def _create_temp_audio_file(self) -> str:
        """創建臨時音頻文件"""
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"processed_audio_{os.getpid()}.wav")
        return temp_file