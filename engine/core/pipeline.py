"""5-layer audio filtering pipeline with configurable stages."""

import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import soundfile as sf
import librosa
import webrtcvad
from scipy import signal

logger = logging.getLogger(__name__)


@dataclass
class StageResult:
    """Result from a pipeline stage."""
    path: Path
    meta: Dict[str, Any]
    duration: float
    sample_rate: int


class FilterPipeline:
    """5-layer audio filtering pipeline."""
    
    def __init__(self, config: Dict[str, Any], artifacts_dir: Optional[Path] = None):
        """
        Initialize filter pipeline.
        
        Args:
            config: Pipeline configuration with enable flags for each stage.
            artifacts_dir: Directory to save intermediate artifacts.
        """
        self.config = config
        self.artifacts_dir = artifacts_dir or Path("docs/artifacts")
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Default configuration
        self.vad_enabled = config.get("vad_enabled", True)
        self.bgm_suppress_enabled = config.get("bgm_suppress_enabled", True)
        self.denoise_enabled = config.get("denoise_enabled", True)
        self.segment_enabled = config.get("segment_enabled", True)
        self.ts_fix_enabled = config.get("ts_fix_enabled", True)
        
        # Stage-specific configs
        self.vad_config = config.get("vad", {
            "aggressiveness": 2,  # 0-3, higher = more aggressive
            "frame_duration_ms": 30,
            "min_speech_duration_ms": 250,
            "min_silence_duration_ms": 100,
            "energy_threshold": 0.02
        })
        
        self.bgm_config = config.get("bgm", {
            "method": "spectral_gating",  # or "bandpass"
            "noise_gate_threshold": 0.02,
            "freq_mask_threshold": 0.3
        })
        
        self.denoise_config = config.get("denoise", {
            "method": "spectral_subtraction",  # lightweight method
            "noise_floor": 0.02
        })
        
        self.segment_config = config.get("segment", {
            "max_segment_length": 30.0,  # seconds
            "overlap_duration": 0.5  # seconds
        })
        
        self.ts_fix_config = config.get("ts_fix", {
            "max_offset": 0.2,  # seconds
            "word_confidence_threshold": 0.5
        })
        
    def run(self, input_path: Path, save_intermediates: bool = False) -> Dict[str, Any]:
        """
        Run the complete filtering pipeline.
        
        Args:
            input_path: Path to input audio file.
            save_intermediates: Whether to save intermediate files.
            
        Returns:
            dict: Pipeline results with metadata from each stage.
        """
        results = {}
        current_path = input_path
        
        # Load audio
        audio, sr = librosa.load(str(input_path), sr=16000, mono=True)
        
        # Stage 1: VAD/Energy threshold
        if self.vad_enabled:
            result = self.stage_vad(audio, sr, save_intermediates)
            results["vad"] = asdict(result)
            audio = self._load_audio(result.path)
        
        # Stage 2: BGM/Sound effect suppression
        if self.bgm_suppress_enabled:
            result = self.stage_bgm_suppress(audio, sr, save_intermediates)
            results["bgm_suppress"] = asdict(result)
            audio = self._load_audio(result.path)
        
        # Stage 3: Denoise/Speech enhancement
        if self.denoise_enabled:
            result = self.stage_denoise(audio, sr, save_intermediates)
            results["denoise"] = asdict(result)
            audio = self._load_audio(result.path)
        
        # Stage 4: Segmentation strategy
        if self.segment_enabled:
            result = self.stage_segment(audio, sr, save_intermediates)
            results["segment"] = asdict(result)
            audio = self._load_audio(result.path)
        
        # Stage 5: Timestamp post-correction (applied after transcription)
        if self.ts_fix_enabled:
            # This stage is applied after transcription
            results["ts_fix"] = {"enabled": True, "config": self.ts_fix_config}
        
        # Save final processed audio
        final_path = self.artifacts_dir / "final_processed.wav"
        sf.write(str(final_path), audio, sr)
        results["final_audio"] = str(final_path)
        
        return results
    
    def stage_vad(self, audio: np.ndarray, sr: int, save: bool = False) -> StageResult:
        """
        Stage 1: Voice Activity Detection and energy thresholding.
        
        Args:
            audio: Audio signal.
            sr: Sample rate.
            save: Whether to save intermediate file.
            
        Returns:
            StageResult: Processed audio and metadata.
        """
        logger.info("Stage 1: VAD/Energy threshold filtering")
        
        # Initialize WebRTC VAD
        vad = webrtcvad.Vad(self.vad_config["aggressiveness"])
        
        # Convert to int16 for VAD
        audio_int16 = np.int16(audio * 32767)
        
        # Frame parameters
        frame_duration_ms = self.vad_config["frame_duration_ms"]
        frame_length = int(sr * frame_duration_ms / 1000)
        
        # Process frames
        voiced_frames = []
        for i in range(0, len(audio_int16) - frame_length, frame_length):
            frame = audio_int16[i:i + frame_length].tobytes()
            if vad.is_speech(frame, sr):
                # Also check energy threshold
                frame_audio = audio[i:i + frame_length]
                energy = np.sqrt(np.mean(frame_audio ** 2))
                if energy > self.vad_config["energy_threshold"]:
                    voiced_frames.append(frame_audio)
        
        # Concatenate voiced frames
        if voiced_frames:
            filtered_audio = np.concatenate(voiced_frames)
        else:
            filtered_audio = audio  # Keep original if no speech detected
        
        # Save if requested
        output_path = self.artifacts_dir / "stage1_vad.wav"
        if save:
            sf.write(str(output_path), filtered_audio, sr)
        
        return StageResult(
            path=output_path,
            meta={
                "original_duration": len(audio) / sr,
                "filtered_duration": len(filtered_audio) / sr,
                "reduction_ratio": 1 - (len(filtered_audio) / len(audio))
            },
            duration=len(filtered_audio) / sr,
            sample_rate=sr
        )
    
    def stage_bgm_suppress(self, audio: np.ndarray, sr: int, save: bool = False) -> StageResult:
        """
        Stage 2: BGM and sound effect suppression.
        
        Args:
            audio: Audio signal.
            sr: Sample rate.
            save: Whether to save intermediate file.
            
        Returns:
            StageResult: Processed audio and metadata.
        """
        logger.info("Stage 2: BGM/Sound effect suppression")
        
        if self.bgm_config["method"] == "spectral_gating":
            # Simple spectral gating
            stft = librosa.stft(audio)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Apply noise gate
            threshold = self.bgm_config["noise_gate_threshold"] * np.max(magnitude)
            magnitude[magnitude < threshold] = 0
            
            # Reconstruct
            stft_gated = magnitude * np.exp(1j * phase)
            filtered_audio = librosa.istft(stft_gated)
            
        elif self.bgm_config["method"] == "bandpass":
            # Simple bandpass filter for speech frequencies
            nyquist = sr / 2
            low_freq = 80 / nyquist
            high_freq = 8000 / nyquist
            b, a = signal.butter(4, [low_freq, high_freq], btype='band')
            filtered_audio = signal.filtfilt(b, a, audio)
        else:
            filtered_audio = audio
        
        # Save if requested
        output_path = self.artifacts_dir / "stage2_bgm_suppress.wav"
        if save:
            sf.write(str(output_path), filtered_audio, sr)
        
        return StageResult(
            path=output_path,
            meta={
                "method": self.bgm_config["method"],
                "duration": len(filtered_audio) / sr
            },
            duration=len(filtered_audio) / sr,
            sample_rate=sr
        )
    
    def stage_denoise(self, audio: np.ndarray, sr: int, save: bool = False) -> StageResult:
        """
        Stage 3: Denoising and speech enhancement.
        
        Args:
            audio: Audio signal.
            sr: Sample rate.
            save: Whether to save intermediate file.
            
        Returns:
            StageResult: Processed audio and metadata.
        """
        logger.info("Stage 3: Denoise/Speech enhancement")
        
        if self.denoise_config["method"] == "spectral_subtraction":
            # Simple spectral subtraction
            stft = librosa.stft(audio)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise floor (from quiet parts)
            noise_floor = self.denoise_config["noise_floor"] * np.mean(magnitude)
            
            # Subtract noise floor
            magnitude_clean = np.maximum(magnitude - noise_floor, 0)
            
            # Reconstruct
            stft_clean = magnitude_clean * np.exp(1j * phase)
            filtered_audio = librosa.istft(stft_clean)
        else:
            filtered_audio = audio
        
        # Save if requested
        output_path = self.artifacts_dir / "stage3_denoise.wav"
        if save:
            sf.write(str(output_path), filtered_audio, sr)
        
        return StageResult(
            path=output_path,
            meta={
                "method": self.denoise_config["method"],
                "duration": len(filtered_audio) / sr
            },
            duration=len(filtered_audio) / sr,
            sample_rate=sr
        )
    
    def stage_segment(self, audio: np.ndarray, sr: int, save: bool = False) -> StageResult:
        """
        Stage 4: Segmentation strategy for long audio.
        
        Args:
            audio: Audio signal.
            sr: Sample rate.
            save: Whether to save intermediate file.
            
        Returns:
            StageResult: Processed audio and metadata.
        """
        logger.info("Stage 4: Segmentation")
        
        max_samples = int(self.segment_config["max_segment_length"] * sr)
        overlap_samples = int(self.segment_config["overlap_duration"] * sr)
        
        segments = []
        segment_info = []
        
        # Create segments with overlap
        for i in range(0, len(audio), max_samples - overlap_samples):
            segment = audio[i:i + max_samples]
            segments.append(segment)
            segment_info.append({
                "start": i / sr,
                "end": min((i + len(segment)) / sr, len(audio) / sr),
                "duration": len(segment) / sr
            })
        
        # For pipeline, we keep the original audio
        # Segmentation info is used during transcription
        filtered_audio = audio
        
        # Save if requested
        output_path = self.artifacts_dir / "stage4_segment.wav"
        if save:
            sf.write(str(output_path), filtered_audio, sr)
            # Also save segment info
            with open(self.artifacts_dir / "segment_info.json", "w") as f:
                json.dump(segment_info, f, indent=2)
        
        return StageResult(
            path=output_path,
            meta={
                "num_segments": len(segments),
                "segments": segment_info
            },
            duration=len(filtered_audio) / sr,
            sample_rate=sr
        )
    
    def stage_ts_fix(self, segments: List[Dict], audio_path: str) -> List[Dict]:
        """
        Stage 5: Timestamp post-correction (applied after transcription).
        
        Args:
            segments: Transcription segments with word timestamps.
            audio_path: Path to audio file for alignment.
            
        Returns:
            list: Segments with corrected timestamps.
        """
        logger.info("Stage 5: Timestamp correction")
        
        max_offset = self.ts_fix_config["max_offset"]
        confidence_threshold = self.ts_fix_config["word_confidence_threshold"]
        
        corrected_segments = []
        for segment in segments:
            # Check if word timestamps are available
            if "words" in segment and segment["words"]:
                # Find high-confidence words for alignment
                high_conf_words = [
                    w for w in segment["words"]
                    if w.get("probability", 0) > confidence_threshold
                ]
                
                if high_conf_words:
                    # Adjust segment boundaries based on high-confidence words
                    first_word = high_conf_words[0]
                    last_word = high_conf_words[-1]
                    
                    # Check if adjustment is needed
                    if abs(segment["start"] - first_word["start"]) > max_offset:
                        segment["start"] = first_word["start"]
                    if abs(segment["end"] - last_word["end"]) > max_offset:
                        segment["end"] = last_word["end"]
            
            corrected_segments.append(segment)
        
        return corrected_segments
    
    def _load_audio(self, path: Path) -> np.ndarray:
        """Load audio from file."""
        if path.exists():
            audio, _ = librosa.load(str(path), sr=16000, mono=True)
            return audio
        return np.array([])