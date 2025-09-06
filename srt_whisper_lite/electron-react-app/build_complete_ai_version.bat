@echo off
chcp 65001 > nul
echo.
echo ====================================================================
echo        SRT GO 完整版 AI 字幕生成器 - 構建腳本
echo ====================================================================
echo.
echo 構建日期: %date% %time%
echo 版本: v2.2.1 完整版 (系統Python + 完整AI)
echo.

echo [1/8] 清理環境...
if exist "dist" (
    echo 清理舊構建文件...
    rmdir /s /q "dist" 2>nul
)
if exist "node_modules" (
    echo 清理 Node 模組...
    rmdir /s /q "node_modules" 2>nul
)

echo [2/8] 檢查環境...
echo 檢查 Node.js...
node --version
npm --version

echo 檢查 Python...
python --version
python -c "import faster_whisper; print('Faster-Whisper:', 'OK')" 2>nul || echo "需要安裝 faster-whisper"

echo [3/8] 安裝依賴...
call npm install
if errorlevel 1 (
    echo 錯誤: Node.js 依賴安裝失敗
    pause
    exit /b 1
)

echo [4/8] 構建 React 應用...
cd react-app
call npm install
call npm run build
if errorlevel 1 (
    echo 錯誤: React 構建失敗
    cd ..
    pause
    exit /b 1
)
cd ..

echo [5/8] 準備 AI 模型...
echo 複製 AI 模型快取...
if not exist "models" mkdir "models"

set "HUGGINGFACE_CACHE=%USERPROFILE%\.cache\huggingface\hub"
if exist "%HUGGINGFACE_CACHE%" (
    echo 找到 Hugging Face 快取目錄
    for /d %%i in ("%HUGGINGFACE_CACHE%\models--*whisper*") do (
        echo 複製模型: %%~ni
        xcopy "%%i" "models\%%~ni\" /E /I /Y /Q 2>nul
    )
) else (
    echo 警告: 未找到 AI 模型快取，將在運行時下載
)

echo [6/8] 準備 Python 後端...
echo 複製 Python 腳本...
copy "python\electron_backend_ai_complete.py" "python\electron_backend_complete.py" 2>nul
copy "python\test_backend_minimal.py" "python\" 2>nul

echo [7/8] 構建 Electron 應用...
echo 使用簡化架構進行打包...
call npm run dist
if errorlevel 1 (
    echo 錯誤: Electron 構建失敗
    pause
    exit /b 1
)

echo [8/8] 創建發布包...
if exist "dist\win-unpacked" (
    echo ✅ 構建成功！
    echo.
    echo 輸出位置: dist\win-unpacked\
    if exist "dist\*.exe" (
        echo 安裝程式: dist\*.exe
    )
    
    echo.
    echo 完整版特性:
    echo ✅ 系統 Python 優先 + 嵌入式備用
    echo ✅ 完整 AI 語音轉錄功能 
    echo ✅ 自動模型下載管理
    echo ✅ 支援中英日韓多語言
    echo ✅ 標準 SRT 字幕格式
    echo ✅ 商業級部署就緒
    
) else (
    echo ❌ 構建失敗，請檢查錯誤訊息
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo                     構建完成！
echo ====================================================================
echo.
echo 版本: SRT GO v2.2.1 完整版
echo 架構: 系統 Python 優先 + 完整 AI 功能
echo 部署: 可直接分發給最終用戶
echo ====================================================================

pause