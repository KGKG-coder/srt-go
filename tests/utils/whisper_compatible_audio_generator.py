#!/usr/bin/env python3
"""
Whisper相容的語音測試音頻生成器
生成能夠通過Whisper VAD和語音識別的測試音頻
"""

import numpy as np
import wave
from pathlib import Path
from typing import Tuple, Optional
import tempfile

class WhisperCompatibleAudioGenerator:
    """生成Whisper相容的測試音頻"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
    
    def generate_whisper_speech_audio(self, 
                                    duration: float = 5.0,
                                    words_per_minute: int = 120,
                                    language_hint: str = 'en') -> np.ndarray:
        """
        生成Whisper能夠識別的語音模式 - 增強版本以提高識別信心度
        
        Args:
            duration: 音頻長度（秒）
            words_per_minute: 語速（每分鐘字數）
            language_hint: 語言提示
        """
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # 基於語言特徵設置頻率參數 - 使用更精確的語音參數
        if language_hint == 'zh':
            # 中文語音特徵
            fundamental_base = 180.0  # 較高基頻
            formants = (600, 900, 2200)  # 中文共振峰
            pitch_variation = 0.3  # 聲調變化
        elif language_hint == 'ja':
            # 日文語音特徵
            fundamental_base = 160.0
            formants = (700, 1100, 2100)
            pitch_variation = 0.15
        else:
            # 英文語音特徵（默認）- 增強參數提高識別率
            fundamental_base = 120.0  # 降低基頻更接近真實語音
            formants = (700, 1220, 2600)  # 更精確的英語共振峰
            pitch_variation = 0.25  # 增加自然的音調變化
        
        # 1. 創建類似語音的韻律模式
        # 計算大致的音節數量
        syllables_per_minute = words_per_minute * 2.3  # 英語平均每個詞2.3音節
        syllable_rate = syllables_per_minute / 60.0  # 每秒音節數
        total_syllables = int(duration * syllable_rate)
        
        # 生成音節時間點
        syllable_times = np.linspace(0.1, duration - 0.1, total_syllables)
        
        # 2. 生成基頻變化（模擬語調）
        fundamental_freq = np.ones(samples) * fundamental_base
        
        # 添加語調變化
        for i, syllable_time in enumerate(syllable_times):
            # 每個音節的基頻變化
            syllable_start = int(syllable_time * self.sample_rate)
            syllable_duration = int(0.3 * self.sample_rate)  # 300ms音節
            syllable_end = min(syllable_start + syllable_duration, samples)
            
            if syllable_end > syllable_start:
                # 創建音節內的基頻變化
                syllable_length = syllable_end - syllable_start
                syllable_t = np.linspace(0, 1, syllable_length)
                
                # 隨機語調模式
                pitch_pattern = np.random.choice(['rising', 'falling', 'level', 'dip'])
                
                if pitch_pattern == 'rising':
                    pitch_mod = 1 + pitch_variation * syllable_t
                elif pitch_pattern == 'falling':
                    pitch_mod = 1 + pitch_variation * (1 - syllable_t)
                elif pitch_pattern == 'dip':
                    pitch_mod = 1 + pitch_variation * np.sin(np.pi * syllable_t)
                else:  # level
                    pitch_mod = np.ones(syllable_length)
                
                fundamental_freq[syllable_start:syllable_end] *= pitch_mod
        
        # 3. 生成基頻信號
        phase = np.cumsum(2 * np.pi * fundamental_freq / self.sample_rate)
        fundamental_signal = np.sin(phase)
        
        # 4. 添加共振峰
        speech_signal = fundamental_signal * 0.4  # 基頻成分
        
        for formant_freq in formants:
            # 每個共振峰都有帶寬和衰減
            bandwidth = formant_freq * 0.1  # 10%帶寬
            formant_env = np.exp(-0.5 * ((t - duration/2) / (duration/4))**2)  # 高斯包絡
            
            formant_signal = (
                0.3 * np.sin(2 * np.pi * formant_freq * t) * formant_env +
                0.1 * np.sin(2 * np.pi * (formant_freq + bandwidth/2) * t) * formant_env +
                0.1 * np.sin(2 * np.pi * (formant_freq - bandwidth/2) * t) * formant_env
            )
            
            speech_signal += formant_signal
        
        # 5. 添加更真實的語音間歇和呼吸音
        # 創建基於音節的語音活動模式
        voice_activity = np.ones(samples)
        
        # 添加更自然的詞間停頓（基於音節位置）
        pause_positions = []
        for i, syllable_time in enumerate(syllable_times[::3]):  # 每3個音節一個停頓
            pause_pos = int(syllable_time * self.sample_rate)
            if pause_pos > int(0.3 * self.sample_rate) and pause_pos < samples - int(0.3 * self.sample_rate):
                pause_positions.append(pause_pos)
        
        for pause_pos in pause_positions:
            pause_duration = np.random.randint(400, 1200)  # 0.025-0.075秒自然停頓
            pause_start = pause_pos
            pause_end = min(pause_pos + pause_duration, samples)
            # 不完全靜音，保持低水平的呼吸音
            fade_in_length = min(200, pause_duration // 3)
            fade_out_length = min(200, pause_duration // 3)
            
            pause_envelope = np.ones(pause_end - pause_start) * 0.15
            if len(pause_envelope) > fade_in_length + fade_out_length:
                pause_envelope[:fade_in_length] = np.linspace(1.0, 0.15, fade_in_length)
                pause_envelope[-fade_out_length:] = np.linspace(0.15, 1.0, fade_out_length)
            
            voice_activity[pause_start:pause_end] *= pause_envelope
        
        # 6. 添加語音噪音（呼吸、摩擦音等）
        # 這是關鍵 - Whisper需要這些細節來識別為語音
        speech_noise = np.random.normal(0, 0.02, samples)
        
        # 過濾噪音到語音頻率範圍
        speech_noise = self._enhanced_bandpass_filter(speech_noise, 80, 8000)
        
        # 7. 添加微小的harmonics（諧波）
        for harmonic in range(2, 6):  # 2到5次諧波
            harmonic_strength = 0.1 / harmonic
            harmonic_signal = harmonic_strength * np.sin(phase * harmonic)
            speech_signal += harmonic_signal
        
        # 8. 添加真實語音的嘶嘶聲和呼吸音（關鍵改進）
        # 這些高頻成分對 Whisper 識別信心度至關重要
        fricative_noise = np.random.normal(0, 0.05, samples)
        fricative_noise = self._enhanced_bandpass_filter(fricative_noise, 2000, 8000)
        
        # 呼吸音和咝音
        breath_noise = np.random.normal(0, 0.03, samples)
        breath_noise = self._enhanced_bandpass_filter(breath_noise, 50, 500)
        
        # 9. 組合所有成分 - 增加語音噪音比例
        final_audio = (speech_signal + 0.4 * speech_noise + 0.2 * fricative_noise + 0.1 * breath_noise) * voice_activity
        
        # 10. 應用語音包絡（重要：模擬自然語音的振幅變化）
        envelope = self._create_realistic_speech_envelope(t, syllable_times)
        final_audio *= envelope
        
        # 11. 添加語音顫抖（Jitter）和震顫（Shimmer）- 真實語音的特徵
        jitter = np.random.normal(1.0, 0.02, samples)  # 頻率抖動
        shimmer = np.random.normal(1.0, 0.03, samples)  # 振幅抖動
        final_audio *= jitter * shimmer
        
        # 12. 最終處理 - 更強的動態壓縮
        # 添加subtle DC偏移（某些音頻格式的特徵）
        final_audio += np.random.normal(0, 0.002, samples)
        
        # 更強的壓縮效果，模擬人聲的自然壓縮
        final_audio = np.tanh(final_audio * 1.5) * 0.9
        
        # 正規化並增加整體響度
        max_val = np.max(np.abs(final_audio))
        if max_val > 0:
            final_audio = final_audio / max_val * 0.95  # 更高的響度
        
        return final_audio.astype(np.float32)
    
    def _enhanced_bandpass_filter(self, signal: np.ndarray, low_freq: float, high_freq: float) -> np.ndarray:
        """增強的帶通濾波器"""
        fft = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(signal), 1/self.sample_rate)
        
        # 創建更平滑的濾波器響應
        mask = np.zeros_like(freqs, dtype=float)
        
        # 漸進式濾波器
        for i, freq in enumerate(np.abs(freqs)):
            if low_freq <= freq <= high_freq:
                mask[i] = 1.0
            elif low_freq * 0.8 <= freq < low_freq:
                # 低頻漸降
                mask[i] = (freq - low_freq * 0.8) / (low_freq * 0.2)
            elif high_freq < freq <= high_freq * 1.2:
                # 高頻漸降  
                mask[i] = 1.0 - (freq - high_freq) / (high_freq * 0.2)
        
        fft *= mask
        return np.real(np.fft.ifft(fft))
    
    def _create_realistic_speech_envelope(self, t: np.ndarray, syllable_times: np.ndarray) -> np.ndarray:
        """創建更真實的語音包絡 - 增強版"""
        envelope = np.zeros_like(t)
        
        for i, syllable_time in enumerate(syllable_times):
            # 每個音節的包絡 - 更自然的時間分布
            syllable_start = syllable_time - 0.08
            syllable_end = syllable_time + 0.25  # 稍微延長音節長度
            
            # 在時間軸上找到對應的樣本點
            start_idx = np.searchsorted(t, syllable_start)
            end_idx = np.searchsorted(t, syllable_end)
            
            if end_idx > start_idx:
                syllable_length = end_idx - start_idx
                syllable_t = np.linspace(0, 1, syllable_length)
                
                # 音節包絡形狀（更自然的ADSR包絡）
                attack_time = 0.05   # 5%攻擊時間 - 更快攻擊
                decay_time = 0.15    # 15%衰減時間
                sustain_level = 0.8  # 80%保持水平
                release_time = 0.8   # 80%釋放時間
                
                attack_samples = int(attack_time * syllable_length)
                decay_samples = int(decay_time * syllable_length)
                release_start = int((1 - release_time) * syllable_length)
                
                syllable_envelope = np.ones(syllable_length) * sustain_level
                
                # 攻擊段 - 快速上升
                if attack_samples > 0:
                    syllable_envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
                
                # 衰減段 - 衰減到保持水平
                if decay_samples > 0 and attack_samples + decay_samples < syllable_length:
                    decay_end = attack_samples + decay_samples
                    syllable_envelope[attack_samples:decay_end] = np.linspace(1, sustain_level, decay_samples)
                
                # 釋放段 - 緩慢衰減
                if release_start < syllable_length:
                    release_samples = syllable_length - release_start
                    # 使用指數衰減曲線
                    decay_curve = np.exp(-2 * np.linspace(0, 1, release_samples))
                    syllable_envelope[release_start:] *= decay_curve * sustain_level
                
                # 添加微妙的隨機變化（模擬自然語音的不規律性）
                random_modulation = 0.9 + 0.2 * np.random.random()
                syllable_envelope *= random_modulation
                
                # 應用到總包絡（疊加效果）
                envelope[start_idx:end_idx] = np.maximum(
                    envelope[start_idx:end_idx], 
                    syllable_envelope
                )
        
        # 平滑包絡
        window_size = int(0.01 * self.sample_rate)  # 10ms平滑窗口
        if window_size > 1:
            # 簡單的移動平均
            kernel = np.ones(window_size) / window_size
            envelope = np.convolve(envelope, kernel, mode='same')
        
        # 確保包絡在合理範圍內
        envelope = np.clip(envelope, 0.0, 1.0)
        
        # 整體淡入淡出
        fade_samples = int(0.05 * len(t))  # 50ms淡入淡出
        if len(envelope) > 2 * fade_samples:
            envelope[:fade_samples] *= np.linspace(0, 1, fade_samples)
            envelope[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        
        return envelope

def create_whisper_test_audio(output_dir: Optional[str] = None) -> dict:
    """
    創建Whisper相容的測試音頻文件
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="whisper_test_audio_")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    generator = WhisperCompatibleAudioGenerator()
    audio_files = {}
    
    # 生成英語語音樣本
    english_speech = generator.generate_whisper_speech_audio(
        duration=5.0, 
        words_per_minute=120, 
        language_hint='en'
    )
    en_path = output_dir / "whisper_speech_english.wav"
    if save_audio_wav(english_speech, str(en_path)):
        audio_files['english_speech'] = str(en_path)
    
    # 生成中文語音樣本
    chinese_speech = generator.generate_whisper_speech_audio(
        duration=5.0,
        words_per_minute=100,  # 中文語速稍慢
        language_hint='zh'
    )
    zh_path = output_dir / "whisper_speech_chinese.wav"
    if save_audio_wav(chinese_speech, str(zh_path)):
        audio_files['chinese_speech'] = str(zh_path)
    
    # 生成短語音（邊界測試）
    short_speech = generator.generate_whisper_speech_audio(
        duration=2.0,
        words_per_minute=150,
        language_hint='en'
    )
    short_path = output_dir / "whisper_speech_short.wav"
    if save_audio_wav(short_speech, str(short_path)):
        audio_files['short_speech'] = str(short_path)
    
    print(f"Created {len(audio_files)} Whisper-compatible test audio files at: {output_dir}")
    for name, path in audio_files.items():
        file_size = Path(path).stat().st_size / 1024  # KB
        print(f"   {name}: {Path(path).name} ({file_size:.1f} KB)")
    
    return audio_files

