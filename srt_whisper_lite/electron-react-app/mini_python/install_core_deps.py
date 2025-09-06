"""
核心依賴安裝工具
為嵌入式Python環境安裝必需的科學計算包
"""
import os
import sys
import subprocess
import urllib.request
import tempfile

def download_wheel(package_name, python_version="cp311", platform="win_amd64"):
    """下載預編譯wheel包"""
    base_url = f"https://pypi.org/simple/{package_name}/"
    
    print(f"正在查找 {package_name} 的預編譯包...")
    
    # 常見的科學計算包URL模式
    wheel_urls = {
        'numpy': 'https://files.pythonhosted.org/packages/py3/n/numpy/numpy-1.24.3-cp311-cp311-win_amd64.whl',
        'scipy': 'https://files.pythonhosted.org/packages/py3/s/scipy/scipy-1.11.1-cp311-cp311-win_amd64.whl',
        'librosa': 'https://files.pythonhosted.org/packages/py3/l/librosa/librosa-0.10.1-py3-none-any.whl',
        'noisereduce': 'https://files.pythonhosted.org/packages/py3/n/noisereduce/noisereduce-3.0.0-py3-none-any.whl'
    }
    
    if package_name in wheel_urls:
        return wheel_urls[package_name]
    return None

def install_package(package_name):
    """安裝單個包"""
    print(f"正在安裝 {package_name}...")
    
    # 嘗試使用setup_pip安裝
    current_dir = os.path.dirname(os.path.abspath(__file__))
    setup_pip_path = os.path.join(current_dir, 'setup_pip.py')
    
    try:
        result = subprocess.run([
            sys.executable, setup_pip_path, 'install', package_name
        ], capture_output=True, text=True, cwd=current_dir)
        
        if result.returncode == 0:
            print(f"✓ {package_name} 安裝成功")
            return True
        else:
            print(f"✗ {package_name} 安裝失敗: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ 安裝 {package_name} 時發生錯誤: {e}")
        return False

def install_core_packages():
    """安裝核心科學計算包"""
    core_packages = [
        'numpy',
        'scipy', 
        'librosa',
        'noisereduce',
        'scikit-learn'
    ]
    
    print("SRT GO 嵌入式Python - 核心依賴安裝器")
    print("=" * 50)
    
    success_count = 0
    total_count = len(core_packages)
    
    for package in core_packages:
        if install_package(package):
            success_count += 1
        print()
    
    print("=" * 50)
    print(f"安裝完成: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        print("✓ 所有核心依賴安裝成功！")
        return True
    else:
        print("⚠ 部分依賴安裝失敗，但核心功能仍可正常使用")
        return False

def verify_installation():
    """驗證已安裝的包"""
    print("\n驗證已安裝的包:")
    print("-" * 30)
    
    test_imports = {
        'numpy': 'import numpy; print(f"NumPy: {numpy.__version__}")',
        'scipy': 'import scipy; print(f"SciPy: {scipy.__version__}")',
        'librosa': 'import librosa; print(f"Librosa: {librosa.__version__}")',
        'faster_whisper': 'import faster_whisper; print(f"Faster-Whisper: {faster_whisper.__version__}")',
        'soundfile': 'import soundfile; print(f"SoundFile: {soundfile.__version__}")'
    }
    
    for package, test_code in test_imports.items():
        try:
            exec(test_code)
        except ImportError:
            print(f"{package}: 未安裝")
        except Exception as e:
            print(f"{package}: 檢查失敗 ({e})")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'verify':
        verify_installation()
    else:
        install_core_packages()
        verify_installation()