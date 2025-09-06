@echo off
chcp 65001 > nul
echo ========================================
echo SRT GO 快速構建腳本
echo ========================================
echo.

cd electron-react-app

echo [1/4] 構建 React 應用...
cd react-app
call npm run build
cd ..

echo.
echo [2/4] 複製 preload.js 到正確位置...
if not exist "dist\win-unpacked" mkdir "dist\win-unpacked"
copy /Y "preload.js" "dist\win-unpacked\preload.js"
echo 已複製 preload.js

echo.
echo [3/4] 複製 Python 和模型資源...
if not exist "dist\win-unpacked\resources" mkdir "dist\win-unpacked\resources"
if not exist "dist\win-unpacked\resources\python" mkdir "dist\win-unpacked\resources\python"
if not exist "dist\win-unpacked\resources\mini_python" mkdir "dist\win-unpacked\resources\mini_python"
if not exist "dist\win-unpacked\resources\models" mkdir "dist\win-unpacked\resources\models"

xcopy /E /Y /Q "python\*" "dist\win-unpacked\resources\python\"
xcopy /E /Y /Q "mini_python\*" "dist\win-unpacked\resources\mini_python\" /EXCLUDE:exclude_list.txt
xcopy /E /Y /Q "models\*" "dist\win-unpacked\resources\models\"

echo.
echo [4/4] 測試應用程式...
cd dist\win-unpacked
if exist "SRT GO - AI Subtitle Generator.exe" (
    echo ✅ 可執行文件存在
) else (
    echo ⚠️ 可執行文件不存在，可能需要完整構建
    echo 運行: npm run dist
)

cd ..\..\..
echo.
echo ========================================
echo 構建完成！
echo 應用程式位置: electron-react-app\dist\win-unpacked
echo ========================================
pause