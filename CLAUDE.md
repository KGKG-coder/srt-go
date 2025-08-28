# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SRT GO is an AI-powered subtitle generation tool using Faster-Whisper, featuring a modern Electron + React GUI with adaptive voice detection and SubEasy 5-layer filtering. Version 2.2.1 is production-ready with complete CI/CD pipeline, comprehensive testing framework, and achieved 100% E2E test success rate.

## Core Architecture

### High-Level Structure
The system uses a 3-tier architecture with IPC communication between Electron frontend and Python backend:

```
Electron GUI (main.js + React) → IPC Bridge → Python Backend (electron_backend.py)
                                                        ↓
                                    Smart Backend Selector (system/embedded/fallback)
                                                        ↓
                                    Faster-Whisper AI + Voice Detection + SubEasy Filter
```

### Key Files and Their Responsibilities
- **srt_whisper_lite/electron-react-app/main.js**: Electron main process, handles IPC and spawns Python backend
- **srt_whisper_lite/electron-react-app/python/electron_backend.py**: Main entry point for Python processing
- **srt_whisper_lite/electron-react-app/python/smart_backend_selector.py**: Selects best available Python environment
- **srt_whisper_lite/electron-react-app/python/simplified_subtitle_core.py**: Core Faster-Whisper transcription engine
- **srt_whisper_lite/electron-react-app/python/adaptive_voice_detector.py**: ML-based voice detection (25D features)
- **srt_whisper_lite/electron-react-app/python/subeasy_multilayer_filter.py**: 5-layer quality enhancement filter
- **srt_whisper_lite/electron-react-app/python/large_v3_fp16_performance_manager.py**: GPU/CPU performance optimization

## Development Commands

### Build and Run
```bash
# Development mode (hot reload)
cd srt_whisper_lite/electron-react-app
npm run dev

# Build production app
npm run build:with-models  # Includes AI models
npm run dist:nsis         # Create Windows installer
npm run dist:portable     # Create portable version

# Run production executable
cd dist/win-unpacked
"SRT GO - AI Subtitle Generator.exe"

# Install dependencies
npm run install:all       # Install both Electron and React dependencies
```

### Testing
```bash
# Unit tests
cd tests
python -m pytest unit/ -v --tb=short

# Integration tests  
cd tests/integration
python debug_test_integration.py
python debug_test_integration_low_vad.py

# Performance benchmarks
cd tests/performance
python quick_rtf_test.py --basic-only
python comprehensive_performance_suite.py --standard

# E2E automation suite
cd tests/e2e
python test_automation_suite.py --quick-mode
python test_automation_suite.py --full-suite

# Test Python backend directly
cd srt_whisper_lite/electron-react-app
python python/electron_backend.py --files "[\"test_VIDEO/hutest.mp4\"]" --settings "{\"model\":\"large\",\"language\":\"auto\",\"enablePureVoiceMode\":true}" --corrections "[]"
```

### CI/CD Pipeline
```bash
# GitHub Actions workflows available:
- .github/workflows/ci-cd-pipeline.yml: Complete 7-stage pipeline (unit → integration → performance → E2E → build → security → deploy)
- .github/workflows/quick-test.yml: Fast development testing
- .github/workflows/manual-testing.yml: Component-specific testing
- .github/workflows/performance-monitoring.yml: Daily performance tracking
- .github/workflows/release-builder.yml: Release packaging automation
```

## Key Configuration

### Model Management
- **Primary Model**: `openai/whisper-large-v3-turbo` (Float16/INT8)
- **Fallback Models**: Medium, Small (auto-selected based on system resources)
- **Location**: Auto-downloads to `~/.cache/huggingface/hub/`
- **GPU Mode**: CUDA with FP16 (RTF < 0.15)
- **CPU Mode**: INT8 quantization (RTF < 0.8)

### Processing Settings
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

## IPC Communication Flow

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

## Critical Implementation Details

### Smart Backend Selection (`smart_backend_selector.py`)
The system automatically selects the best available Python environment:
1. **System Python**: Uses system-installed Python 3.13 if available
2. **Embedded Python**: Falls back to bundled `mini_python/` (Python 3.11)
3. **Simplified Backend**: Minimal fallback for emergency operation

