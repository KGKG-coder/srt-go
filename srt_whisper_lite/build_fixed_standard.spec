# -*- mode: python ; coding: utf-8 -*-
"""
SRT Whisper Lite - 修復版標準打包配置
平衡功能與大小，包含核心功能但移除非必要依賴
"""

import os
import sys
from pathlib import Path

# 專案根目錄
project_root = Path('.').absolute()
block_cipher = None

# 資料文件（標準版 - 核心功能）
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
    ('i18n.py', '.'),
    
    # 基本依賴清單
    ('requirements.txt', '.'),
]

# 修復 pkg_resources 問題
from PyInstaller.utils.hooks import copy_metadata, collect_data_files

# 複製必要的 metadata
try:
    datas += copy_metadata('setuptools')
    datas += copy_metadata('pkg_resources')
    datas += copy_metadata('packaging')
except:
    pass

# 隱藏導入 - 標準版核心功能 + 修復缺失模組
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
    
    # GPU 支援（基礎）
    'torch',
    'torch.cuda',
    'torch.nn',
    
    # GUI 基礎功能
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    
    # 音頻處理（基礎）
    'scipy',
    'scipy.signal',
    'scipy.io',
    'scipy.io.wavfile',
    
    # 文本處理（基礎）
    'opencc',
    
    # 工具庫
    'tqdm',
    'colorama',
    
    # 修復核心模組缺失問題
    # Email 模組
    'email',
    'email.message',
    'email.policy',
    'email.parser',
    'email.header',
    'email.generator',
    'email.utils',
    'email.mime',
    'email.mime.text',
    'email.mime.multipart',
    
    # XML 模組
    'xml',
    'xml.etree',
    'xml.etree.ElementTree',
    'xml.parsers',
    'xml.parsers.expat',
    'xml.dom',
    'xml.dom.minidom',
    
    # Pickle 和序列化
    'pickle',
    '_pickle',
    'copyreg',
    
    # HTTP 和網路
    'http',
    'http.client',
    'http.cookies',
    'http.cookiejar',
    'xmlrpc',
    'xmlrpc.client',
    
    # 多處理和並發
    'multiprocessing',
    'multiprocessing.pool',
    
    # HTML 處理
    'html',
    'html.parser',
    'html.entities',
    
    # 其他核心標準庫
    'sqlite3',
    'dbm',
    'shelve',
    'unittest',
    'unittest.mock',
    
    # 內部模組
    'simplified_subtitle_core',
    'audio_processor',
    'semantic_processor',
    'subtitle_formatter',
    'config_manager',
    'i18n',
]

# 二進制文件
binaries = []

# Windows 特定
if sys.platform == 'win32':
    from PyInstaller.utils.hooks import collect_dynamic_libs
    
    # 只收集核心 DLL
    for package in ['av', 'soundfile', 'onnxruntime']:
        try:
            binaries += collect_dynamic_libs(package)
        except:
            pass

# 標準版排除 - 平衡功能與大小
excludes = [
    # 開發和測試工具
    'pytest',
    'pytest_cov',
    'coverage',
    'nose',
    'nose2',
    'jupyter',
    'notebook',
    'IPython',
    'spyder',
    'sphinx',
    'sphinx_rtd_theme',
    'pylint',
    'flake8',
    'black',
    'autopep8',
    'isort',
    'mypy',
    
    # Web 框架
    'flask',
    'django',
    'fastapi',
    'starlette',
    'uvicorn',
    'gunicorn',
    'aiohttp',
    
    # 大數據和可視化
    'pandas',
    'matplotlib',
    'seaborn',
    'plotly',
    'bokeh',
    
    # 機器學習框架（保留基礎 torch）
    'tensorflow',
    'keras',
    'sklearn',
    'xgboost',
    'lightgbm',
    'transformers',
    
    # 高級音頻處理
    'librosa',
    'noisereduce',
    'numba',
    'llvmlite',
    
    # 高級文本處理
    'jieba',
    'spacy',
    'nltk',
    
    # GUI 高級功能
    'customtkinter',
    'tkinterdnd2',
    
    # 性能分析工具
    'cProfile',
    'profile',
    'pstats',
    'timeit',
    'tracemalloc',
    
    # GPU 高級功能
    'torchvision',
    'torchaudio',
    
    # 系統特定（非 Windows）
    'pwd',
    'grp',
    'termios',
    'tty',
    'pty',
    'fcntl',
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

# 標準優化
def standard_optimize_binaries(binaries):
    """標準優化，移除測試文件和部分重複項"""
    keep = []
    seen_base = set()
    
    for name, path, type_code in binaries:
        # 跳過測試和示例文件
        if any(skip in name.lower() for skip in ['test', '_test', 'example', 'demo', 'sample', 'benchmark']):
            continue
        
        # 跳過部分大型但非必要的庫
        if any(skip in name.lower() for skip in ['mkl_', 'intel_', 'tbb', 'iomp']):
            continue
            
        # 基本去重
        basename = os.path.basename(name)
        if basename.endswith('.dll'):
            if basename not in seen_base:
                seen_base.add(basename)
                keep.append((name, path, type_code))
        else:
            keep.append((name, path, type_code))
    
    return keep

a.binaries = standard_optimize_binaries(a.binaries)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SRT_Whisper_Lite_Standard_Fixed',
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
    upx_exclude=['*.pyd'],
    name='SRT_Whisper_Lite_Standard_Fixed',
)