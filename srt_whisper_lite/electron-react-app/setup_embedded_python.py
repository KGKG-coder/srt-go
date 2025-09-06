#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
嵌入式 Python 環境完整設置腳本
安裝所有必要的依賴和元件
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import platform

def setup_encoding():
    """設置正確的編碼"""
    if sys.platform.startswith('win'):
        # Windows 環境設置
        os.system('chcp 65001 > NUL 2>&1')
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')

def check_python_version():
    """檢查 Python 版本"""
    print("檢查 Python 版本...")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("[警告] Python 版本過低，建議使用 3.8 以上版本")
        return False
    return True

def install_pip_if_needed():
    """確保 pip 已安裝並更新"""
    print("\n更新 pip...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            check=True,
            capture_output=True
        )
        # 升級 pip
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            check=False
        )
        print("[OK] pip 已更新")
        return True
    except:
        print("[錯誤] pip 未安裝，嘗試安裝...")
        try:
            import ensurepip
            ensurepip.bootstrap()
            return True
        except:
            print("[錯誤] 無法安裝 pip")
            return False

def get_dependencies():
    """獲取所有必要的依賴列表"""
    return {
        # 核心 AI 依賴
        "faster-whisper": {
            "version": ">=1.0.0",
            "description": "Faster-Whisper AI 引擎",
            "required": True
        },
        "ctranslate2": {
            "version": ">=3.24.0",
            "description": "CTranslate2 加速引擎",
            "required": True
        },
        
        # 音頻處理
        "numpy": {
            "version": ">=1.24.0,<2.0.0",
            "description": "數值計算庫",
            "required": True
        },
        "scipy": {
            "version": ">=1.10.0",
            "description": "科學計算庫",
            "required": True
        },
        "librosa": {
            "version": ">=0.10.0",
            "description": "音頻分析庫",
            "required": True
        },
        "soundfile": {
            "version": ">=0.12.0",
            "description": "音頻文件處理",
            "required": True
        },
        "pydub": {
            "version": ">=0.25.0",
            "description": "音頻格式轉換",
            "required": False
        },
        
        # 機器學習相關
        "scikit-learn": {
            "version": ">=1.3.0",
            "description": "機器學習庫（語音檢測用）",
            "required": True
        },
        "torch": {
            "version": "",  # 版本根據系統自動選擇
            "description": "PyTorch（可選，GPU加速）",
            "required": False,
            "special": "torch"
        },
        
        # 工具庫
        "tqdm": {
            "version": ">=4.65.0",
            "description": "進度條顯示",
            "required": True
        },
        "requests": {
            "version": ">=2.31.0",
            "description": "HTTP 請求庫",
            "required": True
        },
        "pyannote.audio": {
            "version": "",
            "description": "語音活動檢測（VAD）",
            "required": False
        },
        
        # 字幕處理
        "pysrt": {
            "version": ">=1.1.0",
            "description": "SRT 字幕處理",
            "required": False
        },
        "webvtt-py": {
            "version": ">=0.4.0",
            "description": "WebVTT 字幕處理",
            "required": False
        },
        
        # 中文處理
        "opencc-python-reimplemented": {
            "version": ">=0.1.0",
            "description": "繁簡轉換",
            "required": False
        },
        "jieba": {
            "version": ">=0.42.0",
            "description": "中文分詞",
            "required": False
        },
        
        # Hugging Face 模型支援
        "huggingface-hub": {
            "version": ">=0.19.0",
            "description": "Hugging Face 模型下載",
            "required": True
        },
        "tokenizers": {
            "version": ">=0.15.0",
            "description": "分詞器",
            "required": True
        },
        "transformers": {
            "version": ">=4.36.0",
            "description": "Transformers 模型庫",
            "required": False
        }
    }

def install_torch_cpu():
    """安裝 CPU 版本的 PyTorch"""
    print("\n安裝 PyTorch (CPU)...")
    try:
        # CPU 版本 PyTorch
        subprocess.run(
            [sys.executable, "-m", "pip", "install", 
             "torch", "torchvision", "torchaudio",
             "--index-url", "https://download.pytorch.org/whl/cpu"],
            check=True
        )
        print("[OK] PyTorch CPU 版本已安裝")
        return True
    except:
        print("[警告] PyTorch 安裝失敗（可選依賴）")
        return False

def install_dependency(name, info):
    """安裝單個依賴"""
    try:
        # 特殊處理 torch
        if info.get("special") == "torch":
            return install_torch_cpu()
        
        # 構建安裝命令
        if info["version"]:
            package = f"{name}{info['version']}"
        else:
            package = name
        
        print(f"安裝 {name} - {info['description']}...")
        
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"[OK] {name} 安裝成功")
            return True
        else:
            if info["required"]:
                print(f"[錯誤] {name} 安裝失敗（必要依賴）")
                print(f"錯誤信息: {result.stderr}")
            else:
                print(f"[警告] {name} 安裝失敗（可選依賴）")
            return False
            
    except Exception as e:
        print(f"[錯誤] 安裝 {name} 時發生異常: {e}")
        return False

