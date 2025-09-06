@echo off
chcp 65001 >nul
title SRT GO - Environment Setup

echo ========================================
echo  SRT GO - Automatic Environment Setup
echo ========================================
echo.

:: Check if Python is already installed
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo [✓] Python is already installed
    for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
    echo     Version: %PYTHON_VERSION%
    goto :install_packages
)

echo [!] Python not found, installing...
echo.

:: Create temp directory
set TEMP_DIR=%TEMP%\srtgo_setup
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

:: Download Python installer
echo [1/3] Downloading Python 3.11...
set PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
set PYTHON_INSTALLER=%TEMP_DIR%\python-installer.exe

powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'}"

if not exist "%PYTHON_INSTALLER%" (
    echo [ERROR] Failed to download Python installer
    pause
    exit /b 1
)

echo [2/3] Installing Python...
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0

:: Wait for installation
timeout /t 10 /nobreak >nul

:: Refresh PATH
call "%~dp0refresh_path.bat"

:: Verify Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python installation failed
    pause
    exit /b 1
)

echo [✓] Python installed successfully

:install_packages
echo.
echo [3/3] Installing required packages...
echo This may take several minutes...

:: Upgrade pip
python -m pip install --upgrade pip

:: Install requirements
python -m pip install faster-whisper
python -m pip install librosa
python -m pip install soundfile
python -m pip install numpy
python -m pip install scipy

echo.
echo [✓] Environment setup completed successfully!
echo.
echo You can now use SRT GO to generate subtitles.
echo.

:: Cleanup
if exist "%TEMP_DIR%" rd /s /q "%TEMP_DIR%" 2>nul

pause