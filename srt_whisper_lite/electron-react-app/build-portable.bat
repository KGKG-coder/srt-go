@echo off
echo ========================================
echo  SRT GO Electron 便攜版打包
echo ========================================
echo.

:: 設置環境變量禁用簽名
set CSC_IDENTITY_AUTO_DISCOVERY=false
set WIN_CSC_LINK=
set CSC_LINK=

echo 1. 構建 React 應用...
cd react-app
call npm run build
cd ..

echo 2. 開始 Electron 打包（便攜版）...
echo 正在創建自包含的便攜版本...

:: 只打包便攜版，跳過簽名
npx electron-builder --win portable --publish=never

if exist "dist\*.exe" (
    echo.
    echo ✅ 打包成功！
    echo 📦 便攜版位置: dist\
    dir dist\*.exe
    echo.
    echo 🎉 現在您有了自包含的 Electron GUI！
    echo 無需安裝 Node.js，直接雙擊即可運行
) else (
    echo ❌ 打包失敗
)

echo.
pause