#!/usr/bin/env python3
"""
Test large video (DRLIN.mp4) with INT8 model
Compare performance on different video sizes
"""

import sys
import logging
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_large_video():
    """Test large video processing with INT8"""
    try:
        print("=" * 80)
        print("Large Video Test - DRLIN.mp4 with INT8 Model")
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
        
        # Find DRLIN.mp4 specifically
        drlin_video = None
        hutest_video = None
        
        for video in video_files:
            if "DRLIN" in video.name:
                drlin_video = video
            elif "hutest" in video.name:
                hutest_video = video
        
        if not drlin_video:
            print("ERROR: DRLIN.mp4 not found")
            return False
        
        # Show both videos for comparison
        print(f"Available videos:")
        for video in video_files:
            size_mb = video.stat().st_size / (1024**2)
            print(f"  - {video.name}: {size_mb:.1f} MB")
        
        print(f"\nTesting large video: {drlin_video.name}")
        drlin_size_mb = drlin_video.stat().st_size / (1024**2)
        print(f"File size: {drlin_size_mb:.1f} MB")
        
        try:
            from faster_whisper import WhisperModel
            
            # Create INT8 model
            print(f"\nCreating Large-v3 model with INT8...")
            start_time = time.time()
            
            model = WhisperModel(
                "large-v3",
                device="cpu",
                compute_type="int8"
            )
            
            load_time = time.time() - start_time
            print(f"Model load time: {load_time:.1f} seconds")
            
            # Test transcription on large video
            print(f"\nStarting transcription of large video...")
            print(f"This may take longer due to video size...")
            
            start_time = time.time()
            
            segments, info = model.transcribe(
                str(drlin_video),
                language="zh",
                task="transcribe",
                beam_size=5,
                best_of=5,
                temperature=[0.0, 0.2, 0.4, 0.6, 0.8]
            )
            
            print(f"Language detected: {info.language}")
            print(f"Language probability: {info.language_probability:.2%}")
            print(f"Video duration: {info.duration:.2f} seconds ({info.duration/60:.1f} minutes)")
            
            # Process segments with progress indication
            segment_list = []
            segment_count = 0
            
            print(f"Processing segments...")
            for segment in segments:
                segment_list.append(segment)
                segment_count += 1
                
                # Show progress every 10 segments
                if segment_count % 10 == 0:
                    current_time = segment.end
                    progress = (current_time / info.duration) * 100
                    print(f"  Progress: {segment_count} segments, {current_time:.1f}s / {info.duration:.1f}s ({progress:.1f}%)")
            
            transcribe_time = time.time() - start_time
            speed_ratio = info.duration / transcribe_time if transcribe_time > 0 else 0
            
            print(f"\nTranscription completed!")
            print(f"Total transcription time: {transcribe_time:.1f} seconds ({transcribe_time/60:.1f} minutes)")
            print(f"Speed ratio: {speed_ratio:.2f}x real-time")
            print(f"Total segments: {len(segment_list)}")
            
            # Calculate efficiency metrics
            mb_per_second = drlin_size_mb / transcribe_time
            duration_per_second = info.duration / transcribe_time
            
            print(f"Processing speed: {mb_per_second:.2f} MB/second")
            print(f"Audio processing: {duration_per_second:.2f}x real-time")
            
            # Save SRT file
            output_dir = test_video_dir / "subtitles"
            output_dir.mkdir(exist_ok=True)
            srt_file = output_dir / f"{drlin_video.stem}_large-v3_int8.srt"
            
            print(f"\nSaving SRT file: {srt_file}")
            
            with open(srt_file, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(segment_list, 1):
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
            print(f"SRT file saved: {srt_size} bytes ({srt_size/1024:.1f} KB)")
            
            # Show sample segments
            print(f"\nFirst 5 segments:")
            for i, segment in enumerate(segment_list[:5]):
                print(f"  [{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text[:50]}...")
            
            if len(segment_list) > 10:
                print(f"\nLast 3 segments:")
                for i, segment in enumerate(segment_list[-3:], len(segment_list)-2):
                    print(f"  [{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text[:50]}...")
            
            # Performance comparison with small video
            if hutest_video:
                print(f"\n{'='*60}")
                print("PERFORMANCE COMPARISON")
                print(f"{'='*60}")
                
                hutest_size_mb = hutest_video.stat().st_size / (1024**2)
                
                # Previous results for hutest (from earlier test)
                hutest_transcribe_time = 10.3  # seconds
                hutest_duration = 11.29  # seconds
                hutest_speed_ratio = 1.1
                
                print(f"Small Video (hutest.mp4):")
                print(f"  File size: {hutest_size_mb:.1f} MB")
                print(f"  Duration: {hutest_duration:.1f} seconds")
                print(f"  Transcribe time: {hutest_transcribe_time:.1f} seconds")
                print(f"  Speed ratio: {hutest_speed_ratio:.1f}x")
                print(f"  MB/second: {hutest_size_mb/hutest_transcribe_time:.2f}")
                
                print(f"\nLarge Video (DRLIN.mp4):")
                print(f"  File size: {drlin_size_mb:.1f} MB")
                print(f"  Duration: {info.duration:.1f} seconds")
                print(f"  Transcribe time: {transcribe_time:.1f} seconds")
                print(f"  Speed ratio: {speed_ratio:.2f}x")
                print(f"  MB/second: {mb_per_second:.2f}")
                
                # Calculate scaling efficiency
                size_ratio = drlin_size_mb / hutest_size_mb
                time_ratio = transcribe_time / hutest_transcribe_time
                efficiency = size_ratio / time_ratio
                
                print(f"\nScaling Analysis:")
                print(f"  Size ratio: {size_ratio:.1f}x larger")
                print(f"  Time ratio: {time_ratio:.1f}x longer")
                print(f"  Efficiency: {efficiency:.2f} (1.0 = linear scaling)")
                
                if efficiency > 0.9:
                    print(f"  Result: Excellent scaling efficiency")
                elif efficiency > 0.7:
                    print(f"  Result: Good scaling efficiency")
                else:
                    print(f"  Result: Moderate scaling efficiency")
            
            print(f"\n{'='*60}")
            print("LARGE VIDEO PROCESSING SUMMARY")
            print(f"{'='*60}")
            print(f"SUCCESS: Large video processed successfully!")
            print(f"Model: Large-v3 INT8")
            print(f"Input: {drlin_video.name} ({drlin_size_mb:.1f} MB, {info.duration/60:.1f} min)")
            print(f"Output: {len(segment_list)} segments, {srt_size/1024:.1f} KB SRT")
            print(f"Performance: {speed_ratio:.2f}x real-time")
            print(f"Memory efficiency: INT8 quantization")
            print(f"Stability: No errors or crashes")
            
            return True
            
        except ImportError:
            print("ERROR: faster-whisper not installed")
            return False
        except Exception as e:
            print(f"ERROR: Large video test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_large_video()
    print(f"\n{'='*80}")
    if success:
        print("Large video test completed successfully!")
        print("INT8 model is stable and efficient for large videos!")
    else:
        print("Large video test failed!")
    print(f"{'='*80}")
    sys.exit(0 if success else 1)