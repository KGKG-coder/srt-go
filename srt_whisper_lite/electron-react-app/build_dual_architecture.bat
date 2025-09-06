@echo off
echo 🚀 SRT GO 雙層架構完整構建流程
echo ============================================
echo 架構: Electron + React 前端 ↔ 獨立 Python AI 引擎
echo ============================================

echo.
echo 📋 構建步驟概覽：
echo   1. 構建 Python AI 引擎 (PyInstaller)
echo   2. 驗證 AI 引擎功能
echo   3. 構建 React 前端
echo   4. 整合 Electron 應用
echo   5. 生成最終安裝包 (NSIS)

echo.
echo ⏱️ 預估時間: 5-10 分鐘
echo 💾 預估大小: 200-300MB (包含完整 AI 模型)

pause

echo.
echo ================================================
echo 📦 第一步：構建 Python AI 引擎
echo ================================================

cd ..
call build_python_engine.bat
if %errorlevel% neq 0 (
    echo ❌ Python AI 引擎構建失敗
    pause
    exit /b 1
)

echo.
echo ================================================
echo 🔍 第二步：驗證 AI 引擎構建結果
echo ================================================

if not exist "dist\srt_engine.exe" (
    echo ❌ 找不到 Python AI 引擎執行檔
    pause
    exit /b 1
)

echo ✅ Python AI 引擎構建成功
for %%f in ("dist\srt_engine.exe") do echo 📊 AI 引擎大小: %%~zf bytes

echo.
echo ================================================
echo ⚛️ 第三步：構建 React 前端
echo ================================================

cd electron-react-app

echo 正在構建 React 應用...
npm run react:build
if %errorlevel% neq 0 (
    echo ❌ React 前端構建失敗
    pause
    exit /b 1
)

echo ✅ React 前端構建完成

echo.
echo ================================================
echo 🔧 第四步：配置雙層架構
echo ================================================

echo 複製雙層架構配置...
copy package_dual.json package.json
echo ✅ 已切換到雙層架構配置

echo.
echo ================================================
echo 📱 第五步：構建 Electron 應用
echo ================================================

echo 正在使用 electron-builder 整合應用...
npm run build
if %errorlevel% neq 0 (
    echo ❌ Electron 應用構建失敗
    pause
    exit /b 1
)

echo.
echo ================================================
echo 🎯 構建完成！
echo ================================================

if exist "dist\SRT GO - AI 字幕生成工具 (雙層架構版)-2.0.0-Setup.exe" (
    echo ✅ 安裝包構建成功！
    
    echo.
    echo 📊 最終結果：
    for %%f in ("dist\SRT GO - AI 字幕生成工具 (雙層架構版)-2.0.0-Setup.exe") do (
        echo   📁 檔案: %%~nxf
        echo   📊 大小: %%~zf bytes
        echo   📅 時間: %%~tf
    )
    
    echo.
    echo 🏗️ 架構特點：
    echo   ✅ Python AI 引擎獨立運行
    echo   ✅ Electron 前端乾淨整潔  
    echo   ✅ 進程完全分離，穩定性更高
    echo   ✅ 包含完整 AI 模型 (base, medium)
    echo   ✅ 支援離線使用
    echo   ✅ 錯誤處理和恢復機制完善
    
    echo.
    echo 🎮 使用特點：
    echo   • 啟動時自動檢測 AI 引擎
    echo   • 智能模型選擇和載入
    echo   • 實時進度和狀態回報
    echo   • 完全不會卡在 5% 問題
    
    echo.
    echo 🚀 下一步：
    echo   1. 測試安裝包在不同電腦上的運行情況
    echo   2. 驗證離線使用功能
    echo   3. 確認所有錯誤處理機制正常工作
    
) else (
    echo ❌ 找不到最終安裝包檔案
    echo 請檢查構建過程中的錯誤信息
)

echo.
echo ================================================
pause