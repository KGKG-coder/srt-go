import os
import shutil
from pathlib import Path

def create_exe_launcher():
    """Create an EXE launcher for SRT GO Enhanced v2.0"""
    
    print("Creating EXE launcher for SRT GO Enhanced v2.0...")
    
    # Source and target directories
    source_dir = Path("dist/SRT-GO-Enhanced-v2.0-Portable")
    target_dir = Path("dist/SRT-GO-Enhanced-v2.0-EXE")
    
    # Ensure target directory exists
    target_dir.mkdir(exist_ok=True)
    
    print(f"Source: {source_dir}")
    print(f"Target: {target_dir}")
    
    # Copy all files to target directory
    if source_dir.exists():
        print("Copying files...")
        
        # Copy all content
        for item in source_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, target_dir / item.name)
                print(f"Copied: {item.name}")
            elif item.is_dir():
                shutil.copytree(item, target_dir / item.name, dirs_exist_ok=True)
                print(f"Copied directory: {item.name}")
    
    # Create EXE launcher script
    exe_launcher_content = '''@echo off
cd /d "%~dp0"
echo Starting SRT GO Enhanced v2.0...
start "" /min cmd /c "SRT GO Enhanced v2.0.bat"
'''
    
    with open(target_dir / "SRT GO Enhanced v2.0 Launcher.bat", 'w', encoding='utf-8') as f:
        f.write(exe_launcher_content)
    
    print("Created launcher batch file")
    
    # Create README file
    readme_content = '''# SRT GO Enhanced v2.0 EXE Version

## Execution Methods

Double-click one of the following files to start:

1. **SRT GO Enhanced v2.0.bat** - Shows startup process
2. **SRT GO Enhanced v2.0 Launcher.bat** - Minimized startup

## File Description

This is a complete version with all necessary files:
- Built-in Python 3.11 environment
- Includes Large V3 Turbo AI models
- Enhanced Voice Detector v2.0 technology
- Modern Electron + React GUI

## System Requirements

- Windows 10/11 (64-bit)
- 4GB+ RAM (8GB+ recommended)
- Node.js 16+ (Electron auto-installed on first run)

## First Use

1. Ensure Node.js is installed
2. Double-click startup file
3. Wait for Electron environment installation
4. Start using AI subtitle generation

---
SRT GO Enhanced v2.0 - Revolutionary AI Subtitle Generator
'''
    
    with open(target_dir / "README_EXE.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("Created README file")
    
    # Check results
    total_files = len(list(target_dir.rglob('*')))
    total_size = sum(f.stat().st_size for f in target_dir.rglob('*') if f.is_file()) / (1024**3)
    
    print("\nEXE version created successfully!")
    print(f"Location: {target_dir.absolute()}")
    print(f"Total files: {total_files}")
    print(f"Total size: {total_size:.2f} GB")
    print("\nStartup methods:")
    print("   - Double-click 'SRT GO Enhanced v2.0.bat'")
    print("   - Or double-click 'SRT GO Enhanced v2.0 Launcher.bat'")

if __name__ == "__main__":
    create_exe_launcher()