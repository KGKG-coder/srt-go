# 商用級測試架構 - SRT GO v2.2.1

## 📋 測試策略總覽

### 測試金字塔架構
```
         ╔═══════════════╗
         ║   E2E Tests   ║  10% - 端到端測試
         ╠═══════════════╣
       ║ Integration Tests ║  30% - 整合測試
       ╠═══════════════════╣
     ║    Unit Tests       ║  60% - 單元測試
     ╚═══════════════════════╝
```

### 測試覆蓋率目標
- **總體覆蓋率**: ≥ 85%
- **核心功能覆蓋率**: ≥ 95%
- **關鍵路徑覆蓋率**: 100%
- **錯誤處理覆蓋率**: ≥ 90%

## 🏗️ 測試框架架構

### 1. 技術堆疊
```yaml
Python測試:
  - pytest: 主要測試框架
  - pytest-cov: 覆蓋率報告
  - pytest-xdist: 並行測試
  - pytest-benchmark: 效能測試
  - pytest-mock: Mock框架
  - pytest-asyncio: 異步測試

JavaScript測試:
  - Jest: 單元測試
  - Playwright: E2E測試
  - React Testing Library: 組件測試
  - Electron Playwright: Electron應用測試

效能測試:
  - Locust: 負載測試
  - memory_profiler: 記憶體分析
  - line_profiler: 程式碼效能分析
```

### 2. 測試分層架構

```
tests/
├── unit/                      # 單元測試
│   ├── test_audio_processor.py
│   ├── test_voice_detector.py
│   ├── test_subtitle_formatter.py
│   └── test_model_manager.py
│
├── integration/               # 整合測試
│   ├── test_ipc_communication.py
│   ├── test_backend_integration.py
│   ├── test_model_loading.py
│   └── test_file_processing.py
│
├── e2e/                      # 端到端測試
│   ├── test_complete_workflow.py
│   ├── test_ui_interactions.py
│   ├── test_batch_processing.py
│   └── test_error_recovery.py
│
├── performance/              # 效能測試
│   ├── test_processing_speed.py
│   ├── test_memory_usage.py
│   ├── test_concurrent_processing.py
│   └── test_large_file_handling.py
│
├── security/                 # 安全測試
│   ├── test_input_validation.py
│   ├── test_file_upload_security.py
│   └── test_path_traversal.py
│
└── fixtures/                 # 測試資料
    ├── audio_samples/
    ├── video_samples/
    ├── mock_data/
    └── expected_outputs/
```

## 🧪 詳細測試規範

### 1. 單元測試 (Unit Tests)

#### 音頻處理測試
```python
# tests/unit/test_audio_processor.py
import pytest
from audio_processor import AudioProcessor

class TestAudioProcessor:
    @pytest.fixture
    def processor(self):
        return AudioProcessor()
    
    def test_dynamic_range_compression(self, processor):
        """測試動態範圍壓縮功能"""
        audio_data = load_test_audio("sample.wav")
        compressed = processor.compress_dynamic_range(audio_data)
        assert compressed.max() < audio_data.max()
        assert compressed.std() < audio_data.std()
    
    def test_speech_frequency_enhancement(self, processor):
        """測試語音頻率增強"""
        audio_data = load_test_audio("speech.wav")
        enhanced = processor.enhance_speech_frequencies(audio_data)
        speech_freq_energy = calculate_speech_band_energy(enhanced)
        assert speech_freq_energy > calculate_speech_band_energy(audio_data)
    
    @pytest.mark.parametrize("sample_rate", [16000, 22050, 44100, 48000])
    def test_various_sample_rates(self, processor, sample_rate):
        """測試不同採樣率的相容性"""
        audio_data = generate_test_audio(sample_rate)
        result = processor.process(audio_data, sample_rate)
        assert result is not None
        assert len(result) > 0
```

