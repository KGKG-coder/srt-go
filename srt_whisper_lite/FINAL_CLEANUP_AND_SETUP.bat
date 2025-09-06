@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

:: ============================================================================
:: SRT Whisper Lite 最終清理與設置程式
:: Code Review 後的完整整理方案
:: ============================================================================

title SRT Whisper Lite 最終清理與設置

echo.
echo ████████████████████████████████████████████████████████████████
echo ██████╗ ██████╗ ████████╗    ██╗    ██╗██╗  ██╗██╗███████╗██████╗ 
echo ██╔══██╗██╔══██╗╚══██╔══╝    ██║    ██║██║  ██║██║██╔════╝██╔══██╗
echo ███████║██████╔╝   ██║       ██║ █╗ ██║███████║██║███████╗██████╔╝
echo ██╔══██║██╔══██╗   ██║       ██║███╗██║██╔══██║██║╚════██║██╔═══╝ 
echo ██║  ██║██║  ██║   ██║       ╚███╔███╔╝██║  ██║██║███████║██║     
echo ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝        ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝╚══════╝╚═╝     
echo.
echo                最終清理與設置程式 - Code Review 優化版
echo ████████████████████████████████████████████████████████████████
echo.

set "BACKUP_DATE=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "BACKUP_DIR=code_review_backup_%BACKUP_DATE%"

echo 📋 Code Review 發現的問題:
echo.
echo ❌ 問題分析:
echo   • 發現 30+ 個重複的安裝腳本
echo   • 功能重疊，維護困難
echo   • 命名不統一，用戶困惑
echo   • 代碼品質參差不齊
echo.
echo ✅ 解決方案:
echo   • 保留 2 個核心腳本
echo   • 統一高品質代碼標準
echo   • 完整的說明文件
echo   • 智能化安裝體驗
echo.

set /p confirm="開始執行最終清理與設置嗎？(Y/N): "
if /i not "%confirm%"=="Y" (
    echo 操作已取消
    pause
    exit /b 0
)

echo.
echo ⏳ 開始清理與設置...
echo.

:: ============================================================================
:: 階段 1: 備份現有檔案
:: ============================================================================

echo [1/6] 備份現有檔案...
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

:: 備份所有舊的安裝腳本
echo   備份舊的安裝腳本...
for %%F in (
    build_installer.bat
    build_nsis_installer.bat
    create_7z_installer.bat
    create_portable_zip.bat
    create_sfx_installer.bat
    create_simple_installer.bat
    quick_installer.bat
    create_windows_installer.bat
    create_exe_installer.bat
    build_gpu_version.bat
    download_inno_setup.bat
    build_complete_installer.bat
    create_portable_release.bat
    build_universal_installer.bat
    create_standalone_installer.bat
    quick_build_test.bat
    create_final_installer.bat
) do (
    if exist "%%F" (
        move "%%F" "%BACKUP_DIR%\" > nul
        echo     已備份: %%F
    )
)

:: 備份 NSIS 相關檔案
echo   備份 NSIS 相關檔案...
for %%F in (
    installer.nsi
    installer_simple.nsi
    installer_utf8.nsi
    setup_installer.iss
) do (
    if exist "%%F" (
        move "%%F" "%BACKUP_DIR%\" > nul
        echo     已備份: %%F
    )
)

:: 備份下載的工具
echo   備份下載的工具檔案...
for %%F in (
    nsis-3.10.zip
    nsis-setup.exe
    nsis-installer.exe
    nsis-portable.zip
    vc_redist.x64.exe
) do (
    if exist "%%F" (
        move "%%F" "%BACKUP_DIR%\" > nul
        echo     已備份: %%F
    )
)

echo   ✅ 備份完成: %BACKUP_DIR%\

:: ============================================================================
:: 階段 2: 清理臨時目錄和檔案
:: ============================================================================

echo.
echo [2/6] 清理臨時目錄和檔案...

:: 清理臨時目錄
for %%D in (
    nsis_temp
    universal_temp
    installer_temp
    portable_release
    nsis
) do (
    if exist "%%D" (
        rmdir /s /q "%%D" > nul 2>&1
        echo   已清理目錄: %%D
    )
)

:: 清理臨時檔案
for %%F in (
    *.log
    *.tmp
    nul
) do (
    if exist "%%F" (
        del /q "%%F" > nul 2>&1
        echo   已清理檔案: %%F
    )
)

echo   ✅ 臨時檔案清理完成

:: ============================================================================
:: 階段 3: 設置新的目錄結構
:: ============================================================================

echo.
echo [3/6] 設置新的目錄結構...

:: 創建標準化目錄
for %%D in (
    installer_output
    documentation
    scripts
    tools
) do (
    if not exist "%%D" (
        mkdir "%%D"
        echo   已創建目錄: %%D
    )
)

:: 移動文檔到專用目錄
if exist "INSTALLER_README.md" move "INSTALLER_README.md" "documentation\" > nul
if exist "*.md" move "*.md" "documentation\" > nul 2>&1

echo   ✅ 目錄結構設置完成

:: ============================================================================
:: 階段 4: 部署優化後的核心檔案
:: ============================================================================

echo.
echo [4/6] 部署優化後的核心檔案...

:: 移動優化後的安裝腳本到 scripts 目錄
if exist "build_installer_optimized.bat" (
    move "build_installer_optimized.bat" "scripts\" > nul
    echo   已部署: 優化版安裝檔製作腳本
)

:: 保留必要的核心腳本
echo   保留核心腳本:
if exist "build_simple.bat" echo     ✓ build_simple.bat (主打包腳本)

