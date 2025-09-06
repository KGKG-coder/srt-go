"""Model loading and management with automatic download."""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, Callable

from faster_whisper import WhisperModel

from engine.utils.runtime import pick_runtime, get_model_repo
from engine.utils.download import ModelDownloader

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages Whisper model loading with automatic download and runtime selection."""
    
    def __init__(self, models_dir: Optional[Path] = None, progress_callback: Optional[Callable] = None):
        """
        Initialize model manager.
        
        Args:
            models_dir: Directory for storing models. Defaults to user app data.
            progress_callback: Callback for download progress (percent, stage, message).
        """
        if models_dir is None:
            # Use %LOCALAPPDATA%/SRTWhisperTurbo/models on Windows
            import os
            app_data = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
            models_dir = app_data / 'SRTWhisperTurbo' / 'models'
        
        self.models_dir = models_dir
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.downloader = ModelDownloader(self.models_dir, progress_callback)
        self.model = None
        self.runtime_config = None
        
    def load_model(self, model_dir_override: Optional[str] = None, 
                  force_download: bool = False) -> WhisperModel:
        """
        Load Whisper model with automatic download if needed.
        
        Args:
            model_dir_override: Optional path to override default model location.
            force_download: Force re-download even if model exists.
            
        Returns:
            WhisperModel: Loaded Whisper model.
        """
        # Get runtime configuration
        self.runtime_config = pick_runtime()
        
        # Determine model path
        if model_dir_override:
            model_path = Path(model_dir_override)
            if not model_path.exists():
                raise RuntimeError(f"Model directory not found: {model_path}")
        else:
            # Use standard model name
            model_name = "whisper-large-v3-turbo-ct2"
            model_path = self.models_dir / model_name
            
            # Download if needed
            if force_download or not model_path.exists():
                repo_id = get_model_repo()
                model_path = self.downloader.download_model(repo_id, model_name)
        
        # Load model with runtime configuration
        logger.info(f"Loading model from {model_path} with config: {self.runtime_config}")
        
        self.model = WhisperModel(
            str(model_path),
            device=self.runtime_config["device"],
            compute_type=self.runtime_config["compute_type"],
            download_root=None  # Don't use default download
        )
        
        logger.info("Model loaded successfully")
        return self.model
    
    def transcribe(self, audio_path: str, language: Optional[str] = None,
                  initial_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Transcribe audio file.
        
        Args:
            audio_path: Path to audio file.
            language: Language code (zh, en, ja, ko) or None for auto-detect.
            initial_prompt: Optional initial prompt for better context.
            **kwargs: Additional arguments for transcribe.
            
        Returns:
            dict: Transcription results with segments and info.
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Map our language codes to Whisper language codes
        lang_map = {
            "zh": "zh",  # Chinese
            "en": "en",  # English
            "ja": "ja",  # Japanese
            "ko": "ko",  # Korean
        }
        
        whisper_lang = lang_map.get(language) if language else None
        
        # Transcribe
        segments, info = self.model.transcribe(
            audio_path,
            language=whisper_lang,
            initial_prompt=initial_prompt,
            word_timestamps=True,  # Enable for better timestamp alignment
            vad_filter=True,  # Basic VAD filtering
            vad_parameters=dict(
                threshold=0.35,
                min_speech_duration_ms=250,
                min_silence_duration_ms=100
            ),
            **kwargs
        )
        
        # Convert generator to list and extract info
        segment_list = []
        for segment in segments:
            segment_list.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "words": [
                    {"start": w.start, "end": w.end, "word": w.word, "probability": w.probability}
                    for w in (segment.words or [])
                ] if hasattr(segment, 'words') else []
            })
        
        return {
            "segments": segment_list,
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "all_language_probs": info.all_language_probs if hasattr(info, 'all_language_probs') else None
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about loaded model and runtime.
        
        Returns:
            dict: Model and runtime information.
        """
        return {
            "loaded": self.model is not None,
            "runtime_config": self.runtime_config,
            "models_dir": str(self.models_dir),
            "repo_id": get_model_repo()
        }