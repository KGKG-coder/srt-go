# SRT GO v2.2.1 測試架構 | Testing Framework

## 🎯 概述 | Overview

SRT GO v2.2.1 商用級測試架構，提供完整的自動化測試解決方案，涵蓋從單元測試到端到端測試的完整鏈條。

**完整測試統整計劃已實施 ✅**
- 📊 **25+ 測試檔案**統一管理
- 🤖 **13 個 GitHub Actions 工作流程**自動化執行  
- ⚡ **RTF 效能監控系統**即時追蹤
- 🧪 **統一測試執行器**一鍵運行所有測試

## 🚀 快速開始 | Quick Start

### 統一測試執行器 (推薦)
```bash
# 執行所有測試
cd tests
python run_all_tests.py

# 按類別執行測試
python run_all_tests.py --categories 單元測試
python run_all_tests.py --categories 效能測試
python run_all_tests.py --categories E2E測試

# 查看所有可用類別
python run_all_tests.py --list
```

## 📂 測試架構 | Test Structure

```
tests/
├── 📋 TEST_CONSOLIDATION_PLAN.md     # 完整測試統整計劃
├── 📋 TEST_INDEX.md                  # 測試索引與導航
├── 🚀 run_all_tests.py              # 統一測試執行器
├── ⚙️  conftest.py                   # 統一測試配置
├── 📊 UNIFIED_TEST_REPORT.json      # 統一測試報告
│
├── unit/                             # 🔧 單元測試
├── integration/                      # 🔗 整合測試  
├── performance/                      # ⚡ 效能測試
├── e2e/                             # 🎯 端到端測試
├── fixtures/                        # 🗂️ 測試夾具
└── utils/                           # 🛠️ 測試工具
```

## 📚 詳細文檔 | Detailed Documentation

- 📋 **[TEST_CONSOLIDATION_PLAN.md](TEST_CONSOLIDATION_PLAN.md)** - 完整測試統整計劃
- 📋 **[TEST_INDEX.md](TEST_INDEX.md)** - 測試索引與快速導航

## 📊 測試覆蓋與效能基準 | Coverage & Baselines

### RTF效能目標 | RTF Performance Targets
- 🏆 **Excellent**: RTF ≤ 0.2 (即時處理能力)
- ✅ **Good**: RTF ≤ 0.5 (批次處理適用)
- ⚠️ **Acceptable**: RTF ≤ 1.0 (基本需求)
- ❌ **Needs Improvement**: RTF > 1.0

### 測試覆蓋目標 | Coverage Targets  
- **單元測試覆蓋率**: ≥ 90%
- **整合測試成功率**: ≥ 95%
- **E2E測試成功率**: ≥ 90%
- **記憶體使用**: < 2GB 峰值

### Individual Test Categories

#### 1. Performance Tests
```bash
cd tests/performance
python comprehensive_performance_suite.py --standard
python monitor_processing_performance.py
```

#### 2. Integration Tests  
```bash
cd tests/integration
python debug_test_integration.py
python debug_test_integration_low_vad.py
```

#### 3. E2E Tests
```bash
cd tests/e2e
python test_automation_suite.py --full-suite
```

## 📊 Test Coverage

### Components Tested
- **FP16/INT8 Model Management**: GPU/CPU adaptive selection
- **Adaptive Voice Detection v2.0**: 25D feature analysis
- **Smart Backend Selector**: Python environment fallback
- **Performance Monitor**: Real-time RTF calculation
- **Multi-language Processing**: Auto-detect + Traditional Chinese
- **UI Integration**: Electron + React workflow

### Test Scenarios
1. **Basic Audio Processing**: Short clips (11.3s)
2. **Medical Dialogue**: Professional content (40.3s)
3. **Multi-language**: Chinese to Traditional conversion
4. **Format Support**: SRT, VTT, TXT, JSON outputs
5. **Performance Benchmarks**: RTF < 0.8 validation
6. **Error Handling**: Graceful degradation testing

