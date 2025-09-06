"""
簡化的pip替代工具
用於嵌入式Python環境的包管理
"""
import sys
import os
import subprocess
import json

def install_package(package_name):
    """使用系統Python安裝包到嵌入式環境"""
    try:
        # 獲取當前目錄
        current_dir = os.path.dirname(os.path.abspath(__file__))
        site_packages = os.path.join(current_dir, 'Lib', 'site-packages')
        
        # 確保目錄存在
        os.makedirs(site_packages, exist_ok=True)
        
        print(f"Installing {package_name} to embedded Python environment...")
        print(f"Target directory: {site_packages}")
        
        # 使用系統pip安裝到指定目錄
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            '--target', site_packages,
            '--no-user',
            '--upgrade',
            package_name
        ], capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            print(f"✓ Successfully installed {package_name}")
            return True
        else:
            print(f"✗ Failed to install {package_name}")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error installing {package_name}: {e}")
        return False

def list_packages():
    """列出已安裝的包"""
    site_packages = os.path.join(os.path.dirname(__file__), 'Lib', 'site-packages')
    if not os.path.exists(site_packages):
        print("No packages installed")
        return
        
    # 查找.dist-info目錄
    packages = []
    for item in os.listdir(site_packages):
        if item.endswith('.dist-info'):
            package_name = item.replace('.dist-info', '').split('-')[0]
            packages.append(package_name)
    
    if packages:
        print("Installed packages:")
        for package in sorted(packages):
            print(f"  {package}")
    else:
        print("No packages found")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python setup_pip.py [install <package>|list]")
        print("Example: python setup_pip.py install requests")
        print("Example: python setup_pip.py list")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'install' and len(sys.argv) > 2:
        package_name = sys.argv[2]
        install_package(package_name)
    elif command == 'list':
        list_packages()
    else:
        print("Invalid command. Use 'install <package>' or 'list'")