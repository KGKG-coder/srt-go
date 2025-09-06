#!/usr/bin/env python3
"""Main engine entry point for subtitle generation."""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import opencc

from engine.core.model import ModelManager
from engine.core.pipeline import FilterPipeline
from engine.io.subtitle import SubtitleFormatter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SubtitleEngine:
    """Main subtitle generation engine."""
    
    def __init__(self, models_dir: Optional[Path] = None):
        """
        Initialize subtitle engine.
        
        Args:
            models_dir: Directory for storing models.
        """
        self.model_manager = ModelManager(models_dir)
        self.pipeline = None
        self.formatter = SubtitleFormatter()
        
        # Initialize OpenCC for Traditional/Simplified Chinese conversion
        self.cc_s2t = opencc.OpenCC('s2t')  # Simplified to Traditional
        self.cc_t2s = opencc.OpenCC('t2s')  # Traditional to Simplified
        
    def initialize(self, model_dir_override: Optional[str] = None,
                  progress_callback: Optional[callable] = None):
        """
        Initialize model and pipeline.
        
        Args:
            model_dir_override: Optional path to override model location.
            progress_callback: Callback for download progress.
        """
        # Set progress callback
        if progress_callback:
            self.model_manager.downloader.progress_callback = progress_callback
        
        # Load model
        self.model_manager.load_model(model_dir_override)
        
    def transcribe(self, input_path: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transcribe audio/video file with specified settings.
        
        Args:
            input_path: Path to input audio/video file.
            settings: Transcription settings including:
                - language: Input language (zh, en, ja, ko)
                - zh_output: Chinese output type (traditional, simplified)
                - output_format: Output format (srt, vtt, txt, json)
                - filter_config: 5-layer filter configuration
                - save_intermediates: Save intermediate filter outputs
                
        Returns:
            dict: Transcription results with paths and metadata.
        """
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Initialize pipeline with filter config
        filter_config = settings.get("filter_config", {})
        self.pipeline = FilterPipeline(filter_config)
        
        # Run 5-layer filtering pipeline
        logger.info("Running 5-layer filtering pipeline...")
        save_intermediates = settings.get("save_intermediates", False)
        pipeline_results = self.pipeline.run(input_file, save_intermediates)
        
        # Get processed audio path
        processed_audio = pipeline_results["final_audio"]
        
        # Transcribe with model
        logger.info("Transcribing with Whisper model...")
        language = settings.get("language")  # None for auto-detect
        transcription = self.model_manager.transcribe(
            processed_audio,
            language=language
        )
        
        # Apply timestamp correction (Stage 5)
        if self.pipeline.ts_fix_enabled:
            transcription["segments"] = self.pipeline.stage_ts_fix(
                transcription["segments"],
                processed_audio
            )
        
        # Handle Chinese output conversion
        if language == "zh" or transcription["language"] == "zh":
            zh_output = settings.get("zh_output", "traditional")
            transcription["segments"] = self._convert_chinese(
                transcription["segments"],
                zh_output
            )
        
        # Format output
        output_format = settings.get("output_format", "srt")
        output_path = input_file.parent / f"{input_file.stem}.{output_format}"
        
        if output_format == "json":
            # Save as JSON
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(transcription, f, ensure_ascii=False, indent=2)
        else:
            # Format as subtitle
            subtitle_content = self.formatter.format(
                transcription["segments"],
                output_format
            )
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(subtitle_content)
        
        return {
            "output_path": str(output_path),
            "language": transcription["language"],
            "language_probability": transcription["language_probability"],
            "duration": transcription["duration"],
            "num_segments": len(transcription["segments"]),
            "pipeline_results": pipeline_results,
            "settings": settings
        }
    
    def _convert_chinese(self, segments: list, output_type: str) -> list:
        """
        Convert Chinese text between Traditional and Simplified.
        
        Args:
            segments: Transcription segments.
            output_type: "traditional" or "simplified".
            
        Returns:
            list: Segments with converted text.
        """
        if output_type == "simplified":
            converter = self.cc_t2s
        else:  # traditional
            converter = self.cc_s2t
        
        for segment in segments:
            segment["text"] = converter.convert(segment["text"])
            # Also convert word-level if available
            if "words" in segment:
                for word in segment["words"]:
                    word["word"] = converter.convert(word["word"])
        
        return segments
    
    def import_offline_pack(self, pack_path: str) -> bool:
        """
        Import model from offline pack.
        
        Args:
            pack_path: Path to offline model pack.
            
        Returns:
            bool: True if successful.
        """
        try:
            self.model_manager.downloader.import_offline_pack(Path(pack_path))
            return True
        except Exception as e:
            logger.error(f"Failed to import offline pack: {e}")
            return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Subtitle generation engine")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Transcribe command
    transcribe_parser = subparsers.add_parser("transcribe", help="Transcribe audio/video")
    transcribe_parser.add_argument("input", help="Input audio/video file")
    transcribe_parser.add_argument("--language", choices=["zh", "en", "ja", "ko"],
                                  help="Input language (auto-detect if not specified)")
    transcribe_parser.add_argument("--zh-output", choices=["traditional", "simplified"],
                                  default="traditional",
                                  help="Chinese output type (only for Chinese input)")
    transcribe_parser.add_argument("--format", choices=["srt", "vtt", "txt", "json"],
                                  default="srt", help="Output format")
    transcribe_parser.add_argument("--model-dir", help="Override model directory")
    transcribe_parser.add_argument("--save-intermediates", action="store_true",
                                  help="Save intermediate filter outputs")
    transcribe_parser.add_argument("--disable-vad", action="store_true",
                                  help="Disable VAD filtering")
    transcribe_parser.add_argument("--disable-bgm", action="store_true",
                                  help="Disable BGM suppression")
    transcribe_parser.add_argument("--disable-denoise", action="store_true",
                                  help="Disable denoising")
    
    # Import command
    import_parser = subparsers.add_parser("import-model-pack",
                                         help="Import offline model pack")
    import_parser.add_argument("pack", help="Path to model pack file")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show model and runtime info")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize engine
    engine = SubtitleEngine()
    
    if args.command == "transcribe":
        # Prepare settings
        settings = {
            "language": args.language,
            "zh_output": args.zh_output,
            "output_format": args.format,
            "save_intermediates": args.save_intermediates,
            "filter_config": {
                "vad_enabled": not args.disable_vad,
                "bgm_suppress_enabled": not args.disable_bgm,
                "denoise_enabled": not args.disable_denoise,
                "segment_enabled": True,
                "ts_fix_enabled": True
            }
        }
        
        # Initialize model
        def progress_callback(percent, stage, message):
            print(f"[{stage}] {message}")
        
        engine.initialize(args.model_dir, progress_callback)
        
        # Transcribe
        try:
            result = engine.transcribe(args.input, settings)
            print(f"\nTranscription completed!")
            print(f"Output: {result['output_path']}")
            print(f"Language: {result['language']} ({result['language_probability']:.2%})")
            print(f"Duration: {result['duration']:.1f}s")
            print(f"Segments: {result['num_segments']}")
            return 0
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return 1
    
    elif args.command == "import-model-pack":
        if engine.import_offline_pack(args.pack):
            print("Model pack imported successfully!")
            return 0
        else:
            print("Failed to import model pack")
            return 1
    
    elif args.command == "info":
        engine.initialize()
        info = engine.model_manager.get_model_info()
        print(json.dumps(info, indent=2))
        return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(main())