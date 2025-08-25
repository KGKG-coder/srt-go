#!/usr/bin/env python3
"""
語音特徵測試音頻生成器
生成包含真實語音特徵的測試音頻，用於驗證VAD和整合測試
"""

import numpy as np
import wave
from pathlib import Path
from typing import Tuple, Optional
import tempfile

class SpeechLikeAudioGenerator:
    """生成類似語音特徵的測試音頻"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
    
    def generate_speech_like_audio(self, 
                                 duration: float = 5.0,
                                 fundamental_freq: float = 150.0,
                                 formant_freqs: Tuple[float, ...] = (800, 1200, 2400)) -> np.ndarray:
        """
        生成包含語音特徵的音頻
        
        Args:
            duration: 音頻長度（秒）
            fundamental_freq: 基頻（Hz）- 模擬人聲音高
            formant_freqs: 共振峰頻率（Hz）- 模擬語音腔體共鳴
        
        Returns:
            音頻數據陣列
        """
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # 1. 基頻信號（模擬聲帶振動）
        fundamental = np.sin(2 * np.pi * fundamental_freq * t)
        
        # 2. 共振峰（模擬口腔共鳴）- 語音的關鍵特徵
        formant_signal = np.zeros(samples)
        for formant_freq in formant_freqs:
            # 每個共振峰都有一定的帶寬
            formant_signal += 0.3 * np.sin(2 * np.pi * formant_freq * t) * np.exp(-0.1 * t)
        
        # 3. 頻率調制（模擬自然語調變化）
        freq_modulation = 1 + 0.1 * np.sin(2 * np.pi * 2 * t)  # 2Hz的調制
        modulated_fundamental = fundamental * freq_modulation
        
        # 4. 振幅包絡（模擬語音的音量變化）
        envelope = self._create_speech_envelope(t)
        
        # 5. 添加微量語音噪音（模擬呼吸音、摩擦音等）
        speech_noise = np.random.normal(0, 0.05, samples)
        # 過濾噪音至語音頻率範圍 (100-4000Hz)
        speech_noise = self._bandpass_filter(speech_noise, 100, 4000)
        
        # 6. 組合所有成分
        speech_audio = (modulated_fundamental + formant_signal + 0.2 * speech_noise) * envelope
        
        # 7. 正規化到合理範圍
        max_val = np.max(np.abs(speech_audio))
        if max_val > 0:
            speech_audio = speech_audio / max_val * 0.8  # 避免削波
        
        return speech_audio.astype(np.float32)
    
    def _create_speech_envelope(self, t: np.ndarray) -> np.ndarray:
        """創建語音振幅包絡"""
        # 模擬語音的典型振幅變化模式
        # 使用多個不同頻率的正弦波組合
        envelope = (
            0.7 +  # 基礎音量
            0.2 * np.sin(2 * np.pi * 1.5 * t) +  # 慢變化（句子層級）
            0.1 * np.sin(2 * np.pi * 8 * t)      # 快變化（音節層級）
        )
        
        # 確保包絡為正值且在合理範圍內
        envelope = np.clip(envelope, 0.1, 1.0)
        
        # 添加語音開始和結束的淡入淡出
        fade_samples = int(0.1 * len(t))  # 100ms 淡入淡出
        if len(envelope) > 2 * fade_samples:
            # 淡入
            envelope[:fade_samples] *= np.linspace(0, 1, fade_samples)
            # 淡出
            envelope[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        
        return envelope
    
    def _bandpass_filter(self, signal: np.ndarray, low_freq: float, high_freq: float) -> np.ndarray:
        """簡單的帶通濾波器"""
        # 使用FFT實現簡單的帶通濾波
        fft = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(signal), 1/self.sample_rate)
        
        # 創建帶通遮罩
        mask = (np.abs(freqs) >= low_freq) & (np.abs(freqs) <= high_freq)
        fft[~mask] = 0
        
        return np.real(np.fft.ifft(fft))
    
    def generate_multilingual_samples(self) -> dict:
        """生成多語言特徵的測試音頻"""
        samples = {}
        
        # 中文特徵（較高基頻，特定共振峰）
        samples['chinese'] = self.generate_speech_like_audio(
            duration=3.0,
            fundamental_freq=180.0,  # 中文平均基頻較高
            formant_freqs=(700, 1100, 2300)
        )
        
        # 英文特徵（中等基頻，典型英語共振峰）
        samples['english'] = self.generate_speech_like_audio(
            duration=3.0,
            fundamental_freq=150.0,
            formant_freqs=(800, 1200, 2400)
        )
        
        # 日文特徵（較穩定的基頻，特殊共振峰結構）
        samples['japanese'] = self.generate_speech_like_audio(
            duration=3.0,
            fundamental_freq=160.0,
            formant_freqs=(750, 1150, 2200)
        )
        
        return samples
    
    def save_test_audio(self, audio: np.ndarray, output_path: str) -> bool:
        """保存測試音頻到WAV文件"""
        try:
            with wave.open(output_path, 'wb') as wav:
                wav.setnchannels(1)  # 單聲道
                wav.setsampwidth(2)  # 16-bit
                wav.setframerate(self.sample_rate)
                
                # 轉換為16-bit整數
                audio_int16 = (audio * 32767).astype(np.int16)
                wav.writeframes(audio_int16.tobytes())
            
            return True
        except Exception as e:
            print(f"保存音頻失敗: {e}")
            return False

def create_realistic_test_audio(output_dir: Optional[str] = None) -> dict:
    """
    創建用於測試的真實語音特徵音頻文件
    
    Returns:
        包含音頻文件路徑的字典
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="srt_test_audio_")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    generator = SpeechLikeAudioGenerator()
    audio_files = {}
    
    # 生成基本語音特徵音頻
    basic_speech = generator.generate_speech_like_audio(duration=5.0)
    basic_path = output_dir / "speech_sample.wav"
    if generator.save_test_audio(basic_speech, str(basic_path)):
        audio_files['basic_speech'] = str(basic_path)
    
    # 生成多語言樣本
    multilingual_samples = generator.generate_multilingual_samples()
    for lang, audio in multilingual_samples.items():
        lang_path = output_dir / f"speech_{lang}.wav"
        if generator.save_test_audio(audio, str(lang_path)):
            audio_files[f'speech_{lang}'] = str(lang_path)
    
    # 生成短語音片段（用於邊界測試）
    short_speech = generator.generate_speech_like_audio(duration=0.5)
    short_path = output_dir / "speech_short.wav"
    if generator.save_test_audio(short_speech, str(short_path)):
        audio_files['short_speech'] = str(short_path)
    
    # 生成長語音片段（用於性能測試）
    long_speech = generator.generate_speech_like_audio(duration=30.0)
    long_path = output_dir / "speech_long.wav"
    if generator.save_test_audio(long_speech, str(long_path)):
        audio_files['long_speech'] = str(long_path)
    
    print(f"Created {len(audio_files)} test audio files at: {output_dir}")
    for name, path in audio_files.items():
        file_size = Path(path).stat().st_size / 1024  # KB
        print(f"   {name}: {Path(path).name} ({file_size:.1f} KB)")
    
    return audio_files

