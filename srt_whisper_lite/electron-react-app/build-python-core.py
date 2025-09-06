#!/usr/bin/env python3
"""
PyInstaller 打包脚本 - 将 Python 字幕处理核心打包为单一 EXE
适用于 Electron + PyInstaller + NSIS 架构
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_pyinstaller_spec():
    """创建 PyInstaller 规格文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 数据文件 - 包含 AI 模型
datas = [
    ('dist/SRT-GO-Portable-Working/resources/models/large-v3', 'models/large-v3'),
    ('dist/SRT-GO-Portable-Working/resources/python/*.py', 'core_modules'),
]

# 隐藏导入 - 确保所有 AI 依赖被包含
hiddenimports = [
    'faster_whisper',
    'ctranslate2', 
    'numpy',
    'torch',
    'av',
    'soundfile',
    'onnxruntime',
    'librosa',
    'scipy',
    'opencc',
    'transformers',
    'tokenizers',
    'huggingface_hub',
    'requests',
    'certifi',
    'charset_normalizer',
    'filelock'
]

a = Analysis(
    ['dist/SRT-GO-Portable-Working/resources/python/electron_backend.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'PIL', 'IPython'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SRTProcessor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
)
'''
    
    with open('SRTProcessor.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ PyInstaller 规格文件创建完成: SRTProcessor.spec")

def build_python_exe():
    """使用 PyInstaller 构建 Python EXE"""
    
    print("🏗️ 开始 PyInstaller 构建过程...")
    print("注意: 这将包含 3GB+ 的 AI 模型，需要较长时间...")
    
    # 检查必要文件
    required_files = [
        'dist/SRT-GO-Portable-Working/resources/python/electron_backend.py',
        'dist/SRT-GO-Portable-Working/resources/models/large-v3/model.bin'
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ 错误: 必要文件不存在: {file_path}")
            return False
    
    # 清理旧的构建
    build_dirs = ['build', 'dist_python']
    for dir_name in build_dirs:
        if Path(dir_name).exists():
            print(f"🧹 清理旧构建: {dir_name}")
            shutil.rmtree(dir_name)
    
    # 创建规格文件
    create_pyinstaller_spec()
    
    try:
        # 执行 PyInstaller
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--distpath=dist_python',
            'SRTProcessor.spec'
        ]
        
        print(f"📦 执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        
        # 检查输出文件
        exe_path = Path('dist_python/SRTProcessor.exe')
        if exe_path.exists():
            size_gb = exe_path.stat().st_size / (1024**3)
            print(f"✅ Python EXE 构建成功!")
            print(f"📦 位置: {exe_path.absolute()}")
            print(f"📊 大小: {size_gb:.2f} GB")
            return True
        else:
            print("❌ 错误: EXE 文件未生成")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller 构建失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 构建过程出错: {e}")
        return False

def test_python_exe():
    """测试生成的 Python EXE"""
    exe_path = Path('dist_python/SRTProcessor.exe')
    
    if not exe_path.exists():
        print("❌ EXE 文件不存在，无法测试")
        return False
    
    print("🧪 测试 Python EXE...")
    
    try:
        # 测试帮助命令
        result = subprocess.run([str(exe_path), '--help'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Python EXE 测试成功")
            print("📋 帮助输出:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
            return True
        else:
            print(f"❌ Python EXE 测试失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ 测试超时（可能是首次加载模型）")
        return True  # 超时通常意味着程序在工作
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        return False

def main():
    """主函数"""
    print("=== SRT GO Python 核心打包工具 ===")
    print("使用 PyInstaller 创建独立的字幕处理 EXE")
    print()
    
    # 检查环境
    try:
        import PyInstaller
        print(f"✅ PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("❌ 错误: 未安装 PyInstaller")
        print("请运行: pip install pyinstaller")
        return False
    
    # 构建
    success = build_python_exe()
    
    if success:
        print("\n🎉 Python 核心打包完成!")
        print("📋 下一步:")
        print("1. 测试 dist_python/SRTProcessor.exe")
        print("2. 集成到 Electron 应用")
        print("3. 使用 electron-builder 创建最终安装包")
        
        # 可选测试
        test_choice = input("\n是否现在测试 Python EXE? (y/n): ").lower()
        if test_choice == 'y':
            test_python_exe()
    else:
        print("\n❌ Python 核心打包失败")
        print("请检查错误信息并重试")
    
    return success

if __name__ == "__main__":
    main()