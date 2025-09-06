"""
基礎包驗證工具 - 兼容CP950編碼
"""

def verify_packages():
    """驗證包的可用性"""
    print("SRT GO Python Environment Verification")
    print("=" * 50)
    
    # 必需的核心包
    core_packages = [
        ('faster_whisper', 'Speech Recognition Core'),
        ('soundfile', 'Audio File Processing'),
        ('ctranslate2', 'AI Model Inference'),
        ('huggingface_hub', 'Model Hub Access')
    ]
    
    # 可選的增強包
    optional_packages = [
        ('numpy', 'Numerical Computing'),
        ('scipy', 'Scientific Computing'),
        ('librosa', 'Audio Analysis'),
        ('noisereduce', 'Audio Denoising')
    ]
    
    print("Core Packages Status:")
    print("-" * 30)
    core_available = 0
    for package, description in core_packages:
        try:
            mod = __import__(package)
            version = getattr(mod, '__version__', 'unknown')
            print(f"[OK] {package:<15} {version:<10} - {description}")
            core_available += 1
        except ImportError:
            print(f"[--] {package:<15} {'missing':<10} - {description}")
    
    print(f"\nCore Package Availability: {core_available}/{len(core_packages)}")
    
    print("\nOptional Enhancement Packages:")
    print("-" * 30)
    optional_available = 0
    for package, description in optional_packages:
        try:
            mod = __import__(package)
            version = getattr(mod, '__version__', 'unknown')
            print(f"[OK] {package:<15} {version:<10} - {description}")
            optional_available += 1
        except ImportError:
            print(f"[--] {package:<15} {'optional':<10} - {description}")
    
    print(f"\nOptional Package Availability: {optional_available}/{len(optional_packages)}")
    
    # 功能狀態評估
    print("\nFunctionality Assessment:")
    print("=" * 50)
    
    if core_available == len(core_packages):
        print("[EXCELLENT] Core functionality: Fully operational")
        status = "excellent"
    elif core_available >= len(core_packages) - 1:
        print("[GOOD] Core functionality: Basically operational")
        status = "good"
    else:
        print("[NEEDS_FIX] Core functionality: Incomplete")
        status = "needs_fix"
    
    if optional_available >= 3:
        print("[OK] Enhanced features: Fully available")
    elif optional_available >= 1:
        print("[PARTIAL] Enhanced features: Partially available")
    else:
        print("[BASIC] Enhanced features: Using fallback implementations")
    
    # 當前已安裝包列表
    print("\nCurrently Installed Packages:")
    print("-" * 40)
    import sys
    import os
    
    # 檢查Lib/site-packages目錄
    lib_path = os.path.join(os.path.dirname(sys.executable), 'Lib')
    if os.path.exists(lib_path):
        print(f"Library path: {lib_path}")
        try:
            site_packages = os.path.join(lib_path, 'site-packages')
            if os.path.exists(site_packages):
                packages = [d for d in os.listdir(site_packages) if d.endswith('.dist-info')]
                print(f"Found {len(packages)} installed packages via dist-info")
        except:
            pass
    
    return status

if __name__ == '__main__':
    verify_packages()