if __name__ == "__main__":
    # 測試音頻生成器
    test_files = create_realistic_test_audio()
    
    # 驗證生成的音頻具有語音特徵
    print("\nVerifying speech features of generated audio:")
    
    generator = SpeechLikeAudioGenerator()
    
    # 讀取並分析基本語音樣本
    basic_audio_path = test_files.get('basic_speech')
    if basic_audio_path:
        with wave.open(basic_audio_path, 'rb') as wav:
            frames = wav.readframes(wav.getnframes())
            audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32767
        
        # 簡單的語音特徵驗證
        # 1. 能量檢測
        energy = np.mean(audio_data ** 2)
        print(f"   Audio energy: {energy:.6f} (should be > 0.01)")
        
        # 2. 零交叉率（語音通常較低）
        zero_crossings = np.sum(np.diff(np.sign(audio_data)) != 0) / len(audio_data)
        print(f"   Zero crossing rate: {zero_crossings:.4f} (speech should be < 0.3)")
        
        # 3. 頻譜分析
        fft = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(audio_data), 1/16000)
        power_spectrum = np.abs(fft) ** 2
        
        # 語音頻率範圍的能量分布
        speech_range = (np.abs(freqs) >= 100) & (np.abs(freqs) <= 4000)
        speech_energy = np.sum(power_spectrum[speech_range])
        total_energy = np.sum(power_spectrum)
        speech_ratio = speech_energy / total_energy if total_energy > 0 else 0
        
        print(f"   Speech frequency energy ratio: {speech_ratio:.3f} (should be > 0.6)")
        
        # 判斷是否具有語音特徵
        is_speech_like = (energy > 0.01 and zero_crossings < 0.3 and speech_ratio > 0.6)
        print(f"   Speech feature validation: {'PASS' if is_speech_like else 'FAIL'}")