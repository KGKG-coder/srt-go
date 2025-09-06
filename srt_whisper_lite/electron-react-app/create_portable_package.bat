@echo off
chcp 65001 >nul
echo 🚀 創建 SRT GO Enhanced v2.0 便攜版執行檔包
echo ===================================================
echo.

set "SOURCE_DIR=C:\Users\USER-ART0\Desktop\SRTGO\srt_whisper_lite\electron-react-app\dist\SRT-GO-Enhanced-v2.0"
set "PORTABLE_DIR=C:\Users\USER-ART0\Desktop\SRTGO\srt_whisper_lite\electron-react-app\dist\SRT-GO-Enhanced-v2.0-Portable"
set "ARCHIVE_NAME=SRT-GO-Enhanced-v2.0-Portable.7z"

echo 📁 檢查來源目錄...
if not exist "%SOURCE_DIR%" (
    echo ❌ 錯誤：來源目錄不存在
    pause
    exit /b 1
)

echo ✅ 來源目錄確認存在
echo.

echo 🧹 清理舊的便攜版目錄...
if exist "%PORTABLE_DIR%" rmdir /s /q "%PORTABLE_DIR%"

echo 📋 複製核心檔案到便攜版目錄...
mkdir "%PORTABLE_DIR%"

echo   → 複製 main.js (Electron主程序)
copy "%SOURCE_DIR%\main.js" "%PORTABLE_DIR%\" >nul
copy "%SOURCE_DIR%\preload.js" "%PORTABLE_DIR%\" >nul
copy "%SOURCE_DIR%\package.json" "%PORTABLE_DIR%\" >nul
copy "%SOURCE_DIR%\environment-manager.js" "%PORTABLE_DIR%\" >nul
copy "%SOURCE_DIR%\icon.ico" "%PORTABLE_DIR%\" >nul

echo   → 複製 React 前端應用...
xcopy "%SOURCE_DIR%\react-app" "%PORTABLE_DIR%\react-app" /e /i /q >nul

echo   → 複製 Python 執行環境...
xcopy "%SOURCE_DIR%\resources\mini_python" "%PORTABLE_DIR%\resources\mini_python" /e /i /q >nul

echo   → 複製 AI 模型...
xcopy "%SOURCE_DIR%\resources\models" "%PORTABLE_DIR%\resources\models" /e /i /q >nul

echo   → 複製 Python 後端...
xcopy "%SOURCE_DIR%\resources\python" "%PORTABLE_DIR%\resources\python" /e /i /q >nul

echo.
echo 🧹 清理不必要的檔案...

rem 移除測試和調試檔案
del "%PORTABLE_DIR%\resources\python\electron_backend.log" 2>nul
del "%PORTABLE_DIR%\resources\mini_python\electron_backend.log" 2>nul

rem 移除備份和測試目錄
if exist "%PORTABLE_DIR%\resources\python\cleanup_backup" rmdir /s /q "%PORTABLE_DIR%\resources\python\cleanup_backup"
if exist "%PORTABLE_DIR%\resources\python\comparison_output" rmdir /s /q "%PORTABLE_DIR%\resources\python\comparison_output"

rem 移除測試腳本
del "%PORTABLE_DIR%\resources\python\test_*.py" 2>nul
del "%PORTABLE_DIR%\resources\python\*_test.py" 2>nul
del "%PORTABLE_DIR%\resources\python\*.json" 2>nul

echo.
echo 📄 創建啟動腳本...

echo @echo off > "%PORTABLE_DIR%\SRT GO Enhanced v2.0.bat"
echo chcp 65001 ^>nul >> "%PORTABLE_DIR%\SRT GO Enhanced v2.0.bat"
echo cd /d "%%~dp0" >> "%PORTABLE_DIR%\SRT GO Enhanced v2.0.bat"
echo echo 🚀 啟動 SRT GO Enhanced v2.0... >> "%PORTABLE_DIR%\SRT GO Enhanced v2.0.bat"
echo echo. >> "%PORTABLE_DIR%\SRT GO Enhanced v2.0.bat"
echo if not exist "node_modules\electron\dist\electron.exe" ( >> "%PORTABLE_DIR%\SRT GO Enhanced v2.0.bat"
echo     echo 📦 安裝 Electron 執行環境... >> "%PORTABLE_DIR%\SRT GO Enhanced v2.0.bat"
echo     npm install electron --save-dev >> "%PORTABLE_DIR%\SRT GO Enhanced v2.0.bat"
echo ) >> "%PORTABLE_DIR%\SRT GO Enhanced v2.0.bat"
echo start "" npx electron . >> "%PORTABLE_DIR%\SRT GO Enhanced v2.0.bat"

