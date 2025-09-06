@echo off
echo =====================================
echo SRT GO - AI 字幕生成工具 打包腳本
echo =====================================

echo 1. 安裝/更新依賴...
call npm install
cd react-app
call npm install
cd ..

echo 2. 建構 React 應用...
cd react-app
call npm run build
cd ..

echo 3. 檢查 Python 環境...
python --version
if %errorlevel% neq 0 (
    echo 錯誤：未找到 Python 環境！
    echo 請確保已安裝 Python 3.8+ 並添加到 PATH
    pause
    exit /b 1
)

echo 4. 安裝 Python 依賴...
cd ..
pip install -r requirements.txt
cd electron-react-app

echo 5. 清理舊的打包文件...
if exist dist rmdir /s /q dist

echo 6. 開始打包...
echo 正在生成安裝檔和執行檔...
call npm run dist

echo 7. 打包完成！
echo 安裝檔位置: dist/
echo 可攜版位置: dist/
echo =====================================
echo 打包完成！請檢查 dist 目錄
echo =====================================

pause