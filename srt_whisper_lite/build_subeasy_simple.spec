# -*- mode: python ; coding: utf-8 -*-
# SubEasy 多層過濾版本打包規格

import os

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('models/*', 'models/') if os.path.exists('models') else [],
        ('i18n.py', '.'),
        ('config_manager.py', '.'),
        ('subeasy_multilayer_filter.py', '.'),
        ('semantic_processor.py', '.'),
        ('simplified_subtitle_core.py', '.'),
        ('subtitle_formatter.py', '.'),
        ('large_only_model_manager.py', '.'),
        ('user_config.json', '.') if os.path.exists('user_config.json') else []
    ],
    hiddenimports=[
        'faster_whisper', 'ctranslate2', 'numpy', 
        'soundfile', 'av', 'scipy', 'opencc',
        'subeasy_multilayer_filter', 'semantic_processor',
        'simplified_subtitle_core', 'large_only_model_manager',
        'tkinter', 'tkinter.ttk', 'tkinter.filedialog',
        'tkinter.messagebox', 'threading', 'queue',
        'subprocess', 'logging', 'json', 'pathlib',
        'wave', 'struct', 'math', 'typing'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'plotly', 'pandas', 'librosa', 'noisereduce'],
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
    name='SRT_Whisper_Lite_SubEasy_Final',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
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
    upx=True,
    upx_exclude=[],
    name='SRT_Whisper_Lite_SubEasy_Final',
)