echo.
echo 📄 創建說明文件...

echo # SRT GO Enhanced v2.0 便攜版 > "%PORTABLE_DIR%\README.md"
echo. >> "%PORTABLE_DIR%\README.md"
echo ## 🚀 快速開始 >> "%PORTABLE_DIR%\README.md"
echo. >> "%PORTABLE_DIR%\README.md"
echo 1. 雙擊 `SRT GO Enhanced v2.0.bat` 啟動應用程式 >> "%PORTABLE_DIR%\README.md"
echo 2. 首次運行會自動安裝 Electron 執行環境 >> "%PORTABLE_DIR%\README.md"
echo 3. 拖拽視頻檔案到應用程式中開始生成字幕 >> "%PORTABLE_DIR%\README.md"
echo. >> "%PORTABLE_DIR%\README.md"
echo ## 🎯 特色功能 >> "%PORTABLE_DIR%\README.md"
echo. >> "%PORTABLE_DIR%\README.md"
echo - Enhanced Voice Detector v2.0 - 25維音頻特徵分析 >> "%PORTABLE_DIR%\README.md"
echo - Large V3 Turbo INT8 模型 - 快速高精度字幕生成 >> "%PORTABLE_DIR%\README.md"
echo - 自適應內容檢測 - 自動識別對話、宣傳片等類型 >> "%PORTABLE_DIR%\README.md"
echo - 多語言支援 - 中文、英文、日文、韓文 >> "%PORTABLE_DIR%\README.md"
echo - 多格式輸出 - SRT、VTT、TXT、JSON >> "%PORTABLE_DIR%\README.md"
echo. >> "%PORTABLE_DIR%\README.md"
echo ## 💻 系統需求 >> "%PORTABLE_DIR%\README.md"
echo. >> "%PORTABLE_DIR%\README.md"
echo - Windows 10/11 (64-bit) >> "%PORTABLE_DIR%\README.md"
echo - 4GB RAM 以上 >> "%PORTABLE_DIR%\README.md"
echo - Node.js 16+ (自動安裝) >> "%PORTABLE_DIR%\README.md"
echo. >> "%PORTABLE_DIR%\README.md"
echo *版本: v2.0.0 - Enhanced Voice Detection Edition* >> "%PORTABLE_DIR%\README.md"

echo.
echo 📊 計算檔案大小...
for /f "tokens=3" %%a in ('dir "%PORTABLE_DIR%" /s /-c ^| findstr /E "個檔案"') do set TOTAL_SIZE=%%a

echo   → 便攜版總大小: %TOTAL_SIZE% 位元組
echo.

echo ✅ 便攜版執行檔包創建完成！
echo 📁 位置: %PORTABLE_DIR%
echo.

echo 📦 是否要創建 7z 壓縮檔？(y/n)
set /p CREATE_ARCHIVE=

if /i "%CREATE_ARCHIVE%"=="y" (
    echo.
    echo 🗜️ 創建 7z 壓縮檔...
    cd /d "%PORTABLE_DIR%\.."
    if exist "C:\Program Files\7-Zip\7z.exe" (
        "C:\Program Files\7-Zip\7z.exe" a -t7z -m0=lzma2 -mx=9 -mfb=64 -md=32m -ms=on -mmt=on "%ARCHIVE_NAME%" "SRT-GO-Enhanced-v2.0-Portable\*" >nul
        echo ✅ 壓縮檔創建完成: %ARCHIVE_NAME%
    ) else (
        echo ❌ 未找到 7-Zip，跳過壓縮
    )
)

echo.
echo 🎉 便攜版包裝完成！
pause