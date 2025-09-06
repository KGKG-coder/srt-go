"""
測試 GUI 啟動功能
"""
import sys
import threading
import time

def test_gui():
    """測試 GUI 是否能正常啟動"""
    try:
        # 匯入 GUI 模組
        from local_gui import SubtitleGeneratorGUI
        import tkinter as tk
        
        print("[OK] GUI 模組匯入成功")
        
        # 創建主視窗
        root = tk.Tk()
        
        # 創建 GUI 實例
        app = SubtitleGeneratorGUI(root)
        
        print("[OK] GUI 實例創建成功")
        
        # 設定 3 秒後自動關閉
        def close_after_delay():
            time.sleep(3)
            root.quit()
            root.destroy()
            print("[OK] GUI 自動關閉成功")
        
        # 在另一個線程中執行關閉
        close_thread = threading.Thread(target=close_after_delay, daemon=True)
        close_thread.start()
        
        print("[OK] GUI 啟動中（3秒後自動關閉）...")
        
        # 啟動主循環
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"[FAIL] GUI 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== 測試 GUI 功能 ===")
    print(f"Python: {sys.version}")
    print()
    
    success = test_gui()
    
    if success:
        print("\n✅ GUI 測試完成！")
    else:
        print("\n❌ GUI 測試失敗！")
    
    sys.exit(0 if success else 1)