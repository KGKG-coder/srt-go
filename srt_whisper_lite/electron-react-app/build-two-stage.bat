@echo off
REM Build SRT GO Two-Stage Installer

echo === Building SRT GO Two-Stage Installer ===
echo.

REM Step 1: Ensure React app is built
echo Building React app...
cd react-app
call npm run build
cd ..

if errorlevel 1 (
    echo React build failed
    pause
    exit /b 1
)

REM Step 2: Build Stage 1 installer (without models)
echo.
echo Building Stage 1 installer (base app only)...
copy package-stage1.json package.json.temp
copy package.json package.json.original
copy package-stage1.json package.json

call npx electron-builder --win nsis

if errorlevel 1 (
    echo Stage 1 build failed
    copy package.json.original package.json
    pause
    exit /b 1
)

REM Restore original package.json
copy package.json.original package.json
del package.json.temp
del package.json.original

echo.
echo ✅ Stage 1 installer build complete!
echo Check dist\ directory for: SRT GO - AI Subtitle Generator-Stage1-Setup-2.1.0.exe

REM Step 3: Create model package
echo.
echo Creating model package for Stage 2...
call create-model-package.bat

echo.
echo === Two-Stage Installer Build Complete ===
echo.
echo Next steps:
echo 1. Upload srt-go-models.zip to your download server
echo 2. Update MODELS_URL in stage1-installer-script.nsh
echo 3. Test the Stage 1 installer
echo.
pause