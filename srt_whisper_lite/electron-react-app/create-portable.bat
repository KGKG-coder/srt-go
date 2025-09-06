@echo off
echo ===============================
echo   SRT GO Portable Package Builder  
echo   Version 2.1.0
echo ===============================
echo.

REM 檢查打包目錄
if not exist "dist\win-unpacked" (
    echo Error: No unpacked build found at dist\win-unpacked
    echo Please run 'npm run build' first
    pause
    exit /b 1
)

echo Creating portable package...
echo.

REM 創建臨時目錄
if exist "dist\SRT-GO-Portable" rmdir /s /q "dist\SRT-GO-Portable"
mkdir "dist\SRT-GO-Portable"

echo Copying files...
xcopy "dist\win-unpacked\*.*" "dist\SRT-GO-Portable\" /E /Y /Q

REM 創建便攜版啟動檔
echo @echo off > "dist\SRT-GO-Portable\Start SRT GO.bat"
echo start "" "SRT GO - AI Subtitle Generator.exe" >> "dist\SRT-GO-Portable\Start SRT GO.bat"

REM 使用PowerShell壓縮成ZIP
echo.
echo Compressing to ZIP...
powershell -Command "Compress-Archive -Path 'dist\SRT-GO-Portable\*' -DestinationPath 'dist\SRT-GO-Portable-2.1.0.zip' -Force"

if exist "dist\SRT-GO-Portable-2.1.0.zip" (
    echo.
    echo ================================
    echo   Portable Package Created!
    echo ================================
    echo.
    echo File: dist\SRT-GO-Portable-2.1.0.zip
    
    REM 顯示檔案大小
    for %%A in ("dist\SRT-GO-Portable-2.1.0.zip") do (
        set size=%%~zA
        set /a sizeMB=!size! / 1048576
        echo Size: !sizeMB! MB
    )
    
    echo.
    echo This portable package can be extracted and run from any location!
) else (
    echo Failed to create portable package
)

REM 清理臨時目錄
if exist "dist\SRT-GO-Portable" rmdir /s /q "dist\SRT-GO-Portable"

echo.
pause