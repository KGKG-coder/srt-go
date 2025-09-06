#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 模型下載和管理腳本
"""

import os
import sys
import json
import shutil
from pathlib import Path
from huggingface_hub import hf_hub_download, snapshot_download
import requests

def setup_encoding():
    """設置編碼"""
    if sys.platform.startswith('win'):
        os.system('chcp 65001 > NUL 2>&1')

def get_model_config():
    """獲取模型配置"""
    return {
        "whisper_large_v3_turbo": {
            "repo_id": "openai/whisper-large-v3-turbo",
            "description": "Whisper Large v3 Turbo（主要模型）",
            "size": "1.5GB",
            "required": True,
            "download_method": "snapshot"
        },
        "whisper_large_v3_turbo_ct2": {
            "repo_id": "zzxxcc0805/my-whisper-large-v3-turbo-ct2",
            "description": "優化的 CT2 格式（更快）",
            "size": "800MB", 
            "required": False,
            "download_method": "snapshot"
        },
        "whisper_medium": {
            "repo_id": "openai/whisper-medium",
            "description": "Whisper Medium（備用模型）",
            "size": "769MB",
            "required": False,
            "download_method": "snapshot"
        }
    }

def check_disk_space(required_gb=5):
    """檢查磁碟空間"""
    current_dir = Path(__file__).parent
    free_bytes = shutil.disk_usage(current_dir).free
    free_gb = free_bytes / (1024**3)
    
    print(f"可用磁碟空間: {free_gb:.1f} GB")
    
    if free_gb < required_gb:
        print(f"[警告] 磁碟空間不足，建議至少 {required_gb} GB")
        return False
    return True

def check_internet_connection():
    """檢查網路連線"""
    try:
        response = requests.get("https://huggingface.co", timeout=5)
        if response.status_code == 200:
            print("[OK] 網路連線正常")
            return True
    except:
        pass
    
    print("[錯誤] 無法連接到 Hugging Face，請檢查網路連線")
    return False

def setup_models_directory():
    """設置模型目錄"""
    models_dir = Path(__file__).parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    print(f"模型目錄: {models_dir}")
    return models_dir

def download_model(repo_id, description, download_method="snapshot"):
    """下載單個模型"""
    print(f"\n下載 {description}...")
    print(f"倉庫: {repo_id}")
    
    try:
        models_dir = setup_models_directory()
        local_dir = models_dir / repo_id.replace("/", "_")
        
        if local_dir.exists():
            print(f"[跳過] 模型已存在: {local_dir}")
            return True
        
        if download_method == "snapshot":
            # 下載整個倉庫
            snapshot_download(
                repo_id=repo_id,
                local_dir=local_dir,
                local_dir_use_symlinks=False
            )
        else:
            # 下載特定文件
            hf_hub_download(
                repo_id=repo_id,
                filename="pytorch_model.bin",
                local_dir=local_dir
            )
        
        print(f"[OK] {description} 下載完成")
        return True
        
    except Exception as e:
        print(f"[錯誤] {description} 下載失敗: {e}")
        return False

def verify_model(model_path):
    """驗證模型完整性"""
    if not model_path.exists():
        return False
    
    # 檢查基本文件
    required_files = ["config.json"]
    for file_name in required_files:
        if not (model_path / file_name).exists():
            return False
    
    return True

def create_model_manifest():
    """創建模型清單"""
    models_dir = setup_models_directory()
    manifest = {
        "version": "2.2.1",
        "updated": str(Path(__file__).stat().st_mtime),
        "models": {}
    }
    
    config = get_model_config()
    for model_id, model_info in config.items():
        local_path = models_dir / model_info["repo_id"].replace("/", "_")
        
        manifest["models"][model_id] = {
            "repo_id": model_info["repo_id"],
            "description": model_info["description"],
            "local_path": str(local_path),
            "available": verify_model(local_path),
            "size": model_info["size"]
        }
    
    # 保存清單
    manifest_file = models_dir / "model_manifest.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] 模型清單已保存: {manifest_file}")
    return manifest

def show_model_status():
    """顯示模型狀態"""
    print("\n" + "="*60)
    print("模型狀態")
    print("="*60)
    
    manifest = create_model_manifest()
    
    for model_id, model_info in manifest["models"].items():
        status = "[已安裝]" if model_info["available"] else "[未安裝]"
        print(f"{status} {model_info['description']}")
        print(f"         大小: {model_info['size']}")
        print(f"         路徑: {model_info['local_path']}")
        print()

def main():
    """主函數"""
    setup_encoding()
    
    print("AI 模型設置腳本")
    print("版本: 2.2.1-simplified")
    print("="*60)
    
    # 檢查先決條件
    if not check_internet_connection():
        return False
    
    if not check_disk_space():
        answer = input("磁碟空間可能不足，是否繼續？ (y/N): ")
        if answer.lower() != 'y':
            return False
    
    # 設置模型目錄
    models_dir = setup_models_directory()
    
    # 獲取模型配置
    config = get_model_config()
    
    print(f"\n發現 {len(config)} 個可用模型:")
    for model_id, info in config.items():
        status = "必要" if info["required"] else "可選"
        print(f"  [{status}] {info['description']} ({info['size']})")
    
    # 詢問用戶選擇
    print(f"\n選項:")
    print("1. 只下載必要模型（推薦）")
    print("2. 下載所有模型")
    print("3. 自定義選擇")
    print("4. 顯示當前模型狀態")
    print("0. 退出")
    
    choice = input("\n請選擇 (1): ").strip() or "1"
    
    if choice == "0":
        return True
    elif choice == "4":
        show_model_status()
        return True
    
    # 決定要下載的模型
    to_download = []
    
    if choice == "1":
        # 只下載必要模型
        to_download = [k for k, v in config.items() if v["required"]]
    elif choice == "2":
        # 下載所有模型
        to_download = list(config.keys())
    elif choice == "3":
        # 自定義選擇
        print(f"\n自定義選擇:")
        for i, (model_id, info) in enumerate(config.items(), 1):
            answer = input(f"下載 {info['description']} ({info['size']})? (Y/n): ")
            if answer.lower() != 'n':
                to_download.append(model_id)
    
    # 開始下載
    success_count = 0
    for model_id in to_download:
        model_info = config[model_id]
        success = download_model(
            model_info["repo_id"],
            model_info["description"],
            model_info["download_method"]
        )
        if success:
            success_count += 1
    
    # 生成清單
    create_model_manifest()
    
    # 顯示結果
    print(f"\n" + "="*60)
    print(f"下載完成: {success_count}/{len(to_download)} 個模型")
    print("="*60)
    
    if success_count == len(to_download):
        print("[成功] 所有模型下載完成！")
        print("\n下一步:")
        print("1. 執行 check_embedded_environment.py 檢查環境")
        print("2. 執行 test_simplified_backend.bat 測試後端")
        return True
    else:
        print("[警告] 部分模型下載失敗")
        print("可以稍後重新執行此腳本")
        return False

if __name__ == "__main__":
    success = main()
    input("\n按 Enter 鍵退出...")
    sys.exit(0 if success else 1)