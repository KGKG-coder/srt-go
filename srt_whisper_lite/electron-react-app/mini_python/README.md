# SRT GO 嵌入式 Python 環境

## 環境狀態

此嵌入式 Python 3.11 環境目前存在 `_ctypes` 模組缺失的問題，這影響了某些科學計算包的正常載入。

### 目前可用的套件

✓ **完全可用的套件**:
- `huggingface_hub` (0.34.3) - 模型下載和管理
- `PyYAML` - YAML 配置文件支援
- `charset_normalizer` - 字符編碼處理
- `coloredlogs` - 彩色日誌輸出
- `urllib3` - HTTP 客戶端庫
- `requests` - HTTP 請求庫

⚠ **部分受限的套件** (需要 ctypes):
- `faster-whisper` (1.1.1) - 語音識別核心 **(已安裝但無法載入)**
- `soundfile` (0.12.1) - 音頻檔案處理 **(已安裝但無法載入)**
- `ctranslate2` (4.6.0) - AI 模型推理引擎 **(已安裝但無法載入)**

## 解決方案

### 方案 1: 使用系統 Python (推薦)

```bash
# 切換到系統 Python 環境進行處理
cd ../
python python/electron_backend_simplified.py --help
```

### 方案 2: 修復嵌入式環境

已提供修復工具，但由於 Windows 嵌入式 Python 的限制，修復成功率有限：

```bash
# 嘗試修復 ctypes 問題
python fix_ctypes_simple.py

# 驗證修復結果
python basic_verify.py
```

### 方案 3: 重新構建環境

如需完整重建嵌入式環境，建議：
1. 下載完整 Python 3.11 安裝包
2. 重新安裝所有依賴套件
3. 確保包含所有必需的 .pyd 檔案

## 應用程式執行建議

由於嵌入式環境存在限制，建議應用程式：

1. **優先使用系統 Python**: 檢測到系統 Python 時自動切換
2. **降級功能**: 當嵌入式環境不完整時，使用基礎功能
3. **用戶提示**: 明確告知用戶環境狀態和建議

## 測試指令

```bash
# 基礎環境驗證
python basic_verify.py

# 檢查套件安裝狀態  
python -m pip list

# 測試核心模組
python -c "import huggingface_hub; print('HuggingFace Hub OK')"
```

## 技術細節

- **Python 版本**: 3.11 (嵌入式版本)
- **缺失模組**: `_ctypes`, `_socket`, `_ssl` (部分)
- **影響功能**: 科學計算、音頻處理、AI 推理
- **建議方案**: 混合使用系統 Python + 嵌入式 Python

## 更新日期

最後更新: 2025-01-05
環境檢查工具版本: 1.0