"""
SRT GO v2.2.1 統一測試配置
Unified Test Configuration - pytest 全域配置和共用 fixtures

提供所有測試的共用fixtures、配置和工具函數
Provides shared fixtures, configurations, and utility functions for all tests.
"""

import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path
import json
import numpy as np
from unittest.mock import Mock, MagicMock
import asyncio

# 將專案路徑加入 Python 路徑
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "srt_whisper_lite" / "electron-react-app"))
sys.path.insert(0, str(PROJECT_ROOT / "srt_whisper_lite" / "electron-react-app" / "python"))

# 測試資料目錄
TEST_DATA_DIR = Path(__file__).parent / "fixtures"
AUDIO_SAMPLES_DIR = TEST_DATA_DIR / "audio_samples"
VIDEO_SAMPLES_DIR = TEST_DATA_DIR / "video_samples"
EXPECTED_OUTPUTS_DIR = TEST_DATA_DIR / "expected_outputs"

# ==================== 全域 Fixtures ====================

@pytest.fixture(scope="session")
def test_config():
    """測試配置"""
    return {
        "model": "medium",  # 使用較小模型加速測試
        "language": "auto",
        "enable_gpu": False,
        "enablePureVoiceMode": True,
        "vad_threshold": 0.35,
        "test_timeout": 60,  # 秒
        "max_file_size": 100 * 1024 * 1024,  # 100MB
    }