### Adaptive Voice Detection (`adaptive_voice_detector.py`)
- Uses 25-dimensional audio features (MFCC, pitch, formants, spectral)
- K-means clustering for voice/non-voice classification
- Dynamic threshold calculation (75th percentile)
- Achieves ±0.05s timing precision
- Solves the "non-speech interlude" problem (e.g., DRLIN.mp4 segment 12)

### Performance Monitoring System
- **Real-time RTF calculation**: Processing speed monitoring
- **5-tier performance classification**: Excellent → Needs Optimization
- **Automatic mode selection**: Auto/GPU/CPU based on hardware
- **Comprehensive test dataset**: 370 audio files (short clips to 73.8h videos)

## Testing Framework

### Test Structure
```
tests/
├── unit/                # Unit tests for individual components
├── integration/         # Integration tests for workflow
├── performance/         # RTF benchmarks and monitoring
├── e2e/                # End-to-end automation suite
└── utils/              # Test utilities and generators
```

### Performance Baselines
- **GPU RTF**: 0.736 (target < 0.15 for Excellent tier)
- **CPU RTF**: 2.012 (target < 0.8 for Acceptable tier)
- **E2E Success Rate**: 100% (11/11 scenarios)

### Performance Tiers
- **Excellent**: RTF < 0.15
- **Good**: RTF < 0.3
- **Standard**: RTF < 0.5
- **Acceptable**: RTF < 0.8
- **Needs Optimization**: RTF > 0.8

## Troubleshooting Guide

### Common Issues
- **GPU not detected**: Requires CUDA 11.8+, falls back to CPU INT8 mode
- **UI crashes ("閃退")**: Use GPU-disabled launcher or check `electron_backend.log`
- **Model download fails**: Check internet connection, models auto-download to `~/.cache/huggingface/`
- **Encoding errors**: Ensure all files use UTF-8, check Python environment encoding

### Debug Commands
```bash
# Check Python environment
python -c "import sys; print(sys.version, sys.executable)"

# Test model loading
python srt_whisper_lite/electron-react-app/python/large_v3_int8_model_manager.py

# Check GPU support
python srt_whisper_lite/electron-react-app/python/test_gpu_support.py

# View logs
tail -f electron_backend.log
tail -f subtitle_generator.log
```

## Recent Updates (2025-08-27)

### CI/CD Infrastructure Complete
- **7-stage pipeline**: Unit → Integration → Performance → E2E → Build → Security → Deploy
- **GitHub Actions ready**: 12 workflow files configured and tested
- **Performance baselines established**: GPU RTF 0.736, CPU RTF 2.012
- **100% E2E success rate**: All 11 test scenarios passing

### Testing Framework Deployment
- **370 test files**: Comprehensive dataset from 5s clips to 73.8h videos
- **5-tier performance classification**: Automatic RTF-based performance grading
- **Automated test suites**: Quick validation, standard benchmark, stress testing
- **Enterprise-grade pytest**: Full unit/integration/performance/E2E coverage

### FP16 Model Management (Priority)
- **Primary model**: Large V3 FP16 for highest accuracy (openai/whisper-large-v3-turbo)
- **GPU acceleration**: CUDA + Float16 for RTX 4070 (RTF < 0.15)
- **Fallback chain**: FP16 → INT8 → Medium model based on resources
- **Model manager**: `large_v3_fp16_performance_manager.py` handles optimization

## Package Structure

### File Organization
```
srt_whisper_lite/
├── electron-react-app/
│   ├── main.js                    # Electron main process
│   ├── package.json              # Node dependencies
│   ├── react-app/                # React frontend
│   ├── python/                   # Python backend modules
│   ├── mini_python/              # Embedded Python 3.11
│   ├── models/                   # AI models location
│   └── dist/                     # Build output
└── tests/                        # Complete test suite
```

### Build Outputs
- **NSIS Installer**: `dist/SRT-GO-Enhanced-v2.2.1-Setup.exe` (~500MB without models)
- **Complete Installer**: `dist/SRT-GO-Enhanced-v2.2.1-Complete.exe` (~2GB with models)
- **Portable Version**: `dist/win-unpacked/` (ready-to-run directory)
- **Models**: Auto-download to `~/.cache/huggingface/hub/` on first run