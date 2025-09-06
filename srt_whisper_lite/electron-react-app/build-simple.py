#!/usr/bin/env python3
"""
Simple PyInstaller build - Test basic packaging without large model
"""

import subprocess
import sys
from pathlib import Path

def build_simple():
    """Build basic Python EXE without model files"""
    
    print("=== Simple PyInstaller Test ===")
    print("Building basic EXE without model files...")
    
    # Check source file exists
    source_file = 'dist/SRT-GO-Portable-Working/resources/python/electron_backend.py'
    if not Path(source_file).exists():
        print(f"ERROR: Source file not found: {source_file}")
        return False
    
    try:
        # Simple PyInstaller command
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--console',
            '--name=SRTProcessor-Simple',
            '--distpath=dist_simple',
            '--clean',
            source_file
        ]
        
        print(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Check output
        exe_path = Path('dist_simple/SRTProcessor-Simple.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024**2)
            print(f"SUCCESS: Simple EXE created!")
            print(f"Location: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
            return True
        else:
            print("ERROR: EXE not generated")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Build failed")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

if __name__ == "__main__":
    build_simple()