"""
修復嵌入式Python的ctypes模組問題
從標準Python安裝中複製必需的ctypes文件
"""
import os
import sys
import shutil
import glob

def find_system_python():
    """查找系統Python安裝"""
    common_paths = [
        r"C:\Python311",
        r"C:\Python310", 
        r"C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311",
        r"C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310",
        r"C:\Program Files\Python311",
        r"C:\Program Files\Python310"
    ]
    
    # 展開環境變數
    import os
    expanded_paths = []
    for path in common_paths:
        expanded = os.path.expandvars(path)
        expanded_paths.append(expanded)
    
    for path in expanded_paths:
        if os.path.exists(path):
            python_exe = os.path.join(path, "python.exe")
            if os.path.exists(python_exe):
                return path
    
    return None

def copy_ctypes_files():
    """從系統Python複製ctypes相關文件"""
    print("正在修復嵌入式Python的ctypes模組...")
    
    # 當前嵌入式Python目錄
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 查找系統Python
    system_python = find_system_python()
    if not system_python:
        print("錯誤: 找不到系統Python安裝")
        print("請確保已安裝Python 3.10或3.11")
        return False
    
    print(f"找到系統Python: {system_python}")
    
    # 需要複製的文件
    files_to_copy = [
        "_ctypes.pyd",
        "_decimal.pyd", 
        "_sqlite3.pyd",
        "_ssl.pyd",
        "_uuid.pyd"
    ]
    
    copied_count = 0
    for filename in files_to_copy:
        source = os.path.join(system_python, filename)
        dest = os.path.join(current_dir, filename)
        
        if os.path.exists(source):
            try:
                shutil.copy2(source, dest)
                print(f"✓ 已複製: {filename}")
                copied_count += 1
            except Exception as e:
                print(f"✗ 複製失敗 {filename}: {e}")
        else:
            print(f"○ 未找到: {filename}")
    
    # 複製ctypes模組目錄
    ctypes_source = os.path.join(system_python, "Lib", "ctypes")
    ctypes_dest = os.path.join(current_dir, "Lib", "ctypes")
    
    if os.path.exists(ctypes_source):
        try:
            if os.path.exists(ctypes_dest):
                shutil.rmtree(ctypes_dest)
            shutil.copytree(ctypes_source, ctypes_dest)
            print("✓ 已複製: ctypes模組目錄")
            copied_count += 1
        except Exception as e:
            print(f"✗ 複製ctypes目錄失敗: {e}")
    
    print(f"\n修復完成: {copied_count}/{len(files_to_copy)+1} 個組件")
    
    if copied_count > 0:
        print("請重新測試package imports")
        return True
    else:
        print("修復失敗，建議使用系統Python環境")
        return False

def test_imports():
    """測試修復後的imports"""
    print("\n測試ctypes修復結果:")
    print("-" * 30)
    
    try:
        import ctypes
        print("✓ ctypes 模組載入成功")
        
        # 測試基本ctypes功能
        ctypes.c_int(42)
        print("✓ ctypes 基本功能正常")
        
    except Exception as e:
        print(f"✗ ctypes 仍有問題: {e}")
        return False
    
    # 測試依賴ctypes的包
    test_packages = ['soundfile', 'ctranslate2']
    success_count = 0
    
    for package in test_packages:
        try:
            __import__(package)
            print(f"✓ {package} 載入成功")
            success_count += 1
        except Exception as e:
            print(f"✗ {package} 載入失敗: {e}")
    
    return success_count > 0

if __name__ == '__main__':
    success = copy_ctypes_files()
    if success:
        test_imports()