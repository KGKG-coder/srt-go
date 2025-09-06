@echo off
echo =====================================
echo 修復 SRT GO 打包配置
echo =====================================

echo 1. 確認 mini_python 位置...
if not exist "..\mini_python\python.exe" (
    echo 錯誤：找不到 mini_python！
    pause
    exit /b 1
)

echo 2. 複製 mini_python 到臨時位置...
if exist "temp_resources" rmdir /s /q "temp_resources"
mkdir temp_resources\mini_python
xcopy /E /I /Y "..\mini_python" "temp_resources\mini_python"

echo 3. 清理舊的打包文件...
if exist dist rmdir /s /q dist

echo 4. 安裝依賴...
call npm install
cd react-app
call npm install
cd ..

echo 5. 建構 React 應用...
cd react-app
call npm run build
cd ..

echo 6. 開始打包（包含 NSIS 和 ZIP）...
call npm run dist

echo 7. 手動複製 mini_python 到打包輸出...
if exist "dist\win-unpacked\resources" (
    echo 複製 mini_python 到解壓版本...
    xcopy /E /I /Y "..\mini_python" "dist\win-unpacked\resources\mini_python"
)

echo 8. 驗證打包結果...
if exist "dist\win-unpacked\resources\mini_python\python.exe" (
    echo ✓ mini_python 已成功包含
) else (
    echo ✗ 警告：mini_python 未正確包含
)

if exist "dist\SRT-GO-Setup-*.exe" (
    echo ✓ NSIS 安裝程式已生成
) else (
    echo ✗ 警告：NSIS 安裝程式未生成
)

if exist "dist\SRT-GO-Setup-*.zip" (
    echo ✓ ZIP 壓縮包已生成
) else (
    echo ✗ 警告：ZIP 壓縮包未生成
)

echo =====================================
echo 打包完成！請檢查 dist 目錄
echo =====================================

echo.
echo 檔案位置：
dir dist\*.exe /b 2>nul
dir dist\*.zip /b 2>nul

pause