#### 語音檢測測試
```python
# tests/unit/test_voice_detector.py
import pytest
import numpy as np
from adaptive_voice_detector import AdaptiveVoiceDetector

class TestAdaptiveVoiceDetector:
    @pytest.fixture
    def detector(self):
        return AdaptiveVoiceDetector()
    
    def test_feature_extraction_dimensions(self, detector):
        """確認特徵維度為25維"""
        audio = np.random.randn(16000)  # 1秒音頻
        features = detector.extract_features(audio)
        assert features.shape[-1] == 25
    
    def test_voice_segment_detection_precision(self, detector):
        """測試語音段檢測精度 ±0.05s"""
        audio_path = "fixtures/audio_samples/speech_with_silence.wav"
        segments = detector.detect_voice_segments(audio_path)
        
        # 驗證每個段落的時間精度
        for segment in segments:
            assert segment['confidence'] > 0.7
            assert segment['end'] > segment['start']
            # 驗證時間戳精度到小數點後兩位
            assert round(segment['start'], 2) == segment['start']
    
    @pytest.mark.benchmark
    def test_detection_performance(self, detector, benchmark):
        """效能基準測試"""
        audio = np.random.randn(16000 * 60)  # 60秒音頻
        result = benchmark(detector.detect_voice_segments_from_array, audio)
        assert result is not None
```

### 2. 整合測試 (Integration Tests)

#### IPC 通訊測試
```python
# tests/integration/test_ipc_communication.py
import pytest
import json
import asyncio
from electron_backend import ElectronBackend

class TestIPCCommunication:
    @pytest.fixture
    async def backend(self):
        backend = ElectronBackend()
        await backend.initialize()
        yield backend
        await backend.cleanup()
    
    @pytest.mark.asyncio
    async def test_message_format_validation(self, backend):
        """測試訊息格式驗證"""
        valid_message = {
            "files": ["test.mp4"],
            "settings": {"model": "large", "language": "auto"}
        }
        response = await backend.process_message(json.dumps(valid_message))
        assert response["type"] in ["progress", "result", "error"]
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self, backend):
        """測試並發處理能力"""
        tasks = []
        for i in range(5):
            message = {
                "files": [f"test_{i}.mp4"],
                "settings": {"model": "medium"}
            }
            tasks.append(backend.process_message(json.dumps(message)))
        
        results = await asyncio.gather(*tasks)
        assert len(results) == 5
        assert all(r["status"] == "success" for r in results)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, backend):
        """測試錯誤處理機制"""
        invalid_message = {"files": None, "settings": {}}
        response = await backend.process_message(json.dumps(invalid_message))
        assert response["type"] == "error"
        assert "message" in response["data"]
```

### 3. 端到端測試 (E2E Tests)

```python
# tests/e2e/test_complete_workflow.py
import pytest
from playwright.sync_api import Page, expect
import time

class TestCompleteWorkflow:
    @pytest.fixture
    def app_page(self, electron_app):
        """啟動 Electron 應用"""
        page = electron_app.firstWindow()
        yield page
    
    def test_single_file_processing(self, app_page: Page):
        """測試單檔案完整處理流程"""
        # 1. 開啟應用
        expect(app_page).to_have_title("SRT GO - AI Subtitle Generator")
        
        # 2. 上傳檔案
        app_page.set_input_files('input[type="file"]', 'fixtures/video_samples/test.mp4')
        
        # 3. 設定參數
        app_page.select_option('#model-select', 'large')
        app_page.select_option('#language-select', 'auto')
        app_page.check('#enable-voice-detection')
        
        # 4. 開始處理
        app_page.click('#process-button')
        
        # 5. 等待處理完成（最多5分鐘）
        expect(app_page.locator('#progress-bar')).to_have_attribute(
            'value', '100', timeout=300000
        )
        
        # 6. 驗證輸出
        output_text = app_page.locator('#output-preview').text_content()
        assert len(output_text) > 0
        assert '00:00:00,000' in output_text  # SRT格式驗證
    
    def test_batch_processing(self, app_page: Page):
        """測試批次處理功能"""
        files = [
            'fixtures/video_samples/test1.mp4',
            'fixtures/video_samples/test2.mp4',
            'fixtures/video_samples/test3.mp4'
        ]
        
        # 上傳多個檔案
        app_page.set_input_files('input[type="file"]', files)
        app_page.click('#batch-process-button')
        
        # 監控批次進度
        for i in range(3):
            progress_locator = app_page.locator(f'#file-{i}-progress')
            expect(progress_locator).to_have_attribute('value', '100', timeout=180000)
        
        # 驗證所有輸出
        results = app_page.locator('.result-item').all()
        assert len(results) == 3
```

