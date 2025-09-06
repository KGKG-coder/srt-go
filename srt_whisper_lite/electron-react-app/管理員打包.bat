@echo off
:: 請以管理員身份運行此腳本
title 管理員打包 - SRT GO Electron

echo ========================================
echo  SRT GO Electron 管理員打包工具
echo ========================================
echo.
echo 注意：請確保以管理員身份運行此腳本！
echo.

:: 檢查管理員權限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ 管理員權限確認
) else (
    echo ❌ 錯誤：需要管理員權限！
    echo.
    echo 請按以下步驟操作：
    echo 1. 右鍵點擊此文件
    echo 2. 選擇「以系統管理員身分執行」
    echo 3. 重新運行此腳本
    echo.
    pause
    exit /b 1
)

echo.
echo [1/6] 設置環境變數（禁用簽名）...
set CSC_IDENTITY_AUTO_DISCOVERY=false
set WIN_CSC_LINK=
set CSC_LINK=
set ELECTRON_BUILDER_ALLOW_UNRESOLVED_DEPENDENCIES=true
echo ✅ 環境變數設置完成

echo.
echo [2/6] 清理舊的緩存...
if exist "%APPDATA%\electron-builder\Cache" (
    echo 正在清理 electron-builder 緩存...
    rd /s /q "%APPDATA%\electron-builder\Cache" 2>nul
)
if exist "dist" (
    echo 正在清理舊的打包結果...
    rd /s /q "dist" 2>nul
)
echo ✅ 緩存清理完成

echo.
echo [3/6] 檢查依賴...
if not exist "node_modules" (
    echo 安裝 Node.js 依賴...
    npm install
)
echo ✅ 依賴檢查完成

echo.
echo [4/6] 構建 React 應用...
cd react-app
if not exist "build" (
    echo React 應用尚未構建，正在構建...
    npm run build
) else (
    echo ✅ React 應用已構建
)
cd ..

echo.
echo [5/6] 開始 Electron 打包...
echo 正在打包，這可能需要幾分鐘...
echo.

:: 使用便攜版目標，跳過簽名
npx electron-builder --win portable --publish=never

echo.
echo [6/6] 檢查打包結果...
if exist "dist\*.exe" (
    echo.
    echo ✅ 🎉 打包成功！
    echo.
    echo 📦 生成的文件：
    dir dist\*.exe
    echo.
    
    :: 獲取文件大小
    for %%f in (dist\*.exe) do (
        echo 文件：%%~nxf
        echo 大小：%%~zf bytes
    )
    
    echo.
    echo 🎊 恭喜！您現在有了自包含的 Electron 應用！
    echo 📍 位置：%cd%\dist\
    echo.
    echo 特色：
    echo • 無需安裝 Node.js 即可運行
    echo • 包含完整的 Electron runtime
    echo • 精美的 React 用戶界面
    echo • 便攜版，可複製到其他電腦使用
    echo.
    
    :: 詢問是否測試
    set /p test_choice="是否現在測試打包的應用？(y/n): "
    if /i "!test_choice!"=="y" (
        echo 啟動測試...
        start "" "dist\*.exe"
    )
    
) else (
    echo.
    echo ❌ 打包失敗：找不到輸出文件
    echo.
    echo 可能的解決方案：
    echo 1. 確保以管理員身份運行
    echo 2. 檢查防毒軟體是否阻擋
    echo 3. 確保有足夠的磁碟空間
    echo 4. 檢查上面的錯誤訊息
)

echo.
echo 腳本執行完成
pause