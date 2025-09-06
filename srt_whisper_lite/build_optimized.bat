@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

:: =======================================================
:: SRT Whisper Lite - 優化打包腳本
:: 生成精簡版安裝檔（預期大小：300-500MB）
:: =======================================================

echo.
echo ========================================
echo SRT Whisper Lite 優化打包程式
echo ========================================
echo.

:: 檢查 Python 3.11
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：未找到 Python 3.11
    echo 請確保已安裝 Python 3.11+ 並可通過 py -3.11 使用
    pause
    exit /b 1
)

:: 顯示當前配置
echo 📋 打包配置：
echo   - 使用優化版 build.spec
echo   - 排除測試和開發依賴
echo   - 啟用 UPX 壓縮
echo   - 預期大小：300-500MB
echo.

:: 詢問是否繼續
set /p confirm="是否開始打包？(Y/N): "
if /i not "%confirm%"=="Y" (
    echo 打包已取消
    pause
    exit /b 0
)

:: 清理舊的構建
echo.
echo [1/5] 清理舊的構建檔案...
if exist dist rmdir /s /q dist >nul 2>&1
if exist build rmdir /s /q build >nul 2>&1
echo ✅ 清理完成

:: 安裝最小依賴
echo.
echo [2/5] 檢查依賴...
py -3.11 -m pip install -r requirements-minimal.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo ❌ 依賴安裝失敗
    pause
    exit /b 1
)
echo ✅ 依賴檢查完成

:: 生成版本信息（可選）
echo.
echo [3/5] 準備版本信息...
(
echo # UTF-8
echo VSVersionInfo(
echo   ffi=FixedFileInfo(
echo     filevers=(2, 0, 0, 0^),
echo     prodvers=(2, 0, 0, 0^),
echo     mask=0x3f,
echo     flags=0x0,
echo     OS=0x40004,
echo     fileType=0x1,
echo     subtype=0x0,
echo     date=(0, 0^)
echo   ^),
echo   kids=[
echo     StringFileInfo([
echo       StringTable(
echo         '040904B0',
echo         [StringStruct('CompanyName', 'SRT GO Team'^),
echo          StringStruct('FileDescription', 'AI 智能字幕生成工具'^),
echo          StringStruct('FileVersion', '2.0.0.0'^),
echo          StringStruct('InternalName', 'SRT_Whisper_Lite'^),
echo          StringStruct('LegalCopyright', 'Copyright © 2025 SRT GO Team'^),
echo          StringStruct('OriginalFilename', 'SRT_Whisper_Lite.exe'^),
echo          StringStruct('ProductName', 'SRT Whisper Lite'^),
echo          StringStruct('ProductVersion', '2.0.0.0'^)]
echo       ^)
echo     ]^),
echo     VarFileInfo([VarStruct('Translation', [0x0409, 1200]^)]^)
echo   ]
echo ^)
) > file_version_info.txt
echo ✅ 版本信息已準備

:: 執行打包
echo.
echo [4/5] 開始打包（這可能需要幾分鐘）...
echo.
py -3.11 -m PyInstaller build_optimized.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo ❌ 打包失敗！
    echo 請檢查錯誤信息並修復問題
    pause
    exit /b 1
)

:: 檢查輸出
echo.
echo [5/5] 驗證打包結果...
if not exist "dist\SRT_Whisper_Lite\SRT_Whisper_Lite.exe" (
    echo ❌ 找不到輸出檔案！
    pause
    exit /b 1
)

:: 顯示檔案大小
for %%I in ("dist\SRT_Whisper_Lite\SRT_Whisper_Lite.exe") do set size=%%~zI
set /a sizeMB=%size% / 1048576
echo ✅ 主程式大小：%sizeMB% MB

:: 計算總大小
set totalSize=0
for /r "dist\SRT_Whisper_Lite" %%f in (*) do (
    set /a totalSize+=%%~zf
)
set /a totalSizeMB=%totalSize% / 1048576
echo ✅ 總大小：%totalSizeMB% MB

:: 清理臨時文件
del file_version_info.txt >nul 2>&1

:: 完成
echo.
echo ========================================
echo ✅ 打包完成！
echo ========================================
echo.
echo 📁 輸出位置：
echo    %cd%\dist\SRT_Whisper_Lite\
echo.
echo 📊 優化結果：
echo    原始大小：~2600 MB
echo    優化後：%totalSizeMB% MB
echo    減少：約 %expr 2600 - %totalSizeMB%% MB
echo.
echo 💡 下一步：
echo    1. 測試 dist\SRT_Whisper_Lite\SRT_Whisper_Lite.exe
echo    2. 如需進一步優化，修改 build_optimized.spec
echo    3. 使用 Inno Setup 創建安裝檔
echo.
pause