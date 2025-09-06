"""Runtime detection utilities for GPU/CPU and compute type selection."""

from __future__ import annotations
import shutil
import subprocess
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def gpu_available() -> bool:
    """
    Check if GPU is available for CUDA acceleration.
    
    Returns:
        bool: True if CUDA-capable GPU is available, False otherwise.
    """
    # Check nvidia-smi
    if shutil.which("nvidia-smi"):
        try:
            subprocess.run(
                ["nvidia-smi"], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL, 
                timeout=3,
                check=True
            )
            logger.info("CUDA GPU detected via nvidia-smi")
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
    
    # Optional: Check torch.cuda
    try:
        import torch
        if torch.cuda.is_available():
            logger.info(f"CUDA GPU detected via torch: {torch.cuda.get_device_name(0)}")
            return True
    except ImportError:
        pass
    
    logger.info("No CUDA GPU detected, will use CPU")
    return False


def pick_runtime() -> Dict[str, Any]:
    """
    Select optimal runtime configuration based on hardware.
    
    Returns:
        dict: Configuration with device, compute_type, and model_size.
    """
    if gpu_available():
        config = {
            "device": "cuda",
            "compute_type": "float16",
            "model_size": "large-v3-turbo"
        }
        logger.info(f"Selected GPU runtime: {config}")
    else:
        config = {
            "device": "cpu",
            "compute_type": "int8",
            "model_size": "large-v3-turbo"
        }
        logger.info(f"Selected CPU runtime: {config}")
    
    return config


def get_model_repo() -> str:
    """
    Get the HuggingFace repository ID for the model.
    
    Returns:
        str: HuggingFace repository ID.
    """
    return "zzxxcc0805/my-whisper-large-v3-turbo-ct2"