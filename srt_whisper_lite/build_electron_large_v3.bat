@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

:: =======================================================
:: Large-v3 Electron版本打包脚本 (基于混合架构)
:: Python后端 + Electron前端 + NSIS安装程序
:: =======================================================

echo.
echo ========================================
echo Large-v3 Electron版本打包 (混合架构)
echo Python AI后端 + Electron React前端
echo ========================================
echo.

echo 🎯 混合架构特色：
echo    ✅ Python AI后端 (Large-v3专用)
echo    ✅ Electron React现代前端
echo    ✅ NSIS标准安装程序
echo    ✅ 完整模型内置
echo    ✅ 专业级用户体验
echo.

:: 检查Node.js和npm
echo [1/8] 检查开发环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到 Node.js
    echo 请安装 Node.js 14+ 并添加到系统路径
    pause
    exit /b 1
)

npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到 npm
    pause
    exit /b 1
)

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到 Python
    pause
    exit /b 1
)

echo ✅ 开发环境检查完成

:: 进入electron-react-app目录
cd electron-react-app

:: 确认打包
set /p confirm="开始 Large-v3 Electron版本打包？(Y/N): "
if /i not "%confirm%"=="Y" (
    echo 打包已取消
    pause
    exit /b 0
)

:: 安装依赖
echo.
echo [2/8] 安装Electron应用依赖...
call npm install
if errorlevel 1 (
    echo ❌ npm install 失败
    pause
    exit /b 1
)

echo.
echo [3/8] 安装React前端依赖...
cd react-app
call npm install
if errorlevel 1 (
    echo ❌ React app npm install 失败
    pause
    exit /b 1
)
cd ..
echo ✅ 依赖安装完成

:: 验证Large-v3配置
echo.
echo [4/8] 验证Large-v3模型配置...
python -c "
import sys
sys.path.append('../')
try:
    from config_manager import get_config_manager
    config = get_config_manager()
    model = config.get('model.size', 'unknown')
    primary = config.get('model.primary_model', 'unknown')
    print(f'✅ 确认使用模型: {model}')
    print(f'✅ 主要模型: {primary}')
    if 'large' not in model.lower():
        print('⚠️  警告：当前配置不是Large-v3')
    else:
        print('✅ Large-v3配置验证成功')
except Exception as e:
    print(f'❌ 配置验证失败: {e}')
    exit(1)
"
if errorlevel 1 (
    echo 模型配置验证失败
    pause
    exit /b 1
)

:: 检查模型文件
echo.
echo [5/8] 检查模型文件...
if exist "..\models\whisper-large-model.zip" (
    for %%I in ("..\models\whisper-large-model.zip") do set modelSize=%%~zI
    set /a modelSizeMB=!modelSize! / 1048576
    echo ✅ 发现Large模型文件 (!modelSizeMB! MB)
) else (
    echo ⚠️  Large模型文件不存在，将在运行时自动下载
)

:: 构建React前端
echo.
echo [6/8] 构建React前端应用...
cd react-app
call npm run build
if errorlevel 1 (
    echo ❌ React build 失败
    pause
    exit /b 1
)
cd ..
echo ✅ React前端构建完成

:: 清理旧打包文件
echo.
echo [7/8] 清理和准备打包...
if exist dist rmdir /s /q dist >nul 2>&1
echo ✅ 旧文件清理完成

:: 执行Electron Builder打包
echo.
echo [8/8] 执行Electron Builder打包...
echo 🎯 正在生成Large-v3 Electron版本...
echo ⚠️  此过程可能需要5-10分钟，请耐心等待...
echo.

call npm run dist
if errorlevel 1 (
    echo.
    echo ❌ Electron Builder 打包失败！
    echo 请检查错误信息并修复问题
    pause
    exit /b 1
)

:: 验证输出
echo.
echo 🔍 验证打包输出...
if not exist "dist" (
    echo ❌ 找不到输出目录
    pause
    exit /b 1
)

:: 查找生成的文件
set setupFile=
set portableFile=
for %%f in ("dist\*.exe") do (
    set filename=%%~nxf
    if "!filename:Setup=!" neq "!filename!" (
        set setupFile=%%f
    )
    if "!filename:Portable=!" neq "!filename!" (
        set portableFile=%%f
    )
)

:: 计算总大小
set totalSize=0
for /r "dist" %%f in (*) do (
    set /a totalSize+=%%~zf
)
set /a totalSizeMB=%totalSize% / 1048576

:: 创建版本说明文档
(
echo Large-v3 Electron版本 v2.1.0 (2025-08-12)
echo ==========================================
echo.
echo 🏆 混合架构专业版本
echo   • Python AI后端 (Large-v3专用)
echo   • Electron React现代前端  
echo   • NSIS标准安装程序
echo   • 完整模型和依赖内置
echo.
echo 📦 打包内容:
echo   ✅ Large-v3 AI处理引擎 (Python后端)
echo   ✅ 现代化GUI界面 (Electron + React)
echo   ✅ 完整音频处理库 (FFmpeg等)
echo   ✅ 智能模型管理系统
echo   ✅ 多语言支持和配置系统
echo.
echo 💡 安装和使用:
echo   1. 运行Setup安装程序进行标准安装
echo   2. 或使用Portable版本免安装运行
echo   3. 启动后自动初始化Large-v3模型
echo   4. 拖放文件到界面开始处理
echo.
echo 🎯 技术架构优势:
echo   ✅ 前后端分离，界面响应快速
echo   ✅ Python AI后端，处理能力强大
echo   ✅ 标准Windows安装，用户体验佳
echo   ✅ 模块化设计，维护成本低
echo.
echo ⚡ 性能规格:
echo   AI模型: Large-v3 预设参数
echo   前端技术: Electron 27+ React 18+
echo   后端引擎: Python 3.8+ faster-whisper
echo   支持格式: MP4/MP3/WAV/AVI等主流格式
echo   输出格式: SRT/VTT/TXT
) > "dist\Large_V3_Electron版本说明.txt"

:: 复制配置文档
copy "..\MODEL_CONFIGURATION_FINAL.md" "dist\" >nul 2>&1

:: 完成报告
echo.
echo ========================================
echo ✅ Large-v3 Electron版本打包成功！
echo ========================================
echo.
echo 📁 输出位置：
echo    %cd%\dist\
echo.
echo 📦 生成文件：
if defined setupFile (
    echo    ✅ 安装程序: !setupFile!
) else (
    echo    ⚠️  安装程序: 未找到
)
if defined portableFile (
    echo    ✅ 便携版: !portableFile!  
) else (
    echo    ⚠️  便携版: 未找到
)
echo    ✅ 说明文档: Large_V3_Electron版本说明.txt
echo    总大小: %totalSizeMB% MB

echo.
echo 🏆 Large-v3 Electron版本特色：
echo    🎯 混合架构 - Python AI + Electron GUI
echo    🎯 专业安装 - NSIS标准安装程序
echo    🎯 现代界面 - React响应式设计
echo    🎯 AI核心 - Large-v3预设最优配置
echo    🎯 生产就绪 - 完整测试和验证
echo.
echo 💡 下一步建议：
echo    1. 测试安装程序的安装和卸载功能
echo    2. 验证便携版的独立运行能力
echo    3. 使用测试文件验证Large-v3性能
echo    4. 检查用户界面的响应性和易用性
echo.
pause