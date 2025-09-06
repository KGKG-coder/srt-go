#!/usr/bin/env python3
"""
PyInstaller build script - Package Python subtitle processing core into single EXE
For Electron + PyInstaller + NSIS architecture
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_pyinstaller_spec():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Data files - Include AI model
datas = [
    ('dist/SRT-GO-Portable-Working/resources/models/large-v3', 'models/large-v3'),
    ('dist/SRT-GO-Portable-Working/resources/python/*.py', 'core_modules'),
]

# Hidden imports - Ensure all AI dependencies are included
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
    icon='icon.ico' if Path('icon.ico').exists() else None
)
'''
    
    with open('SRTProcessor.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("PyInstaller spec file created: SRTProcessor.spec")

def build_python_exe():
    """Build Python EXE using PyInstaller"""
    
    print("Starting PyInstaller build process...")
    print("Note: This includes 3GB+ AI model, will take time...")
    
    # Check required files
    required_files = [
        'dist/SRT-GO-Portable-Working/resources/python/electron_backend.py',
        'dist/SRT-GO-Portable-Working/resources/models/large-v3/model.bin'
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"ERROR: Required file missing: {file_path}")
            return False
    
    # Clean old builds
    build_dirs = ['build', 'dist_python']
    for dir_name in build_dirs:
        if Path(dir_name).exists():
            print(f"Cleaning old build: {dir_name}")
            shutil.rmtree(dir_name)
    
    # Create spec file
    create_pyinstaller_spec()
    
    try:
        # Run PyInstaller
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--distpath=dist_python',
            'SRTProcessor.spec'
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        
        # Check output
        exe_path = Path('dist_python/SRTProcessor.exe')
        if exe_path.exists():
            size_gb = exe_path.stat().st_size / (1024**3)
            print(f"SUCCESS: Python EXE built!")
            print(f"Location: {exe_path.absolute()}")
            print(f"Size: {size_gb:.2f} GB")
            return True
        else:
            print("ERROR: EXE file not generated")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"ERROR: PyInstaller build failed: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Build process failed: {e}")
        return False

def main():
    """Main function"""
    print("=== SRT GO Python Core Packager ===")
    print("Using PyInstaller to create standalone subtitle processor EXE")
    print()
    
    # Check environment
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("ERROR: PyInstaller not installed")
        print("Please run: pip install pyinstaller")
        return False
    
    # Build
    success = build_python_exe()
    
    if success:
        print("\nPython core packaging complete!")
        print("Next steps:")
        print("1. Test dist_python/SRTProcessor.exe")
        print("2. Integrate with Electron app")
        print("3. Use electron-builder to create final installer")
    else:
        print("\nPython core packaging failed")
        print("Please check error messages and retry")
    
    return success

if __name__ == "__main__":
    main()