### 4. 效能測試 (Performance Tests)

```python
# tests/performance/test_processing_speed.py
import pytest
import time
import psutil
import memory_profiler
from simplified_subtitle_core import SimplifiedSubtitleCore

class TestPerformance:
    @pytest.fixture
    def core(self):
        return SimplifiedSubtitleCore()
    
    def test_rtf_requirement(self, core):
        """測試 RTF (Real-Time Factor) 要求"""
        test_files = [
            ("fixtures/audio_samples/1min.wav", 0.8),   # CPU mode
            ("fixtures/audio_samples/10min.wav", 0.8),
            ("fixtures/audio_samples/30min.wav", 0.8),
        ]
        
        for file_path, max_rtf in test_files:
            start_time = time.time()
            core.process_audio(file_path)
            processing_time = time.time() - start_time
            
            audio_duration = get_audio_duration(file_path)
            rtf = processing_time / audio_duration
            
            assert rtf < max_rtf, f"RTF {rtf:.2f} exceeds limit {max_rtf}"
    
    @memory_profiler.profile
    def test_memory_usage(self, core):
        """測試記憶體使用量"""
        # 處理大檔案
        large_file = "fixtures/video_samples/2hour_video.mp4"
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        core.process_audio(large_file)
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        assert memory_increase < 4096, f"Memory usage {memory_increase}MB exceeds 4GB limit"
    
    def test_concurrent_processing_limit(self, core):
        """測試並發處理限制"""
        from concurrent.futures import ThreadPoolExecutor
        
        files = ["fixtures/audio_samples/test.wav"] * 10
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            start_time = time.time()
            futures = [executor.submit(core.process_audio, f) for f in files]
            results = [f.result() for f in futures]
            total_time = time.time() - start_time
        
        assert all(r is not None for r in results)
        assert total_time < 60, "Concurrent processing too slow"
```

### 5. 安全測試 (Security Tests)

```python
# tests/security/test_input_validation.py
import pytest
from pathlib import Path

class TestSecurity:
    def test_path_traversal_prevention(self, backend):
        """測試路徑遍歷攻擊防護"""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "file:///etc/passwd",
            "\\\\server\\share\\file"
        ]
        
        for path in malicious_paths:
            with pytest.raises(SecurityError):
                backend.process_file(path)
    
    def test_file_size_limit(self, backend):
        """測試檔案大小限制"""
        # 創建超大檔案
        large_file = create_large_file(size_gb=11)  # 11GB
        
        with pytest.raises(FileSizeError):
            backend.process_file(large_file)
    
    def test_malformed_input_handling(self, backend):
        """測試異常輸入處理"""
        malformed_inputs = [
            None,
            "",
            "not_a_file",
            {"evil": "payload"},
            "<script>alert('xss')</script>"
        ]
        
        for input_data in malformed_inputs:
            result = backend.process_file(input_data)
            assert result["type"] == "error"
            assert "Invalid input" in result["message"]
```

## 📊 測試指標與報告

### 1. 覆蓋率報告配置

