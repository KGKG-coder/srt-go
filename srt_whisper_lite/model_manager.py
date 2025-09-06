#!/usr/bin/env python3
"""
模型管理器 - 處理預置模型的安裝和管理
"""

import os
import sys
import json
import shutil
import zipfile
import logging
from pathlib import Path
import urllib.request

logger = logging.getLogger(__name__)

class ModelManager:
    """模型管理器"""
    
    def __init__(self):
        # 模型存放目錄
        self.models_dir = Path(__file__).parent / "models"
        self.cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        
        # 支援的模型資訊
        self.model_info = {
            "tiny": {
                "size_mb": 39,
                "description": "最小模型，快速但精度較低",
                "package_name": "whisper-tiny-model.zip"
            },
            "base": {
                "size_mb": 74, 
                "description": "基礎模型，速度與精度平衡",
                "package_name": "whisper-base-model.zip"
            },
            "medium": {
                "size_mb": 244,
                "description": "中等模型，推薦日常使用",
                "package_name": "whisper-medium-model.zip"
            },
            "large": {
                "size_mb": 769,
                "description": "大型模型，最高精度",
                "package_name": "whisper-large-model.zip"
            }
        }
        
    def check_local_model(self, model_name):
        """檢查本地模型是否存在"""
        # 檢查應用程式內建模型
        bundled_model = self.models_dir / f"{model_name}"
        if bundled_model.exists():
            return True, "bundled", str(bundled_model)
            
        # 檢查 HuggingFace 緩存
        if self.cache_dir.exists():
            for item in self.cache_dir.iterdir():
                if f"whisper-{model_name}" in item.name.lower():
                    return True, "cached", str(item)
                    
        return False, "not_found", None
        
    def install_bundled_model(self, model_name, progress_callback=None):
        """安裝內建的預置模型"""
        try:
            if progress_callback:
                progress_callback(0, f"準備安裝 {model_name} 模型...")
                
            # 檢查預置模型包
            model_package = self.models_dir / self.model_info[model_name]["package_name"]
            if not model_package.exists():
                logger.warning(f"預置模型包不存在: {model_package}")
                return False, "package_not_found"
                
            # 創建目標目錄
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            target_dir = self.cache_dir / f"models--openai--whisper-{model_name}"
            
            if progress_callback:
                progress_callback(20, "正在解壓模型文件...")
                
            # 解壓模型包
            with zipfile.ZipFile(model_package, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
                
            if progress_callback:
                progress_callback(80, "正在驗證模型完整性...")
                
            # 驗證模型文件
            required_files = ["config.json", "model.bin", "tokenizer.json"]
            for file_name in required_files:
                if not (target_dir / file_name).exists():
                    logger.error(f"模型文件缺失: {file_name}")
                    return False, "incomplete_model"
                    
            if progress_callback:
                progress_callback(100, f"{model_name} 模型安裝完成")
                
            logger.info(f"預置模型安裝成功: {model_name}")
            return True, str(target_dir)
            
        except Exception as e:
            logger.error(f"預置模型安裝失敗: {e}")
            return False, str(e)
            
    def download_model_if_needed(self, model_name, force_download=False, progress_callback=None):
        """智能模型獲取：優先使用預置，其次下載"""
        try:
            # 檢查本地模型
            exists, source, path = self.check_local_model(model_name)
            
            if exists and not force_download:
                logger.info(f"發現本地模型: {model_name} ({source})")
                if progress_callback:
                    progress_callback(100, f"使用本地 {model_name} 模型")
                return True, path, source
                
            # 如果有預置模型包，優先安裝
            model_package = self.models_dir / self.model_info[model_name]["package_name"]
            if model_package.exists():
                logger.info(f"發現預置模型包，開始安裝: {model_name}")
                if progress_callback:
                    progress_callback(10, "發現預置模型包，開始安裝...")
                    
                success, result = self.install_bundled_model(model_name, progress_callback)
                if success:
                    return True, result, "bundled_installed"
                else:
                    logger.warning(f"預置模型安裝失敗，嘗試網路下載: {result}")
                    
            # 嘗試網路下載
            if self._check_internet_connection():
                if progress_callback:
                    progress_callback(5, "正在從網路下載模型...")
                    
                return self._download_from_huggingface(model_name, progress_callback)
            else:
                logger.error("無網路連接且無可用的預置模型")
                return False, "no_network_no_bundled", "network_error"
                
        except Exception as e:
            logger.error(f"模型獲取失敗: {e}")
            return False, str(e), "error"
            
    def _check_internet_connection(self):
        """檢查網路連接"""
        try:
            urllib.request.urlopen('https://huggingface.co', timeout=10)
            return True
        except:
            return False
            
    def _download_from_huggingface(self, model_name, progress_callback=None):
        """從 HuggingFace 下載模型"""
        try:
            # 這裡會觸發 faster-whisper 的自動下載機制
            # 實際下載由 faster-whisper 處理
            if progress_callback:
                progress_callback(50, f"正在下載 {model_name} 模型...")
                
            # 返回給 faster-whisper 處理
            return True, "download_in_progress", "huggingface"
            
        except Exception as e:
            return False, str(e), "download_error"
            
    def get_model_status(self):
        """獲取所有模型的狀態"""
        status = {}
        
        for model_name in self.model_info.keys():
            exists, source, path = self.check_local_model(model_name)
            package_exists = (self.models_dir / self.model_info[model_name]["package_name"]).exists()
            
            status[model_name] = {
                "available_locally": exists,
                "source": source if exists else "not_available", 
                "path": path,
                "bundled_package_available": package_exists,
                "size_mb": self.model_info[model_name]["size_mb"],
                "description": self.model_info[model_name]["description"]
            }
            
        return status
        
    def create_model_package(self, model_name, output_dir=None):
        """創建模型安裝包（開發用）"""
        try:
            if not output_dir:
                output_dir = self.models_dir
                
            # 查找模型在 HuggingFace 緩存中的位置
            exists, source, model_path = self.check_local_model(model_name)
            
            if not exists or source != "cached":
                logger.error(f"模型 {model_name} 不在 HuggingFace 緩存中")
                return False
                
            # 創建壓縮包
            package_name = self.model_info[model_name]["package_name"]
            package_path = Path(output_dir) / package_name
            
            logger.info(f"創建模型包: {package_path}")
            
            with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                model_dir = Path(model_path)
                for file_path in model_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(model_dir)
                        zip_ref.write(file_path, arcname)
                        
            logger.info(f"模型包創建完成: {package_path}")
            return True
            
        except Exception as e:
            logger.error(f"創建模型包失敗: {e}")
            return False


def test_model_manager():
    """測試模型管理器"""
    manager = ModelManager()
    
    print("=== 模型狀態檢查 ===")
    status = manager.get_model_status()
    for model, info in status.items():
        print(f"{model}: 本地={info['available_locally']}, 預置包={info['bundled_package_available']}")
        
    print("\n=== 測試模型獲取 ===")
    def progress_callback(percent, message):
        print(f"[{percent:3d}%] {message}")
        
    success, path, source = manager.download_model_if_needed("base", progress_callback=progress_callback)
    print(f"結果: success={success}, path={path}, source={source}")


if __name__ == "__main__":
    test_model_manager()
