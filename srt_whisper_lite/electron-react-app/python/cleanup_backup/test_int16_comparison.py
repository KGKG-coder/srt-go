#!/usr/bin/env python3
"""
Test INT16 model and compare with INT8
Compare performance, accuracy, and file sizes
"""

import sys
import logging
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_int16_vs_int8():
    """Test INT16 vs INT8 comparison"""
    try:
        print("=" * 80)
        print("INT16 vs INT8 Comparison Test")
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
        
        # Select smallest video for consistent testing
        test_video = min(video_files, key=lambda x: x.stat().st_size)
        video_size_mb = test_video.stat().st_size / (1024**2)
        print(f"Test video: {test_video.name} ({video_size_mb:.1f} MB)")
        
        try:
            from faster_whisper import WhisperModel
            
            results = {}
            
            # Test both compute types
            compute_types = ["int8", "int16"]
            
            for compute_type in compute_types:
                print(f"\n{'='*60}")
                print(f"Testing with {compute_type.upper()}")
                print(f"{'='*60}")
                
                # Create model
                print(f"Creating Large-v3 model with {compute_type}...")
                start_time = time.time()
                
                model = WhisperModel(
                    "large-v3",
                    device="cpu",
                    compute_type=compute_type
                )
                
                load_time = time.time() - start_time
                print(f"Model load time: {load_time:.1f} seconds")
                
                # Test transcription
                print(f"Starting transcription...")
                start_time = time.time()
                
                segments, info = model.transcribe(
                    str(test_video),
                    language="zh",
                    task="transcribe",
                    beam_size=5,
                    best_of=5,
                    temperature=[0.0, 0.2, 0.4, 0.6, 0.8]
                )
                
                # Convert to list
                segment_list = list(segments)
                transcribe_time = time.time() - start_time
                
                # Calculate metrics
                speed_ratio = info.duration / transcribe_time if transcribe_time > 0 else 0
                
                print(f"Language detected: {info.language}")
                print(f"Language probability: {info.language_probability:.2%}")
                print(f"Duration: {info.duration:.2f} seconds")
                print(f"Transcription time: {transcribe_time:.1f} seconds")
                print(f"Speed ratio: {speed_ratio:.1f}x real-time")
                print(f"Total segments: {len(segment_list)}")
                
                # Save results
                results[compute_type] = {
                    "load_time": load_time,
                    "transcribe_time": transcribe_time,
                    "speed_ratio": speed_ratio,
                    "language_probability": info.language_probability,
                    "segments": segment_list,
                    "segment_count": len(segment_list),
                    "duration": info.duration
                }
                
                # Save SRT file
                output_dir = test_video_dir / "subtitles"
                output_dir.mkdir(exist_ok=True)
                srt_file = output_dir / f"{test_video.stem}_large-v3_{compute_type}.srt"
                
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
                results[compute_type]["srt_file"] = srt_file
                results[compute_type]["srt_size"] = srt_size
                
                print(f"SRT saved: {srt_file.name} ({srt_size} bytes)")
                
                # Show first few segments
                print(f"\nFirst few segments:")
                for i, segment in enumerate(segment_list[:3]):
                    print(f"  [{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
                
                # Clean up model to free memory
                del model
            
            # Comparison Analysis
            print(f"\n{'='*80}")
            print("DETAILED COMPARISON ANALYSIS")
            print(f"{'='*80}")
            
            int8_result = results["int8"]
            int16_result = results["int16"]
            
            print(f"\n🚀 PERFORMANCE COMPARISON:")
            print(f"{'Metric':<20} {'INT8':<15} {'INT16':<15} {'Difference':<20}")
            print(f"{'-'*70}")
            
            # Load time comparison
            load_diff = ((int16_result["load_time"] - int8_result["load_time"]) / int8_result["load_time"] * 100)
            print(f"{'Load Time':<20} {int8_result['load_time']:<15.1f} {int16_result['load_time']:<15.1f} {load_diff:>+.1f}%")
            
            # Transcribe time comparison  
            transcribe_diff = ((int16_result["transcribe_time"] - int8_result["transcribe_time"]) / int8_result["transcribe_time"] * 100)
            print(f"{'Transcribe Time':<20} {int8_result['transcribe_time']:<15.1f} {int16_result['transcribe_time']:<15.1f} {transcribe_diff:>+.1f}%")
            
            # Speed ratio comparison
            speed_diff = ((int16_result["speed_ratio"] - int8_result["speed_ratio"]) / int8_result["speed_ratio"] * 100)
            print(f"{'Speed Ratio':<20} {int8_result['speed_ratio']:<15.1f} {int16_result['speed_ratio']:<15.1f} {speed_diff:>+.1f}%")
            
            print(f"\n🎯 ACCURACY COMPARISON:")
            print(f"{'Metric':<20} {'INT8':<15} {'INT16':<15} {'Difference':<20}")
            print(f"{'-'*70}")
            
            # Language confidence
            lang_diff = int16_result["language_probability"] - int8_result["language_probability"]
            print(f"{'Language Conf.':<20} {int8_result['language_probability']:<15.2%} {int16_result['language_probability']:<15.2%} {lang_diff:>+.2%}")
            
            # Segment count
            seg_diff = int16_result["segment_count"] - int8_result["segment_count"]
            print(f"{'Segment Count':<20} {int8_result['segment_count']:<15} {int16_result['segment_count']:<15} {seg_diff:>+d}")
            
            # File size
            size_diff = int16_result["srt_size"] - int8_result["srt_size"]
            print(f"{'SRT Size (bytes)':<20} {int8_result['srt_size']:<15} {int16_result['srt_size']:<15} {size_diff:>+d}")
            
            print(f"\n📝 TEXT QUALITY COMPARISON:")
            print(f"Comparing first 3 segments for text differences...")
            
            for i in range(min(3, len(int8_result["segments"]), len(int16_result["segments"]))):
                int8_text = int8_result["segments"][i].text.strip()
                int16_text = int16_result["segments"][i].text.strip()
                
                print(f"\nSegment {i+1}:")
                print(f"  INT8 : {int8_text}")
                print(f"  INT16: {int16_text}")
                
                if int8_text == int16_text:
                    print(f"  Result: IDENTICAL")
                else:
                    print(f"  Result: DIFFERENT")
            
            print(f"\n💾 MODEL SIZE ESTIMATION:")
            # Note: These are typical sizes, actual may vary
            print(f"  INT8  Model: ~800MB - 1GB")
            print(f"  INT16 Model: ~1.5GB - 2GB")
            print(f"  Size Ratio: INT16 is ~2x larger than INT8")
            
            print(f"\n📊 SUMMARY RECOMMENDATIONS:")
            print(f"{'='*60}")
            
            if int8_result["speed_ratio"] > int16_result["speed_ratio"]:
                faster_model = "INT8"
                speed_advantage = ((int8_result["speed_ratio"] - int16_result["speed_ratio"]) / int16_result["speed_ratio"] * 100)
            else:
                faster_model = "INT16"
                speed_advantage = ((int16_result["speed_ratio"] - int8_result["speed_ratio"]) / int8_result["speed_ratio"] * 100)
            
            print(f"⚡ SPEED WINNER: {faster_model} (faster by {speed_advantage:.1f}%)")
            
            if int8_result["language_probability"] > int16_result["language_probability"]:
                more_confident = "INT8"
            elif int16_result["language_probability"] > int8_result["language_probability"]:
                more_confident = "INT16"  
            else:
                more_confident = "TIE"
                
            print(f"🎯 ACCURACY: {more_confident} (higher language confidence)")
            
            print(f"\n🏆 FOR NSIS PACKAGING:")
            print(f"  - File Size: INT8 WINS (smaller)")
            print(f"  - Speed: {faster_model} WINS")
            print(f"  - Memory Usage: INT8 WINS (lower)")
            print(f"  - Distribution: INT8 WINS (easier to distribute)")
            
            if faster_model == "INT8":
                print(f"\n✅ RECOMMENDATION: Use INT8 for optimal packaging")
            else:
                print(f"\n⚖️ RECOMMENDATION: Consider trade-offs - INT8 for size, INT16 for accuracy")
            
            return True
            
        except ImportError:
            print("ERROR: faster-whisper not installed")
            return False
        except Exception as e:
            print(f"ERROR: Comparison test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_int16_vs_int8()
    print(f"\n{'='*80}")
    if success:
        print("INT16 vs INT8 comparison completed successfully!")
    else:
        print("INT16 vs INT8 comparison failed!")
    print(f"{'='*80}")
    sys.exit(0 if success else 1)