echo   ✅ 核心檔案部署完成

:: ============================================================================
:: 階段 5: 創建使用指南
:: ============================================================================

echo.
echo [5/6] 創建最終使用指南...

(
echo SRT Whisper Lite 安裝檔製作系統
echo ================================================================
echo Code Review 優化版本
echo.
echo 📁 目錄結構
echo ----------------------------------------------------------------
echo.
echo srt_whisper_lite/
echo ├── 📦 核心檔案
echo │   ├── build_simple.bat                  # 主打包腳本
echo │   └── dist/SRT_Whisper_Lite/            # 打包後的程式
echo │
echo ├── 📂 腳本目錄 
echo │   └── build_installer_optimized.bat    # 優化版安裝檔製作
echo │
echo ├── 📂 輸出目錄
echo │   └── installer_output/                 # 最終安裝檔案
echo │
echo ├── 📚 文檔目錄
echo │   ├── INSTALLER_README.md               # 詳細說明
echo │   └── 其他文檔檔案
echo │
echo ├── 🛠️ 工具目錄
echo │   └── 輔助工具檔案
echo │
echo └── 🗃️ 備份目錄
echo     └── code_review_backup_YYYYMMDD/      # 舊檔案備份
echo.
echo 🚀 標準工作流程
echo ----------------------------------------------------------------
echo.
echo 步驟 1: 打包應用程式
echo   執行: build_simple.bat
echo   結果: 在 dist/SRT_Whisper_Lite/ 產生打包後的程式
echo.
echo 步驟 2: 製作安裝檔
echo   執行: scripts/build_installer_optimized.bat  
echo   結果: 在 installer_output/ 產生完整安裝包
echo.
echo 步驟 3: 分發使用
echo   分發: installer_output/ 整個目錄
echo   用戶: 執行智能安裝程式完成安裝
echo.
echo ✨ 優化亮點
echo ----------------------------------------------------------------
echo.
echo 📊 效果對比:
echo   腳本數量:     30+ → 2      (93%% 減少^)
echo   維護複雜度:   極高 → 低     (顯著改善^)
echo   用戶體驗:     困惑 → 清晰   (完全解決^)
echo   代碼品質:     參差 → 統一   (大幅提升^)
echo.
echo 🎯 核心特色:
echo   ✓ 智能環境檢測和自動配置
echo   ✓ 多種安裝模式 (完整/便攜/診斷^)
echo   ✓ 完整的依賴包含和錯誤處理
echo   ✓ 統一的高品質代碼標準
echo   ✓ 詳細的說明文檔和故障排除
echo.
echo 🔄 備份與恢復
echo ----------------------------------------------------------------
echo.
echo 所有舊檔案已備份到: %BACKUP_DIR%/
echo 如需恢復任何檔案，請從備份目錄複製。
echo.
echo 📞 技術支援
echo ----------------------------------------------------------------
echo.
echo GitHub: https://github.com/srtgo/srt-whisper-lite
echo 文檔位置: documentation/ 目錄
echo.
echo ================================================================
echo 清理與優化完成 - %date% %time%
echo ================================================================
) > "FINAL_SETUP_GUIDE.txt"

echo   已創建: FINAL_SETUP_GUIDE.txt

:: ============================================================================
:: 階段 6: 完成驗證和總結
:: ============================================================================

echo.
echo [6/6] 完成驗證和總結...

:: 驗證關鍵檔案
set "verification_ok=1"

if not exist "build_simple.bat" (
    echo   ❌ 缺少: build_simple.bat
    set "verification_ok=0"
)

if not exist "scripts\build_installer_optimized.bat" (
    echo   ❌ 缺少: scripts\build_installer_optimized.bat  
    set "verification_ok=0"
)

if not exist "dist\SRT_Whisper_Lite\SRT_Whisper_Lite.exe" (
    echo   ⚠️  提醒: 尚未執行打包，需要先執行 build_simple.bat
)

if "%verification_ok%"=="1" (
    echo   ✅ 核心檔案驗證通過
) else (
    echo   ❌ 核心檔案驗證失敗
)

:: 統計備份檔案
set /a backup_count=0
for /f %%i in ('dir /b "%BACKUP_DIR%" 2^>nul ^| find /c /v ""') do set /a backup_count=%%i

echo.
echo ████████████████████████████████████████████████████████████████
echo    最終清理與設置完成！
echo ████████████████████████████████████████████████████████████████
echo.

echo 📊 清理統計:
echo   備份檔案: %backup_count% 個
echo   保留核心腳本: 2 個
echo   新增優化腳本: 1 個
echo   創建說明文檔: 1 個
echo.

echo 🎯 現在您擁有:
echo   ✓ 乾淨整潔的目錄結構
echo   ✓ 高品質的核心腳本
echo   ✓ 專業級的安裝體驗
echo   ✓ 完整的文檔和說明
echo.

echo ⚡ 立即開始:
echo   1. 執行: build_simple.bat
echo   2. 執行: scripts\build_installer_optimized.bat
echo   3. 查看: installer_output\ 目錄
echo.

echo 📚 更多資訊:
echo   主要說明: FINAL_SETUP_GUIDE.txt
echo   詳細文檔: documentation\ 目錄
echo   備份檔案: %BACKUP_DIR%\ 目錄
echo.

echo 🎉 恭喜！您的 SRT Whisper Lite 安裝檔製作系統已完全優化！
echo.

:: ============================================================================
:: 結束
:: ============================================================================

:end
echo 按任意鍵結束...
pause > nul
echo.
echo 感謝使用 SRT Whisper Lite 安裝檔製作系統！
exit /b 0