@pytest.fixture(scope="session")
def temp_dir():
    """創建臨時測試目錄"""
    temp_path = tempfile.mkdtemp(prefix="srt_go_test_")
    yield Path(temp_path)
    # 清理
    shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def mock_audio_file(temp_dir):
    """創建模擬音頻檔案"""
    audio_file = temp_dir / "test_audio.wav"
    # 創建1秒的靜音音頻
    sample_rate = 16000
    duration = 1.0
    samples = int(sample_rate * duration)
    audio_data = np.zeros(samples, dtype=np.float32)
    
    # 模擬寫入WAV檔案
    import wave
    with wave.open(str(audio_file), 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes((audio_data * 32767).astype(np.int16).tobytes())
    
    return audio_file

@pytest.fixture
def mock_video_file(temp_dir):
    """創建模擬視頻檔案"""
    video_file = temp_dir / "test_video.mp4"
    # 創建一個小的測試視頻檔案
    video_file.write_bytes(b"fake_video_content")
    return video_file

@pytest.fixture
def mock_whisper_model():
    """模擬 Whisper 模型"""
    model = MagicMock()
    model.transcribe = MagicMock(return_value={
        "segments": [
            {"start": 0.0, "end": 1.0, "text": "測試文字"},
            {"start": 1.0, "end": 2.0, "text": "Test text"}
        ],
        "language": "zh"
    })
    return model

@pytest.fixture
def mock_ipc_channel():
    """模擬 IPC 通訊通道"""
    class MockIPCChannel:
        def __init__(self):
            self.messages = []
            self.responses = []
        
        async def send(self, message):
            self.messages.append(message)
            return {"type": "success", "data": {}}
        
        async def receive(self):
            if self.responses:
                return self.responses.pop(0)
            return {"type": "progress", "data": {"percentage": 50}}
    
    return MockIPCChannel()

@pytest.fixture
def performance_monitor():
    """效能監控器"""
    import time
    import psutil
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.start_memory = None
            self.process = psutil.Process()
        
        def start(self):
            self.start_time = time.time()
            self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        def stop(self):
            elapsed_time = time.time() - self.start_time
            end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            memory_used = end_memory - self.start_memory
            
            return {
                "elapsed_time": elapsed_time,
                "memory_used": memory_used,
                "cpu_percent": self.process.cpu_percent()
            }
    
    return PerformanceMonitor()

@pytest.fixture
def sample_srt_content():
    """範例 SRT 內容"""
    return """1
00:00:00,000 --> 00:00:01,000
測試字幕第一行

2
00:00:01,000 --> 00:00:02,000
測試字幕第二行

3
00:00:02,000 --> 00:00:03,000
Test subtitle line three
"""

@pytest.fixture
async def async_backend():
    """非同步後端模擬"""
    from electron_backend import ElectronBackend
    backend = ElectronBackend()
    await backend.initialize()
    yield backend
    await backend.cleanup()

# ==================== 測試標記 ====================

def pytest_configure(config):
    """配置自定義標記"""
    config.addinivalue_line(
        "markers", "slow: 標記慢速測試 (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "gpu: 需要 GPU 的測試"
    )
    config.addinivalue_line(
        "markers", "integration: 整合測試"
    )
    config.addinivalue_line(
        "markers", "e2e: 端到端測試"
    )
    config.addinivalue_line(
        "markers", "performance: 效能測試"
    )
    config.addinivalue_line(
        "markers", "security: 安全測試"
    )

# ==================== 測試工具函數 ====================

def create_test_audio(duration=1.0, sample_rate=16000):
    """創建測試音頻數據"""
    samples = int(sample_rate * duration)
    # 創建包含語音頻率的測試信號
    t = np.linspace(0, duration, samples)
    # 模擬語音頻率 (300-3000 Hz)
    signal = np.sin(2 * np.pi * 440 * t)  # 440 Hz
    signal += np.sin(2 * np.pi * 880 * t) * 0.5  # 880 Hz
    signal += np.sin(2 * np.pi * 1320 * t) * 0.3  # 1320 Hz
    return signal.astype(np.float32)

def create_test_segments(count=5):
    """創建測試字幕段落"""
    segments = []
    for i in range(count):
        segments.append({
            "start": float(i),
            "end": float(i + 0.9),
            "text": f"測試段落 {i+1}"
        })
    return segments

def validate_srt_format(content):
    """驗證 SRT 格式"""
    lines = content.strip().split('\n')
    segment_count = 0
    i = 0
    
    while i < len(lines):
        # 序號
        if not lines[i].strip().isdigit():
            return False, f"Invalid sequence number at line {i+1}"
        
        # 時間戳
        i += 1
        if i >= len(lines) or ' --> ' not in lines[i]:
            return False, f"Invalid timestamp at line {i+1}"
        
        # 文字內容
        i += 1
        if i >= len(lines):
            return False, f"Missing text content at line {i+1}"
        
        # 跳過文字行直到空行
        while i < len(lines) and lines[i].strip():
            i += 1
        
        segment_count += 1
        i += 1  # 跳過空行
    
    return True, f"Valid SRT with {segment_count} segments"

# ==================== 測試資料載入器 ====================

class TestDataLoader:
    """測試資料載入器"""
    
    @staticmethod
    def load_audio_sample(name="speech.wav"):
        """載入音頻樣本"""
        file_path = AUDIO_SAMPLES_DIR / name
        if not file_path.exists():
            # 如果檔案不存在，創建測試檔案
            os.makedirs(AUDIO_SAMPLES_DIR, exist_ok=True)
            audio_data = create_test_audio(duration=5.0)
            # 儲存為 WAV
            import wave
            with wave.open(str(file_path), 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(16000)
                wav.writeframes((audio_data * 32767).astype(np.int16).tobytes())
        return file_path
    
    @staticmethod
    def load_expected_output(name="expected.srt"):
        """載入預期輸出"""
        file_path = EXPECTED_OUTPUTS_DIR / name
        if file_path.exists():
            return file_path.read_text(encoding='utf-8')
        return None

# ==================== 效能基準配置 ====================

@pytest.fixture
def benchmark_config():
    """效能基準配置"""
    return {
        "rtf_limit_cpu": 0.8,
        "rtf_limit_gpu": 0.15,
        "memory_limit_mb": 4096,
        "processing_timeout": 300,  # 5分鐘
        "accuracy_threshold": 0.85
    }

# ==================== 測試報告生成 ====================

def pytest_sessionfinish(session, exitstatus):
    """測試會話結束時生成報告"""
    if hasattr(session.config, '_test_results'):
        results = session.config._test_results
        report = {
            "total": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if r.failed),
            "skipped": sum(1 for r in results if r.skipped),
            "duration": sum(r.duration for r in results)
        }
        
        # 儲存報告
        report_path = Path(__file__).parent / "test_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n測試報告已生成: {report_path}")