#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bridge module to integrate new faster-whisper engine with existing Electron app.
This replaces the old electron_backend.py functionality.
"""

import sys
import json
import logging
import argparse
from pathlib import Path
import os

# Set console encoding to UTF-8
if sys.platform.startswith('win'):
    os.system('chcp 65001 > NUL')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('electron_bridge.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# Add engine path
engine_dir = Path(__file__).parent.parent
sys.path.insert(0, str(engine_dir))

from engine.core.model import ModelManager
from engine.core.pipeline import FilterPipeline
from engine.io.subtitle import SubtitleFormatter

def progress_callback(percent, stage, message):
    """Progress callback function for Electron IPC"""
    progress_data = {
        "type": "progress",
        "percent": percent,
        "stage": stage,
        "filename": message,
        "message": message
    }
    output = f"PROGRESS:{json.dumps(progress_data, ensure_ascii=False)}"
    print(output.encode('utf-8').decode('utf-8'))
    sys.stdout.flush()

def process_files(files, settings, corrections):
    """
    Process subtitle files with new engine.
    
    Args:
        files: List of file paths to process
        settings: Dictionary with settings
        corrections: List of corrections to apply
    """
    try:
        # Parse settings
        model_size = settings.get('model', 'large')  # Always use large per spec
        language = settings.get('language', None)
        zh_output = settings.get('zhOutput', 'traditional')
        output_format = settings.get('outputFormat', 'srt')
        output_dir = settings.get('customDir', '')
        
        # Map language codes
        if language == 'auto':
            language = None
        elif language in ['zh-TW', 'zh-CN']:
            language = 'zh'
        
        # Filter configuration
        filter_config = {
            "vad_enabled": settings.get('enableVAD', True),
            "bgm_suppress_enabled": settings.get('enableBGMSuppress', True),
            "denoise_enabled": settings.get('enableDenoise', True),
            "segment_enabled": True,
            "ts_fix_enabled": True
        }
        
        # Initialize model manager with progress callback
        logger.info(f"Processing {len(files)} files")
        logger.info(f"Settings: model={model_size}, language={language}, format={output_format}")
        
        model_manager = ModelManager(progress_callback=progress_callback)
        model_manager.load_model()
        
        # Initialize pipeline
        pipeline = FilterPipeline(filter_config)
        formatter = SubtitleFormatter()
        
        results = []
        total_files = len(files)
        
        for idx, file_path in enumerate(files):
            try:
                file_path = Path(file_path)
                base_percent = (idx * 100) // total_files
                
                # Update progress
                progress_callback(
                    base_percent,
                    "processing",
                    f"Processing {file_path.name} ({idx+1}/{total_files})"
                )
                
                # Run pipeline
                logger.info(f"Running 5-layer filter pipeline on {file_path}")
                pipeline_results = pipeline.run(file_path, save_intermediates=False)
                processed_audio = pipeline_results["final_audio"]
                
                # Transcribe
                logger.info(f"Transcribing {file_path}")
                transcription = model_manager.transcribe(
                    processed_audio,
                    language=language
                )
                
                # Apply timestamp correction
                if pipeline.ts_fix_enabled:
                    transcription["segments"] = pipeline.stage_ts_fix(
                        transcription["segments"],
                        processed_audio
                    )
                
                # Handle Chinese output conversion if needed
                if language == "zh" or transcription["language"] == "zh":
                    transcription["segments"] = convert_chinese(
                        transcription["segments"],
                        zh_output
                    )
                
                # Apply corrections
                if corrections and settings.get('enableCorrections', True):
                    transcription["segments"] = apply_corrections(
                        transcription["segments"],
                        corrections
                    )
                
                # Format and save output
                if output_dir:
                    output_path = Path(output_dir) / f"{file_path.stem}.{output_format}"
                else:
                    output_path = file_path.parent / f"{file_path.stem}.{output_format}"
                
                if output_format == "json":
                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(transcription, f, ensure_ascii=False, indent=2)
                else:
                    subtitle_content = formatter.format(
                        transcription["segments"],
                        output_format
                    )
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(subtitle_content)
                
                results.append({
                    "success": True,
                    "input": str(file_path),
                    "output": str(output_path),
                    "language": transcription["language"],
                    "segments": len(transcription["segments"])
                })
                
                logger.info(f"Successfully processed {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                results.append({
                    "success": False,
                    "input": str(file_path),
                    "error": str(e)
                })
        
        # Final progress
        progress_callback(100, "completed", "All files processed")
        
        return {
            "success": True,
            "results": results,
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"])
        }
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def convert_chinese(segments, output_type):
    """Convert Chinese text between Traditional and Simplified"""
    try:
        import opencc
        
        if output_type == "simplified":
            converter = opencc.OpenCC('t2s')
        else:  # traditional
            converter = opencc.OpenCC('s2t')
        
        for segment in segments:
            segment["text"] = converter.convert(segment["text"])
            if "words" in segment:
                for word in segment["words"]:
                    word["word"] = converter.convert(word["word"])
        
    except ImportError:
        logger.warning("OpenCC not available, skipping Chinese conversion")
    
    return segments

def apply_corrections(segments, corrections):
    """Apply custom corrections to segments"""
    for segment in segments:
        text = segment["text"]
        for correction in corrections:
            if correction.get("find") and correction.get("replace"):
                text = text.replace(correction["find"], correction["replace"])
        segment["text"] = text
    return segments

def main():
    """Main entry point for Electron integration"""
    parser = argparse.ArgumentParser(description='Electron Bridge for Subtitle Generation')
    parser.add_argument('--files', type=str, help='JSON array of file paths')
    parser.add_argument('--settings', type=str, help='JSON settings object')
    parser.add_argument('--corrections', type=str, default='[]', help='JSON corrections array')
    
    args = parser.parse_args()
    
    if args.files and args.settings:
        try:
            files = json.loads(args.files)
            settings = json.loads(args.settings)
            corrections = json.loads(args.corrections) if args.corrections else []
            
            result = process_files(files, settings, corrections)
            print(f"RESULT:{json.dumps(result, ensure_ascii=False)}")
            
        except json.JSONDecodeError as e:
            error_result = {"success": False, "error": f"Invalid JSON: {e}"}
            print(f"RESULT:{json.dumps(error_result, ensure_ascii=False)}")
            sys.exit(1)
        except Exception as e:
            error_result = {"success": False, "error": str(e)}
            print(f"RESULT:{json.dumps(error_result, ensure_ascii=False)}")
            sys.exit(1)
    else:
        print("Usage: python electron_bridge.py --files '[\"file1.mp4\"]' --settings '{...}'")
        sys.exit(1)

if __name__ == "__main__":
    main()