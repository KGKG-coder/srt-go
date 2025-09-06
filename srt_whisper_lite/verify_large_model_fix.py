#!/usr/bin/env python3
"""
驗證 LARGE 模型 UI 修正是否成功
"""

import json
from pathlib import Path

def verify_app_js():
    """驗證 App.js 是否已正確修正"""
    app_js_path = Path("electron-react-app/react-app/src/App.js")
    
    if not app_js_path.exists():
        print("[ERROR] App.js 不存在")
        return False
    
    with open(app_js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        "model: 'large',  // 強制使用 LARGE 模型 - 不可更改",
        "console.log('[FIX] 檢測到模型設定不是 large，強制修正為 large');",
        "useEffect(() => {",
        "if (settings.model !== 'large')"
    ]
    
    all_found = True
    for check in checks:
        if check in content:
            print(f"[OK] 找到: {check[:50]}...")
        else:
            print(f"[ERROR] 未找到: {check[:50]}...")
            all_found = False
    
    return all_found

def verify_electron_backend():
    """驗證 electron_backend.py 是否已正確修正"""
    backend_path = Path("electron_backend.py")
    
    if not backend_path.exists():
        print("[ERROR] electron_backend.py 不存在")
        return False
    
    with open(backend_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        "settings['model'] = 'large'",
        "[FIX] 強制使用 LARGE 模型"
    ]
    
    all_found = True
    for check in checks:
        if check in content:
            print(f"[OK] 找到: {check}")
        else:
            print(f"[ERROR] 未找到: {check}")
            all_found = False
    
    return all_found

def check_cache_script():
    """檢查清除緩存腳本是否已創建"""
    script_path = Path("electron-react-app/clear_cache.js")
    
    if script_path.exists():
        print(f"[OK] 清除緩存腳本已創建: {script_path}")
        return True
    else:
        print(f"[ERROR] 清除緩存腳本不存在: {script_path}")
        return False

def main():
    """主函數"""
    print("=" * 60)
    print("驗證 LARGE 模型 UI 修正")
    print("=" * 60)
    
    print("\n1. 檢查 App.js 修正:")
    app_ok = verify_app_js()
    
    print("\n2. 檢查 electron_backend.py 修正:")
    backend_ok = verify_electron_backend()
    
    print("\n3. 檢查清除緩存腳本:")
    script_ok = check_cache_script()
    
    print("\n" + "=" * 60)
    if all([app_ok, backend_ok, script_ok]):
        print("[SUCCESS] 所有修正已完成！")
        print("\n接下來的步驟:")
        print("1. 關閉現有的 SRT GO 應用程式")
        print("2. 重新啟動應用程式")
        print("3. 檢查 UI 是否顯示 'Large (專業版)' 模型")
        print("4. 如果仍顯示錯誤，開啟開發者工具 (F12) 並在 Console 執行:")
        print("   localStorage.removeItem('srtgo-settings'); location.reload();")
        print("5. 執行測試確認實際使用 LARGE 模型")
    else:
        print("[ERROR] 部分修正失敗，請檢查錯誤訊息")
    
    print("=" * 60)
    return all([app_ok, backend_ok, script_ok])

if __name__ == "__main__":
    main()