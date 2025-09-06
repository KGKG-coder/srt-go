# -*- mode: python ; coding: utf-8 -*-
"""
SRT Whisper Lite - 最小化打包配置
真正的精簡版本，只包含核心功能
"""

import os
import sys
from pathlib import Path

# 專案根目錄
project_root = Path('.').absolute()
block_cipher = None

# 資料文件（最小化）
datas = [
    # 核心配置文件
    ('custom_corrections.json', '.'),
    ('user_config.json', '.'),
    
    # 資源文件
    ('icon.ico', '.'),
    ('logo.png', '.'),
    
    # 核心 Python 腳本
    ('simplified_subtitle_core.py', '.'),
    ('audio_processor.py', '.'),
    ('semantic_processor.py', '.'),
    ('subtitle_formatter.py', '.'),
    ('config_manager.py', '.'),
    ('i18n.py', '.'),
]

# 隱藏導入 - 只包含絕對必要模組
hiddenimports = [
    # 核心 AI 模組
    'faster_whisper',
    'ctranslate2',
    'tokenizers',
    'huggingface_hub',
    'filelock',
    'packaging',
    'requests',
    'certifi',
    'charset_normalizer',
    'idna',
    'urllib3',
    
    # 音視頻處理
    'av',
    'av.audio',
    'av.audio.stream',
    'av.container',
    'soundfile',
    'numpy',
    'numpy.core',
    'numpy.core.multiarray',
    'onnxruntime',
    
    # 基本工具
    'tqdm',
    'colorama',
    
    # 內部模組
    'simplified_subtitle_core',
    'audio_processor',
    'semantic_processor',
    'subtitle_formatter',
    'config_manager',
    'i18n',
]

# 排除大型不必要的模組
excludes = [
    # 大型 ML 框架
    'torch',
    'torchvision',
    'torchaudio',
    'tensorflow',
    'tensorflow_core',
    'keras',
    'transformers',
    'datasets',
    'diffusers',
    'peft',
    'optimum',
    
    # GUI 框架（只使用基本界面）
    'customtkinter',
    'tkinterdnd2',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageTk',
    
    # 科學計算（保留基本的）
    'scipy',
    'pandas',
    'matplotlib',
    'seaborn',
    'plotly',
    'sklearn',
    'skimage',
    'cv2',
    
    # Web 框架
    'flask',
    'fastapi', 
    'uvicorn',
    'starlette',
    'aiohttp',
    'websockets',
    
    # 開發工具
    'pytest',
    'jupyter',
    'notebook',
    'IPython',
    'sphinx',
    
    # 其他大型依賴
    'sympy',
    'nltk',
    'jieba',
    'librosa',
    'numba',
    'llvmlite',
    
    # 系統相關
    'email',
    'html',
    'http',
    'xml',
    'xmlrpc',
    'test',
    'tests',
    'unittest',
    'pip',
]

# 分析配置
a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 積極優化：移除不必要的二進制文件
def filter_binaries(binaries):
    keep = []
    for name, path, type_code in binaries:
        # 跳過測試相關
        if any(skip in name.lower() for skip in ['test', '_test', 'example']):
            continue
        # 跳過大型 CUDA 庫（如果不需要 GPU）
        if any(skip in name.lower() for skip in ['cublas', 'cudnn', 'cufft', 'cusolver', 'cusparse']):
            continue
        # 跳過 torch 相關
        if any(skip in name.lower() for skip in ['torch_', 'libtorch']):
            continue
        keep.append((name, path, type_code))
    return keep

a.binaries = filter_binaries(a.binaries)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SRT_Whisper_Lite',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI 程序
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=['*.pyd', '*.dll'],
    name='SRT_Whisper_Lite',
)