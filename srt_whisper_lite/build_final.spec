# -*- mode: python ; coding: utf-8 -*-
"""
SRT Whisper Lite - 最終打包配置
生成可在任何 Windows 電腦運行的版本
"""

import os
import sys
from pathlib import Path

# 專案根目錄
project_root = Path('.').absolute()
block_cipher = None

# 資料文件
datas = [
    # 配置文件
    ('custom_corrections.json', '.'),
    ('user_config.json', '.'),
    
    # 資源文件
    ('icon.ico', '.'),
    ('logo.png', '.'),
    
    # Python 後端腳本
    ('electron_backend.py', '.'),
    ('simplified_subtitle_core.py', '.'),
    ('audio_processor.py', '.'),
    ('semantic_processor.py', '.'),
    ('subtitle_formatter.py', '.'),
    ('config_manager.py', '.'),
    ('logo_manager.py', '.'),
    
    # 完整 Python 環境 (支援GPU)
    ('portable_python', 'portable_python'),
    
    # Electron React 應用
    ('electron-react-app/dist', 'electron-react-app/dist'),
    
    # 國際化
    ('i18n.py', '.'),
]

# 隱藏導入 - 確保所有必要模組都包含
hiddenimports = [
    # 核心 AI 模組
    'faster_whisper',
    'ctranslate2',
    'tokenizers',
    'huggingface_hub',
    'filelock',
    'packaging',
    'yaml',
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
    
    # GUI
    'customtkinter',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    'tkinterdnd2',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageTk',
    
    # 音頻處理
    'scipy',
    'scipy.signal',
    'scipy.io',
    'scipy.io.wavfile',
    'librosa',
    'noisereduce',
    
    # 文本處理
    'opencc',
    
    # 工具
    'tqdm',
    'colorama',
    
    # 內部模組
    'simplified_subtitle_core',
    'audio_processor',
    'semantic_processor',
    'subtitle_formatter',
    'config_manager',
    'local_gui',
    'i18n',
    'logo_manager',
    
    # 系統
    'setuptools',
    'jaraco',
    'jaraco.text',
    'jaraco.context',
    'jaraco.functools',
    'pkg_resources',
]

# 二進制文件
binaries = []

# Windows 特定
if sys.platform == 'win32':
    from PyInstaller.utils.hooks import collect_dynamic_libs
    
    # 收集必要的 DLL
    for package in ['av', 'soundfile', 'onnxruntime']:
        try:
            binaries += collect_dynamic_libs(package)
        except:
            pass

# GPU 支援模組 (不排除)
gpu_support = [
    'torch',
    'torchvision', 
    'torchaudio',
    'torchtext',
    'cuda',
    'cudnn',
    'cublas',
    'curand',
    'cusparse',
    'cufft',
    'cusolver',
]

# 添加GPU支援到隱藏導入
hiddenimports.extend([
    'torch',
    'torch.cuda',
    'torch.nn',
    'torch.tensor',
    'torchvision',
    'torchaudio',
])

# 排除不需要的模組 (保留GPU支援)
excludes = [
    # Web 框架
    'flask',
    'fastapi', 
    'uvicorn',
    'starlette',
    
    # 開發工具
    'pytest',
    'jupyter',
    'notebook',
    'IPython',
    'sphinx',
    
    # 其他大型框架
    'tensorflow',
    'keras',
    'matplotlib',
    'pandas',
    'sklearn',
]

# 分析配置
a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=binaries,
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

# 優化
a.binaries = [x for x in a.binaries if not x[0].startswith('api-ms-win')]

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
    upx_exclude=[],
    name='SRT_Whisper_Lite',
)