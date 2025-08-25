"""
音頻處理器單元測試
測試音頻預處理的所有功能
"""

import pytest
import numpy as np
from pathlib import Path
import sys

# 導入測試模組
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "python"))
from audio_processor import AudioProcessor

class TestAudioProcessor:
    """音頻處理器測試類"""
    
    @pytest.fixture
    def processor(self):
        """創建音頻處理器實例"""
        return AudioProcessor()
    
    @pytest.fixture
    def sample_audio(self):
        """創建樣本音頻數據"""
        # 16kHz, 5秒
        duration = 5.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # 混合信號：語音頻率 + 噪音
        speech_freq = np.sin(2 * np.pi * 440 * t)  # 440Hz (語音範圍)
        noise = np.random.normal(0, 0.1, len(t))   # 高斯噪音
        
        return speech_freq + noise, sample_rate
    
    def test_initialization(self, processor):
        """測試初始化"""
        assert processor is not None
        assert hasattr(processor, 'target_sample_rate')
        assert processor.target_sample_rate == 16000
    
    def test_dynamic_range_compression(self, processor, sample_audio):
        """測試動態範圍壓縮"""
        audio, sr = sample_audio
        
        # 添加一些極端值
        audio[100:200] = 5.0  # 高峰值
        audio[500:600] = -5.0  # 低谷值
        
        compressed = processor.compress_dynamic_range(audio)
        
        # 驗證壓縮效果
        assert compressed.max() < audio.max()
        assert compressed.min() > audio.min()
        assert compressed.std() < audio.std()
        
        # 確保沒有削波
        assert np.all(np.abs(compressed) <= 1.0)
    
    def test_speech_frequency_enhancement(self, processor, sample_audio):
        """測試語音頻率增強"""
        audio, sr = sample_audio
        
        enhanced = processor.enhance_speech_frequencies(audio, sr)
        
        # 計算頻譜能量
        from scipy import signal
        
        # 原始信號頻譜
        f_orig, pxx_orig = signal.periodogram(audio, sr)
        # 增強後頻譜
        f_enh, pxx_enh = signal.periodogram(enhanced, sr)
        
        # 語音頻率範圍 (300-3000 Hz)
        speech_range = (f_enh >= 300) & (f_enh <= 3000)
        
        # 語音頻率能量應該增加
        speech_energy_orig = np.sum(pxx_orig[speech_range])
        speech_energy_enh = np.sum(pxx_enh[speech_range])
        
        assert speech_energy_enh > speech_energy_orig * 1.1  # 至少增加10%
    
    def test_denoise(self, processor):
        """測試降噪功能"""
        # 創建含噪音的音頻
        duration = 2.0
        sr = 16000
        t = np.linspace(0, duration, int(sr * duration))
        
        # 純淨語音信號
        clean_signal = np.sin(2 * np.pi * 440 * t)
        # 添加強噪音
        noise = np.random.normal(0, 0.5, len(t))
        noisy_signal = clean_signal + noise
        
        # 降噪
        denoised = processor.denoise(noisy_signal, sr)
        
        # 計算信噪比改善
        def calculate_snr(signal, noise):
            signal_power = np.mean(signal ** 2)
            noise_power = np.mean(noise ** 2)
            return 10 * np.log10(signal_power / noise_power)
        
        snr_before = calculate_snr(clean_signal, noisy_signal - clean_signal)
        snr_after = calculate_snr(clean_signal, denoised - clean_signal)
        
        # SNR 應該有所改善
        assert snr_after > snr_before
    
    @pytest.mark.parametrize("sample_rate", [8000, 16000, 22050, 44100, 48000])
    def test_resample(self, processor, sample_rate):
        """測試重採樣功能"""
        duration = 1.0
        samples = int(sample_rate * duration)
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples))
        
        # 重採樣到目標採樣率
        resampled = processor.resample(audio, sample_rate, processor.target_sample_rate)
        
        # 驗證輸出長度
        expected_length = int(samples * processor.target_sample_rate / sample_rate)
        assert abs(len(resampled) - expected_length) <= 1  # 允許1個樣本的誤差
    
    def test_normalize_audio(self, processor):
        """測試音頻正規化"""
        # 創建不同振幅的音頻
        audio_quiet = np.random.randn(16000) * 0.01  # 很小聲
        audio_loud = np.random.randn(16000) * 10.0   # 很大聲
        
        normalized_quiet = processor.normalize_audio(audio_quiet)
        normalized_loud = processor.normalize_audio(audio_loud)
        
        # 兩者應該有相似的峰值
        assert abs(normalized_quiet.max() - normalized_loud.max()) < 0.2
        
        # 峰值應該接近但不超過1.0
        assert 0.8 < normalized_quiet.max() <= 1.0
        assert 0.8 < normalized_loud.max() <= 1.0
    
    def test_remove_silence(self, processor):
        """測試靜音移除"""
        sr = 16000
        
        # 創建包含靜音段的音頻
        speech = np.sin(2 * np.pi * 440 * np.linspace(0, 1, sr))
        silence = np.zeros(sr)
        
        # 語音-靜音-語音 模式
        audio = np.concatenate([speech, silence, speech])
        
        # 移除靜音
        trimmed = processor.remove_silence(audio, sr, threshold=0.01)
        
        # 應該移除中間的靜音
        assert len(trimmed) < len(audio)
        assert len(trimmed) > len(speech)  # 但不應該完全移除
    
    def test_process_audio_pipeline(self, processor, mock_audio_file):
        """測試完整的音頻處理管道"""
        # 處理完整音頻檔案
        processed = processor.process_audio_file(str(mock_audio_file))
        
        assert processed is not None
        assert len(processed) > 0
        assert processed.dtype == np.float32
        assert np.all(np.abs(processed) <= 1.0)
    
    @pytest.mark.performance
    def test_processing_speed(self, processor, sample_audio, performance_monitor):
        """測試處理速度"""
        audio, sr = sample_audio
        
        performance_monitor.start()
        
        # 執行所有處理步驟
        for _ in range(10):  # 處理10次以獲得平均值
            _ = processor.compress_dynamic_range(audio)
            _ = processor.enhance_speech_frequencies(audio, sr)
            _ = processor.denoise(audio, sr)
            _ = processor.normalize_audio(audio)
        
        metrics = performance_monitor.stop()
        
        # 驗證效能
        avg_time = metrics['elapsed_time'] / 10
        assert avg_time < 0.5  # 每次處理應該小於0.5秒
        assert metrics['memory_used'] < 100  # 記憶體使用小於100MB
    
    def test_edge_cases(self, processor):
        """測試邊界情況"""
        # 空音頻
        empty_audio = np.array([])
        result = processor.normalize_audio(empty_audio)
        assert len(result) == 0
        
        # 全靜音
        silence = np.zeros(16000)
        result = processor.normalize_audio(silence)
        assert np.all(result == 0)
        
        # 單一樣本
        single = np.array([1.0])
        result = processor.process_audio(single, 16000)
        assert result is not None
        
        # 極長音頻 (1小時)
        long_audio = np.random.randn(16000 * 3600)
        result = processor.compress_dynamic_range(long_audio)
        assert len(result) == len(long_audio)