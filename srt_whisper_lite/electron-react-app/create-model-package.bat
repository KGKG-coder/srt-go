@echo off
REM Create SRT GO Models Package
REM This creates the separate models.zip file for stage 2 download

echo === Creating SRT GO Models Package ===
echo.

set SOURCE_DIR=dist\SRT-GO-Portable-Working\resources\models
set OUTPUT_FILE=srt-go-models.zip
set TEMP_DIR=temp_models

if not exist "%SOURCE_DIR%" (
    echo Error: Source models directory not found: %SOURCE_DIR%
    echo Please ensure the portable version is built first.
    pause
    exit /b 1
)

echo Creating temporary directory...
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

echo Copying model files...
xcopy "%SOURCE_DIR%\*" "%TEMP_DIR%\" /s /e /y

echo Creating ZIP archive...
if exist "%OUTPUT_FILE%" del "%OUTPUT_FILE%"

REM Use PowerShell to create ZIP
powershell -Command "& {Compress-Archive -Path '%TEMP_DIR%\*' -DestinationPath '%OUTPUT_FILE%' -CompressionLevel Optimal}"

if exist "%OUTPUT_FILE%" (
    echo.
    echo ✅ Model package created successfully: %OUTPUT_FILE%
    
    REM Get file size
    for %%A in ("%OUTPUT_FILE%") do (
        set SIZE=%%~zA
        set /a SIZE_MB=!SIZE!/1024/1024
        echo Package size: !SIZE_MB! MB
    )
    
    echo.
    echo Upload this file to your release/download server
    echo Update the MODELS_URL in stage1-installer-script.nsh accordingly
) else (
    echo ❌ Failed to create model package
)

echo.
echo Cleaning up temporary files...
rmdir /s /q "%TEMP_DIR%"

echo.
echo === Model Package Creation Complete ===
pause