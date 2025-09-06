@echo off
title SRT GO Enhanced v2.2.1 安裝程式

echo ===============================================
echo    SRT GO Enhanced v2.2.1 AI 字幕生成工具
echo    完整版安裝程式
echo ===============================================
echo.

:: 檢查管理員權限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 需要管理員權限來安裝程式
    echo 請右鍵點擊此檔案並選擇「以系統管理員身分執行」
    pause
    exit /b 1
)

:: 設定安裝目錄
set "INSTALL_DIR=%ProgramFiles%\SRT GO Enhanced"
echo 安裝目錄: %INSTALL_DIR%
echo.

:: 創建安裝目錄
if not exist "%INSTALL_DIR%" (
    echo 創建安裝目錄...
    mkdir "%INSTALL_DIR%"
)

:: 複製檔案
echo 正在安裝 SRT GO Enhanced...
echo 這可能需要幾分鐘時間，請稍候...
echo.

xcopy "%~dp0win-unpacked\*" "%INSTALL_DIR%\" /E /I /H /Y >nul 2>&1
if %errorLevel% neq 0 (
    echo 安裝失敗！請檢查權限或磁碟空間。
    pause
    exit /b 1
)

:: 創建桌面捷徑
echo 創建桌面捷徑...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\SRT GO Enhanced v2.2.1.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\SRT GO - AI Subtitle Generator.exe'; $Shortcut.Save()"

:: 創建開始功能表捷徑
echo 創建開始功能表捷徑...
if not exist "%ProgramData%\Microsoft\Windows\Start Menu\Programs\SRT GO Enhanced" (
    mkdir "%ProgramData%\Microsoft\Windows\Start Menu\Programs\SRT GO Enhanced"
)
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ProgramData%\Microsoft\Windows\Start Menu\Programs\SRT GO Enhanced\SRT GO Enhanced.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\SRT GO - AI Subtitle Generator.exe'; $Shortcut.Save()"

:: 添加到程式和功能
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\SRT GO Enhanced" /v "DisplayName" /t REG_SZ /d "SRT GO Enhanced v2.2.1" /f >nul
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\SRT GO Enhanced" /v "DisplayVersion" /t REG_SZ /d "2.2.1" /f >nul
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\SRT GO Enhanced" /v "Publisher" /t REG_SZ /d "SRT GO Team" /f >nul
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\SRT GO Enhanced" /v "InstallLocation" /t REG_SZ /d "%INSTALL_DIR%" /f >nul
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\SRT GO Enhanced" /v "UninstallString" /t REG_SZ /d "%INSTALL_DIR%\uninstall.bat" /f >nul

:: 創建卸載腳本
echo @echo off > "%INSTALL_DIR%\uninstall.bat"
echo title SRT GO Enhanced v2.2.1 卸載程式 >> "%INSTALL_DIR%\uninstall.bat"
echo. >> "%INSTALL_DIR%\uninstall.bat"
echo echo 正在卸載 SRT GO Enhanced v2.2.1... >> "%INSTALL_DIR%\uninstall.bat"
echo. >> "%INSTALL_DIR%\uninstall.bat"
echo del "%%USERPROFILE%%\Desktop\SRT GO Enhanced v2.2.1.lnk" ^>nul 2^>^&1 >> "%INSTALL_DIR%\uninstall.bat"
echo rmdir /s /q "%%ProgramData%%\Microsoft\Windows\Start Menu\Programs\SRT GO Enhanced" ^>nul 2^>^&1 >> "%INSTALL_DIR%\uninstall.bat"
echo reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\SRT GO Enhanced" /f ^>nul 2^>^&1 >> "%INSTALL_DIR%\uninstall.bat"
echo cd /d "%%ProgramFiles%%" >> "%INSTALL_DIR%\uninstall.bat"
echo rmdir /s /q "SRT GO Enhanced" >> "%INSTALL_DIR%\uninstall.bat"
echo echo 卸載完成！ >> "%INSTALL_DIR%\uninstall.bat"
echo pause >> "%INSTALL_DIR%\uninstall.bat"

echo.
echo ===============================================
echo    安裝完成！
echo ===============================================
echo.
echo SRT GO Enhanced v2.2.1 已成功安裝到:
echo %INSTALL_DIR%
echo.
echo 功能特色:
echo - GPU 加速支援 (NVIDIA 顯示卡)
echo - Large V3 FP16 高精度 AI 模型
echo - 增強型語音檢測系統 v2.0
echo - 多語言字幕輸出支援
echo - 完整離線運作 (無需網路)
echo.
echo 使用方法:
echo 1. 從桌面或開始功能表啟動程式
echo 2. 拖拽音頻/視頻檔案到程式視窗
echo 3. 選擇語言和輸出格式
echo 4. 點擊「開始處理」生成字幕
echo.

set /p "launch=是否現在啟動 SRT GO Enhanced？(Y/N): "
if /i "%launch%"=="Y" (
    start "" "%INSTALL_DIR%\SRT GO - AI Subtitle Generator.exe"
)

echo.
echo 感謝您使用 SRT GO Enhanced！
pause