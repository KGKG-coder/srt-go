# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SRT GO is an AI-powered subtitle generation tool using Faster-Whisper, featuring a modern Electron + React GUI with adaptive voice detection and SubEasy 5-layer filtering. Version 2.2.1 focuses on production-ready deployment with real AI processing.

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
```

### Testing Python Backend
```bash
cd srt_whisper_lite/electron-react-app

# Test transcription directly
python python/electron_backend.py --files "[\"test_VIDEO/hutest.mp4\"]" --settings "{\"model\":\"large\",\"language\":\"auto\",\"enablePureVoiceMode\":true}" --corrections "[]"

# Run test suites
python python/test_adaptive_voice_detection.py  # Voice detection tests
python python/test_enhanced_integration.py       # Full integration test
python python/test_backend_integration.py        # Backend IPC tests
```

## Key Configuration

### Model Management (`large_v3_int8_model_manager.py`)
- **Model**: `openai/whisper-large-v3-turbo` or fallback to Medium
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

## Recent Critical Fixes (2025-08-20)

1. **Real AI Processing**: Fixed UI using demo subtitles → Now uses genuine faster-whisper
2. **IPC Communication**: Fixed UTF-8 encoding and parameter parsing errors
3. **Smart Backend System**: Implemented 3-tier fallback for robust operation
4. **Adaptive Voice Detection**: Fixed non-speech segments (DRLIN.mp4 segment 12: 20.350s→26.960s fixed to 25.308s→26.207s)

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
python python/large_v3_int8_model_manager.py

# Check GPU support
python python/test_gpu_support.py

# View logs
tail -f electron_backend.log
tail -f subtitle_generator.log
```