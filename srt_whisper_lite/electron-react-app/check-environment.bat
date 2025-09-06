@echo off
chcp 65001 >nul
echo =====================================
echo SRT GO 環境全面檢查與修復
echo =====================================

set "TARGET_DIR=dist\win-unpacked"
set "ELECTRON_DIST=node_modules\electron\dist"

echo 1. 檢查基本 Electron 運行檔案...
if not exist "%TARGET_DIR%\SRT GO - AI Subtitle Generator.exe" (
    echo ❌ 主執行檔不存在
    exit /b 1
) else (
    echo ✓ 主執行檔存在
)

echo.
echo 2. 檢查關鍵 DLL 檔案...

:: 檢查並複製 ffmpeg.dll
if not exist "%TARGET_DIR%\ffmpeg.dll" (
    echo 複製 ffmpeg.dll...
    if exist "%ELECTRON_DIST%\ffmpeg.dll" (
        copy "%ELECTRON_DIST%\ffmpeg.dll" "%TARGET_DIR%\"
        echo ✓ ffmpeg.dll 已複製
    ) else (
        echo ❌ 找不到 ffmpeg.dll 源檔案
    )
) else (
    echo ✓ ffmpeg.dll 已存在
)

:: 檢查其他重要 DLL
set "REQUIRED_DLLS=libGLESv2.dll libEGL.dll d3dcompiler_47.dll vk_swiftshader.dll vulkan-1.dll"
for %%f in (%REQUIRED_DLLS%) do (
    if not exist "%TARGET_DIR%\%%f" (
        echo 複製 %%f...
        if exist "%ELECTRON_DIST%\%%f" (
            copy "%ELECTRON_DIST%\%%f" "%TARGET_DIR%\"
            echo ✓ %%f 已複製
        ) else (
            echo ⚠️ 找不到 %%f
        )
    ) else (
        echo ✓ %%f 已存在
    )
)

echo.
echo 3. 檢查 Node.js 運行時...
if not exist "%TARGET_DIR%\node.dll" (
    echo 複製 node.dll...
    if exist "%ELECTRON_DIST%\node.dll" (
        copy "%ELECTRON_DIST%\node.dll" "%TARGET_DIR%\"
        echo ✓ node.dll 已複製
    )
) else (
    echo ✓ node.dll 已存在
)

echo.
echo 4. 檢查必要資源檔案...
if not exist "%TARGET_DIR%\resources.pak" (
    echo 複製 resources.pak...
    if exist "%ELECTRON_DIST%\resources.pak" (
        copy "%ELECTRON_DIST%\resources.pak" "%TARGET_DIR%\"
        echo ✓ resources.pak 已複製
    )
) else (
    echo ✓ resources.pak 已存在
)

echo.
echo 5. 檢查 V8 快照檔案...
if not exist "%TARGET_DIR%\v8_context_snapshot.bin" (
    echo 複製 v8_context_snapshot.bin...
    if exist "%ELECTRON_DIST%\v8_context_snapshot.bin" (
        copy "%ELECTRON_DIST%\v8_context_snapshot.bin" "%TARGET_DIR%\"
        echo ✓ v8_context_snapshot.bin 已複製
    )
) else (
    echo ✓ v8_context_snapshot.bin 已存在
)

if not exist "%TARGET_DIR%\snapshot_blob.bin" (
    echo 複製 snapshot_blob.bin...
    if exist "%ELECTRON_DIST%\snapshot_blob.bin" (
        copy "%ELECTRON_DIST%\snapshot_blob.bin" "%TARGET_DIR%\"
        echo ✓ snapshot_blob.bin 已複製
    )
) else (
    echo ✓ snapshot_blob.bin 已存在
)

echo.
echo 6. 檢查 ICU 數據檔案...
if not exist "%TARGET_DIR%\icudtl.dat" (
    echo 複製 icudtl.dat...
    if exist "%ELECTRON_DIST%\icudtl.dat" (
        copy "%ELECTRON_DIST%\icudtl.dat" "%TARGET_DIR%\"
        echo ✓ icudtl.dat 已複製
    )
) else (
    echo ✓ icudtl.dat 已存在
)

echo.
echo 7. 檢查 Python 環境...
if not exist "%TARGET_DIR%\resources\mini_python\python.exe" (
    echo ❌ Python 環境缺失
    exit /b 1
) else (
    echo ✓ Python 環境存在
)

echo.
echo 8. 檢查應用程式資源...
if not exist "%TARGET_DIR%\resources\app\main.js" (
    echo ❌ 應用程式主檔案缺失
    exit /b 1
) else (
    echo ✓ 應用程式資源存在
)

echo.
echo =====================================
echo 環境檢查完成！
echo =====================================

echo.
echo 9. 嘗試啟動程式進行測試...
start "" "%TARGET_DIR%\SRT GO - AI Subtitle Generator.exe"

echo 程式已啟動！如果出現錯誤，請檢查事件檢視器。
pause