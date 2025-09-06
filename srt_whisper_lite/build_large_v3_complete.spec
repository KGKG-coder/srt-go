# -*- mode: python ; coding: utf-8 -*-
# Large-v3 完整打包规格 - 包含模型和依赖 (2025-08-12 决策)
import os

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[
        # 包含所有FFmpeg和音频处理库 - 如果存在的话
    ],
    datas=[
        # 核心模型文件 - 完整Large-v3支持
        ('models/whisper-large-model.zip', 'models/'), 
        ('models/whisper-medium-model.zip', 'models/'),  # 备用Medium优化版
        ('models/whisper-base-model.zip', 'models/'),    # 降级备用
        ('models/whisper-tiny-model.zip', 'models/'),    # 最小备用
        # 核心Python模块
        ('config_manager.py', '.'),
        ('simplified_subtitle_core.py', '.'),
        ('large_only_model_manager.py', '.'),
        ('local_gui.py', '.'),
        ('subtitle_formatter.py', '.'),
        ('semantic_processor.py', '.'),
        ('audio_processor.py', '.'),
        ('electron_backend.py', '.'),
        # 配置和文档文件
        ('MODEL_CONFIGURATION_FINAL.md', '.'),
        ('user_config.json', '.'),
        ('custom_corrections.json', '.'),
        ('i18n.py', '.'),
        # 界面资源
        ('icon.ico', '.'),
        ('logo.png', '.'),
    ],
    hiddenimports=[
        # 核心AI和音频处理依赖
        'faster_whisper', 'ctranslate2', 'numpy', 
        'soundfile', 'av', 'scipy', 'opencc',
        # 项目核心模块
        'simplified_subtitle_core', 'large_only_model_manager',
        'semantic_processor', 'audio_processor', 'subtitle_formatter',
        'config_manager', 'i18n', 'electron_backend',
        # GUI和界面依赖
        'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox',
        'tkinter.scrolledtext', 'threading', 'queue', 'multiprocessing',
        # 系统和工具依赖
        'subprocess', 'logging', 'json', 'pathlib', 'tempfile',
        'urllib', 'urllib.request', 'http.client', 'ssl',
        # 数据处理依赖
        'collections', 'itertools', 'functools', 'operator',
        're', 'string', 'datetime', 'time', 'os', 'sys',
        # 编码和文本处理
        'unicodedata', 'codecs', 'encodings', 'locale',
        # 必需的包管理依赖
        'pkg_resources', 'setuptools'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的大型依赖以减小体积
        'matplotlib', 'plotly', 'pandas', 'jupyter', 'notebook',
        'IPython', 'sphinx', 'pytest', 'PIL.ImageQt',
        '_pytest'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SRT_Whisper_Lite_Large_V3_Complete',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 关闭UPX避免模型压缩问题
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,  # 关闭UPX保持模型完整性
    upx_exclude=[],
    name='SRT_Whisper_Lite_Large_V3_Complete',
)