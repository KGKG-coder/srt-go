# -*- mode: python ; coding: utf-8 -*-
"""
SRT Whisper Lite - 專業版打包配置
包含完整的 GPU 支援和所有功能
"""

import os
import sys
from pathlib import Path

# 專案根目錄
project_root = Path('.').absolute()
block_cipher = None

# 資料文件（專業版 - 包含所有功能）
datas = [
    # 核心配置文件
    ('custom_corrections.json', '.'),
    ('user_config.json', '.'),
    ('user_config_example.json', '.'),
    
    # 資源文件
    ('icon.ico', '.'),
    ('logo.png', '.'),
    
    # 核心 Python 腳本
    ('main.py', '.'),
    ('simplified_subtitle_core.py', '.'),
    ('audio_processor.py', '.'),
    ('semantic_processor.py', '.'),
    ('subtitle_formatter.py', '.'),
    ('config_manager.py', '.'),
    ('logo_manager.py', '.'),
    ('local_gui.py', '.'),
    ('i18n.py', '.'),
    
    # 依賴清單檔案
    ('requirements.txt', '.'),
    ('requirements-minimal.txt', '.'),
    ('requirements-dev.txt', '.'),
]

# 隱藏導入 - 專業版包含所有功能
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
    
    # GPU 支援 (專業版)
    'torch',
    'torch.cuda',
    'torch.nn',
    'torch.tensor',
    'torchvision',
    'torchaudio',
    
    # GUI 完整功能
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
    
    # 音頻處理完整功能
    'scipy',
    'scipy.signal',
    'scipy.io',
    'scipy.io.wavfile',
    'librosa',
    'noisereduce',
    
    # 文本處理
    'opencc',
    'jieba',
    
    # 工具庫
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
]

# 二進制文件
binaries = []

# Windows 特定
if sys.platform == 'win32':
    from PyInstaller.utils.hooks import collect_dynamic_libs
    
    # 收集必要的 DLL（包含 GPU 支援）
    for package in ['av', 'soundfile', 'onnxruntime', 'torch', 'torchvision', 'torchaudio']:
        try:
            binaries += collect_dynamic_libs(package)
        except:
            pass

# 專業版優化排除 - Python 3.11 相容性
excludes = [
    # 開發工具
    'pytest',
    'jupyter',
    'notebook',
    'IPython',
    'sphinx',
    'pylint',
    'black',
    'flake8',
    'autopep8',
    'isort',
    
    # Web 框架（非必要）
    'flask',
    'fastapi', 
    'uvicorn',
    'starlette',
    'aiohttp',
    'django',
    
    # 測試和調試
    'unittest',
    'doctest',
    'pdb',
    'traceback',
    'cProfile',
    'profile',
    
    # 不常用的標準庫
    'html',
    'http',
    'xml',
    'xmlrpc',
    'sqlite3',
    'dbm',
    'pickle',
    'shelve',
    
    # 系統管理
    'getpass',
    'pwd',
    'grp',
    'pty',
    'tty',
    
    # 網絡相關（非核心）
    'smtplib',
    'poplib',
    'imaplib',
    'ftplib',
    'telnetlib',
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

# 輕量優化：只移除明顯的重複和測試文件
def light_optimize_binaries(binaries):
    """輕量優化，只移除最明顯的重複檔案"""
    seen_files = {}
    keep = []
    
    for name, path, type_code in binaries:
        # 跳過測試相關
        if any(skip in name.lower() for skip in ['test', '_test', 'example', 'demo']):
            continue
            
        # 處理重複的 DLL（保留最新版本）
        basename = os.path.basename(name)
        if basename.endswith('.dll'):
            if basename in seen_files:
                # 比較檔案大小，保留較大的（通常是較新版本）
                try:
                    old_size = os.path.getsize(seen_files[basename][1]) if os.path.exists(seen_files[basename][1]) else 0
                    new_size = os.path.getsize(path) if os.path.exists(path) else 0
                    if new_size > old_size:
                        # 移除舊版本，添加新版本
                        keep = [item for item in keep if item[0] != seen_files[basename][0]]
                        seen_files[basename] = (name, path, type_code)
                        keep.append((name, path, type_code))
                except:
                    # 如果比較失敗，保留第一個
                    pass
            else:
                seen_files[basename] = (name, path, type_code)
                keep.append((name, path, type_code))
        else:
            keep.append((name, path, type_code))
    
    return keep

a.binaries = light_optimize_binaries(a.binaries)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SRT_Whisper_Lite_Professional',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 啟用壓縮
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
    upx_exclude=['*.pyd'],  # 不壓縮 Python 擴展
    name='SRT_Whisper_Lite_Professional',
)