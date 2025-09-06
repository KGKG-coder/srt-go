@echo off
setlocal enabledelayedexpansion

echo ===============================
echo   SRT GO Installer Builder
echo   Version 2.1.0
echo ===============================
echo.

REM 檢查是否有打包好的檔案
if not exist "dist\win-unpacked" (
    echo Error: No unpacked build found at dist\win-unpacked
    echo Please run 'npm run build' first
    pause
    exit /b 1
)

REM 檢查模型檔案
if not exist "..\models\whisper-large-model.zip" (
    echo Warning: Model file not found at ..\models\whisper-large-model.zip
    echo The installer will be created without the model file
    pause
)

REM 設置環境變數避免簽名錯誤
set CSC_IDENTITY_AUTO_DISCOVERY=false
set WIN_CSC_LINK=

echo Creating NSIS installer...
echo This may take a few minutes...
echo.

REM 執行 electron-builder 創建安裝檔
call npm run dist -- --win nsis

REM 檢查結果
if exist "dist\SRT-GO-Setup-*.exe" (
    echo.
    echo ================================
    echo   Installer Created Successfully!
    echo ================================
    
    REM 找到實際的安裝檔名稱
    for %%f in (dist\SRT-GO-Setup-*.exe) do (
        echo.
        echo Installer: %%f
        
        REM 顯示檔案大小
        for %%A in (%%f) do (
            set size=%%~zA
            set /a sizeMB=!size! / 1048576
            echo Size: !sizeMB! MB
        )
    )
    
    echo.
    echo You can now distribute this installer to users!
) else (
    echo.
    echo ================================
    echo   Failed to create installer
    echo ================================
    echo Please check the error messages above
)

echo.
pause