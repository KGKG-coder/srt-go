"""Model download manager with HuggingFace primary and GitHub mirror fallback."""

import hashlib
import json
import logging
import shutil
import time
import zipfile
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from urllib.parse import urlparse

import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1024 * 1024  # 1MB chunks
GITHUB_MIRROR_URL = "https://github.com/zzxxcc0805/whisper-mirrors/releases/download/ct2-large-v3-turbo-2025-08-18-r1/whisper-large-v3-turbo-ct2.zip"
GITHUB_MIRROR_SHA256 = "A30872B8826A4F77B973CDDA325E182E520A4C965BC53DFEEAD33BBCE049F828"
GITHUB_MIRROR_SIZE = 1492336108


class ModelDownloader:
    """Handles model downloading with multiple mirrors and verification."""
    
    def __init__(self, model_dir: Path, progress_callback: Optional[Callable] = None):
        """
        Initialize model downloader.
        
        Args:
            model_dir: Directory to store models.
            progress_callback: Callback for progress updates (percent, stage, message).
        """
        self.model_dir = model_dir
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.progress_callback = progress_callback or (lambda *args: None)
        
    def sha256_file(self, path: Path) -> str:
        """
        Calculate SHA256 hash of a file.
        
        Args:
            path: Path to file.
            
        Returns:
            str: Hex string of SHA256 hash.
        """
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
                h.update(chunk)
        return h.hexdigest().upper()
    
    def download_with_resume(self, url: str, dest: Path, expected_size: Optional[int] = None,
                            expected_sha256: Optional[str] = None) -> bool:
        """
        Download file with resume support and verification.
        
        Args:
            url: URL to download from.
            dest: Destination file path.
            expected_size: Expected file size in bytes.
            expected_sha256: Expected SHA256 hash.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        tmp = dest.with_suffix(dest.suffix + ".part")
        
        try:
            # Check existing partial download
            pos = tmp.stat().st_size if tmp.exists() else 0
            headers = {"Range": f"bytes={pos}-"} if pos > 0 else {}
            
            logger.info(f"Downloading from {url} (resume from {pos} bytes)")
            
            with requests.get(url, stream=True, timeout=30, headers=headers) as r:
                r.raise_for_status()
                
                # Get total size
                total_size = int(r.headers.get('content-length', 0))
                if expected_size and pos == 0:
                    total_size = expected_size
                
                # Setup progress bar
                with tqdm(total=total_size, initial=pos, unit='B', unit_scale=True) as pbar:
                    mode = "ab" if pos > 0 else "wb"
                    with tmp.open(mode) as f:
                        for chunk in r.iter_content(CHUNK_SIZE):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                                
                                # Update callback
                                percent = int((pbar.n / total_size) * 100) if total_size else 0
                                self.progress_callback(percent, "downloading", f"Downloading model... {percent}%")
            
            # Verify size
            if expected_size and tmp.stat().st_size != expected_size:
                logger.error(f"Size mismatch: {tmp.stat().st_size} != {expected_size}")
                return False
            
            # Verify SHA256
            if expected_sha256:
                self.progress_callback(0, "verifying", "Verifying model integrity...")
                actual_sha = self.sha256_file(tmp)
                if actual_sha != expected_sha256.upper():
                    logger.error(f"SHA256 mismatch: {actual_sha} != {expected_sha256}")
                    return False
            
            # Atomic replace
            tmp.replace(dest)
            logger.info(f"Successfully downloaded to {dest}")
            return True
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def download_from_huggingface(self, repo_id: str, model_name: str) -> Optional[Path]:
        """
        Download model from HuggingFace Hub.
        
        Args:
            repo_id: HuggingFace repository ID.
            model_name: Model directory name.
            
        Returns:
            Optional[Path]: Path to model directory if successful.
        """
        model_path = self.model_dir / model_name
        
        # Check if already exists
        if model_path.exists() and self._verify_model_files(model_path):
            logger.info(f"Model already exists at {model_path}")
            return model_path
        
        try:
            # Try using huggingface_hub if available
            from huggingface_hub import snapshot_download
            
            self.progress_callback(0, "downloading", "Downloading from HuggingFace...")
            
            snapshot_download(
                repo_id=repo_id,
                local_dir=model_path,
                local_dir_use_symlinks=False,
                resume_download=True
            )
            
            if self._verify_model_files(model_path):
                logger.info(f"Successfully downloaded from HuggingFace to {model_path}")
                return model_path
                
        except ImportError:
            logger.warning("huggingface_hub not available, trying direct download")
        except Exception as e:
            logger.error(f"HuggingFace download failed: {e}")
        
        return None
    
    def download_from_github_mirror(self, model_name: str) -> Optional[Path]:
        """
        Download model from GitHub mirror as ZIP.
        
        Args:
            model_name: Model directory name.
            
        Returns:
            Optional[Path]: Path to model directory if successful.
        """
        model_path = self.model_dir / model_name
        zip_path = self.model_dir / f"{model_name}.zip"
        
        # Check if already exists
        if model_path.exists() and self._verify_model_files(model_path):
            logger.info(f"Model already exists at {model_path}")
            return model_path
        
        logger.info("Trying GitHub mirror...")
        self.progress_callback(0, "downloading", "Downloading from GitHub mirror...")
        
        # Download ZIP
        if self.download_with_resume(
            GITHUB_MIRROR_URL,
            zip_path,
            GITHUB_MIRROR_SIZE,
            GITHUB_MIRROR_SHA256
        ):
            # Extract ZIP
            self.progress_callback(0, "unpacking", "Extracting model files...")
            try:
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    zf.extractall(model_path)
                
                # Verify extracted files
                if self._verify_model_files(model_path):
                    logger.info(f"Successfully extracted to {model_path}")
                    # Clean up ZIP
                    zip_path.unlink()
                    return model_path
                    
            except Exception as e:
                logger.error(f"Extraction failed: {e}")
                if model_path.exists():
                    shutil.rmtree(model_path)
        
        return None
    
    def download_model(self, repo_id: str = "zzxxcc0805/my-whisper-large-v3-turbo-ct2",
                      model_name: str = "whisper-large-v3-turbo-ct2") -> Path:
        """
        Download model with fallback strategy.
        
        Args:
            repo_id: HuggingFace repository ID.
            model_name: Model directory name.
            
        Returns:
            Path: Path to model directory.
            
        Raises:
            RuntimeError: If all download methods fail.
        """
        self.progress_callback(0, "checking", "Checking for existing model...")
        
        # Try HuggingFace first
        model_path = self.download_from_huggingface(repo_id, model_name)
        
        # Fallback to GitHub mirror
        if not model_path:
            model_path = self.download_from_github_mirror(model_name)
        
        if model_path:
            self.progress_callback(100, "completed", "Model ready!")
            return model_path
        
        raise RuntimeError("Failed to download model from all sources. "
                         "Please check your internet connection or use offline model pack.")
    
    def _verify_model_files(self, model_path: Path) -> bool:
        """
        Verify that essential model files exist.
        
        Args:
            model_path: Path to model directory.
            
        Returns:
            bool: True if all essential files exist.
        """
        required_files = ["model.bin", "config.json", "tokenizer.json"]
        for file_name in required_files:
            if not (model_path / file_name).exists():
                logger.warning(f"Missing required file: {file_name}")
                return False
        return True
    
    def import_offline_pack(self, pack_path: Path, model_name: str = "whisper-large-v3-turbo-ct2") -> Path:
        """
        Import model from offline pack (ZIP or tar.zst).
        
        Args:
            pack_path: Path to offline pack file.
            model_name: Model directory name.
            
        Returns:
            Path: Path to imported model directory.
            
        Raises:
            RuntimeError: If import fails.
        """
        model_path = self.model_dir / model_name
        
        self.progress_callback(0, "unpacking", "Importing offline model pack...")
        
        try:
            if pack_path.suffix == ".zip":
                with zipfile.ZipFile(pack_path, 'r') as zf:
                    zf.extractall(model_path)
            else:
                raise RuntimeError(f"Unsupported pack format: {pack_path.suffix}")
            
            if self._verify_model_files(model_path):
                self.progress_callback(100, "completed", "Model imported successfully!")
                return model_path
            
        except Exception as e:
            if model_path.exists():
                shutil.rmtree(model_path)
            raise RuntimeError(f"Failed to import offline pack: {e}")
        
        raise RuntimeError("Imported model files are incomplete")