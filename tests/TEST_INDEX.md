# SRT GO v2.2.1 測試索引
# Test Index for SRT GO v2.2.1

## 📋 快速導航 | Quick Navigation

本文檔提供所有測試檔案的索引，按功能分類並附上詳細說明。

### 🚀 快速執行 | Quick Execution

```bash
# 執行所有測試
cd tests
python run_all_tests.py

# 執行特定類別測試
python run_all_tests.py --categories 單元測試
python run_all_tests.py --categories 效能測試

# 列出所有測試類別
python run_all_tests.py --list
```

---

## 🧪 測試分類清單 | Test Category List

### 1. **單元測試 | Unit Tests** 🔧
**路徑**: `tests/unit/`

#### 1.1 音頻處理器測試 | Audio Processor Tests
- **檔案**: `test_audio_processor.py`
- **功能描述**: 音頻處理器完整測試套件
- **測試內容**:
  - ✅ 動態範圍壓縮測試 (Dynamic Range Compression)
  - ✅ 語音頻率增強驗證 (Speech Frequency Enhancement) 
  - ✅ 降噪功能測試 (Denoising Functionality)
  - ✅ 重採樣精度驗證 (Resampling Precision)
  - ✅ 音頻正規化測試 (Audio Normalization)
  - ✅ 靜音移除功能 (Silence Removal)
  - ✅ 邊界情況處理 (Edge Cases: 空音頻、全靜音、極長音頻)
  - ✅ 效能基準測試 (Performance: 處理速度 < 0.5秒)
- **執行方式**: `pytest unit/test_audio_processor.py -v`

#### 1.2 簡化音頻處理器測試
- **檔案**: `test_audio_processor_simple.py`  
- **功能描述**: 簡化版音頻處理器測試
- **執行方式**: `pytest unit/test_audio_processor_simple.py -v`

---

### 2. **整合測試 | Integration Tests** 🔗
**路徑**: `tests/integration/`

#### 2.1 完整工作流程測試 | Complete Workflow Tests
- **檔案**: `test_complete_workflow.py`
- **功能描述**: 完整工作流程整合測試
- **測試內容**:
  - ✅ Electron GUI → Python Backend → AI模型完整鏈路
  - ✅ IPC通信測試 (Inter-Process Communication)
  - ✅ 檔案輸入輸出驗證 (File I/O Validation)
  - ✅ 多格式支援測試 (SRT, VTT, TXT formats)
- **執行方式**: `pytest integration/test_complete_workflow.py -v`

#### 2.2 整合除錯測試 | Integration Debug Tests
- **檔案**: `debug_test_integration.py`
- **功能描述**: 整合測試除錯工具
- **測試內容**:
  - ✅ 完整工作流程除錯
  - ✅ 錯誤追蹤與診斷
  - ✅ 系統相容性檢查
- **執行方式**: `python debug_test_integration.py`

#### 2.3 低VAD整合測試 | Low VAD Integration Tests  
- **檔案**: `debug_test_integration_low_vad.py`
- **功能描述**: 低VAD閾值整合測試
- **測試內容**:
  - ✅ 語音檢測敏感度測試
  - ✅ 靜音處理驗證
- **執行方式**: `python debug_test_integration_low_vad.py`

---

### 3. **效能測試 | Performance Tests** ⚡
**路徑**: `tests/performance/`

#### 3.1 快速RTF測試 | Quick RTF Tests
- **檔案**: `quick_rtf_test.py`
- **功能描述**: 快速RTF效能測試
- **測試內容**:
  - ✅ Medium_CPU, Small_CPU, Medium_GPU配置測試
  - ✅ 實時因子 (RTF) 計算
  - ✅ 5級效能評級系統 (Excellent → Needs Improvement)
  - ✅ 處理速度基準驗證
- **執行方式**: `python performance/quick_rtf_test.py`

#### 3.2 RTF基準測試 | RTF Benchmark Tests
- **檔案**: `test_rtf_benchmarks.py`
- **功能描述**: RTF基準測試套件
- **執行方式**: `pytest performance/test_rtf_benchmarks.py -v`

#### 3.3 RTF監控系統 | RTF Monitoring System
- **檔案**: `rtf_monitoring_system.py`
- **功能描述**: 實時RTF監控系統
- **測試內容**:
  - ✅ 實時效能監控
  - ✅ 自動效能警報 
  - ✅ 歷史效能數據追蹤
