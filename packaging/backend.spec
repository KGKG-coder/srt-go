# PyInstaller spec file for backend engine
# Note: Models are NOT included, only runtime and necessary resources

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Collect hidden imports
hidden_imports = []
hidden_imports += collect_submodules('faster_whisper')
hidden_imports += collect_submodules('ctranslate2')
hidden_imports += collect_submodules('librosa')
hidden_imports += collect_submodules('soundfile')
hidden_imports += collect_submodules('webrtcvad')
hidden_imports += collect_submodules('opencc')
hidden_imports += collect_submodules('numpy')
hidden_imports += collect_submodules('scipy')
hidden_imports += collect_submodules('torch')  # Optional, for GPU detection

# Collect data files
datas = []
# OpenCC conversion data
try:
    import opencc
    opencc_path = Path(opencc.__file__).parent
    datas.append((str(opencc_path / 'config'), 'opencc/config'))
    datas.append((str(opencc_path / 'dictionary'), 'opencc/dictionary'))
except:
    pass

a = Analysis(
    ['../engine_main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'tkinter',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='srt_engine',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Keep console for CLI usage
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='srt_engine'
)