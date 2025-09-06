"""
pip替代工具 for 嵌入式Python環境
提供基本的包管理功能
"""
import sys
import os

# 重定向到我們的setup_pip工具
if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    setup_pip_path = os.path.join(current_dir, 'setup_pip.py')
    
    # 構建新的命令行參數
    if len(sys.argv) > 1:
        if sys.argv[1] == 'list':
            os.system(f'python "{setup_pip_path}" list')
        elif sys.argv[1] == 'install' and len(sys.argv) > 2:
            package = sys.argv[2]
            os.system(f'python "{setup_pip_path}" install {package}')
        else:
            print("Usage: python pip.py [list|install <package>]")
            print("Available commands:")
            print("  list        - List installed packages")
            print("  install <pkg> - Install a package")
    else:
        print("SRT GO Embedded Python Package Manager")
        print("Usage: python pip.py [list|install <package>]")
        print("")
        print("This embedded Python environment comes pre-configured with all")
        print("necessary packages for SRT GO subtitle generation:")
        print("  [OK] faster-whisper - AI subtitle generation")
        print("  [OK] torch - Deep learning framework") 
        print("  [OK] soundfile - Audio processing")
        print("  [OK] requests - HTTP client")
        print("  [OK] PyYAML - Configuration files")
        print("  ... and more")
        print("")
        print("No additional packages need to be installed for normal operation.")