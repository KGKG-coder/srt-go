@echo off
echo 安裝必要依賴...
cd /d "%~dp0"

:: 找到 mini_python
set PYTHON_EXE=mini_python\python.exe
if not exist "%PYTHON_EXE%" (
    echo 錯誤：找不到 Python 環境
    pause
    exit /b 1
)

echo 使用 Python: %PYTHON_EXE%

:: 安裝基本依賴
echo 安裝 faster-whisper...
"%PYTHON_EXE%" -m pip install faster-whisper --no-deps --quiet

echo 安裝 numpy...
"%PYTHON_EXE%" -m pip install numpy --quiet

echo 安裝 av...
"%PYTHON_EXE%" -m pip install av --quiet

echo 安裝 soundfile...
"%PYTHON_EXE%" -m pip install soundfile --quiet

echo.
echo ✅ 依賴安裝完成！
pause