def verify_installation():
    """驗證核心模組是否安裝成功"""
    print("\n驗證核心模組...")
    
    core_modules = [
        ("numpy", "NumPy"),
        ("faster_whisper", "Faster-Whisper"),
        ("ctranslate2", "CTranslate2"),
        ("librosa", "Librosa"),
        ("soundfile", "SoundFile"),
        ("sklearn", "Scikit-learn"),
        ("tqdm", "TQDM"),
        ("huggingface_hub", "Hugging Face Hub")
    ]
    
    all_ok = True
    for module_name, display_name in core_modules:
        try:
            __import__(module_name)
            print(f"[OK] {display_name} 可用")
        except ImportError:
            print(f"[錯誤] {display_name} 不可用")
            all_ok = False
    
    return all_ok

def create_requirements_txt():
    """創建 requirements.txt 文件"""
    print("\n創建 requirements.txt...")
    
    deps = get_dependencies()
    required_deps = []
    optional_deps = []
    
    for name, info in deps.items():
        if info.get("special") == "torch":
            continue  # PyTorch 需要特殊處理
            
        if info["version"]:
            line = f"{name}{info['version']}"
        else:
            line = name
            
        if info["required"]:
            required_deps.append(line)
        else:
            optional_deps.append(f"# {line}  # {info['description']}")
    
    content = "# 必要依賴\n"
    content += "\n".join(required_deps)
    content += "\n\n# 可選依賴\n"
    content += "\n".join(optional_deps)
    content += "\n\n# PyTorch (CPU版本)\n"
    content += "# torch --index-url https://download.pytorch.org/whl/cpu\n"
    
    req_path = Path(__file__).parent / "mini_python_requirements.txt"
    with open(req_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[OK] 已創建 {req_path}")

def setup_mini_python_path():
    """設置 mini_python 路徑"""
    mini_python = Path(__file__).parent / "mini_python" / "python.exe"
    
    if mini_python.exists():
        print(f"\n使用嵌入式 Python: {mini_python}")
        return str(mini_python)
    else:
        print("\n[警告] 未找到 mini_python，使用當前 Python")
        return sys.executable

def main():
    """主函數"""
    print("="*60)
    print("嵌入式 Python 環境設置")
    print("="*60)
    
    # 設置編碼
    setup_encoding()
    
    # 檢查 Python 版本
    if not check_python_version():
        return False
    
    # 確保 pip 可用
    if not install_pip_if_needed():
        return False
    
    # 獲取依賴列表
    deps = get_dependencies()
    
    print(f"\n準備安裝 {len(deps)} 個依賴包...")
    
    # 安裝依賴
    required_failed = []
    optional_failed = []
    
    for name, info in deps.items():
        success = install_dependency(name, info)
        if not success:
            if info["required"]:
                required_failed.append(name)
            else:
                optional_failed.append(name)
    
    # 驗證安裝
    print("\n" + "="*60)
    core_ok = verify_installation()
    
    # 創建 requirements.txt
    create_requirements_txt()
    
    # 總結
    print("\n" + "="*60)
    print("安裝總結")
    print("="*60)
    
    if required_failed:
        print(f"\n[錯誤] {len(required_failed)} 個必要依賴安裝失敗:")
        for name in required_failed:
            print(f"  - {name}")
    
    if optional_failed:
        print(f"\n[警告] {len(optional_failed)} 個可選依賴安裝失敗:")
        for name in optional_failed:
            print(f"  - {name}")
    
    if core_ok and not required_failed:
        print("\n[成功] 核心環境設置完成！")
        print("\n下一步:")
        print("1. 執行 test_simplified_backend.bat 測試")
        print("2. 執行 npm run dev:simplified 啟動開發模式")
        return True
    else:
        print("\n[失敗] 部分核心依賴未能安裝")
        print("請檢查網絡連接並重試")
        return False

if __name__ == "__main__":
    # 如果是從 mini_python 執行，直接使用
    # 否則嘗試使用 mini_python
    if "mini_python" not in sys.executable:
        mini_python = Path(__file__).parent / "mini_python" / "python.exe"
        if mini_python.exists():
            print(f"切換到嵌入式 Python: {mini_python}")
            # 重新執行腳本
            result = subprocess.run(
                [str(mini_python), __file__],
                cwd=Path(__file__).parent
            )
            sys.exit(result.returncode)
    
    # 執行主函數
    success = main()
    sys.exit(0 if success else 1)