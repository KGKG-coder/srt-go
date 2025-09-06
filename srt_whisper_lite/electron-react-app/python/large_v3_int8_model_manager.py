#!/usr/bin/env python3
"""
Whisper Large V3 Turbo INT8 Model Manager
使用 INT8 量化版本，大小約 1GB，最適合 NSIS 打包
速度比 FP16 快 3.5 倍，精度損失極小
"""

import os
import logging
import requests
import shutil
import hashlib
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
from tqdm import tqdm
import time

logger = logging.getLogger(__name__)

class LargeV3INT8ModelManager:
    """Large V3 Turbo INT8 模型管理器 - 最優化打包版本"""
    
    def __init__(self):
        # 使用 Large V3 Turbo INT8 版本
        self.model_name = "large-v3-turbo"
        self.model_variant = "int8"
        self.model_full_name = f"{self.model_name}-{self.model_variant}"
        
        # Hugging Face 下載 URL - Zoont 的 INT8 版本
        self.model_repo = "Zoont/faster-whisper-large-v3-turbo-int8-ct2"
        self.base_url = f"https://huggingface.co/{self.model_repo}/resolve/main"
        
        # 必要文件列表及其預期大小（估計值）
        self.required_files = {
            "model.bin": {
                "url": f"{self.base_url}/model.bin",
                "min_size": 500_000_000,  # 至少 500MB
                "max_size": 1_500_000_000  # 最多 1.5GB
            },
            "config.json": {
                "url": f"{self.base_url}/config.json",
                "min_size": 100,
                "max_size": 10_000
            },
            "tokenizer.json": {
                "url": f"{self.base_url}/tokenizer.json",
                "min_size": 1000,
                "max_size": 10_000_000
            },
            "vocabulary.txt": {
                "url": f"{self.base_url}/vocabulary.txt",
                "min_size": 1000,
                "max_size": 1_000_000
            },
            "preprocessor_config.json": {
                "url": f"{self.base_url}/preprocessor_config.json",
                "min_size": 100,
                "max_size": 10_000
            }
        }
        
        # 備用下載源（如果主源失敗）
        self.backup_repos = [
            "mukowaty/faster-whisper-int8",  # 通用 INT8 版本
            "Systran/faster-whisper-large-v3"  # 標準版（較大）
        ]
        
        # 路徑設定
        self.app_models_dir = Path(__file__).parent.parent / "models"
        self.model_dir = self.app_models_dir / self.model_full_name
        self.cache_dir = Path.home() / ".cache" / "whisper" / self.model_full_name
        self.temp_dir = self.app_models_dir / "temp"
        
        # 確保目錄存在
        self.app_models_dir.mkdir(parents=True, exist_ok=True)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Large V3 Turbo INT8 Model Manager 初始化:")
        logger.info(f"  - 模型: {self.model_full_name}")
        logger.info(f"  - 模型目錄: {self.model_dir}")
        logger.info(f"  - 快取目錄: {self.cache_dir}")
        logger.info(f"  - 來源: {self.model_repo}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """獲取模型信息"""
        available = self.check_model_availability()
        
        return {
            "name": self.model_full_name,
            "variant": "INT8 量化版（超快速）",
            "available": available,
            "status_text": "已安裝" if available else "需要下載",
            "estimated_size": "~1 GB",
            "actual_size": self._format_size(self._get_model_size()) if available else "0 MB",
            "path": str(self.model_dir) if available else None,
            "performance": "速度最快（比 FP16 快 3.5 倍）",
            "accuracy": "精度優秀（與 FP16 相差 < 1%）"
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
            Path.home() / ".cache" / "huggingface" / "hub" / "models--Zoont--faster-whisper-large-v3-turbo-int8-ct2"
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
            
            # 檢查文件大小
            if file_name == "model.bin":
                size_bytes = file_path.stat().st_size
                expected = self.required_files.get("model.bin", {})
                min_size = expected.get("min_size", 500_000_000)
                max_size = expected.get("max_size", 1_500_000_000)
                
                if size_bytes < min_size or size_bytes > max_size:
                    size_gb = size_bytes / (1024**3)
                    logger.warning(f"模型大小可能異常: {size_gb:.2f}GB (預期: 0.5-1.5GB)")
                    # INT8 模型應該在 0.5-1.5GB 之間
        
        return True
    
    def _copy_model_files(self, source: Path, target: Path) -> bool:
        """複製模型文件"""
        try:
            target.mkdir(parents=True, exist_ok=True)
            
            copied_count = 0
            for file_name in self.required_files.keys():
                source_file = source / file_name
                if source_file.exists():
                    target_file = target / file_name
                    if not target_file.exists() or target_file.stat().st_size != source_file.stat().st_size:
                        logger.info(f"  複製: {file_name}")
                        shutil.copy2(source_file, target_file)
                        copied_count += 1
            
            if copied_count > 0:
                logger.info(f"✅ 複製了 {copied_count} 個文件")
            
            return self._validate_model(target)
        except Exception as e:
            logger.error(f"❌ 複製模型文件失敗: {e}")
            return False
    
    def download_model(self, progress_callback: Optional[callable] = None) -> Tuple[bool, str]:
        """下載 Large V3 Turbo INT8 模型（支援斷點續傳）"""
        try:
            self.model_dir.mkdir(parents=True, exist_ok=True)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            
            total_files = len(self.required_files)
            completed_files = 0
            
            for file_name, file_info in self.required_files.items():
                target_file = self.model_dir / file_name
                temp_file = self.temp_dir / f"{file_name}.download"
                
                # 檢查文件是否已存在且有效
                if target_file.exists():
                    file_size = target_file.stat().st_size
                    if file_info["min_size"] <= file_size <= file_info["max_size"]:
                        logger.info(f"  ✓ 已存在: {file_name} ({self._format_size(file_size)})")
                        completed_files += 1
                        if progress_callback:
                            progress_callback(completed_files / total_files, f"已存在 {file_name}")
                        continue
                
                # 下載文件（支援斷點續傳）
                success = self._download_file_with_resume(
                    url=file_info["url"],
                    target_path=target_file,
                    temp_path=temp_file,
                    expected_size_range=(file_info["min_size"], file_info["max_size"]),
                    progress_callback=lambda p, m: progress_callback(
                        (completed_files + p) / total_files, m
                    ) if progress_callback else None
                )
                
                if not success:
                    logger.error(f"❌ 下載失敗: {file_name}")
                    return False, f"無法下載 {file_name}"
                
                completed_files += 1
                logger.info(f"  ✅ 完成: {file_name}")
            
            # 清理臨時目錄
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            
            # 驗證所有文件
            if self._validate_model(self.model_dir):
                total_size = self._get_model_size()
                logger.info(f"✅ Large V3 Turbo INT8 模型下載成功")
                logger.info(f"   總大小: {self._format_size(total_size)}")
                return True, str(self.model_dir)
            else:
                logger.error("❌ 模型驗證失敗")
                return False, "模型文件不完整"
                
        except Exception as e:
            logger.error(f"❌ 下載過程出錯: {e}")
            return False, str(e)
    
    def _download_file_with_resume(
        self,
        url: str,
        target_path: Path,
        temp_path: Path,
        expected_size_range: Tuple[int, int],
        progress_callback: Optional[callable] = None,
        max_retries: int = 3
    ) -> bool:
        """下載文件（支援斷點續傳和重試）"""
        file_name = target_path.name
        
        for attempt in range(max_retries):
            try:
                # 檢查臨時文件
                resume_pos = 0
                if temp_path.exists():
                    resume_pos = temp_path.stat().st_size
                    logger.info(f"  續傳: {file_name} (從 {self._format_size(resume_pos)} 開始)")
                else:
                    logger.info(f"  下載: {file_name}")
                
                # 設置請求頭
                headers = {}
                if resume_pos > 0:
                    headers['Range'] = f'bytes={resume_pos}-'
                
                # 發送請求
                response = requests.get(url, headers=headers, stream=True, timeout=30)
                
                # 檢查是否支援斷點續傳
                if resume_pos > 0 and response.status_code != 206:
                    logger.warning("伺服器不支援斷點續傳，重新下載")
                    resume_pos = 0
                    temp_path.unlink(missing_ok=True)
                    response = requests.get(url, stream=True, timeout=30)
                
                response.raise_for_status()
                
                # 獲取文件總大小
                content_length = response.headers.get('content-length')
                if content_length:
                    total_size = int(content_length) + resume_pos
                else:
                    total_size = None
                
                # 下載文件
                chunk_size = 8192 * 4  # 32KB chunks
                mode = 'ab' if resume_pos > 0 else 'wb'
                
                with open(temp_path, mode) as f:
                    if total_size:
                        with tqdm(
                            total=total_size,
                            initial=resume_pos,
                            unit='B',
                            unit_scale=True,
                            desc=file_name
                        ) as pbar:
                            for chunk in response.iter_content(chunk_size=chunk_size):
                                if chunk:
                                    f.write(chunk)
                                    pbar.update(len(chunk))
                                    
                                    if progress_callback:
                                        progress = pbar.n / total_size
                                        progress_callback(progress, f"下載 {file_name}...")
                    else:
                        # 沒有內容長度，無法顯示進度
                        downloaded = resume_pos
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                
                                if progress_callback and downloaded % (1024 * 1024) == 0:  # 每 MB 更新一次
                                    progress_callback(0.5, f"下載 {file_name}... {self._format_size(downloaded)}")
                
                # 驗證文件大小
                final_size = temp_path.stat().st_size
                min_size, max_size = expected_size_range
                
                if final_size < min_size:
                    logger.error(f"文件太小: {self._format_size(final_size)} < {self._format_size(min_size)}")
                    temp_path.unlink(missing_ok=True)
                    if attempt < max_retries - 1:
                        logger.info(f"重試 {attempt + 2}/{max_retries}...")
                        time.sleep(2 ** attempt)  # 指數退避
                        continue
                    return False
                
                if final_size > max_size:
                    logger.warning(f"文件較大: {self._format_size(final_size)} > {self._format_size(max_size)}")
                
                # 移動到目標位置
                shutil.move(str(temp_path), str(target_path))
                logger.info(f"  ✓ 保存: {file_name} ({self._format_size(final_size)})")
                return True
                
            except requests.exceptions.RequestException as e:
                logger.error(f"下載錯誤 (嘗試 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指數退避
                    continue
                return False
            
            except Exception as e:
                logger.error(f"意外錯誤: {e}")
                return False
        
        return False
    
    def get_model_path(self) -> Tuple[bool, str]:
        """獲取模型路徑"""
        if self.check_model_availability():
            logger.info(f"使用 Large V3 Turbo INT8 模型: {self.model_dir}")
            return True, str(self.model_dir)
        else:
            logger.warning("模型不可用，需要先下載")
            return False, ""
    
    def _get_model_size(self) -> int:
        """獲取模型總大小（字節）"""
        try:
            if self.model_dir.exists():
                total_size = 0
                for file_path in self.model_dir.glob('*'):
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
    
    def prepare_model(self) -> Tuple[bool, str]:
        """準備模型（確保可用）"""
        logger.info("🔄 準備 Large V3 Turbo INT8 模型...")
        
        if self.check_model_availability():
            size = self._format_size(self._get_model_size())
            logger.info(f"✅ 模型已就緒: {self.model_dir}")
            logger.info(f"   大小: {size}")
            logger.info(f"   類型: INT8 量化（超快速）")
            return True, str(self.model_dir)
        else:
            logger.info("📥 需要下載模型...")
            return self.download_model()
    
    def ensure_model_ready(self) -> Tuple[bool, str]:
        """確保模型已準備好，如果需要則下載"""
        # 檢查模型是否已經可用
        if self.check_model_availability():
            success, model_path = self.get_model_path()
            return success, model_path
        
        # 嘗試下載模型
        logger.info("模型不可用，嘗試下載...")
        success, message = self.download_model()
        
        if success:
            return self.get_model_path()
        else:
            # 下載失敗，返回標準模型名稱作為備用
            logger.warning(f"INT8 模型下載失敗: {message}")
            return True, "large-v3"  # 備用到標準模型

    def get_faster_whisper_config(self) -> Dict[str, Any]:
        """獲取 faster-whisper 的配置參數"""
        return {
            "model_size_or_path": str(self.model_dir) if self.check_model_availability() else self.model_repo,
            "device": "cpu",  # INT8 在 CPU 上效果最佳
            "compute_type": "int8",  # 使用 INT8 計算
            "num_workers": 1,
            "download_root": str(self.cache_dir),
            "local_files_only": False,
            # Large V3 專用配置
            "feature_size": 128,  # Large V3 需要128個mel頻譜帶
            "n_mels": 128  # 設置mel頻譜帶數量
        }
    
    def cleanup_cache(self):
        """清理快取和臨時文件"""
        try:
            # 清理臨時目錄
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                logger.info("✅ 清理臨時文件")
            
            # 可選：清理快取目錄
            # if self.cache_dir.exists():
            #     shutil.rmtree(self.cache_dir, ignore_errors=True)
            #     logger.info("✅ 清理快取目錄")
            
        except Exception as e:
            logger.error(f"清理失敗: {e}")