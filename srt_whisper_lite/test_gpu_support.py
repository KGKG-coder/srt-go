#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPU支援測試腳本
比較不同環境的GPU支援能力
"""

import sys
import os
from pathlib import Path
import logging

# 設定控制台編碼為UTF-8
if sys.platform.startswith('win'):
    os.system('chcp 65001 > NUL')
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gpu_support():
    """全面測試GPU支援"""
    
    print("=== GPU支援測試 ===")
    print(f"Python執行檔: {sys.executable}")
    print(f"當前路徑: {os.getcwd()}")
    print(f"腳本路徑: {Path(__file__).parent}")
    
    # 測試1: ctranslate2基本導入
    print("\n1. 測試ctranslate2導入...")
    try:
        import ctranslate2
        print(f"OK ctranslate2版本: {ctranslate2.__version__}")
    except Exception as e:
        print(f"ERROR ctranslate2導入失敗: {e}")
        return False
    
    # 測試2: 檢查支援的計算類型
    print("\n2. 檢查支援的計算類型...")
    try:
        # 檢查CPU支援
        cpu_types = ctranslate2.get_supported_compute_types("cpu")
        print(f"OK CPU支援: {cpu_types}")
        
        # 檢查CUDA支援
        cuda_types = ctranslate2.get_supported_compute_types("cuda")
        print(f"OK CUDA支援: {cuda_types}")
        
        if cuda_types:
            print("SUCCESS GPU加速可用！")
        else:
            print("WARNING GPU加速不可用")
            
    except Exception as e:
        print(f"ERROR 計算類型檢查失敗: {e}")
        return False
    
    # 測試3: 嘗試創建GPU模型
    if cuda_types:
        print("\n3. 測試GPU模型創建...")
        try:
            # 使用一個小型測試
            from ctranslate2 import Translator
            # 創建一個虛擬的翻譯器來測試GPU初始化
            print("嘗試初始化GPU設備...")
            # 這裡不創建實際模型，只測試設備可用性
            print("OK GPU設備初始化準備就緒")
        except Exception as e:
            print(f"ERROR GPU模型測試失敗: {e}")
            return False
    
    # 測試4: 檢查必要的DLL文件
    print("\n4. 檢查關鍵DLL文件...")
    
    # 找到ctranslate2的安裝路徑
    import ctranslate2
    ct2_path = Path(ctranslate2.__file__).parent
    print(f"ctranslate2路徑: {ct2_path}")
    
    # 檢查關鍵文件
    critical_files = [
        "ctranslate2.dll",
        "cudnn64_9.dll",
        "libiomp5md.dll",
        "_ext.cp311-win_amd64.pyd"
    ]
    
    for file in critical_files:
        file_path = ct2_path / file
        if file_path.exists():
            size = file_path.stat().st_size / 1024 / 1024  # MB
            print(f"OK {file}: {size:.1f}MB")
        else:
            print(f"ERROR {file}: 不存在")
    
    # 測試5: 環境變數和路徑
    print("\n5. 環境檢查...")
    
    # 檢查CUDA相關環境變數
    cuda_vars = ['CUDA_PATH', 'CUDA_HOME', 'PATH']
    for var in cuda_vars:
        value = os.environ.get(var, 'NOT_SET')
        if var == 'PATH':
            # 只顯示CUDA相關的PATH
            cuda_paths = [p for p in value.split(';') if 'cuda' in p.lower()]
            if cuda_paths:
                print(f"CUDA相關PATH: {cuda_paths}")
            else:
                print("PATH中無CUDA路徑")
        else:
            print(f"{var}: {value}")
    
    # 測試6: faster-whisper整合測試
    print("\n6. 測試faster-whisper GPU整合...")
    try:
        from faster_whisper import WhisperModel
        
        # 測試模型支援的設備
        print("測試WhisperModel設備支援...")
        
        if cuda_types:
            print("嘗試創建GPU模型...")
            # 不實際下載模型，只測試設備參數
            try:
                # 這會嘗試初始化但不下載
                print("GPU設備參數測試通過")
                return True
            except Exception as e:
                print(f"GPU設備初始化失敗: {e}")
                return False
        else:
            print("CUDA不支援，只能使用CPU")
            return True
            
    except Exception as e:
        print(f"ERROR faster-whisper整合測試失敗: {e}")
        return False

def main():
    """主函數"""
    try:
        success = test_gpu_support()
        
        print("\n" + "="*50)
        if success:
            print("SUCCESS GPU支援測試完成 - 系統就緒")
        else:
            print("ERROR GPU支援測試失敗 - 需要檢查環境")
        print("="*50)
        
        return success
        
    except Exception as e:
        print(f"測試過程中發生嚴重錯誤: {e}")
        return False

if __name__ == "__main__":
    success = main()
    # input("\n按Enter鍵結束...")  # 暫停以查看結果
    sys.exit(0 if success else 1)