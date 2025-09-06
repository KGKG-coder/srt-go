@echo off
echo Building SRT GO Enhanced Voice Detector v2.0 Installer
echo =====================================================

:: Check if NSIS is installed
set "NSIS_PATH=C:\Program Files (x86)\NSIS\makensis.exe"
if not exist "%NSIS_PATH%" (
    echo ERROR: NSIS not found at %NSIS_PATH%
    echo Please install NSIS from https://nsis.sourceforge.io/Download
    echo.
    pause
    exit /b 1
)

:: Ensure package exists
if not exist "dist\SRT-GO-Enhanced-v2.0" (
    echo ERROR: Enhanced package not found!
    echo Please run create_final_package.bat first
    pause
    exit /b 1
)

:: Build installer
echo Building NSIS installer...
"%NSIS_PATH%" srt-go-enhanced-installer.nsi

if %errorlevel% equ 0 (
    echo.
    echo =====================================================
    echo SUCCESS: Installer created successfully!
    echo =====================================================
    echo Location: dist\SRT-GO-Enhanced-Voice-Detector-v2.0-Setup.exe
    echo Ready for distribution!
) else (
    echo ERROR: Installer compilation failed!
)

pause
