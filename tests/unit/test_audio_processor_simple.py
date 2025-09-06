"""
音頻處理器簡化單元測試
基於實際的 AudioProcessor 實現
"""

import pytest
import numpy as np
from pathlib import Path
import sys
import tempfile
import wave

# 導入測試模組
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "python"))

# Try to import audio processor with graceful fallback
try:
    from audio_processor import AudioProcessor
    AUDIO_PROCESSOR_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSOR_AVAILABLE = False
    class AudioProcessor:
        def __init__(self, **kwargs):
            self.target_sample_rate = 16000

@pytest.mark.skipif(not AUDIO_PROCESSOR_AVAILABLE, reason="AudioProcessor not available")
class TestAudioProcessorSimple:
    """音頻處理器簡化測試類"""
    
    @pytest.fixture
    def processor(self):
        """創建音頻處理器實例"""
        return AudioProcessor()
    
    @pytest.fixture 
    def sample_audio_file(self, temp_dir):
        """創建樣本音頻檔案"""
        audio_file = temp_dir / "test_sample.wav"
        
        # 創建5秒的測試音頻
        sample_rate = 16000
        duration = 5.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = np.sin(2 * np.pi * 440 * t) * 0.8  # 440Hz正弦波
        
        # 寫入WAV檔案
        with wave.open(str(audio_file), 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes((audio_data * 32767).astype(np.int16).tobytes())
        
        return audio_file
    
    def test_initialization(self, processor):
        """測試初始化"""
        assert processor is not None
        assert hasattr(processor, 'target_sample_rate')
        assert processor.target_sample_rate == 16000
        assert hasattr(processor, 'enable_normalize')
        assert hasattr(processor, 'enable_denoise')
    
    def test_audio_processing_with_librosa(self, processor, sample_audio_file):
        """測試音頻處理（如果有librosa）"""
        if not processor.librosa:
            pytest.skip("librosa not available, skipping audio processing test")
        
        output_path = processor.process_audio(str(sample_audio_file))
        
        # 驗證處理結果
        assert output_path is not None
        assert Path(output_path).exists()
        
        # 檢查檔案大小合理
        assert Path(output_path).stat().st_size > 0
    
    def test_audio_processing_fallback(self, processor, sample_audio_file):
        """測試無librosa時的回退行為"""
        # 暫時禁用librosa來測試回退
        original_librosa = processor.librosa
        processor.librosa = None
        
        try:
            output_path = processor.process_audio(str(sample_audio_file))
            
            # 沒有librosa時應該返回原檔案路徑
            assert output_path == str(sample_audio_file)
        finally:
            processor.librosa = original_librosa
    
    def test_invalid_input_file(self, processor):
        """測試無效輸入檔案"""
        invalid_path = "/path/that/does/not/exist.wav"
        
        output_path = processor.process_audio(invalid_path)
        assert output_path is None
    
    def test_progress_callback(self, processor, sample_audio_file):
        """測試進度回調"""
        if not processor.librosa:
            pytest.skip("librosa not available, skipping progress callback test")
        
        progress_calls = []
        
        def progress_callback(percent, message):
            progress_calls.append((percent, message))
        
        processor.process_audio(str(sample_audio_file), progress_callback=progress_callback)
        
        # 驗證進度回調被調用
        assert len(progress_calls) > 0
        
        # 檢查進度順序
        percentages = [call[0] for call in progress_calls]
        assert percentages == sorted(percentages)  # 進度應該遞增
        
        # 檢查最後一個進度是100%
        assert percentages[-1] == 100
    
    def test_custom_sample_rate(self):
        """測試自定義採樣率"""
        custom_processor = AudioProcessor(target_sample_rate=22050)
        assert custom_processor.target_sample_rate == 22050
    
    def test_configuration_options(self):
        """測試配置選項"""
        processor = AudioProcessor(
            enable_normalize=False,
            enable_denoise=False,
            enable_enhancement=False,
            noise_reduce_strength=0.8
        )
        
        assert not processor.enable_normalize
        assert not processor.enable_denoise  
        assert not processor.enable_enhancement
        assert processor.noise_reduce_strength == 0.8