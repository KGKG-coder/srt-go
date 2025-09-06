# -*- mode: python ; coding: utf-8 -*-
"""
SRT Whisper Lite - 修復版專業打包配置
修正核心模組排除問題，確保執行時不出現 ModuleNotFoundError
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

# 修復 pkg_resources 問題
from PyInstaller.utils.hooks import copy_metadata, collect_data_files

# 複製必要的 metadata
try:
    datas += copy_metadata('setuptools')
    datas += copy_metadata('pkg_resources')
    datas += copy_metadata('packaging')
except:
    pass

# 隱藏導入 - 專業版包含所有功能 + 修復缺失模組
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
    'http.server',
    'http.cookies',
    'http.cookiejar',
    'xmlrpc',
    'xmlrpc.client',
    
    # 多處理和並發
    'multiprocessing',
    'multiprocessing.pool',
    'multiprocessing.managers',
    
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

# 修復版排除 - 只排除真正不需要的開發工具
excludes = [
    # 開發和測試工具（安全排除）
    'pytest',
    'pytest_cov',
    'coverage',
    'nose',
    'nose2',
    
    # IDE 和編輯器
    'jupyter',
    'notebook',
    'IPython',
    'spyder',
    
    # 文檔工具
    'sphinx',
    'sphinx_rtd_theme',
    
    # 代碼質量工具
    'pylint',
    'flake8',
    'black',
    'autopep8',
    'isort',
    'mypy',
    
    # 確定不需要的 Web 框架
    'flask',
    'django',
    'fastapi',
    'starlette',
    'uvicorn',
    'gunicorn',
    
    # 大數據處理（如果確定不需要）
    'pandas',
    'matplotlib',
    'seaborn',
    'plotly',
    'bokeh',
    
    # 機器學習框架（保留 torch）
    'tensorflow',
    'keras',
    'sklearn',
    'xgboost',
    'lightgbm',
    
    # 性能分析工具
    'cProfile',
    'profile',
    'pstats',
    'timeit',
    'tracemalloc',
    
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

# 智能二進制優化
def smart_optimize_binaries(binaries):
    """智能優化，保留必要文件，移除重複和測試文件"""
    seen_files = {}
    keep = []
    
    for name, path, type_code in binaries:
        # 跳過明顯的測試文件
        if any(skip in name.lower() for skip in ['test', '_test', 'example', 'demo', 'sample']):
            continue
        
        # 保留所有 DLL（不進行重複檢查，避免版本問題）
        if name.endswith('.dll'):
            keep.append((name, path, type_code))
            continue
        
        # 處理其他文件的重複
        basename = os.path.basename(name)
        if basename not in seen_files:
            seen_files[basename] = (name, path, type_code)
            keep.append((name, path, type_code))
    
    return keep

a.binaries = smart_optimize_binaries(a.binaries)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SRT_Whisper_Lite_Professional_Fixed',
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
    name='SRT_Whisper_Lite_Professional_Fixed',
)