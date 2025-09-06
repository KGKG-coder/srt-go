"""
簡化的包驗證工具
不使用網絡功能，只檢查當前已安裝的包
"""

def verify_core_packages():
    """驗證核心包的可用性"""
    print("SRT GO 嵌入式Python - 包驗證報告")
    print("=" * 50)
    
    # 必需的核心包
    core_packages = [
        ('faster_whisper', '語音識別核心'),
        ('soundfile', '音頻文件處理'),
        ('ctranslate2', 'AI模型推理'),
        ('huggingface_hub', '模型下載')
    ]
    
    # 可選的增強包
    optional_packages = [
        ('numpy', '數值計算'),
        ('scipy', '科學計算'),
        ('librosa', '音頻分析'),
        ('noisereduce', '降噪處理'),
        ('sklearn', '機器學習')
    ]
    
    print("核心包狀態:")
    print("-" * 30)
    core_available = 0
    for package, description in core_packages:
        try:
            __import__(package)
            version = getattr(__import__(package), '__version__', 'unknown')
            print(f"✓ {package:<15} {version:<10} - {description}")
            core_available += 1
        except ImportError:
            print(f"✗ {package:<15} {'missing':<10} - {description}")
    
    print(f"\n核心包可用性: {core_available}/{len(core_packages)}")
    
    print("\n增強功能包狀態:")
    print("-" * 30)
    optional_available = 0
    for package, description in optional_packages:
        try:
            __import__(package)
            version = getattr(__import__(package), '__version__', 'unknown')
            print(f"✓ {package:<15} {version:<10} - {description}")
            optional_available += 1
        except ImportError:
            print(f"○ {package:<15} {'optional':<10} - {description}")
    
    print(f"\n增強包可用性: {optional_available}/{len(optional_packages)}")
    
    # 功能狀態評估
    print("\n功能狀態評估:")
    print("=" * 50)
    
    if core_available == len(core_packages):
        print("✓ 核心功能: 完全可用")
        status = "excellent"
    elif core_available >= len(core_packages) - 1:
        print("⚠ 核心功能: 基本可用")
        status = "good"
    else:
        print("✗ 核心功能: 不完整")
        status = "needs_fix"
    
    if optional_available >= 3:
        print("✓ 增強功能: 完全可用")
    elif optional_available >= 1:
        print("○ 增強功能: 部分可用")
    else:
        print("○ 增強功能: 使用基礎實現")
    
    # 建議
    print("\n建議:")
    print("-" * 20)
    if status == "excellent":
        print("• 環境配置完善，所有功能可正常使用")
    elif status == "good":
        print("• 核心功能完整，可正常生成字幕")
        print("• 建議安裝缺失的核心包以獲得最佳體驗")
    else:
        print("• 需要修復缺失的核心依賴")
        print("• 建議重新安裝或使用系統Python環境")
    
    if optional_available == 0:
        print("• 可考慮安裝numpy以提升音頻處理性能")
    
    return status

if __name__ == '__main__':
    verify_core_packages()