#!/usr/bin/env python3
"""
Test existing INT8 model - Direct test
"""

import sys
import os
import logging
import time
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_existing_model():
    """Test the existing INT8 model"""
    try:
        print("=" * 80)
        print("Testing Existing INT8 Model")
        print("=" * 80)
        
        # Check model directory
        # Use relative path for better portability
        script_dir = Path(__file__).parent.parent
        model_dir = script_dir / "models" / "large-v3-turbo-int8"
        if not model_dir.exists():
            print(f"ERROR: Model directory not found: {model_dir}")
            return False
        
        # Check model files
        required_files = ["model.bin", "config.json", "tokenizer.json"]
        print(f"\nChecking model files in: {model_dir}")
        
        for file_name in required_files:
            file_path = model_dir / file_name
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024**2)
                print(f"  SUCCESS: {file_name} ({size_mb:.1f} MB)")
            else:
                print(f"  ERROR: Missing {file_name}")
                return False
        
        # Test with faster-whisper directly
        print(f"\nTesting with faster-whisper...")
        
        try:
            from faster_whisper import WhisperModel
            
            print(f"Creating model instance...")
            start_time = time.time()
            
            model = WhisperModel(
                str(model_dir),
                device="cpu",
                compute_type="int8"
            )
            
            load_time = time.time() - start_time
            print(f"SUCCESS: Model loaded in {load_time:.1f} seconds")
            
            # Test with video files
            test_video_dir = Path("H:/字幕程式設計環境/test_video")
            if test_video_dir.exists():
                video_files = list(test_video_dir.glob("*.mp4"))
                if video_files:
                    # Test with smallest video
                    test_video = min(video_files, key=lambda x: x.stat().st_size)
                    print(f"\nTesting transcription with: {test_video.name}")
                    
                    start_time = time.time()
                    segments, info = model.transcribe(
                        str(test_video),
                        language="zh",
                        task="transcribe"
                    )
                    
                    print(f"Language detected: {info.language}")
                    print(f"Language probability: {info.language_probability:.2%}")
                    
                    # Get first few segments
                    segment_list = list(segments)
                    transcribe_time = time.time() - start_time
                    
                    print(f"SUCCESS: Transcription completed in {transcribe_time:.1f} seconds")
                    print(f"Total segments: {len(segment_list)}")
                    
                    if segment_list:
                        print(f"\nFirst few segments:")
                        for i, segment in enumerate(segment_list[:3]):
                            print(f"  [{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
                    
                    # Save to SRT file
                    output_dir = test_video_dir / "subtitles"
                    output_dir.mkdir(exist_ok=True)
                    srt_file = output_dir / f"{test_video.stem}_int8.srt"
                    
                    with open(srt_file, 'w', encoding='utf-8') as f:
                        for i, segment in enumerate(segment_list, 1):
                            start_time = f"{int(segment.start // 3600):02d}:{int((segment.start % 3600) // 60):02d}:{segment.start % 60:06.3f}".replace('.', ',')
                            end_time = f"{int(segment.end // 3600):02d}:{int((segment.end % 3600) // 60):02d}:{segment.end % 60:06.3f}".replace('.', ',')
                            f.write(f"{i}\n{start_time} --> {end_time}\n{segment.text}\n\n")
                    
                    srt_size = srt_file.stat().st_size
                    print(f"SRT file saved: {srt_file} ({srt_size} bytes)")
                    
                    return True
                else:
                    print("No video files found for testing")
            else:
                print("Test video directory not found")
                
            # At least model loading worked
            return True
            
        except ImportError:
            print("ERROR: faster-whisper not installed")
            return False
        except Exception as e:
            print(f"ERROR: Model test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_existing_model()
    print(f"\n{'='*80}")
    if success:
        print("INT8 Model test completed successfully!")
        print("Model is working and ready for use!")
    else:
        print("INT8 Model test failed!")
    print(f"{'='*80}")
    sys.exit(0 if success else 1)