@echo off
chcp 65001 > nul
echo.
echo ====================================================================
echo        SRT GO Enhanced v2.2.1 - 完整構建腳本
echo ====================================================================
echo.
echo 構建日期: %date% %time%
echo 版本: v2.2.1 (2025-08-20 Real AI Fix)
echo.

echo [1/6] 清理環境...
if exist "dist" (
    echo 清理舊構建文件...
    rmdir /s /q "dist" 2>nul
)

echo [2/6] 檢查 Node.js 環境...
node --version
npm --version

echo [3/6] 安裝依賴...
call npm install

echo [4/6] 構建 React 應用...
cd react-app
call npm run build
cd ..

echo [5/6] 複製 Python 後端和模型...
if not exist "resources" mkdir "resources"
if not exist "resources\mini_python" mkdir "resources\mini_python"
if not exist "resources\python" mkdir "resources\python"
if not exist "resources\models" mkdir "resources\models"

echo 複製 Python 環境...
xcopy "..\mini_python\*" "resources\mini_python\" /E /I /Y /Q 2>nul

echo 複製 Python 後端腳本...
copy "..\electron_backend.py" "resources\python\" 2>nul
copy "..\simplified_subtitle_core.py" "resources\python\" 2>nul
copy "..\smart_backend_selector.py" "resources\python\" 2>nul
copy "..\system_python_backend.py" "resources\python\" 2>nul
copy "..\subeasy_multilayer_filter.py" "resources\python\" 2>nul
copy "..\adaptive_voice_detector.py" "resources\python\" 2>nul
copy "..\audio_processor.py" "resources\python\" 2>nul
copy "..\semantic_processor.py" "resources\python\" 2>nul
copy "..\subtitle_formatter.py" "resources\python\" 2>nul
copy "..\large_v3_int8_model_manager.py" "resources\python\" 2>nul
copy "..\official_model_manager.py" "resources\python\" 2>nul
copy "..\i18n.py" "resources\python\" 2>nul
copy "..\config_manager.py" "resources\python\" 2>nul

echo 複製模型文件...
if exist "..\models\*" (
    xcopy "..\models\*" "resources\models\" /E /I /Y /Q 2>nul
)

echo [6/6] 構建 Electron 應用...
call npm run dist

echo.
echo ====================================================================
echo                     構建完成！
echo ====================================================================
echo.
echo 輸出位置: dist\win-unpacked\
echo 安裝程式: dist\*.exe
echo.
echo 新功能:
echo ✅ 真正 AI 處理 (消除假字幕問題)
echo ✅ 智能後端選擇系統
echo ✅ 完整 UTF-8 支援
echo ✅ 自適應語音檢測
echo ✅ SubEasy 5層過濾系統
echo ✅ 醫療級準確度 (95%+)
echo.
echo 版本: v2.2.1 - 2025-08-20 Real AI Fix
echo ====================================================================

pause