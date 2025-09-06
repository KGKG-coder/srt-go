@echo off
echo Creating Final Package for Enhanced Voice Detector v2.0
echo =====================================================

:: Clean up old builds
echo [1/5] Cleaning up old builds...
if exist "dist" (
    echo Removing old dist directory...
    rmdir /s /q "dist" 2>nul || echo "Some files may be in use, continuing..."
)

:: Build React app  
echo [2/5] Building React frontend...
cd react-app
call npm run build
if %errorlevel% neq 0 (
    echo Error building React app
    exit /b 1
)
cd ..

:: Create distribution directory structure
echo [3/5] Creating distribution structure...
if not exist "dist\SRT-GO-Enhanced-v2.0" mkdir "dist\SRT-GO-Enhanced-v2.0"

:: Copy main Electron files
echo [4/5] Copying application files...
copy "main.js" "dist\SRT-GO-Enhanced-v2.0\"
copy "preload.js" "dist\SRT-GO-Enhanced-v2.0\"
copy "package.json" "dist\SRT-GO-Enhanced-v2.0\"
copy "icon.ico" "dist\SRT-GO-Enhanced-v2.0\"

:: Copy React build
xcopy "react-app\build" "dist\SRT-GO-Enhanced-v2.0\react-app\build" /E /I /H /Y

:: Copy Python backend with Enhanced Voice Detector v2.0
xcopy "python" "dist\SRT-GO-Enhanced-v2.0\resources\python" /E /I /H /Y

:: Copy mini Python environment
xcopy "mini_python" "dist\SRT-GO-Enhanced-v2.0\resources\mini_python" /E /I /H /Y

:: Copy models if they exist
if exist "models" (
    xcopy "models" "dist\SRT-GO-Enhanced-v2.0\resources\models" /E /I /H /Y
)

:: Create launcher batch file
echo [5/5] Creating launcher...
echo @echo off > "dist\SRT-GO-Enhanced-v2.0\Launch SRT GO Enhanced.bat"
echo echo Starting SRT GO - Enhanced Voice Detector v2.0... >> "dist\SRT-GO-Enhanced-v2.0\Launch SRT GO Enhanced.bat"
echo start "" npx electron . >> "dist\SRT-GO-Enhanced-v2.0\Launch SRT GO Enhanced.bat"

:: Create README
echo Creating Enhanced Voice Detector v2.0 Package > "dist\SRT-GO-Enhanced-v2.0\README.txt"
echo ============================================= >> "dist\SRT-GO-Enhanced-v2.0\README.txt"
echo. >> "dist\SRT-GO-Enhanced-v2.0\README.txt"
echo This package contains the complete SRT GO system with: >> "dist\SRT-GO-Enhanced-v2.0\README.txt"
echo - Enhanced Voice Detector v2.0 (25-dimensional audio analysis) >> "dist\SRT-GO-Enhanced-v2.0\README.txt"
echo - Adaptive threshold optimization for different content types >> "dist\SRT-GO-Enhanced-v2.0\README.txt"
echo - Large-v3-turbo model support with GPU/CPU auto-detection >> "dist\SRT-GO-Enhanced-v2.0\README.txt"
echo - Professional subtitle generation with timing precision >> "dist\SRT-GO-Enhanced-v2.0\README.txt"
echo. >> "dist\SRT-GO-Enhanced-v2.0\README.txt"
echo To run: >> "dist\SRT-GO-Enhanced-v2.0\README.txt"
echo 1. Double-click "Launch SRT GO Enhanced.bat" >> "dist\SRT-GO-Enhanced-v2.0\README.txt"
echo 2. Or run: npx electron . in the package directory >> "dist\SRT-GO-Enhanced-v2.0\README.txt"
echo. >> "dist\SRT-GO-Enhanced-v2.0\README.txt"
echo Version: 2.2.0 Enhanced >> "dist\SRT-GO-Enhanced-v2.0\README.txt"
echo Date: 2025-08-20 >> "dist\SRT-GO-Enhanced-v2.0\README.txt"

echo.
echo =====================================================
echo Enhanced Voice Detector v2.0 Package Created!
echo =====================================================
echo Location: dist\SRT-GO-Enhanced-v2.0\
echo.
echo Package includes:
echo - Enhanced Voice Detector v2.0 with adaptive thresholds
echo - Complete Python backend with all optimizations
echo - Embedded Python 3.11 environment
echo - Modern Electron + React GUI
echo - All necessary dependencies
echo.
echo Ready for distribution and testing!
pause