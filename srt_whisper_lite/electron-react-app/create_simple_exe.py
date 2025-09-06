#!/usr/bin/env python3
"""
Create a complete SRT GO Enhanced v2.0 .exe executable
Uses the successfully built electron-builder output and fixes Python dependencies
"""

import os
import shutil
from pathlib import Path

def create_complete_executable():
    """Create complete executable with full Python environment"""
    
    print("Creating Complete SRT GO Enhanced v2.0 Executable...")
    
    # Paths
    source_base = Path("dist_final/win-unpacked")
    target_base = Path("dist/SRT-GO-Enhanced-v2.0-Complete")
    main_python = Path("mini_python")
    main_python_scripts = Path("python")
    
    # Create target directory
    target_base.mkdir(parents=True, exist_ok=True)
    
    print(f"Source: {source_base.absolute()}")
    print(f"Target: {target_base.absolute()}")
    
    # Step 1: Copy the entire electron-builder output
    print("Copying Electron application...")
    if source_base.exists():
        for item in source_base.iterdir():
            target_item = target_base / item.name
            if item.is_file():
                shutil.copy2(item, target_item)
                print(f"Copied file: {item.name}")
            elif item.is_dir() and item.name != "resources":
                shutil.copytree(item, target_item, dirs_exist_ok=True)
                print(f"Copied directory: {item.name}")
    
    # Step 2: Create resources directory properly
    resources_dir = target_base / "resources"
    resources_dir.mkdir(exist_ok=True)
    
    # Copy app.asar
    asar_source = source_base / "resources" / "app.asar"
    if asar_source.exists():
        shutil.copy2(asar_source, resources_dir / "app.asar")
        print("Copied app.asar")
    
    # Step 3: Copy working Python environment
    print("Setting up complete Python environment...")
    
    # Copy mini_python (working Python)
    target_mini_python = resources_dir / "mini_python"
    if main_python.exists():
        if target_mini_python.exists():
            shutil.rmtree(target_mini_python)
        shutil.copytree(main_python, target_mini_python)
        print("Copied complete Python environment")
    
    # Copy python scripts
    target_python_scripts = resources_dir / "python"
    if main_python_scripts.exists():
        if target_python_scripts.exists():
            shutil.rmtree(target_python_scripts)
        shutil.copytree(main_python_scripts, target_python_scripts)
        print("Copied Python scripts")
    
    # Copy models if they exist
    main_models = Path("models")
    target_models = resources_dir / "models"
    if main_models.exists():
        if target_models.exists():
            shutil.rmtree(target_models)
        shutil.copytree(main_models, target_models)
        print("Copied AI models")
    else:
        # Try to copy from the electron-builder output
        builder_models = source_base / "resources" / "models"
        if builder_models.exists():
            shutil.copytree(builder_models, target_models)
            print("Copied AI models from builder output")
    
    # Step 4: Create README
    readme_content = '''# SRT GO Enhanced v2.0 - Complete Executable

## True Windows Executable Version

This is a complete Windows executable version with all necessary components:

### How to Run
Double-click the main executable file:
- **SRT GO Enhanced v2.0.exe** - Main executable (true .exe file)

### Features
- True Windows .exe executable - No .bat files needed
- Complete Python environment - All packages included
- Large V3 Turbo AI models - Highest accuracy
- Enhanced Voice Detector v2.0 - Revolutionary voice detection
- Modern GUI - Electron + React interface

### System Requirements
- Windows 10/11 (64-bit)
- 4GB+ RAM (8GB+ recommended)
- 8GB disk space

### First Use
1. Ensure system meets requirements
2. Double-click "SRT GO Enhanced v2.0.exe"
3. Wait for application to load
4. Start using AI subtitle generation

---
SRT GO Enhanced v2.0 - Revolutionary AI Subtitle Generator
Using true Windows executable, no batch files needed!
'''
    
    with open(target_base / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("Created README file")
    
    # Step 5: Final verification
    print("Verifying executable structure...")
    
    exe_file = target_base / "SRT GO Enhanced v2.0.exe"
    if exe_file.exists():
        size_mb = exe_file.stat().st_size / (1024*1024)
        print(f"Main executable: {size_mb:.1f} MB")
    
    python_exe = target_base / "resources" / "mini_python" / "python.exe"
    if python_exe.exists():
        print("Python environment: Complete")
    
    python_scripts = target_base / "resources" / "python" / "electron_backend.py"
    if python_scripts.exists():
        print("Python scripts: Complete")
    
    # Calculate total size
    total_size = sum(f.stat().st_size for f in target_base.rglob('*') if f.is_file()) / (1024**3)
    total_files = len(list(target_base.rglob('*')))
    
    print(f"Complete executable created successfully!")
    print(f"Location: {target_base.absolute()}")
    print(f"Total size: {total_size:.2f} GB")
    print(f"File count: {total_files}")
    
    print(f"Usage:")
    print(f"   Double-click: 'SRT GO Enhanced v2.0.exe' (true executable)")
    
    return True

if __name__ == "__main__":
    create_complete_executable()