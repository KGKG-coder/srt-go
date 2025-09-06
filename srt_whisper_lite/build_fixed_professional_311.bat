@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

:: =======================================================
:: SRT Whisper Lite - 修復版專業打包腳本 (Python 3.11)
:: 修正核心模組排除問題，解決 ModuleNotFoundError
:: =======================================================

echo.
echo ========================================
echo SRT Whisper Lite 修復版專業打包程式
echo Python 3.11 環境 - 修正版
echo ========================================
echo.

:: 檢查 Python 3.11
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：未找到 Python 3.11
    echo 請確保已安裝 Python 3.11 並可通過 py -3.11 使用
    pause
    exit /b 1
)

:: 顯示修復內容
echo 📋 修復版特色：
py -3.11 --version
echo   ✅ 修復 email 模組缺失問題
echo   ✅ 修復 xml 模組缺失問題  
echo   ✅ 修復 pickle 模組缺失問題
echo   ✅ 修復 pkg_resources 問題
echo   ✅ 保留所有核心功能
echo   ✅ 智能二進制優化
echo.

:: 詢問是否繼續
set /p confirm="是否開始修復版打包？(Y/N): "
if /i not "%confirm%"=="Y" (
    echo 打包已取消
    pause
    exit /b 0
)

:: 清理舊的構建
echo.
echo [1/6] 清理舊的構建檔案...
if exist dist\SRT_Whisper_Lite_Professional_Fixed rmdir /s /q "dist\SRT_Whisper_Lite_Professional_Fixed" >nul 2>&1
if exist build\build_fixed_professional rmdir /s /q "build\build_fixed_professional" >nul 2>&1
echo ✅ 清理完成

:: 檢查核心依賴
echo.
echo [2/6] 檢查核心依賴...
py -3.11 -m pip show faster-whisper >nul 2>&1
if errorlevel 1 (
    echo 🔧 正在安裝 faster-whisper...
    py -3.11 -m pip install faster-whisper --upgrade
)

py -3.11 -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 🔧 正在安裝 PyInstaller...
    py -3.11 -m pip install pyinstaller --upgrade
)
echo ✅ 核心依賴檢查完成

:: 安裝其他必要依賴
echo.
echo [3/6] 安裝專業版依賴...
py -3.11 -m pip install customtkinter pillow soundfile av scipy opencc jieba librosa noisereduce colorama tqdm --upgrade --quiet
echo ✅ 專業版依賴安裝完成

:: 生成版本信息
echo.
echo [4/6] 準備版本信息...
(
echo # UTF-8
echo VSVersionInfo(
echo   ffi=FixedFileInfo(
echo     filevers=(2, 1, 1, 0^),
echo     prodvers=(2, 1, 1, 0^),
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
echo          StringStruct('FileDescription', 'AI 智能字幕生成工具 - 修復版'^),
echo          StringStruct('FileVersion', '2.1.1.0'^),
echo          StringStruct('InternalName', 'SRT_Whisper_Lite_Professional_Fixed'^),
echo          StringStruct('LegalCopyright', 'Copyright © 2025 SRT GO Team'^),
echo          StringStruct('OriginalFilename', 'SRT_Whisper_Lite_Professional_Fixed.exe'^),
echo          StringStruct('ProductName', 'SRT Whisper Lite Professional Fixed'^),
echo          StringStruct('ProductVersion', '2.1.1.0'^))]
echo       ^)
echo     ]^),
echo     VarFileInfo([VarStruct('Translation', [0x0409, 1200]^)]^)
echo   ]
echo ^)
) > file_version_info.txt
echo ✅ 版本信息已準備

:: 執行修復版打包
echo.
echo [5/6] 開始修復版打包（這可能需要幾分鐘）...
echo.
py -3.11 -m PyInstaller build_fixed_professional.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo ❌ 打包失敗！
    echo 請檢查錯誤信息並修復問題
    pause
    exit /b 1
)

:: 檢查輸出
echo.
echo [6/6] 驗證打包結果...
if not exist "dist\SRT_Whisper_Lite_Professional_Fixed\SRT_Whisper_Lite_Professional_Fixed.exe" (
    echo ❌ 找不到輸出檔案！
    pause
    exit /b 1
)

:: 顯示檔案大小
for %%I in ("dist\SRT_Whisper_Lite_Professional_Fixed\SRT_Whisper_Lite_Professional_Fixed.exe") do set size=%%~zI
set /a sizeMB=%size% / 1048576
echo ✅ 主程式大小：%sizeMB% MB

:: 計算總大小
set totalSize=0
for /r "dist\SRT_Whisper_Lite_Professional_Fixed" %%f in (*) do (
    set /a totalSize+=%%~zf
)
set /a totalSizeMB=%totalSize% / 1048576
echo ✅ 總大小：%totalSizeMB% MB

:: 清理臨時文件
del file_version_info.txt >nul 2>&1

:: 完成
echo.
echo ========================================
echo ✅ 修復版專業打包完成！
echo ========================================
echo.
echo 📁 輸出位置：
echo    %cd%\dist\SRT_Whisper_Lite_Professional_Fixed\
echo.
echo 📊 修復版改進：
echo    ✅ 解決 ModuleNotFoundError
echo    ✅ 修復 email/xml/pickle 模組問題
echo    ✅ 完整 GPU 支援 (CUDA + cuDNN)  
echo    ✅ 所有 AI 功能 (Faster-Whisper + Torch)
echo    ✅ 高級音頻處理 (LibROSA + NoiseReduce)
echo    ✅ 多語言支援 (OpenCC + Jieba)
echo    ✅ 現代 GUI (CustomTkinter)
echo    總大小：%totalSizeMB% MB
echo.
echo 💡 下一步：
echo    1. 測試 dist\SRT_Whisper_Lite_Professional_Fixed\SRT_Whisper_Lite_Professional_Fixed.exe
echo    2. 驗證所有功能正常運作
echo    3. 如需進一步優化，可調整 build_fixed_professional.spec
echo.
pause