def save_audio_wav(audio: np.ndarray, output_path: str, sample_rate: int = 16000) -> bool:
    """保存音頻到WAV文件"""
    try:
        with wave.open(output_path, 'wb') as wav:
            wav.setnchannels(1)  # 單聲道
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(sample_rate)
            
            # 轉換為16-bit整數
            audio_int16 = (audio * 32767).astype(np.int16)
            wav.writeframes(audio_int16.tobytes())
        
        return True
    except Exception as e:
        print(f"Failed to save audio: {e}")
        return False

if __name__ == "__main__":
    # 測試Whisper相容的音頻生成器
    test_files = create_whisper_test_audio()
    
    # 驗證生成的音頻特徵
    print("\nVerifying Whisper-compatible speech features:")
    
    generator = WhisperCompatibleAudioGenerator()
    
    # 分析英語樣本
    english_audio_path = test_files.get('english_speech')
    if english_audio_path:
        with wave.open(english_audio_path, 'rb') as wav:
            frames = wav.readframes(wav.getnframes())
            audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32767
        
        # Whisper特徵驗證
        # 1. 能量分布
        energy = np.mean(audio_data ** 2)
        print(f"   Audio energy: {energy:.6f} (target: > 0.01)")
        
        # 2. 語音活動檢測指標
        # 計算非靜音部分比例
        energy_threshold = np.max(audio_data ** 2) * 0.01  # 1%的峰值作為閾值
        voice_activity = np.sum(audio_data ** 2 > energy_threshold) / len(audio_data)
        print(f"   Voice activity ratio: {voice_activity:.3f} (target: > 0.3)")
        
        # 3. 頻譜特徵
        fft = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(audio_data), 1/16000)
        power_spectrum = np.abs(fft) ** 2
        
        # 語音核心頻率範圍能量
        speech_core_range = (np.abs(freqs) >= 300) & (np.abs(freqs) <= 3000)
        core_energy_ratio = np.sum(power_spectrum[speech_core_range]) / np.sum(power_spectrum)
        print(f"   Core speech frequency ratio: {core_energy_ratio:.3f} (target: > 0.4)")
        
        # 4. 動態範圍
        dynamic_range = np.max(audio_data) - np.min(audio_data)
        print(f"   Dynamic range: {dynamic_range:.3f} (target: > 0.1)")
        
        # 判斷是否可能通過Whisper VAD
        whisper_compatible = (
            energy > 0.01 and 
            voice_activity > 0.3 and 
            core_energy_ratio > 0.4 and
            dynamic_range > 0.1
        )
        print(f"   Whisper VAD compatibility: {'LIKELY PASS' if whisper_compatible else 'MAY FAIL'}")