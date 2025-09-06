@echo off
echo ===================================
echo 測試簡化版後端
echo ===================================
echo.

echo 1. 檢查嵌入式 Python...
if exist "mini_python\python.exe" (
    echo [OK] 找到嵌入式 Python
    mini_python\python.exe --version
) else (
    echo [錯誤] 找不到嵌入式 Python
    exit /b 1
)

echo.
echo 2. 檢查簡化版後端腳本...
if exist "python\electron_backend_simplified.py" (
    echo [OK] 找到簡化版後端腳本
) else (
    echo [警告] 找不到簡化版，使用標準版
)

echo.
echo 3. 測試 Python 模組導入...
mini_python\python.exe -c "import sys; print(f'Python路徑: {sys.executable}')"
mini_python\python.exe -c "import numpy; print('NumPy: OK')" 2>nul || echo NumPy: 未安裝
mini_python\python.exe -c "import faster_whisper; print('Faster-Whisper: OK')" 2>nul || echo Faster-Whisper: 未安裝

echo.
echo 4. 測試簡化版後端執行...
if exist "test_VIDEO\hutest.mp4" (
    echo 使用測試影片: test_VIDEO\hutest.mp4
    mini_python\python.exe python\electron_backend_simplified.py --files "[\"test_VIDEO/hutest.mp4\"]" --settings "{\"model\":\"large\",\"language\":\"auto\",\"enablePureVoiceMode\":true}" --corrections "[]"
) else (
    echo [跳過] 找不到測試影片
)

echo.
echo ===================================
echo 測試完成
echo ===================================
pause