# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
此文件為 Claude Code (claude.ai/code) 在處理此儲存庫代碼時提供指導。

## Project Overview | 項目概述

SRT GO is an AI-powered subtitle generation tool using Faster-Whisper with Large-v3-turbo model, featuring a modern Electron + React GUI with adaptive voice detection and SubEasy 5-layer filtering. Version 2.2.1 is production-ready with complete CI/CD pipeline, comprehensive testing framework, and achieved 100% E2E test success rate.

SRT GO 是一個基於 Faster-Whisper 和 Large-v3-turbo 模型的 AI 字幕生成工具，具有現代化的 Electron + React 圖形界面、自適應語音檢測和 SubEasy 5層過濾系統。2.2.1 版本已達到生產就緒狀態，配備完整的 CI/CD 管道、全面的測試框架，並實現了 100% 的端到端測試成功率。

## Core Architecture | 核心架構

### High-Level Structure (Simplified v2.2.1) | 高層架構（簡化版 v2.2.1）
```
Electron GUI (main.js + React) → IPC Bridge → Python Backend (electron_backend.py)
                                                        ↓
                                    Embedded Python Only (mini_python)
                                                        ↓
                                    Faster-Whisper AI + Voice Detection + SubEasy Filter
```

### Key Files and Their Responsibilities | 關鍵文件及其職責
- **main_simplified.js**: Simplified Electron main process, uses embedded Python only | 簡化的 Electron 主程序，僅使用嵌入式 Python
- **electron_backend_simplified.py**: Simplified backend without smart selection | 無智能選擇的簡化後端
- **simplified_subtitle_core.py**: Core Faster-Whisper transcription engine | 核心 Faster-Whisper 轉錄引擎
- **adaptive_voice_detector.py**: ML-based voice detection (25D features) | 基於機器學習的語音檢測（25維特徵）
- **subeasy_multilayer_filter.py**: 5-layer quality enhancement filter | 5層品質增強過濾器
- **large_v3_fp16_performance_manager.py**: GPU/CPU performance optimization | GPU/CPU 性能優化
- **mini_python/**: Embedded Python 3.11 environment with all dependencies | 內嵌 Python 3.11 環境及所有依賴

## Development Commands | 開發命令

### Run the Application | 運行應用程序
```bash
# Development mode with simplified backend (recommended)
cd srt_whisper_lite/electron-react-app
npm run dev:simplified

# Standard development mode (legacy with smart selection)
npm run dev

# Production executable
cd dist/win-unpacked
"SRT GO - AI Subtitle Generator.exe"

# Test simplified Python backend directly
cd srt_whisper_lite/electron-react-app/mini_python
python.exe ../python/electron_backend_simplified.py --files "[\"../test_VIDEO/hutest.mp4\"]" --settings "{\"model\":\"large\",\"language\":\"auto\",\"enablePureVoiceMode\":true}" --corrections "[]"
```

### Build and Package | 構建和打包
```bash
cd srt_whisper_lite/electron-react-app
npm run install:all               # Install all dependencies
npm run build:with-models         # Build with embedded AI models
npm run dist:nsis                 # Create Windows installer
npm run dist:portable             # Create portable version
```

### Testing | 測試
```bash
# Run all tests via unified runner
cd tests && python run_all_tests.py

# Unit tests
cd tests && python -m pytest unit/ -v --tb=short

# Performance benchmarks  
cd tests/performance && python quick_rtf_test.py --basic-only

# E2E automation
cd tests/e2e && python test_automation_suite.py --quick-mode
```

## IPC Communication Protocol | IPC 通訊協議

The Electron app communicates with Python backend through JSON messages via stdin/stdout:

```javascript
// main.js spawns Python process
const pythonProcess = spawn(pythonPath, [
  'electron_backend.py',
  '--files', JSON.stringify(files),
  '--settings', JSON.stringify(settings)
]);

// Python sends progress updates
{"type": "progress", "data": {"percentage": 50, "message": "Processing..."}}
{"type": "result", "data": {"file": "output.srt", "status": "success"}}
{"type": "error", "data": {"message": "Error details", "code": "ERROR_CODE"}}
```

## Key Configuration | 關鍵配置

### Processing Settings | 處理設置
```json
{
  "model": "large",                  // large-v3-turbo, medium, small
  "language": "auto",                // auto, zh, en, ja, ko
  "outputFormat": "srt",             // srt, vtt, txt, json
  "enablePureVoiceMode": true,       // Adaptive voice detection
  "enableSubEasy": false,            // 5-layer filter (legacy)
  "enable_gpu": false,               // GPU acceleration
  "performanceMode": "auto",         // auto, gpu, cpu
  "vad_threshold": 0.35              // Voice activity threshold
}
```

### Model Management | 模型管理
- **Primary Model**: `openai/whisper-large-v3-turbo` (Float16/INT8)
- **Location**: Auto-downloads to `~/.cache/huggingface/hub/` or embedded in `models/`
- **GPU Mode**: CUDA with FP16 (RTF < 0.15)
- **CPU Mode**: INT8 quantization (RTF < 0.8)

## Critical Implementation Details | 關鍵實現細節

### Simplified Backend Architecture | 簡化後端架構
The system now uses a single, predictable Python environment:
- **Embedded Python Only**: Always uses bundled `mini_python/` (Python 3.11)
- **No Environment Selection**: Removes complexity and potential errors
- **Fixed Dependencies**: All required packages pre-installed in mini_python
- **Consistent Behavior**: Same environment for all users

### Adaptive Voice Detection | 自適應語音檢測 (`adaptive_voice_detector.py`)
- Uses 25-dimensional audio features (MFCC, pitch, formants, spectral)
- K-means clustering for voice/non-voice classification
- Dynamic threshold calculation (75th percentile)
- Achieves ±0.05s timing precision

### Performance Monitoring | 性能監控
- Real-time RTF calculation for processing speed monitoring
- 5-tier performance classification (Excellent → Needs Optimization)
- Automatic mode selection (Auto/GPU/CPU) based on hardware

## Testing Framework | 測試框架

### Test Structure | 測試結構
```
tests/
├── unit/                # Unit tests for individual components
├── integration/         # Integration tests for workflow
├── performance/         # RTF benchmarks and monitoring
├── e2e/                # End-to-end automation suite
└── utils/              # Test utilities and generators
```

### Performance Baselines | 性能基準
- **GPU RTF**: 0.736 (target < 0.15)
- **CPU RTF**: 2.012 (target < 0.8)
- **E2E Success Rate**: 100% (11/11 scenarios)

## Troubleshooting | 故障排除

### Common Issues and Solutions | 常見問題和解決方案
- **GPU not detected | GPU 未檢測到**: Requires CUDA 11.8+, falls back to CPU INT8 mode | 需要 CUDA 11.8+，自動回退到 CPU INT8 模式
- **UI crashes ("閃退") | UI 崩潰**: Use GPU-disabled launcher or check `electron_backend.log` | 使用禁用 GPU 的啟動器或檢查 `electron_backend.log`
- **Model download fails | 模型下載失敗**: Check internet connection, models auto-download to `~/.cache/huggingface/` | 檢查網絡連接，模型自動下載到 `~/.cache/huggingface/`
- **Encoding errors | 編碼錯誤**: Ensure all files use UTF-8, check Python environment encoding | 確保所有文件使用 UTF-8，檢查 Python 環境編碼

### Debug Commands | 調試命令
```bash
# Check embedded Python environment
cd srt_whisper_lite/electron-react-app/mini_python
python.exe -c "import sys; print(sys.version, sys.executable)"

# Test model loading
python.exe ../python/large_v3_int8_model_manager.py

# Check GPU support  
python.exe ../python/test_gpu_support.py

# View logs (Windows)
type electron_backend.log
type subtitle_generator.log
```