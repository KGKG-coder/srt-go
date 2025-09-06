"""
修復嵌入式Python的ctypes模組問題 - 簡化版本
"""
import os
import sys
import shutil

def fix_ctypes():
    """修復ctypes問題"""
    print("Fixing embedded Python ctypes module...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 查找系統Python
    system_python = r"C:\Users\kai\AppData\Local\Programs\Python\Python310"
    
    if not os.path.exists(system_python):
        print("System Python not found. Please install Python 3.10+")
        return False
    
    print(f"Found system Python: {system_python}")
    
    # 複製必需的pyd文件
    files_to_copy = ["_ctypes.pyd", "_decimal.pyd", "_ssl.pyd", "_sqlite3.pyd"]
    copied = 0
    
    for filename in files_to_copy:
        source = os.path.join(system_python, filename)
        dest = os.path.join(current_dir, filename)
        
        if os.path.exists(source):
            try:
                shutil.copy2(source, dest)
                print(f"[OK] Copied: {filename}")
                copied += 1
            except Exception as e:
                print(f"[ERROR] Failed to copy {filename}: {e}")
    
    # 複製ctypes庫目錄
    ctypes_source = os.path.join(system_python, "Lib", "ctypes")
    ctypes_dest = os.path.join(current_dir, "Lib", "ctypes")
    
    if os.path.exists(ctypes_source):
        try:
            if os.path.exists(ctypes_dest):
                shutil.rmtree(ctypes_dest)
            shutil.copytree(ctypes_source, ctypes_dest)
            print("[OK] Copied: ctypes library directory")
            copied += 1
        except Exception as e:
            print(f"[ERROR] Failed to copy ctypes directory: {e}")
    
    print(f"\nFix completed: {copied} components copied")
    return copied > 0

def test_fix():
    """測試修復結果"""
    print("\nTesting ctypes fix:")
    print("-" * 20)
    
    try:
        import ctypes
        print("[OK] ctypes module loaded")
        
        # 測試soundfile和ctranslate2
        try:
            import soundfile
            print(f"[OK] soundfile: {soundfile.__version__}")
        except Exception as e:
            print(f"[--] soundfile: {e}")
        
        try:
            import ctranslate2
            print(f"[OK] ctranslate2: {ctranslate2.__version__}")
        except Exception as e:
            print(f"[--] ctranslate2: {e}")
            
        return True
    except Exception as e:
        print(f"[ERROR] ctypes still broken: {e}")
        return False

if __name__ == '__main__':
    if fix_ctypes():
        test_fix()
    else:
        print("Fix failed. Consider using system Python environment.")