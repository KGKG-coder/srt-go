@echo off
chcp 65001 > NUL 2>&1
echo ============================================================
echo 嵌入式 Python 環境完整設置
echo ============================================================
echo.

cd /d "%~dp0"

:: 檢查 mini_python 是否存在
if not exist "mini_python\python.exe" (
    echo [錯誤] 找不到 mini_python\python.exe
    echo 請確保 mini_python 資料夾存在
    pause
    exit /b 1
)

echo [步驟 1/5] 檢查 Python 版本...
mini_python\python.exe --version

echo.
echo [步驟 2/5] 升級 pip...
mini_python\python.exe -m pip install --upgrade pip --quiet

echo.
echo [步驟 3/5] 安裝核心依賴...
echo 這可能需要幾分鐘，請耐心等待...

:: 核心 AI 依賴
echo - 安裝 Faster-Whisper...
mini_python\python.exe -m pip install faster-whisper --quiet

echo - 安裝 NumPy...
mini_python\python.exe -m pip install "numpy>=1.24.0,<2.0.0" --quiet

echo - 安裝音頻處理庫...
mini_python\python.exe -m pip install librosa soundfile scipy --quiet

echo - 安裝機器學習庫...
mini_python\python.exe -m pip install scikit-learn --quiet

echo - 安裝工具庫...
mini_python\python.exe -m pip install tqdm requests --quiet

echo - 安裝 Hugging Face 支援...
mini_python\python.exe -m pip install huggingface-hub tokenizers --quiet

echo.
echo [步驟 4/5] 安裝可選依賴...
:: 可選但有用的依賴
mini_python\python.exe -m pip install pysrt webvtt-py --quiet 2>NUL
mini_python\python.exe -m pip install opencc-python-reimplemented jieba --quiet 2>NUL
mini_python\python.exe -m pip install pydub --quiet 2>NUL

echo.
echo [步驟 5/5] 驗證安裝...
echo.
echo 核心模組檢查:
mini_python\python.exe -c "import numpy; print('  NumPy: OK -', numpy.__version__)" 2>NUL || echo   NumPy: 失敗
mini_python\python.exe -c "import faster_whisper; print('  Faster-Whisper: OK')" 2>NUL || echo   Faster-Whisper: 失敗
mini_python\python.exe -c "import ctranslate2; print('  CTranslate2: OK -', ctranslate2.__version__)" 2>NUL || echo   CTranslate2: 失敗
mini_python\python.exe -c "import librosa; print('  Librosa: OK')" 2>NUL || echo   Librosa: 失敗
mini_python\python.exe -c "import soundfile; print('  SoundFile: OK')" 2>NUL || echo   SoundFile: 失敗
mini_python\python.exe -c "import sklearn; print('  Scikit-learn: OK')" 2>NUL || echo   Scikit-learn: 失敗
mini_python\python.exe -c "import tqdm; print('  TQDM: OK')" 2>NUL || echo   TQDM: 失敗
mini_python\python.exe -c "import huggingface_hub; print('  Hugging Face Hub: OK')" 2>NUL || echo   Hugging Face Hub: 失敗

echo.
echo ============================================================
echo 設置完成！
echo ============================================================
echo.
echo 下一步:
echo 1. 執行 test_simplified_backend.bat 測試後端
echo 2. 執行 npm run dev:simplified 啟動開發模式
echo.
pause