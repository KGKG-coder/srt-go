#!/usr/bin/env python3
"""
Test scenarios where INT8 vs FP16 might show real differences
Focus on challenging audio conditions
"""

import sys
import logging
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_real_differences():
    """Test scenarios where precision differences matter"""
    try:
        print("=" * 80)
        print("Real Difference Analysis - INT8 vs FP16")
        print("=" * 80)
        
        test_video_dir = Path("H:/字幕程式設計環境/test_video")
        if not test_video_dir.exists():
            print(f"ERROR: Test video directory not found")
            return False
        
        video_files = list(test_video_dir.glob("*.mp4"))
        if not video_files:
            print("ERROR: No video files found")
            return False
        
        # Select test video
        test_video = video_files[0]  # Use first available
        print(f"Test video: {test_video.name}")
        
        try:
            from faster_whisper import WhisperModel
            
            results = {}
            precisions = ["int8", "int16"]
            
            for precision in precisions:
                print(f"\n{'='*60}")
                print(f"Testing with {precision.upper()}")
                print(f"{'='*60}")
                
                start_time = time.time()
                model = WhisperModel(
                    "large-v3",
                    device="cpu",
                    compute_type=precision
                )
                load_time = time.time() - start_time
                
                # Test with different settings to reveal differences
                print(f"Running detailed transcription...")
                start_time = time.time()
                
                segments, info = model.transcribe(
                    str(test_video),
                    language="zh",
                    task="transcribe",
                    beam_size=8,  # Higher for more accuracy
                    best_of=8,    # Higher for more accuracy
                    temperature=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5],  # More temperature steps
                    word_timestamps=True,  # Enable word-level timestamps
                    vad_filter=True,      # Voice activity detection
                    vad_parameters=dict(min_silence_duration_ms=500)
                )
                
                transcribe_time = time.time() - start_time
                segment_list = list(segments)
                
                # Analyze results in detail
                results[precision] = {
                    "load_time": load_time,
                    "transcribe_time": transcribe_time,
                    "segments": segment_list,
                    "language_prob": info.language_probability,
                    "duration": info.duration
                }
                
                print(f"Load time: {load_time:.1f}s")
                print(f"Transcribe time: {transcribe_time:.1f}s")
                print(f"Language confidence: {info.language_probability:.3f}")
                print(f"Total segments: {len(segment_list)}")
                
                # Analyze timing precision
                if segment_list:
                    timing_precision = []
                    for i, segment in enumerate(segment_list[:5]):
                        duration = segment.end - segment.start
                        timing_precision.append(duration)
                        print(f"  Segment {i+1}: [{segment.start:.3f} -> {segment.end:.3f}] ({duration:.3f}s) {segment.text[:30]}...")
                    
                    avg_precision = sum(timing_precision) / len(timing_precision)
                    results[precision]["avg_segment_duration"] = avg_precision
                    results[precision]["timing_precision"] = timing_precision
                
                del model  # Free memory
            
            # Detailed comparison
            print(f"\n{'='*80}")
            print("DETAILED DIFFERENCE ANALYSIS")
            print(f"{'='*80}")
            
            int8_result = results["int8"]
            fp16_result = results["int16"]
            
            # 1. Language Confidence Difference
            conf_diff = fp16_result["language_prob"] - int8_result["language_prob"]
            print(f"\n1. LANGUAGE CONFIDENCE:")
            print(f"   INT8 : {int8_result['language_prob']:.5f}")
            print(f"   INT16: {fp16_result['language_prob']:.5f}")
            print(f"   Diff : {conf_diff:+.5f}")
            if abs(conf_diff) > 0.001:
                print(f"   Impact: Noticeable confidence difference")
            else:
                print(f"   Impact: Negligible confidence difference")
            
            # 2. Segment Count Difference
            seg_diff = len(fp16_result["segments"]) - len(int8_result["segments"])
            print(f"\n2. SEGMENT SEGMENTATION:")
            print(f"   INT8 segments : {len(int8_result['segments'])}")
            print(f"   INT16 segments: {len(fp16_result['segments'])}")
            print(f"   Difference    : {seg_diff:+d}")
            if abs(seg_diff) > 0:
                print(f"   Impact: Different speech segmentation")
            else:
                print(f"   Impact: Identical segmentation")
            
            # 3. Timing Precision Difference
            if "avg_segment_duration" in int8_result and "avg_segment_duration" in fp16_result:
                timing_diff = fp16_result["avg_segment_duration"] - int8_result["avg_segment_duration"]
                print(f"\n3. TIMING PRECISION:")
                print(f"   INT8 avg duration: {int8_result['avg_segment_duration']:.3f}s")
                print(f"   INT16 avg duration: {fp16_result['avg_segment_duration']:.3f}s")
                print(f"   Difference       : {timing_diff:+.3f}s")
                if abs(timing_diff) > 0.1:
                    print(f"   Impact: Significant timing difference")
                else:
                    print(f"   Impact: Minor timing difference")
            
            # 4. Text Content Comparison
            print(f"\n4. TEXT CONTENT COMPARISON:")
            min_segments = min(len(int8_result["segments"]), len(fp16_result["segments"]))
            different_texts = 0
            
            for i in range(min(5, min_segments)):
                int8_text = int8_result["segments"][i].text.strip()
                int16_text = fp16_result["segments"][i].text.strip()
                
                if int8_text != int16_text:
                    different_texts += 1
                    print(f"   Segment {i+1} DIFFERS:")
                    print(f"     INT8 : {int8_text}")
                    print(f"     INT16: {int16_text}")
                else:
                    print(f"   Segment {i+1}: IDENTICAL")
            
            if different_texts > 0:
                print(f"   Impact: {different_texts}/{min(5, min_segments)} segments differ")
            else:
                print(f"   Impact: All compared segments identical")
            
            # 5. Performance vs Quality Trade-off
            speed_diff = ((fp16_result["transcribe_time"] - int8_result["transcribe_time"]) / int8_result["transcribe_time"] * 100)
            
            print(f"\n5. PERFORMANCE vs QUALITY TRADE-OFF:")
            print(f"   Speed difference: INT16 is {speed_diff:+.1f}% slower than INT8")
            print(f"   Quality gain    : {different_texts} text differences found")
            
            if different_texts == 0 and abs(conf_diff) < 0.001:
                print(f"   Verdict: NO MEANINGFUL QUALITY DIFFERENCE")
                print(f"   Recommendation: Use INT8 for better performance")
            elif different_texts > 0:
                print(f"   Verdict: QUALITY DIFFERENCES DETECTED")
                print(f"   Recommendation: Consider INT16 for critical applications")
            else:
                print(f"   Verdict: MARGINAL QUALITY DIFFERENCES")
                print(f"   Recommendation: INT8 sufficient for most use cases")
            
            print(f"\n{'='*80}")
            print("WHEN TO USE EACH PRECISION")
            print(f"{'='*80}")
            
            print(f"\nUse INT8 when:")
            print(f"  - File size matters (NSIS packaging)")
            print(f"  - Processing speed is critical")
            print(f"  - Memory is limited")
            print(f"  - Audio quality is good")
            print(f"  - Single language content")
            
            print(f"\nUse INT16 when:")
            print(f"  - Maximum accuracy is required")
            print(f"  - Poor audio quality")
            print(f"  - Multi-language content")
            print(f"  - Professional/critical applications")
            print(f"  - Subtle speech patterns matter")
            
            print(f"\nFor your NSIS packaging use case:")
            if different_texts == 0:
                print(f"  ✅ INT8 is PERFECT - no quality loss detected")
            else:
                print(f"  ⚖️ Consider trade-offs - {different_texts} differences found")
            
            return True
            
        except ImportError:
            print("ERROR: faster-whisper not installed")
            return False
        except Exception as e:
            print(f"ERROR: Difference analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_real_differences()
    print(f"\n{'='*80}")
    if success:
        print("Real difference analysis completed!")
    else:
        print("Real difference analysis failed!")
    print(f"{'='*80}")
    sys.exit(0 if success else 1)