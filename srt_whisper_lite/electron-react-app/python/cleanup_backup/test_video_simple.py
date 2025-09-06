#!/usr/bin/env python3
"""
Simple video processing test - Using INT8 model
Test videos in test_video directory
"""

import sys
import os
import logging
import time
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_video_processing():
    """Test video processing functionality"""
    try:
        print("=" * 80)
        print("Video Processing Test - INT8 Model")
        print("=" * 80)
        
        # Check test video directory
        test_video_dir = Path("H:/字幕程式設計環境/test_video")
        if not test_video_dir.exists():
            print(f"ERROR: Test video directory not found: {test_video_dir}")
            return False
        
        # Find video files
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
        video_files = []
        for ext in video_extensions:
            video_files.extend(test_video_dir.glob(f"*{ext}"))
        
        if not video_files:
            print("ERROR: No video files found")
            return False
        
        print(f"\nFound {len(video_files)} video files:")
        for i, video_file in enumerate(video_files, 1):
            size_mb = video_file.stat().st_size / (1024**2)
            print(f"  {i}. {video_file.name} ({size_mb:.1f} MB)")
        
        # Import required modules
        print("\nLoading model manager and subtitle core...")
        try:
            from large_v3_int8_model_manager import LargeV3INT8ModelManager
            from simplified_subtitle_core import SimplifiedSubtitleCore
        except ImportError as e:
            print(f"ERROR: Import failed: {e}")
            return False
        
        # Initialize model manager
        print("\nInitializing INT8 model manager...")
        model_manager = LargeV3INT8ModelManager()
        
        # Check model availability
        if not model_manager.check_model_availability():
            print("WARNING: Model not available, will download automatically")
            
            print("\nDownloading model...")
            def progress_callback(progress, message):
                bar_length = 40
                filled = int(bar_length * progress)
                bar = '=' * filled + '-' * (bar_length - filled)
                print(f"\r  [{bar}] {progress*100:.1f}% - {message}", end='', flush=True)
            
            success, path = model_manager.download_model(progress_callback)
            print()  # newline
            if not success:
                print(f"ERROR: Model download failed: {path}")
                return False
            print(f"SUCCESS: Model downloaded: {path}")
        
        # Create subtitle core
        print("\nInitializing subtitle generation core...")
        subtitle_core = SimplifiedSubtitleCore(
            model_size="large-v3",
            device="cpu",  # Use CPU for testing
            compute_type="int8"
        )
        
        # Initialize model
        def init_progress(percent, message):
            print(f"  Progress {percent}%: {message}")
        
        print("Loading AI model...")
        init_start = time.time()
        success = subtitle_core.initialize(init_progress)
        init_time = time.time() - init_start
        
        if not success:
            print("ERROR: Model initialization failed")
            return False
        
        print(f"SUCCESS: Model loaded! Time: {init_time:.1f} seconds")
        
        # Automatically process the first (smaller) video for testing
        print(f"\nAutomatically selecting first video for testing:")
        selected_videos = [video_files[0]]  # Process first video
        print(f"Selected: {selected_videos[0].name}")
        
        # Process selected videos
        print(f"\nStarting to process {len(selected_videos)} video(s)...")
        
        results = []
        for i, video_file in enumerate(selected_videos, 1):
            print(f"\n{'='*60}")
            print(f"Processing video {i}/{len(selected_videos)}: {video_file.name}")
            print(f"{'='*60}")
            
            # Create output directory
            output_dir = video_file.parent / "subtitles"
            output_dir.mkdir(exist_ok=True)
            
            # Generate SRT filename
            srt_file = output_dir / f"{video_file.stem}.srt"
            
            # Progress callback
            def process_progress(percent, message):
                bar_length = 50
                filled = int(bar_length * percent / 100)
                bar = '=' * filled + '-' * (bar_length - filled)
                print(f"\r  [{bar}] {percent:.1f}% - {message}", end='', flush=True)
            
            try:
                start_time = time.time()
                
                # Call subtitle generation
                success = subtitle_core.process_audio(
                    str(video_file),
                    str(srt_file),
                    progress_callback=process_progress,
                    language="zh",  # Chinese
                    task="transcribe"
                )
                
                elapsed = time.time() - start_time
                print()  # newline
                
                if success:
                    # Check generated file
                    if srt_file.exists():
                        file_size = srt_file.stat().st_size
                        print(f"  SUCCESS: Subtitle generated!")
                        print(f"  Output: {srt_file}")
                        print(f"  Size: {file_size} bytes")
                        print(f"  Time: {elapsed:.1f} seconds")
                        
                        # Read and display first few lines
                        try:
                            with open(srt_file, 'r', encoding='utf-8') as f:
                                lines = f.readlines()[:10]  # First 10 lines
                            print(f"  Subtitle preview:")
                            for line in lines:
                                print(f"    {line.strip()}")
                            if len(lines) >= 10:
                                print(f"    ... (total {len(lines)} lines)")
                        except Exception as e:
                            print(f"  WARNING: Cannot read subtitle content: {e}")
                        
                        results.append({
                            "video": video_file.name,
                            "success": True,
                            "time": elapsed,
                            "output": str(srt_file),
                            "size": file_size
                        })
                    else:
                        print(f"  ERROR: Subtitle file not generated")
                        results.append({
                            "video": video_file.name,
                            "success": False,
                            "error": "Subtitle file not generated"
                        })
                else:
                    print(f"  ERROR: Subtitle generation failed")
                    results.append({
                        "video": video_file.name,
                        "success": False,
                        "error": "Processing failed"
                    })
                    
            except Exception as e:
                print(f"\n  ERROR: Processing error: {e}")
                results.append({
                    "video": video_file.name,
                    "success": False,
                    "error": str(e)
                })
        
        # Show summary
        print(f"\n{'='*80}")
        print("Processing Summary")
        print(f"{'='*80}")
        
        successful = sum(1 for r in results if r["success"])
        total_time = sum(r.get("time", 0) for r in results if r["success"])
        
        print(f"Successful: {successful}/{len(results)} videos")
        print(f"Total time: {total_time:.1f} seconds")
        if successful > 0:
            print(f"Average speed: {total_time/successful:.1f} seconds/video")
        
        print(f"\nDetailed results:")
        for result in results:
            if result["success"]:
                print(f"  SUCCESS: {result['video']}")
                print(f"    Time: {result['time']:.1f}s, Output: {result['size']} bytes")
            else:
                print(f"  FAILED: {result['video']}: {result.get('error', 'Unknown error')}")
        
        print(f"\nINT8 Model Performance:")
        print(f"  - Model size: ~1GB (70% smaller than standard)")
        print(f"  - Compute precision: INT8 quantized")
        print(f"  - Speed advantage: ~3.5x faster than FP16")
        print(f"  - Use case: Fast transcription, resource-constrained environments")
        
        return successful > 0
        
    except Exception as e:
        print(f"\nERROR: Test process failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_video_processing()
    print(f"\n{'='*80}")
    if success:
        print("Video processing test completed successfully!")
    else:
        print("Video processing test failed!")
    print(f"{'='*80}")
    sys.exit(0 if success else 1)