@echo off
echo ===================================
echo 安裝嵌入式 Python 依賴
echo ===================================
echo.

cd /d "%~dp0"

echo 檢查 mini_python...
if not exist "mini_python\python.exe" (
    echo [錯誤] 找不到 mini_python\python.exe
    exit /b 1
)

echo.
echo 升級 pip...
mini_python\python.exe -m pip install --upgrade pip

echo.
echo 安裝核心依賴...
mini_python\python.exe -m pip install numpy
mini_python\python.exe -m pip install faster-whisper
mini_python\python.exe -m pip install soundfile
mini_python\python.exe -m pip install librosa

echo.
echo 驗證安裝...
mini_python\python.exe -c "import numpy; print('NumPy:', numpy.__version__)"
mini_python\python.exe -c "import faster_whisper; print('Faster-Whisper: OK')"

echo.
echo ===================================
echo 安裝完成
echo ===================================
pause