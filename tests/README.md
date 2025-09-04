# SRT GO 測試框架 (v2.2.1)

## 概述

完整的測試框架，覆蓋智能FP16優先系統、UI-Backend整合、性能監控和自動修復功能。

## 測試結構

```
tests/
├── unit/                    # 單元測試
│   ├── test_model_selection.py
│   ├── test_fp16_manager.py
│   └── test_backend_integration.py
├── integration/             # 整合測試
│   ├── test_comprehensive_suite.py
│   ├── test_ui_backend_integration.py
│   └── test_system_monitoring.py
├── performance/             # 性能測試
│   ├── rtf_benchmark.py
│   ├── memory_usage_test.py
│   └── gpu_cpu_comparison.py
├── e2e/                    # 端到端測試
│   ├── test_full_workflow.py
│   └── test_user_scenarios.py
└── utils/                  # 測試工具
    ├── test_data_generator.py
    ├── performance_analyzer.py
    └── test_runner.py
```

## 核心測試套件

### 1. 智能FP16優先系統測試 (`comprehensive_test_suite.py`)

測試智能模型選擇器的所有功能：

```bash
cd srt_whisper_lite/electron-react-app/python
python comprehensive_test_suite.py
```

**測試項目：**
- ✅ 自動FP16優先模式 (RTF: 0.579)
- ✅ GPU禁用自動降級 (RTF: 1.322)
- ✅ 強制FP16vs自動選擇性能對比
- ✅ 智能選擇器4種情境處理
- ✅ GUI整合相容性驗證

### 2. UI-Backend整合測試 (`test_ui_backend_integration.py`)

驗證前端與後端的完整連接：

```bash
cd srt_whisper_lite/electron-react-app/python
python test_ui_backend_integration.py
```

**測試項目：**
- ✅ 電子後端直接測試 (8.04秒)
- ✅ 智能選擇器整合測試 (11.01秒)
- ✅ IPC訊息格式測試 (3種模式)
- ✅ UI-Backend連接性驗證

### 3. 自動監控系統測試 (`ui_auto_monitoring_system.py`)

實時系統健康監控和自動修復：

```bash
cd srt_whisper_lite/electron-react-app/python
python ui_auto_monitoring_system.py
```

**監控項目：**
- React服務器狀態 (localhost:3000)
- Electron進程監控
- Python後端健康檢查
- 智能FP16系統狀態
- GPU/CPU資源使用

## 測試命令

### 快速測試
```bash
# 運行所有核心測試
python tests/utils/test_runner.py --quick

# 智能FP16系統測試
python srt_whisper_lite/electron-react-app/python/comprehensive_test_suite.py

# UI整合測試
python srt_whisper_lite/electron-react-app/python/test_ui_backend_integration.py
```

## 測試結果解讀

### 性能等級分類
- **優秀級 (Excellent)**: RTF < 0.15
- **良好級 (Good)**: RTF < 0.3
- **標準級 (Standard)**: RTF < 0.5
- **可接受級 (Acceptable)**: RTF < 0.8
- **需優化級 (Needs Optimization)**: RTF > 0.8

### 測試成功標準
- **智能FP16系統**: 5/5 測試通過 (100%)
- **UI-Backend整合**: 4/4 測試通過 (100%)
- **自動監控系統**: 持續運行無錯誤
- **整體成功率**: 100%

## 最新測試結果 (2025-09-04)

### 智能FP16優先系統
```json
{
  "自動FP16優先模式": {"success": true, "performance": 6.54},
  "GPU禁用自動降級": {"success": true, "performance": 14.16},
  "智能選擇器功能": {"success": true, "4種情境": "全部正確處理"}
}
```

### UI-Backend整合
```json
{
  "電子後端直接測試": {"success": true, "performance": 8.04},
  "智能選擇器整合": {"success": true, "performance": 11.01},
  "IPC訊息格式": {"success": true, "3種格式": "JSON序列化成功"}
}
```

## 硬體環境

- **GPU**: NVIDIA GeForce RTX 4070 (12GB VRAM)
- **CUDA**: 11.8
- **OS**: Windows 10/11
- **Python**: 3.11 (embedded) / 3.13 (system)
- **Node.js**: 18+ (for React/Electron)

## GitHub Actions 整合

已配置完整的CI/CD管道：

- `.github/workflows/ci-cd-pipeline.yml`: 完整7階段測試管道
- `.github/workflows/quick-test.yml`: 快速開發測試
- `.github/workflows/manual-testing.yml`: 參數化手動測試
- `.github/workflows/performance-monitoring.yml`: 每日性能監控

## 聯繫資訊

- **項目**: SRT GO - AI Subtitle Generator
- **版本**: 2.2.1 (智能FP16優先系統)
- **狀態**: ✅ 生產就緒 (100%測試通過)
