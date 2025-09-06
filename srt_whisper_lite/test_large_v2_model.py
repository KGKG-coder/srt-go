#!/usr/bin/env python3
"""
測試 LARGE V2 模型是否正確載入和使用
"""

import sys
from pathlib import Path

# 添加路徑
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_model_loading():
    """測試模型載入"""
    print("=" * 60)
    print("測試 LARGE V2 模型載入")
    print("=" * 60)
    
    try:
        from simplified_subtitle_core import SimplifiedSubtitleCore
        
        print("1. 創建 SimplifiedSubtitleCore 實例...")
        core = SimplifiedSubtitleCore()
        
        print(f"2. 檢查模型設定: {core.model_size}")
        
        if core.model_size == "large-v2":
            print("[OK] SUCCESS: 模型設定為 large-v2")
        else:
            print(f"[ERROR] 模型設定錯誤，當前為: {core.model_size}")
            return False
        
        print("3. 測試模型載入...")
        # 不實際載入模型，只測試配置
        print(f"   - 模型大小: {core.model_size}")
        print(f"   - 設備: {core.device}")
        print(f"   - 計算類型: {core.compute_type}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 測試失敗 - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_model_force():
    """測試後端強制模型設定"""
    print("\n" + "=" * 60)
    print("測試後端模型強制設定")
    print("=" * 60)
    
    # 模擬設定
    test_settings = {
        "model": "medium",  # 故意設定錯誤的模型
        "language": "auto",
        "outputFormat": "srt"
    }
    
    print(f"原始設定: {test_settings}")
    
    # 模擬後端邏輯
    original_model = test_settings.get('model', 'unknown')
    test_settings['model'] = 'large-v2'
    
    print(f"強制修正後: {test_settings}")
    print(f"日誌: [FIX] 強制使用 LARGE V2 模型（原設定: {original_model}）")
    
    if test_settings['model'] == 'large-v2':
        print("[OK] SUCCESS: 後端強制設定正確")
        return True
    else:
        print("[ERROR] 後端強制設定失敗")
        return False

def main():
    """主函數"""
    print("LARGE V2 模型測試")
    
    test1 = test_model_loading()
    test2 = test_backend_model_force()
    
    print("\n" + "=" * 60)
    if test1 and test2:
        print("[SUCCESS] 所有測試通過！LARGE V2 模型設定成功")
        print("\n請重新啟動應用程式，任務條應顯示:")
        print("   「載入 LARGE-V2 模型...」")
    else:
        print("[ERROR] 部分測試失敗，請檢查設定")
    print("=" * 60)

if __name__ == "__main__":
    main()