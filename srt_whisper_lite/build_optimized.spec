# -*- mode: python ; coding: utf-8 -*-
"""
SRT Whisper Lite - 優化打包配置
精簡版本，移除冗餘依賴
"""

import os
import sys
from pathlib import Path

# 專案根目錄
project_root = Path('.').absolute()
block_cipher = None

# 資料文件（精簡版）
datas = [
    # 核心配置文件
    ('custom_corrections.json', '.'),
    ('user_config.json', '.'),
    
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
]

# 隱藏導入 - 只包含必要模組
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
    
    # GUI (精簡)
    'customtkinter',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageTk',
    
    # 音頻處理（核心）
    'scipy',
    'scipy.signal',
    'scipy.io',
    'scipy.io.wavfile',
    
    # 文本處理
    'opencc',
    
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
    
    # 只收集必要的 DLL
    for package in ['av', 'soundfile', 'onnxruntime']:
        try:
            binaries += collect_dynamic_libs(package)
        except:
            pass

# 排除不需要的模組（擴展列表）
excludes = [
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
    'pylint',
    'black',
    'flake8',
    
    # 大型 ML 框架
    'tensorflow',
    'tensorflow_core',
    'keras',
    'torch',
    'torchvision',
    'torchaudio',
    'transformers',
    'datasets',
    'diffusers',
    
    # 數據分析（如果不需要）
    'pandas',
    'matplotlib',
    'seaborn',
    'plotly',
    'bokeh',
    
    # 科學計算（保留必要的）
    'sklearn',
    'skimage',
    'cv2',
    
    # 其他不需要的
    'email',
    'html',
    'http',
    'xml',
    'xmlrpc',
    'test',
    'tests',
    'unittest',
    # 'distutils',  # 註解掉，Python 3.13 有相容性問題
    # 'setuptools', # 註解掉，Python 3.13 有相容性問題
    'pip',
    # 'wheel',     # 註解掉，Python 3.13 有相容性問題
    
    # Tkinter 相關（如果使用 customtkinter）
    'tkinterdnd2',  # 如果不需要拖放功能
    
    # 調試和分析
    'pdb',
    'profile',
    'cProfile',
    'timeit',
    'trace',
    'tracemalloc',
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

# 優化：移除不必要的二進制文件
a.binaries = [x for x in a.binaries if not any([
    x[0].startswith('api-ms-win'),
    'test' in x[0].lower(),
    '_test' in x[0].lower(),
    'example' in x[0].lower(),
])]

# 移除重複的 DLL
seen = set()
new_binaries = []
for item in a.binaries:
    filename = os.path.basename(item[0])
    if filename not in seen:
        seen.add(filename)
        new_binaries.append(item)
a.binaries = new_binaries

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
    version='file_version_info.txt' if os.path.exists('file_version_info.txt') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=['*.pyd', '*.dll'],  # 不壓縮 Python 擴展和 DLL
    name='SRT_Whisper_Lite',
)