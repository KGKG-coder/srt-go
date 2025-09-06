# F 盤開發環境設置指南
# F-Drive Development Environment Setup Guide

**建立時間**: 2025-08-29  
**項目**: SRT GO v2.2.1 Enhanced AI Subtitle Generator  
**狀態**: ✅ 開發環境複製完成，準備開始開發

## 📋 復制內容摘要

已成功將 SRT GO 完整開發環境從 `C:\Users\USER-ART0\Desktop\SRTGO` 復制到 `F:\AI寫程式\語音轉字幕`，包含：

### ✅ 已復制的核心文件和目錄

#### 📁 主要文檔
- **README.md** - 項目概覽和安裝指南
- **CLAUDE.md** - 開發指南和架構細節  
- **CHANGELOG.md** - 版本歷史和更新
- **docs/** - 完整的文檔結構（27個文件，已組織整理）

#### 📁 核心開發目錄
- **engine/** - 核心引擎代碼
- **tests/** - 完整測試框架（單元/集成/性能/E2E測試）
- **optimizations/** - 性能優化相關代碼
- **packaging/** - 打包和分發工具
- **srt_whisper_lite/** - 主要應用程序代碼

#### 📁 Electron + React 應用
- **srt_whisper_lite/electron-react-app/** - 完整的 Electron + React 應用
  - **main.js** - Electron 主進程
  - **preload.js** - 預加載腳本
  - **package.json** - Node.js 依賴配置
  - **python/** - Python 後端模塊（核心 AI 引擎）
  - **mini_python/** - 嵌入式 Python 3.11 環境
  - **test_VIDEO/** - 測試視頻文件

#### 📁 Python 後端核心模塊
- **adaptive_voice_detector.py** - 25維自適應語音檢測
- **subeasy_multilayer_filter.py** - 5層智能過濾系統
- **large_v3_fp16_performance_manager.py** - GPU/CPU 性能優化
- **simplified_subtitle_core.py** - Faster-Whisper 核心引擎
- **electron_backend.py** - 主要後端入口點

## 🚀 開發環境啟動步驟

### 1. 環境檢查
```bash
# 進入項目目錄
cd "F:\AI寫程式\語音轉字幕"

# 檢查項目結構
dir
```

### 2. 安裝 Node.js 依賴
```bash
# 進入 Electron React 應用目錄
cd srt_whisper_lite\electron-react-app

# 安裝所有依賴
npm install

# 或者使用項目腳本
npm run install:all
```

### 3. 設置 Python 環境
```bash
# 安裝 Python 依賴
pip install -r requirements.txt

# 或安裝完整依賴（包含測試工具）
pip install -r requirements-test.txt
```

### 4. 驗證開發環境
```bash
# 運行集成測試
cd tests
python -m pytest integration/ -v

# 運行快速性能測試
cd tests\performance
python quick_rtf_test.py --basic-only

# 測試 Python 後端
cd srt_whisper_lite\electron-react-app
python python\electron_backend.py --help
```

## 🔧 開發命令

### 開發模式（熱重載）
```bash
cd srt_whisper_lite\electron-react-app
npm run dev
```

### 生產構建
```bash
# 構建應用（包含 AI 模型）
npm run build:with-models

# 創建 Windows 安裝程序
npm run dist:nsis

# 創建便攜版本
npm run dist:portable
```

### 測試套件
```bash
# 完整測試套件
cd tests
python -m pytest . -v

# E2E 自動化測試
cd tests\e2e
python test_automation_suite.py --quick-mode

# 性能基準測試
cd tests\performance
python comprehensive_performance_suite.py --standard
```

## 📊 項目狀態概覽

### ✅ 開發就緒狀態
- **版本**: v2.2.1 Enhanced (生產就緒)
- **架構**: Electron + React + Python 後端
- **AI 模型**: Faster-Whisper Large-v3-turbo (4-5x 加速)
- **測試覆蓋**: 100% E2E 成功率
- **CI/CD**: 7階段 GitHub Actions 管道完備

### 🎯 核心技術特性
- **FP16 性能優化**: GPU RTF < 0.15, CPU RTF < 0.8
- **自適應語音檢測**: 25維特徵，±0.05s 精度
- **SubEasy 5層過濾**: +15-25% 識別準確度提升
- **跨平台兼容**: Windows 10/11 完全支持
- **多語言支持**: 中文繁簡轉換、英語、日語、韓語

## 🔍 關鍵文件說明

### 配置文件
- **user_config.json** - 用戶配置
- **package.json** - Node.js 項目配置
- **requirements*.txt** - Python 依賴配置

### 核心入口點
- **main.js** - Electron 主進程（GUI 入口）
- **electron_backend.py** - Python 後端入口
- **engine_main.py** - 核心引擎入口

### 重要開發工具
- **run_tests.py** - 測試執行器
- **validate_ci_cd_setup.py** - CI/CD 驗證工具
- **deployment_verification.py** - 部署驗證腳本

## ⚠️ 開發注意事項

### 模型自動下載
- AI 模型會在首次運行時自動下載到 `~/.cache/huggingface/hub/`
- 確保網絡連接穩定，完整模型約 2.88GB

### GPU 加速（可選）
- 需要 CUDA 11.8+ 支持
- RTX 4070 等現代 GPU 可獲得 4-5x 性能提升
- 自動回退到 CPU INT8 模式

### 開發環境切換
如需在不同電腦間切換開發：
1. 復制整個 `F:\AI寫程式\語音轉字幕` 目錄
2. 重新運行 `npm install`
3. 驗證 Python 依賴：`pip install -r requirements.txt`

## 📞 故障排除

### 常見問題
1. **GUI 閃退**: 檢查 `electron_backend.log`，使用 GPU 禁用啟動器
2. **模型下載失敗**: 檢查網絡連接，清除 HuggingFace 緩存
3. **編碼錯誤**: 確保所有文件使用 UTF-8 編碼

### 調試命令
```bash
# 檢查 Python 環境
python -c "import sys; print(sys.version, sys.executable)"

# 測試模型加載
python srt_whisper_lite\electron-react-app\python\large_v3_fp16_performance_manager.py

# 檢查 GPU 支持
python srt_whisper_lite\electron-react-app\python\test_gpu_support.py
```

---

## 🎉 開發繼續確認

✅ **開發環境復制成功**  
✅ **所有核心文件就位**  
✅ **文檔和配置完整**  
✅ **測試框架可用**  
✅ **CI/CD 管道就緒**

**現在可以在 F 盤環境中無縫繼續 SRT GO v2.2.1 的開發工作！**

---
*本設置指南於 2025-08-29 創建，用於確保跨計算機開發環境的連續性*