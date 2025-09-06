@echo off
echo ===============================================
echo    SRT Whisper Lite - GPU Version Build
echo ===============================================
echo.

echo [1/4] Checking environment...
if not exist "portable_python" (
    echo Creating portable_python environment...
    powershell -ExecutionPolicy Bypass -File "create_portable_python_gpu.ps1"
    if errorlevel 1 (
        echo Failed to create portable_python environment!
        pause
        exit /b 1
    )
) else (
    echo portable_python environment exists
)

echo.
echo [2/4] Checking Electron React app...
if not exist "electron-react-app\dist" (
    echo Building Electron React app...
    cd electron-react-app
    call npm run build
    if errorlevel 1 (
        echo Electron app build failed!
        cd ..
        pause
        exit /b 1
    )
    cd ..
    echo Electron React app build complete
) else (
    echo Electron React app already built
)

echo.
echo [3/4] Cleaning old versions...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"  
if exist "*.log" del /q "*.log"
echo Clean complete

echo.
echo [4/4] Starting PyInstaller packaging (GPU version)...
echo This may take 10-15 minutes...
echo.

pyinstaller build_final.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo Build failed! Please check error messages.
    pause
    exit /b 1
)

echo.
echo ===============================================
echo    GPU Version Build Complete!
echo ===============================================
echo.
echo File location: dist\SRT_Whisper_Lite\
echo Main program: dist\SRT_Whisper_Lite\SRT_Whisper_Lite.exe
echo.
echo This version supports:
echo - CUDA GPU acceleration (requires NVIDIA GPU and CUDA runtime)
echo - CPU fallback mode (automatic detection)
echo - Electron modern interface
echo - Full feature support
echo.

if exist "dist\SRT_Whisper_Lite\SRT_Whisper_Lite.exe" (
    echo Test the packaged result now? (Y/N)
    set /p test_choice=
    if /i "%test_choice%"=="Y" (
        echo Starting test...
        cd "dist\SRT_Whisper_Lite"
        start "" "SRT_Whisper_Lite.exe"
        cd ..\..
    )
)

echo.
echo Complete! Press any key to exit...
pause > nul