@echo off
REM Compression Analysis and Build Script
REM Analyzes file sizes and attempts ultra-compressed build

echo === SRT GO Ultra Compression Analysis ===
echo.

REM Check current portable version size
if exist "dist\SRT-GO-Portable-Working" (
    echo Analyzing current file sizes...
    
    REM Get Python environment size
    for /f %%A in ('powershell -command "(Get-ChildItem 'dist\SRT-GO-Portable-Working\resources\mini_python' -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB"') do set PYTHON_SIZE=%%A
    echo Python environment: %PYTHON_SIZE% MB
    
    REM Get AI models size  
    for /f %%A in ('powershell -command "(Get-ChildItem 'dist\SRT-GO-Portable-Working\resources\models' -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB"') do set MODEL_SIZE=%%A
    echo AI models: %MODEL_SIZE% MB
    
    REM Get application size
    for /f %%A in ('powershell -command "(Get-ChildItem 'dist\SRT-GO-Portable-Working\resources\app' -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB"') do set APP_SIZE=%%A
    echo Application: %APP_SIZE% MB
    
    echo.
    echo Compression targets:
    echo - Python: Exclude docs, tests, cache = ~30%% reduction
    echo - Models: Already optimized
    echo - App: Exclude source maps, docs = ~20%% reduction
    
    set /a TARGET_SIZE=%MODEL_SIZE% + %PYTHON_SIZE% * 70 / 100 + %APP_SIZE% * 80 / 100
    echo Estimated compressed size: %TARGET_SIZE% MB
    
    if %TARGET_SIZE% LSS 3072 (
        echo ✅ Target size under 3GB - NSIS should work!
    ) else (
        echo ❌ Still over 3GB - may need Inno Setup
    )
    
) else (
    echo Error: Portable version not found
    echo Please build portable version first
    pause
    exit /b 1
)

echo.
echo Building with ultra compression...
echo This will take 15-20 minutes due to maximum compression...
echo.

REM Build React app first
cd react-app
call npm run build
cd ..

REM Run ultra compressed build
call npx electron-builder --win nsis

if errorlevel 1 (
    echo.
    echo ❌ Ultra compressed build failed
    echo Trying with reduced compression...
    
    REM Fallback to lower compression
    powershell -Command "(Get-Content package.json) -replace '"compression": "maximum"', '"compression": "normal"' | Set-Content package.json"
    call npx electron-builder --win nsis
)

echo.
echo === Build Complete ===
echo Check dist\ directory for installer file
echo.

REM Analyze final installer size
for %%f in (dist\*.exe) do (
    echo Generated installer: %%f
    for %%A in ("%%f") do (
        set SIZE=%%~zA
        set /a SIZE_MB=!SIZE!/1024/1024
        echo Final installer size: !SIZE_MB! MB
        
        if !SIZE_MB! LSS 3072 (
            echo ✅ SUCCESS: Under 3GB limit!
        ) else (
            echo ⚠️ WARNING: Still over 3GB
        )
    )
)

pause