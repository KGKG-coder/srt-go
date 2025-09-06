#!/usr/bin/env python3
"""
Test with standard large-v3 model (let faster-whisper handle download)
"""

import sys
import logging
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_standard_model():
    """Test with standard large-v3 model"""
    try:
        print("=" * 80)
        print("Testing Standard Large-v3 Model with INT8")
        print("=" * 80)
        
        # Test video files
        test_video_dir = Path("H:/字幕程式設計環境/test_video")
        if not test_video_dir.exists():
            print(f"ERROR: Test video directory not found")
            return False
        
        video_files = list(test_video_dir.glob("*.mp4"))
        if not video_files:
            print("ERROR: No video files found")
            return False
        
        print(f"Found {len(video_files)} video files:")
        for video in video_files:
            size_mb = video.stat().st_size / (1024**2)
            print(f"  - {video.name} ({size_mb:.1f} MB)")
        
        # Select smallest video for testing
        test_video = min(video_files, key=lambda x: x.stat().st_size)
        print(f"\nUsing for test: {test_video.name}")
        
        try:
            from faster_whisper import WhisperModel
            
            print(f"\nCreating standard large-v3 model...")
            print(f"This will download the model if not cached (~3GB)")
            
            start_time = time.time()
            
            # Use standard large-v3 with INT8 compute type
            model = WhisperModel(
                "large-v3",  # Let faster-whisper handle the download
                device="cpu",
                compute_type="int8"  # Use INT8 for speed and memory efficiency
            )
            
            load_time = time.time() - start_time
            print(f"SUCCESS: Model loaded in {load_time:.1f} seconds")
            
            # Test transcription
            print(f"\nStarting transcription...")
            start_time = time.time()
            
            segments, info = model.transcribe(
                str(test_video),
                language="zh",  # Chinese
                task="transcribe",
                beam_size=5,
                best_of=5
            )
            
            print(f"Language detected: {info.language}")
            print(f"Language probability: {info.language_probability:.2%}")
            print(f"Duration: {info.duration:.2f} seconds")
            
            # Convert to list and measure time
            segment_list = list(segments)
            transcribe_time = time.time() - start_time
            
            print(f"SUCCESS: Transcription completed in {transcribe_time:.1f} seconds")
            print(f"Total segments: {len(segment_list)}")
            
            # Calculate speed ratio
            if info.duration > 0:
                speed_ratio = info.duration / transcribe_time
                print(f"Speed ratio: {speed_ratio:.1f}x real-time")
            
            # Show first few segments
            if segment_list:
                print(f"\nFirst segments:")
                for i, segment in enumerate(segment_list[:5]):
                    print(f"  [{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
                if len(segment_list) > 5:
                    print(f"  ... (showing 5 of {len(segment_list)} segments)")
            
            # Save SRT file
            output_dir = test_video_dir / "subtitles"
            output_dir.mkdir(exist_ok=True)
            srt_file = output_dir / f"{test_video.stem}_large-v3_int8.srt"
            
            print(f"\nSaving SRT file: {srt_file}")
            
            with open(srt_file, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(segment_list, 1):
                    # Format timestamps for SRT
                    start_hours = int(segment.start // 3600)
                    start_minutes = int((segment.start % 3600) // 60)
                    start_seconds = segment.start % 60
                    start_time = f"{start_hours:02d}:{start_minutes:02d}:{start_seconds:06.3f}".replace('.', ',')
                    
                    end_hours = int(segment.end // 3600)
                    end_minutes = int((segment.end % 3600) // 60)
                    end_seconds = segment.end % 60
                    end_time = f"{end_hours:02d}:{end_minutes:02d}:{end_seconds:06.3f}".replace('.', ',')
                    
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{segment.text.strip()}\n\n")
            
            srt_size = srt_file.stat().st_size
            print(f"SRT file saved: {srt_size} bytes")
            
            # Performance summary
            print(f"\n{'='*60}")
            print("Performance Summary")
            print(f"{'='*60}")
            print(f"Model: Large-v3 with INT8 quantization")
            print(f"Video: {test_video.name} ({test_video.stat().st_size / (1024**2):.1f} MB)")
            print(f"Duration: {info.duration:.1f} seconds")
            print(f"Transcription time: {transcribe_time:.1f} seconds")
            print(f"Speed: {speed_ratio:.1f}x real-time")
            print(f"Segments: {len(segment_list)}")
            print(f"Output: {srt_size} bytes")
            
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
    success = test_standard_model()
    print(f"\n{'='*80}")
    if success:
        print("Standard Large-v3 INT8 test completed successfully!")
        print("The model is working and ready for production use!")
    else:
        print("Standard Large-v3 INT8 test failed!")
    print(f"{'='*80}")
    sys.exit(0 if success else 1)