- **執行方式**: `python performance/rtf_monitoring_system.py`

#### 3.4 綜合效能測試套件 | Comprehensive Performance Suite
- **檔案**: `comprehensive_performance_suite.py`
- **功能描述**: 完整效能測試套件
- **測試內容**:
  - ✅ 完整370個音頻檔案測試集
  - ✅ GPU vs CPU效能對比
  - ✅ 記憶體使用監控
  - ✅ 長時間穩定性測試
- **執行方式**: `python performance/comprehensive_performance_suite.py`

#### 3.5 簡化RTF測試 | Simple RTF Tests
- **檔案**: `simple_rtf_test.py`
- **功能描述**: 簡化版RTF測試
- **執行方式**: `python performance/simple_rtf_test.py`

---

### 4. **端到端測試 | End-to-End Tests** 🎯
**路徑**: `tests/e2e/`

#### 4.1 E2E自動化測試套件 | E2E Automation Suite
- **檔案**: `test_automation_suite.py`
- **功能描述**: SRT GO E2E測試自動化套件
- **測試內容**:
  - ✅ 核心功能測試 (Medium/Small模型 + GPU加速)
  - ✅ 輸出格式測試 (SRT, VTT, TXT)
  - ✅ 語言檢測測試 (auto, en, zh)
  - ✅ 進階功能測試 (Pure Voice Mode, SubEasy)
  - ✅ 真實音頻處理驗證
  - ✅ 批次處理測試
  - ✅ 錯誤恢復測試
- **執行方式**: `python e2e/test_automation_suite.py`

---

### 5. **測試工具與資料 | Test Utilities & Data** 🛠️
**路徑**: `tests/utils/`, `tests/fixtures/`

#### 5.1 測試音頻生成器 | Test Audio Generators
- **超真實語音生成器**: `utils/ultra_realistic_speech_generator.py`
  - 25維音頻特徵生成
  - 多語言語音合成
  - 真實音頻模擬

- **Whisper相容音頻生成器**: `utils/whisper_compatible_audio_generator.py`
- **通用測試音頻生成器**: `utils/test_audio_generator.py`

#### 5.2 測試夾具 | Test Fixtures
- **音頻樣本庫**: `fixtures/audio_samples/`
- **視訊樣本庫**: `fixtures/video_samples/`
- **預期輸出結果**: `fixtures/expected_outputs/`

---

## 🤖 GitHub Actions 自動化工作流程 | Automated Workflows

### 核心CI/CD管道 | Core CI/CD Pipeline

#### 1. **完整CI/CD管道** | Complete CI/CD Pipeline
- **檔案**: `.github/workflows/ci-cd-pipeline.yml`
- **功能描述**: 7階段完整CI/CD管道
- **執行階段**:
  1. 程式碼品質檢查 (flake8, black, pylint, mypy)
  2. 單元測試 (跨平台 Windows/Ubuntu/macOS)
  3. 整合測試
  4. 效能測試  
  5. E2E測試
  6. 安全掃描
  7. 部署驗證

#### 2. **商用級測試管道** | Commercial Testing Pipeline  
- **檔案**: `.github/workflows/test.yml`
- **功能描述**: 商用級測試工作流程
- **測試類型**:
  - 程式碼品質檢查
  - 跨版本單元測試 (Python 3.9-3.11)
  - 整合測試
  - E2E測試
  - 效能測試  
  - 安全測試
  - 發布測試
  - 測試報告匯總

#### 3. **安裝包自動化測試** | Installer Testing
- **檔案**: `.github/workflows/installer-testing.yml`  
- **功能描述**: 完整安裝包測試工作流程
- **測試內容**:
  - 完整安裝包測試
  - 標準安裝包測試
  - 可攜式版本測試
  - 完整性檢查
  - 跨平台驗證
  - 進階完整性檢查

#### 4. **效能監控工作流程** | Performance Monitoring
- **檔案**: `.github/workflows/performance-monitoring.yml`
- **功能描述**: 自動化效能監控
- **監控內容**:
  - 即時RTF監控
  - 效能回歸檢測
  - 自動化效能報告

#### 5. **快速測試工作流程** | Quick Testing
- **檔案**: `.github/workflows/quick-test.yml`
- **功能描述**: 快速測試驗證
- **測試內容**:
  - 快速單元測試
  - 基本功能驗證

