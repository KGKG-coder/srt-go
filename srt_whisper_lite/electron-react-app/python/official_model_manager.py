#!/usr/bin/env python3
"""
Official Whisper Large V3 Turbo CT2 Model Manager
根據決策要求配置：
- 主源：HF zzxxcc0805/my-whisper-large-v3-turbo-ct2
- 備源：GitHub Releases ZIP
- SHA256：A30872B8826A4F77B973CDDA325E182E520A4C965BC53DFEEAD33BBCE049F828
- 大小：1492336108 bytes
- GPU: cuda+float16 / CPU: cpu+int8
"""

import os
import sys
import logging
import requests
import shutil
import hashlib
import zipfile
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
from tqdm import tqdm
import time

logger = logging.getLogger(__name__)

class OfficialModelManager:
    """官方指定模型管理器 - 完全符合決策要求"""
    
    def __init__(self):
        # 官方指定模型配置
        self.model_name = "whisper-large-v3-turbo-ct2"
        self.model_repo = "zzxxcc0805/my-whisper-large-v3-turbo-ct2"
        
        # 官方指定備源配置
        self.backup_url = "https://github.com/zzxxcc0805/whisper-mirrors/releases/download/ct2-large-v3-turbo-2025-08-18-r1/whisper-large-v3-turbo-ct2.zip"
        self.expected_sha256 = "A30872B8826A4F77B973CDDA325E182E520A4C965BC53DFEEAD33BBCE049F828"
        self.expected_size = 1492336108  # 1,492,336,108 bytes
        
        # 路徑配置
        self.app_models_dir = Path(__file__).parent.parent / "models"
        self.model_dir = self.app_models_dir / self.model_name
        self.cache_dir = Path.home() / ".cache" / "whisper" / self.model_name
        self.temp_dir = self.app_models_dir / "temp"
        
        # 確保目錄存在
        self.app_models_dir.mkdir(parents=True, exist_ok=True)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Official Model Manager 初始化:")
        logger.info(f"  - 模型: {self.model_name}")
        logger.info(f"  - HF源: {self.model_repo}")
        logger.info(f"  - 備源: {self.backup_url}")
        logger.info(f"  - SHA256: {self.expected_sha256[:16]}...")
        logger.info(f"  - 大小: {self._format_size(self.expected_size)}")
        logger.info(f"  - 模型目錄: {self.model_dir}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """獲取模型信息"""
        available = self.check_model_availability()
        
        return {
            "name": self.model_name,
            "variant": "Large V3 Turbo CT2",
            "available": available,
            "status_text": "已安裝" if available else "需要下載",
            "expected_size": self._format_size(self.expected_size),
            "actual_size": self._format_size(self._get_model_size()) if available else "0 MB",
            "path": str(self.model_dir) if available else None,
            "sha256": self.expected_sha256[:16] + "...",
            "sources": ["HuggingFace Hub", "GitHub Mirror"],
            "device_strategy": "GPU: cuda+float16 / CPU: cpu+int8"
        }
    
    def check_model_availability(self) -> bool:
        """檢查模型是否可用"""
        # 檢查本地模型目錄
        if self._validate_model(self.model_dir):
            logger.info(f"✅ 找到本地模型: {self.model_dir}")
            return True
        
        # 檢查快取目錄
        if self._validate_model(self.cache_dir):
            logger.info(f"找到快取模型: {self.cache_dir}")
            # 複製到應用目錄
            if self._copy_model_files(self.cache_dir, self.model_dir):
                return True
        
        # 檢查 HuggingFace 快取
        hf_cache_patterns = [
            Path.home() / ".cache" / "huggingface" / "hub" / f"models--{self.model_repo.replace('/', '--')}",
            Path.home() / ".cache" / "huggingface" / "transformers" / "models" / self.model_repo
        ]
        
        for hf_cache_path in hf_cache_patterns:
            if hf_cache_path.exists():
                logger.info(f"找到 HuggingFace 快取: {hf_cache_path}")
                snapshots = hf_cache_path / "snapshots"
                if snapshots.exists():
                    for snapshot_dir in snapshots.iterdir():
                        if self._validate_model(snapshot_dir):
                            if self._copy_model_files(snapshot_dir, self.model_dir):
                                return True
        
        logger.info("未找到本地模型，需要下載")
        return False
    
    def _validate_model(self, model_path: Path) -> bool:
        """驗證模型文件是否完整"""
        if not model_path.exists():
            return False
        
        # 檢查必要文件
        essential_files = ["model.bin", "config.json"]
        for file_name in essential_files:
            file_path = model_path / file_name
            if not file_path.exists():
                return False
        
        return True
    
    def _copy_model_files(self, source: Path, target: Path) -> bool:
        """複製模型文件"""
        try:
            target.mkdir(parents=True, exist_ok=True)
            
            for source_file in source.iterdir():
                if source_file.is_file():
                    target_file = target / source_file.name
                    if not target_file.exists() or target_file.stat().st_size != source_file.stat().st_size:
                        logger.info(f"  複製: {source_file.name}")
                        shutil.copy2(source_file, target_file)
            
            return self._validate_model(target)
        except Exception as e:
            logger.error(f"❌ 複製模型文件失敗: {e}")
            return False
    
    def download_model(self, progress_callback: Optional[callable] = None) -> Tuple[bool, str]:
        """下載模型（主源→備源策略）"""
        try:
            # 嘗試 HuggingFace Hub
            logger.info("📥 嘗試從 HuggingFace Hub 下載...")
            if progress_callback:
                progress_callback(0.1, "checking", "檢查 HuggingFace Hub...")
            
            success, message = self._download_from_huggingface(progress_callback)
            if success:
                return True, message
            
            # 回退到 GitHub Mirror
            logger.info("📥 回退到 GitHub Mirror...")
            if progress_callback:
                progress_callback(0.1, "downloading", "切換到 GitHub Mirror...")
            
            success, message = self._download_from_github_mirror(progress_callback)
            if success:
                return True, message
            
            # 所有源都失敗
            error_msg = "所有下載源都失敗，請檢查網路連線或使用離線安裝包"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
            
        except Exception as e:
            logger.error(f"❌ 下載過程出錯: {e}")
            return False, str(e)
    
    def _download_from_huggingface(self, progress_callback: Optional[callable] = None) -> Tuple[bool, str]:
        """從 HuggingFace Hub 下載"""
        try:
            # 使用 faster-whisper 的標準下載方式
            from faster_whisper import WhisperModel
            
            if progress_callback:
                progress_callback(0.2, "downloading", "從 HuggingFace 下載模型...")
            
            # 創建模型實例，會自動下載
            model = WhisperModel(
                self.model_repo,
                device="cpu",  # 先用CPU載入檢查
                compute_type="int8",
                download_root=str(self.cache_dir.parent)
            )
            
            # 檢查下載是否成功
            if self.check_model_availability():
                if progress_callback:
                    progress_callback(1.0, "done", "HuggingFace 下載完成")
                return True, f"從 HuggingFace Hub 下載成功: {self.model_dir}"
            else:
                return False, "HuggingFace 下載失敗：模型驗證未通過"
                
        except Exception as e:
            logger.warning(f"HuggingFace 下載失敗: {e}")
            return False, f"HuggingFace 下載失敗: {e}"
    
    def _download_from_github_mirror(self, progress_callback: Optional[callable] = None) -> Tuple[bool, str]:
        """從 GitHub Mirror 下載ZIP文件"""
        try:
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            zip_file = self.temp_dir / "model.zip"
            
            if progress_callback:
                progress_callback(0.2, "downloading", "從 GitHub Mirror 下載...")
            
            # 下載ZIP文件
            success = self._download_file_with_resume(
                url=self.backup_url,
                target_path=zip_file,
                expected_size=self.expected_size,
                progress_callback=lambda p, s: progress_callback(
                    0.2 + p * 0.6, "downloading", f"下載中... {s}"
                ) if progress_callback else None
            )
            
            if not success:
                return False, "GitHub Mirror 下載失敗"
            
            # 驗證 SHA256
            if progress_callback:
                progress_callback(0.8, "verifying", "驗證文件完整性...")
            
            if not self._verify_sha256(zip_file):
                zip_file.unlink(missing_ok=True)
                return False, "SHA256 驗證失敗"
            
            # 解壓縮
            if progress_callback:
                progress_callback(0.9, "unpacking", "解壓縮模型...")
            
            if not self._extract_zip(zip_file):
                return False, "解壓縮失敗"
            
            # 清理
            zip_file.unlink(missing_ok=True)
            self.temp_dir.rmdir() if self.temp_dir.exists() else None
            
            if progress_callback:
                progress_callback(1.0, "done", "GitHub Mirror 下載完成")
            
            return True, f"從 GitHub Mirror 下載成功: {self.model_dir}"
            
        except Exception as e:
            logger.error(f"GitHub Mirror 下載失敗: {e}")
            return False, f"GitHub Mirror 下載失敗: {e}"
    
    def _download_file_with_resume(
        self,
        url: str,
        target_path: Path,
        expected_size: int,
        progress_callback: Optional[callable] = None,
        max_retries: int = 3
    ) -> bool:
        """下載文件（支援斷點續傳）"""
        for attempt in range(max_retries):
            try:
                # 檢查已下載部分
                resume_pos = 0
                if target_path.exists():
                    resume_pos = target_path.stat().st_size
                    if resume_pos == expected_size:
                        logger.info(f"文件已完整下載: {target_path}")
                        return True
                
                # 設置請求頭
                headers = {}
                if resume_pos > 0:
                    headers['Range'] = f'bytes={resume_pos}-'
                    logger.info(f"續傳下載，從 {self._format_size(resume_pos)} 開始")
                
                # 下載
                response = requests.get(url, headers=headers, stream=True, timeout=30)
                response.raise_for_status()
                
                # 獲取內容長度
                content_length = response.headers.get('content-length')
                total_size = int(content_length) + resume_pos if content_length else expected_size
                
                # 寫入文件
                mode = 'ab' if resume_pos > 0 else 'wb'
                chunk_size = 8192 * 8  # 64KB chunks
                
                with open(target_path, mode) as f:
                    downloaded = resume_pos
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if progress_callback:
                                progress = downloaded / total_size
                                progress_callback(progress, f"已下載: {self._format_size(downloaded)} / {self._format_size(total_size)}")
                
                # 驗證大小
                final_size = target_path.stat().st_size
                if abs(final_size - expected_size) > 1024:  # 允許1KB誤差
                    logger.warning(f"文件大小不符: {final_size} vs {expected_size}")
                
                return True
                
            except Exception as e:
                logger.error(f"下載錯誤 (嘗試 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return False
        
        return False
    
    def _verify_sha256(self, file_path: Path) -> bool:
        """驗證 SHA256"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            calculated = sha256_hash.hexdigest().upper()
            expected = self.expected_sha256.upper()
            
            if calculated == expected:
                logger.info("✅ SHA256 驗證通過")
                return True
            else:
                logger.error(f"❌ SHA256 不符: {calculated} != {expected}")
                return False
                
        except Exception as e:
            logger.error(f"SHA256 驗證失敗: {e}")
            return False
    
    def _extract_zip(self, zip_file: Path) -> bool:
        """解壓縮ZIP文件"""
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(self.model_dir)
            
            logger.info(f"✅ 解壓縮完成: {self.model_dir}")
            return self._validate_model(self.model_dir)
            
        except Exception as e:
            logger.error(f"解壓縮失敗: {e}")
            return False
    
    def get_device_strategy(self) -> Dict[str, Any]:
        """獲取設備策略配置"""
        try:
            import torch
            has_cuda = torch.cuda.is_available()
        except:
            try:
                import subprocess
                result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
                has_cuda = result.returncode == 0
            except:
                has_cuda = False
        
        if has_cuda:
            return {
                "device": "cuda",
                "compute_type": "float16",
                "strategy": "GPU加速",
                "description": "使用CUDA GPU + Float16精度"
            }
        else:
            return {
                "device": "cpu", 
                "compute_type": "int8",
                "strategy": "CPU優化",
                "description": "使用CPU + INT8量化"
            }
    
    def get_whisper_model_params(self) -> Dict[str, Any]:
        """獲取 faster-whisper 的配置參數"""
        device_config = self.get_device_strategy()
        
        return {
            "model_size_or_path": str(self.model_dir) if self.check_model_availability() else self.model_repo,
            "device": device_config["device"],
            "compute_type": device_config["compute_type"],
            "num_workers": 1,
            "download_root": str(self.cache_dir.parent),
            "local_files_only": False
        }
    
    def ensure_model_ready(self) -> Tuple[bool, str]:
        """確保模型準備就緒"""
        logger.info("🔄 準備官方指定模型...")
        
        if self.check_model_availability():
            size = self._format_size(self._get_model_size())
            device_config = self.get_device_strategy()
            logger.info(f"✅ 模型已就緒: {self.model_dir}")
            logger.info(f"   大小: {size}")
            logger.info(f"   策略: {device_config['strategy']}")
            return True, str(self.model_dir)
        else:
            logger.info("📥 需要下載模型...")
            return self.download_model()
    
    def _get_model_size(self) -> int:
        """獲取模型總大小（字節）"""
        try:
            if self.model_dir.exists():
                total_size = 0
                for file_path in self.model_dir.rglob('*'):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                return total_size
        except Exception as e:
            logger.debug(f"無法獲取模型大小: {e}")
        
        return 0
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"