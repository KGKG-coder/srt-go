@echo off
chcp 65001 > NUL 2>&1
echo ============================================================
echo SRT GO 簡化版完整環境設置
echo 版本: 2.2.1-simplified
echo ============================================================
echo.

cd /d "%~dp0"

:: 檢查 mini_python 是否存在
if not exist "mini_python\python.exe" (
    echo [錯誤] 找不到 mini_python\python.exe
    echo 請確保以下目錄結構存在:
    echo   electron-react-app\
    echo   ├── mini_python\
    echo   │   └── python.exe
    echo   └── python\
    echo       └── electron_backend_simplified.py
    echo.
    pause
    exit /b 1
)

echo [1/5] 嵌入式 Python 環境設置
echo ============================================================
call setup_embedded_environment.bat
if errorlevel 1 (
    echo [錯誤] 環境設置失敗
    pause
    exit /b 1
)

echo.
echo [2/5] AI 模型下載 (可選)
echo ============================================================
echo 是否下載 AI 模型？
echo 注意：模型總大小約 1-3GB，需要良好的網路連線
set /p download_models="下載模型？ (Y/n): "

if /i "%download_models%"=="n" (
    echo [跳過] 模型下載
) else (
    echo 啟動模型下載程序...
    mini_python\python.exe setup_ai_models.py
)

echo.
echo [3/5] 環境完整性檢查
echo ============================================================
echo 檢查嵌入式環境...
mini_python\python.exe check_embedded_environment.py
if errorlevel 1 (
    echo [警告] 環境檢查發現問題，但將繼續...
)

echo.
echo [4/5] Node.js 依賴安裝
echo ============================================================
echo 安裝 Electron 和 React 依賴...
if exist "package.json" (
    call npm install
    if errorlevel 1 (
        echo [錯誤] npm install 失敗
        pause
        exit /b 1
    )
    
    cd react-app
    if exist "package.json" (
        call npm install
        if errorlevel 1 (
            echo [錯誤] React 依賴安裝失敗
            cd ..
            pause
            exit /b 1
        )
    )
    cd ..
) else (
    echo [警告] 找不到 package.json
)

echo.
echo [5/5] 最終測試
echo ============================================================
echo 執行後端測試...
call test_simplified_backend.bat

echo.
echo ============================================================
echo 設置完成！
echo ============================================================
echo.
echo 環境概覽:
echo   - 嵌入式 Python 3.11 (含所有 AI 依賴)
echo   - Faster-Whisper AI 引擎
echo   - 簡化後端 (無智能選擇)
echo   - Electron + React 前端
echo.
echo 使用方法:
echo   開發模式: npm run dev:simplified
echo   建置:     npm run build:simplified
echo   測試:     test_simplified_backend.bat
echo.
echo 故障排除:
echo   環境檢查: mini_python\python.exe check_embedded_environment.py
echo   重新設置: setup_embedded_environment.bat
echo.
pause