#### 6. **手動測試工作流程** | Manual Testing
- **檔案**: `.github/workflows/manual-testing.yml`
- **功能描述**: 手動觸發測試工作流程

---

## 📊 效能基準與目標 | Performance Baselines & Targets

### RTF效能目標 | RTF Performance Targets
- **🏆 Excellent**: RTF ≤ 0.2 (即時處理能力)
- **✅ Good**: RTF ≤ 0.5 (批次處理適用)  
- **⚠️ Acceptable**: RTF ≤ 1.0 (基本需求)
- **❌ Needs Improvement**: RTF > 1.0

### 測試覆蓋目標 | Test Coverage Targets
- **單元測試覆蓋率**: ≥ 90%
- **整合測試成功率**: ≥ 95%  
- **E2E測試成功率**: ≥ 90%
- **安裝包測試通過率**: 100%

### 效能監控指標 | Performance Monitoring Metrics
- **GPU RTF基準**: < 0.15 (current: 0.736)
- **CPU RTF基準**: < 0.8 (current: 2.012)
- **記憶體使用峰值**: < 2GB
- **處理穩定性**: 24小時+ 連續運行

---

## 🏃‍♂️ 常用測試命令 | Common Test Commands

### 本機測試 | Local Testing
```bash
# 1. 執行所有測試
cd tests
python run_all_tests.py

# 2. 按類別執行
python run_all_tests.py --categories 單元測試
python run_all_tests.py --categories 整合測試  
python run_all_tests.py --categories 效能測試
python run_all_tests.py --categories E2E測試

# 3. 使用pytest直接執行
pytest unit/ -v --tb=short                    # 單元測試
pytest integration/ -v --tb=short             # 整合測試
pytest performance/ -v --tb=short             # 效能測試
pytest e2e/ -v --tb=short                     # E2E測試

# 4. 執行特定測試文件
pytest unit/test_audio_processor.py -v
python performance/quick_rtf_test.py
python e2e/test_automation_suite.py

# 5. 執行整合除錯測試
python debug_test_integration.py
python debug_test_integration_low_vad.py

# 6. 執行效能監控
python performance/rtf_monitoring_system.py
python performance/comprehensive_performance_suite.py
```

### CI/CD觸發 | CI/CD Triggers
```bash
# GitHub CLI 手動觸發工作流程
gh workflow run ci-cd-pipeline.yml
gh workflow run installer-testing.yml
gh workflow run performance-monitoring.yml
gh workflow run quick-test.yml

# Git推送觸發
git push origin main                           # 觸發完整CI/CD
git push origin develop                        # 觸發開發分支測試
```

---

## 📈 測試報告查看 | Test Report Viewing

### 本機報告 | Local Reports
- **統一測試報告**: `tests/UNIFIED_TEST_REPORT.json`
- **E2E測試報告**: `tests/e2e/test_data/E2E_TEST_AUTOMATION_REPORT.md`
- **效能測試報告**: `tests/performance/RTF_BENCHMARK_REPORT.md`
- **基準效能報告**: `tests/performance/RTF_PERFORMANCE_BASELINE_REPORT.md`

### GitHub Actions報告 | GitHub Actions Reports
- 工作流程執行結果: GitHub Actions頁面
- 測試覆蓋率報告: Codecov整合
- 效能趨勢分析: Actions artifacts下載

---

## 🔧 除錯與故障排除 | Debugging & Troubleshooting

### 常見問題 | Common Issues
1. **模型下載失敗**: 檢查網路連接，模型會自動下載到 `~/.cache/huggingface/`
2. **GPU檢測失敗**: 需要CUDA 11.8+，會自動降級到CPU INT8模式
3. **測試超時**: 調整timeout設定或使用較小模型進行測試
4. **依賴套件缺失**: 安裝 `pip install -r tests/requirements-ci.txt`

### 除錯命令 | Debug Commands
```bash
# 檢查Python環境
python -c "import sys; print(sys.version, sys.executable)"

# 檢查AI依賴
python -c "import faster_whisper; print('AI_READY')"

# 檢查GPU支援
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"

# 執行後端測試
cd srt_whisper_lite/electron-react-app
python python/electron_backend.py --help
```

---

**文檔版本**: v2.2.1  
**最後更新**: 2025-08-28  
**維護者**: Claude Code AI Assistant