## 🎯 Quality Metrics

### Target Performance
- **RTF (Real-Time Factor)**
  - GPU Mode: < 0.15 (優秀級)
  - CPU Mode: < 0.8 (標準級)
- **Accuracy**: 95%+ recognition rate
- **Test Success**: 100% E2E pass rate

### Performance Tiers
1. **優秀級 (Excellent)**: RTF < 0.15
2. **良好級 (Good)**: RTF < 0.3  
3. **標準級 (Standard)**: RTF < 0.5
4. **可接受級 (Acceptable)**: RTF < 0.8
5. **需優化級 (Needs Optimization)**: RTF > 0.8

## 🔧 Test Configuration

### Environment Variables
```yaml
PYTHON_VERSION: '3.11'
NODE_VERSION: '18'
ELECTRON_CACHE: .cache/electron
HUGGINGFACE_HUB_CACHE: .cache/huggingface
```

### Test Data
- **Test Files**: Located in `srt_whisper_lite/electron-react-app/test_VIDEO/`
- **Sample Data**: 370 audio files (5s to 73.8h coverage)
- **Formats**: MP4, MP3, WAV for comprehensive testing

## 📈 CI/CD Integration

### GitHub Actions Workflows
1. **ci-cd-pipeline.yml**: Complete 7-stage validation
2. **quick-test.yml**: Fast development testing
3. **performance-monitoring.yml**: Daily performance tracking
4. **manual-testing.yml**: Component-specific testing

### Quality Gates
- Unit tests must pass before integration
- Performance regression detection (>20% slower fails)
- Security scan required for releases
- 100% E2E success rate for deployment

## 🛠️ Development Testing

### Local Development
```bash
# Quick validation
cd tests/performance
python quick_rtf_test.py --basic-only

# Component testing
cd srt_whisper_lite/electron-react-app
python python/electron_backend.py --files "[\"test_VIDEO/hutest.mp4\"]" --settings "{\"model\":\"medium\"}"

# Build verification
npm run build:with-models
npm run dist:nsis
```

### Mock vs Real Testing
- **CI Environment**: Uses mock backend for speed
- **Local Development**: Real AI processing validation
- **Performance Tests**: Always use real models for accuracy

## 📚 Test Documentation

### Test Reports
- **Performance Reports**: `tests/performance/results/`
- **E2E Results**: `tests/e2e/results/`
- **CI Artifacts**: Available in GitHub Actions runs

### Debugging
- **Logs**: Check `electron_backend.log` for processing details
- **Test Output**: Individual test directories in `/temp/`
- **Validation**: JSON reports with detailed validation steps

## 🔍 Troubleshooting

### Common Issues
1. **Model Download Failures**
   - Check network connectivity
   - Verify HuggingFace access
   - Clear cache: `rm -rf ~/.cache/huggingface/`

2. **Path Resolution**
   - Use absolute paths in test configurations
   - Verify test file locations
   - Check working directory settings

3. **Performance Variations**
   - Hardware differences affect RTF values
   - GPU availability impacts test results
   - System load can affect performance metrics

### Debug Commands
```bash
# Check Python environment
python -c "import sys; print(sys.version, sys.executable)"

# Verify AI dependencies
python -c "import faster_whisper, torch; print('✅ AI modules OK')"

# Test model loading
python -c "
import sys; sys.path.append('srt_whisper_lite/electron-react-app/python')
from large_v3_fp16_performance_manager import LargeV3FP16PerformanceManager
manager = LargeV3FP16PerformanceManager()
print('✅ Model manager OK')
"
```

---

**📧 Support**: For testing issues, create GitHub issue with:
- Test name and scenario
- Error logs and stack traces
- System configuration details
- Steps to reproduce

**🔄 Continuous Improvement**: Test suite evolves with each release to maintain quality standards and performance targets.