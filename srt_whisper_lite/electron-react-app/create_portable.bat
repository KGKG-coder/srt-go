@echo off
echo 創建便攜式版本...

:: 創建便攜式目錄結構
mkdir "SRT_GO_Portable\resources\mini_python"
mkdir "SRT_GO_Portable\resources\python"

:: 複製主程式
copy "dist\win-unpacked\*.exe" "SRT_GO_Portable\"
copy "dist\win-unpacked\*.dll" "SRT_GO_Portable\"
xcopy /E /I "dist\win-unpacked\locales" "SRT_GO_Portable\locales"
xcopy /E /I "dist\win-unpacked\resources" "SRT_GO_Portable\resources"

:: 確保 Python 環境完整
xcopy /E /I "..\mini_python" "SRT_GO_Portable\resources\mini_python"

:: 複製 Python 腳本
copy "..\electron_backend.py" "SRT_GO_Portable\resources\python\"
copy "..\simplified_subtitle_core.py" "SRT_GO_Portable\resources\python\"
copy "..\audio_processor.py" "SRT_GO_Portable\resources\python\"
copy "..\semantic_processor.py" "SRT_GO_Portable\resources\python\"
copy "..\subtitle_formatter.py" "SRT_GO_Portable\resources\python\"
copy "..\config_manager.py" "SRT_GO_Portable\resources\python\"
copy "..\i18n.py" "SRT_GO_Portable\resources\python\"
copy "..\logo_manager.py" "SRT_GO_Portable\resources\python\"
copy "..\custom_corrections.json" "SRT_GO_Portable\resources\python\"
copy "..\user_config.json" "SRT_GO_Portable\resources\python\"

:: 創建啟動批次檔
echo @echo off > "SRT_GO_Portable\啟動.bat"
echo cd /d "%%~dp0" >> "SRT_GO_Portable\啟動.bat"
echo start "" "SRT GO - AI 字幕生成工具.exe" >> "SRT_GO_Portable\啟動.bat"

:: 壓縮成 ZIP
powershell Compress-Archive -Path "SRT_GO_Portable\*" -DestinationPath "SRT_GO_Portable_Complete.zip" -Force

echo ✅ 便攜式版本創建完成！
echo 📦 輸出：SRT_GO_Portable_Complete.zip
pause