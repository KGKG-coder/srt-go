@echo off
:: Admin Build Script for SRT GO Electron App
:: Please run as Administrator

title Admin Build - SRT GO Electron
chcp 65001 >nul

echo ========================================
echo  SRT GO Electron Admin Build Tool
echo ========================================
echo.
echo NOTE: Please run this script as Administrator!
echo.

:: Check admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Administrator privileges confirmed
) else (
    echo [ERROR] Administrator privileges required!
    echo.
    echo Please follow these steps:
    echo 1. Right-click this file
    echo 2. Select "Run as administrator"
    echo 3. Run this script again
    echo.
    pause
    exit /b 1
)

echo.
echo [1/6] Setting environment variables...
set CSC_IDENTITY_AUTO_DISCOVERY=false
set WIN_CSC_LINK=
set CSC_LINK=
set ELECTRON_BUILDER_ALLOW_UNRESOLVED_DEPENDENCIES=true
echo [OK] Environment variables set

echo.
echo [2/6] Cleaning old cache...
if exist "%APPDATA%\electron-builder\Cache" (
    echo Cleaning electron-builder cache...
    rd /s /q "%APPDATA%\electron-builder\Cache" 2>nul
)
if exist "dist" (
    echo Cleaning old build results...
    rd /s /q "dist" 2>nul
)
echo [OK] Cache cleaned

echo.
echo [3/6] Checking dependencies...
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    npm install
)
echo [OK] Dependencies checked

echo.
echo [4/6] Building React app...
cd react-app
if not exist "build" (
    echo React app not built, building now...
    npm run build
) else (
    echo [OK] React app already built
)
cd ..

echo.
echo [5/6] Starting Electron packaging...
echo This may take several minutes...
echo.

:: Use portable target, skip signing
npx electron-builder --win portable --publish=never

echo.
echo [6/6] Checking build results...
if exist "dist\*.exe" (
    echo.
    echo [SUCCESS] Packaging completed!
    echo.
    echo Generated files:
    dir dist\*.exe
    echo.
    echo Location: %cd%\dist\
    echo.
    echo Features:
    echo - Self-contained Electron app
    echo - No Node.js installation required
    echo - Beautiful React interface
    echo - Portable version
    echo.
    
    :: Ask for testing
    set /p test_choice="Test the packaged app now? (y/n): "
    if /i "%test_choice%"=="y" (
        echo Starting test...
        for %%f in (dist\*.exe) do start "" "%%f"
    )
    
) else (
    echo.
    echo [FAILED] Packaging failed: No output file found
    echo.
    echo Possible solutions:
    echo 1. Ensure running as Administrator
    echo 2. Check antivirus software
    echo 3. Ensure sufficient disk space
    echo 4. Check error messages above
)

echo.
echo Script completed
pause