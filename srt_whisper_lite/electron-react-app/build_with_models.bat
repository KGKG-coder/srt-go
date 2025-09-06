@echo off
echo 🚀 構建包含預置模型的安裝包...
echo.

echo 📋 第一步：準備模型文件
echo   - 確保已在有網路的環境下載過所需模型
echo   - 模型會自動從 HuggingFace 緩存中提取

echo.
echo 📦 第二步：創建模型安裝包
python -c "
from model_manager import ModelManager
import os

manager = ModelManager()
models_to_package = ['tiny', 'base', 'medium']  # 不包含 large (太大)

# 創建模型目錄
os.makedirs('models', exist_ok=True)

print('正在檢查和打包模型...')
for model in models_to_package:
    print(f'處理模型: {model}')
    success = manager.create_model_package(model, 'models')
    if success:
        print(f'  ✅ {model} 模型打包完成')
    else:
        print(f'  ❌ {model} 模型打包失敗（可能尚未下載）')

print('\n模型打包完成！')
print('包含預置模型的安裝包構建準備就緒。')
"

echo.
echo 📋 第三步：更新 Electron Builder 配置
echo   - 將 models/ 目錄添加到 extraFiles
echo   - 確保模型文件包含在安裝包中

echo.
echo ✅ 準備工作完成！
echo 💡 下一步：運行 'npm run build' 來創建包含預置模型的安裝包

pause
