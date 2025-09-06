@echo off
echo 🚀 構建 SRT GO 雙層架構 - Python AI 引擎
echo ================================================

echo.
echo 📋 第一步：清理舊版本
if exist "dist\srt_engine.exe" del "dist\srt_engine.exe"
if exist "dist\srt_engine" rmdir /s /q "dist\srt_engine"
if exist "build" rmdir /s /q "build"

echo.
echo 📦 第二步：測試獨立引擎
python srt_engine_standalone.py --test
if %errorlevel% neq 0 (
    echo ❌ 獨立引擎測試失敗
    pause
    exit /b 1
)

echo.
echo ⚙️ 第三步：PyInstaller 打包
echo 正在使用 PyInstaller 打包 Python AI 引擎...
pyinstaller srt_engine.spec --clean --noconfirm

if %errorlevel% neq 0 (
    echo ❌ PyInstaller 打包失敗
    pause
    exit /b 1
)

echo.
echo 🔍 第四步：驗證打包結果
if not exist "dist\srt_engine.exe" (
    echo ❌ 找不到打包後的執行檔
    pause
    exit /b 1
)

echo.
echo 📊 打包結果：
for %%f in ("dist\srt_engine.exe") do echo   檔案大小: %%~zf bytes
echo   包含模型: base, medium（預置）

echo.
echo 🧪 第五步：測試打包後的執行檔
echo 測試獨立執行檔...
"dist\srt_engine.exe" --test
if %errorlevel% neq 0 (
    echo ❌ 打包後的執行檔測試失敗
    pause
    exit /b 1
)

echo.
echo ✅ Python AI 引擎打包完成！
echo 📁 輸出檔案: dist\srt_engine.exe
echo 🎯 下一步: 構建 Electron 應用程式並整合此引擎

echo.
echo 💡 使用方法：
echo   dist\srt_engine.exe --init medium     # 初始化模型
echo   dist\srt_engine.exe --process "..."   # 處理檔案

pause