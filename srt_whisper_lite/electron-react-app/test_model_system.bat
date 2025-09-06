@echo off
echo 🧪 測試預置模型系統...
echo.

echo 📋 測試步驟：
echo 1. 檢查模型管理器
python ../model_manager.py

echo.
echo 2. 測試首次運行嚮導
python ../first_run_guide.py list

echo.
echo ✅ 測試完成！
pause
