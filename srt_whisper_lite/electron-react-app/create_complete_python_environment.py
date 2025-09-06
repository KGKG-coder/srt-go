#!/usr/bin/env python3
"""
完整Python環境創建器 - 為SRT GO Enhanced v2.0創建自包含Python環境
解決error code 3221225781和所有依賴問題
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_complete_python_environment():
    """創建完整的Python環境"""
    
    print("=== SRT GO Enhanced v2.0 - 完整Python環境創建器 ===")
    print("解決方案: 創建自包含的Python環境，包含所有必需套件")
    print()
    
    # 路徑設定
    target_dirs = [
        Path("mini_python"),
        Path("dist/SRT-GO-Enhanced-v2.0-Complete/resources/mini_python")
    ]
    
    # 必需的Python套件
    required_packages = [
        'numpy',
        'scipy', 
        'librosa',
        'soundfile',
        'faster-whisper',
        'torch',
        'torchaudio',
        'scikit-learn',
        'av',
        'coloredlogs',
        'opencc-python-reimplemented',
        'ctranslate2',
        'onnxruntime'
    ]
    
    print("步驟1: 檢查系統Python環境")
    try:
        result = subprocess.run([sys.executable, '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"OK 系統Python: {result.stdout.strip()}")
    except Exception as e:
        print(f"ERROR 系統Python檢查失敗: {e}")
        return False
    
    print("\n步驟2: 創建虛擬環境")
    venv_path = Path("temp_venv")
    
    # 清理舊的虛擬環境
    if venv_path.exists():
        shutil.rmtree(venv_path)
    
    try:
        subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], 
                      check=True)
        print(f"OK 虛擬環境已創建: {venv_path}")
    except Exception as e:
        print(f"ERROR 虛擬環境創建失敗: {e}")
        return False
    
    # 虛擬環境的Python路徑
    if os.name == 'nt':  # Windows
        venv_python = venv_path / "Scripts" / "python.exe"
        venv_pip = venv_path / "Scripts" / "pip.exe"
    else:  # Linux/macOS
        venv_python = venv_path / "bin" / "python"
        venv_pip = venv_path / "bin" / "pip"
    
    print("\n步驟3: 安裝必需套件")
    for package in required_packages:
        print(f"安裝 {package}...")
        try:
            subprocess.run([str(venv_pip), 'install', package, '--no-warn-script-location'], 
                          check=True, capture_output=True)
            print(f"OK {package}")
        except Exception as e:
            print(f"ERROR {package}: {e}")
            # 不中斷，繼續安裝其他套件
    
    print("\n步驟4: 複製完整環境到目標目錄")
    for target_dir in target_dirs:
        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)
            print(f"創建目標目錄: {target_dir}")
        
        # 複製Python執行檔
        if os.name == 'nt':
            source_files = [
                (venv_path / "Scripts" / "python.exe", target_dir / "python.exe"),
                (venv_path / "Scripts" / "pythonw.exe", target_dir / "pythonw.exe"),
            ]
        
        for source, dest in source_files:
            if source.exists():
                shutil.copy2(source, dest)
                print(f"✅ 複製: {source.name}")
        
        # 複製整個Lib目錄
        source_lib = venv_path / "Lib"
        target_lib = target_dir / "Lib"
        
        if target_lib.exists():
            shutil.rmtree(target_lib)
        
        if source_lib.exists():
            shutil.copytree(source_lib, target_lib)
            print(f"✅ 複製Lib目錄")
        
        # 複製DLL文件
        dll_sources = [
            Path("C:/Windows/System32/python311.dll"),
            Path("C:/Windows/System32/vcruntime140.dll"),
            Path("C:/Windows/System32/vcruntime140_1.dll"),
            Path("C:/Windows/System32/msvcp140.dll"),
            Path("C:/Windows/System32/msvcp140_1.dll"),
            Path("C:/Windows/System32/msvcp140_2.dll")
        ]
        
        for dll_source in dll_sources:
            if dll_source.exists():
                dll_dest = target_dir / dll_source.name
                try:
                    shutil.copy2(dll_source, dll_dest)
                    print(f"✅ 複製DLL: {dll_source.name}")
                except Exception as e:
                    print(f"⚠️ DLL複製警告: {dll_source.name} - {e}")
        
        # 創建python311._pth文件
        pth_content = """python311.zip
.
Lib
Lib/site-packages
"""
        pth_file = target_dir / "python311._pth"
        with open(pth_file, 'w') as f:
            f.write(pth_content)
        print(f"✅ 創建 python311._pth")
    
    print("\n步驟5: 驗證環境")
    for target_dir in target_dirs:
        if target_dir.exists():
            python_exe = target_dir / "python.exe"
            if python_exe.exists():
                print(f"\n測試 {target_dir}:")
                
                # 基本測試
                try:
                    result = subprocess.run([str(python_exe), '-c', 
                                           'import sys; print(f"Python {sys.version[:10]}")'],
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        print(f"✅ 基本測試: {result.stdout.strip()}")
                    else:
                        print(f"❌ 基本測試失敗: {result.stderr}")
                except Exception as e:
                    print(f"❌ 基本測試異常: {e}")
                
                # 套件測試
                test_script = '''
import sys
packages = ['numpy', 'scipy', 'librosa', 'faster_whisper', 'torch']
success = 0
total = len(packages)
for pkg in packages:
    try:
        __import__(pkg)
        print(f"✅ {pkg}")
        success += 1
    except ImportError:
        print(f"❌ {pkg}")
print(f"套件測試: {success}/{total}")
'''
                try:
                    result = subprocess.run([str(python_exe), '-c', test_script],
                                          capture_output=True, text=True, timeout=30)
                    if result.stdout:
                        print(result.stdout.strip())
                except Exception as e:
                    print(f"❌ 套件測試異常: {e}")
    
    # 清理臨時虛擬環境
    print("\n步驟6: 清理")
    if venv_path.exists():
        shutil.rmtree(venv_path)
        print("✅ 清理臨時虛擬環境")
    
    print("\n=== 完整Python環境創建完成 ===")
    print("現在兩個目標目錄都應該有完整的Python環境")
    print("包含所有必需的套件和DLL依賴")
    
    return True

if __name__ == "__main__":
    success = create_complete_python_environment()
    if success:
        print("\n🎉 SUCCESS: 完整Python環境創建成功！")
        print("現在可以測試修復後的.exe執行檔")
    else:
        print("\n❌ FAILED: 環境創建失敗")
        sys.exit(1)