```python
# pytest.ini
[tool:pytest]
addopts = 
    --cov=srt_whisper_lite
    --cov-report=html
    --cov-report=term-missing
    --cov-report=xml
    --cov-fail-under=85
    --benchmark-only
    --benchmark-autosave

testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### 2. 測試報告生成

```python
# tests/generate_report.py
import json
import datetime
from pathlib import Path

def generate_test_report():
    """生成商用級測試報告"""
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "2.2.1",
        "summary": {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "coverage": 0
        },
        "categories": {
            "unit_tests": {},
            "integration_tests": {},
            "e2e_tests": {},
            "performance_tests": {},
            "security_tests": {}
        },
        "critical_metrics": {
            "rtf_cpu": 0,
            "rtf_gpu": 0,
            "memory_peak": 0,
            "accuracy_rate": 0,
            "error_rate": 0
        }
    }
    
    # 收集所有測試結果
    collect_pytest_results(report)
    collect_coverage_data(report)
    collect_performance_metrics(report)
    
    # 生成HTML報告
    generate_html_report(report)
    
    # 生成JSON報告供CI/CD使用
    with open('test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    return report
```

## 🔄 CI/CD 整合

### GitHub Actions 配置

```yaml
# .github/workflows/test.yml
name: Commercial Grade Testing

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: windows-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
        node-version: [16, 18]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements-test.txt
        cd electron-react-app && npm ci
    
    - name: Run unit tests
      run: pytest tests/unit --cov --cov-report=xml
    
    - name: Run integration tests
      run: pytest tests/integration
    
    - name: Run E2E tests
      run: |
        npm run build
        pytest tests/e2e
    
    - name: Run performance tests
      run: pytest tests/performance --benchmark-only
    
    - name: Run security tests
      run: pytest tests/security
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
    
    - name: Generate test report
      run: python tests/generate_report.py
    
    - name: Upload test report
      uses: actions/upload-artifact@v3
      with:
        name: test-report
        path: |
          test_report.json
          test_report.html
          coverage/
```

## 🎯 測試檢查清單

### 發布前必須通過的測試

- [ ] **單元測試**: 100% 通過，覆蓋率 ≥ 85%
- [ ] **整合測試**: 100% 通過
- [ ] **E2E測試**: 核心流程 100% 通過
- [ ] **效能測試**: 
  - [ ] RTF < 0.8 (CPU)
  - [ ] RTF < 0.15 (GPU)
  - [ ] 記憶體 < 4GB
- [ ] **安全測試**: 無高危漏洞
- [ ] **回歸測試**: 無功能退化
- [ ] **壓力測試**: 10小時連續運行無崩潰
- [ ] **相容性測試**: Windows 10/11 x64 通過

## 📈 持續改進

### 測試債務追蹤
```python
# tests/test_debt_tracker.py
def track_test_debt():
    """追蹤測試債務"""
    debt_items = [
        {"module": "voice_detector", "missing_tests": 5, "priority": "high"},
        {"module": "ipc_handler", "missing_tests": 3, "priority": "medium"},
        {"module": "ui_components", "missing_tests": 8, "priority": "low"}
    ]
    
    total_debt = sum(item["missing_tests"] for item in debt_items)
    print(f"Total test debt: {total_debt} tests")
    
    # 生成改進計劃
    generate_improvement_plan(debt_items)
```

### 測試品質指標
- **測試執行時間**: < 10分鐘（單元測試）
- **測試穩定性**: 連續100次執行無隨機失敗
- **測試可維護性**: 每個測試 < 50行程式碼
- **測試獨立性**: 無測試間依賴

## 🚀 執行測試

```bash
# 完整測試套件
pytest tests/ --cov --benchmark-autosave

# 快速測試（開發時）
pytest tests/unit -x --ff

# 發布測試
pytest tests/ --strict-markers --tb=short

# 生成報告
python tests/generate_report.py
```

這個商用級測試架構確保了 SRT GO 的品質、穩定性和可靠性。