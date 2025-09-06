#!/usr/bin/env python3
"""
Analyze the comparison results from previous test
"""

import sys

def analyze_results():
    """Analyze INT16 vs INT8 results"""
    
    print("=" * 80)
    print("INT16 vs INT8 COMPARISON RESULTS")
    print("=" * 80)
    
    # Data from the test output
    int8_data = {
        "load_time": 4.3,
        "transcribe_time": 10.3,
        "speed_ratio": 1.1,
        "language_prob": 1.00,
        "segments": 12,
        "srt_size": 606
    }
    
    int16_data = {
        "load_time": 4.7,
        "transcribe_time": 13.4,
        "speed_ratio": 0.8,
        "language_prob": 1.00,
        "segments": 12,
        "srt_size": 606
    }
    
    print("\nPERFORMANCE COMPARISON:")
    print("Metric               INT8           INT16          Difference")
    print("-" * 70)
    
    # Load time comparison
    load_diff = ((int16_data["load_time"] - int8_data["load_time"]) / int8_data["load_time"] * 100)
    print(f"Load Time            {int8_data['load_time']:<15.1f}{int16_data['load_time']:<15.1f}{load_diff:>+6.1f}%")
    
    # Transcribe time comparison
    transcribe_diff = ((int16_data["transcribe_time"] - int8_data["transcribe_time"]) / int8_data["transcribe_time"] * 100)
    print(f"Transcribe Time      {int8_data['transcribe_time']:<15.1f}{int16_data['transcribe_time']:<15.1f}{transcribe_diff:>+6.1f}%")
    
    # Speed ratio comparison
    speed_diff = ((int16_data["speed_ratio"] - int8_data["speed_ratio"]) / int8_data["speed_ratio"] * 100)
    print(f"Speed Ratio          {int8_data['speed_ratio']:<15.1f}{int16_data['speed_ratio']:<15.1f}{speed_diff:>+6.1f}%")
    
    print("\nACCURACY COMPARISON:")
    print("Metric               INT8           INT16          Difference")
    print("-" * 70)
    
    # Language confidence (both 100%)
    lang_diff = int16_data["language_prob"] - int8_data["language_prob"]
    print(f"Language Confidence  {int8_data['language_prob']:<15.0%}{int16_data['language_prob']:<15.0%}      {lang_diff:+.0%}")
    
    # Segment count
    seg_diff = int16_data["segments"] - int8_data["segments"]
    print(f"Segment Count        {int8_data['segments']:<15}{int16_data['segments']:<15}      {seg_diff:+d}")
    
    # File size
    size_diff = int16_data["srt_size"] - int8_data["srt_size"]
    print(f"SRT Size (bytes)     {int8_data['srt_size']:<15}{int16_data['srt_size']:<15}      {size_diff:+d}")
    
    print("\nTEXT QUALITY ANALYSIS:")
    print("Based on the output samples:")
    print("INT8 : [0.00s -> 0.80s] (text content)")
    print("INT16: [0.00s -> 0.84s] (text content)")
    print("Result: Timing slightly different, text identical")
    
    print("\nMODEL SIZE COMPARISON:")
    print("INT8  Model: ~800MB - 1GB")
    print("INT16 Model: ~1.5GB - 2GB")  
    print("Size Ratio: INT16 is ~2x larger than INT8")
    
    print("\nKEY FINDINGS:")
    print("=" * 60)
    print("1. SPEED PERFORMANCE:")
    print(f"   - INT8 is {abs(transcribe_diff):.1f}% FASTER than INT16")
    print(f"   - INT8: {int8_data['speed_ratio']:.1f}x real-time")
    print(f"   - INT16: {int16_data['speed_ratio']:.1f}x real-time")
    
    print("\n2. LOAD TIME:")
    print(f"   - INT8 loads {abs(load_diff):.1f}% faster")
    print(f"   - Both load in under 5 seconds")
    
    print("\n3. ACCURACY:")
    print("   - Both achieve 100% language detection confidence")
    print("   - Same number of segments (12)")
    print("   - Identical text content")
    print("   - Only minor timing differences")
    
    print("\n4. FILE SIZE:")
    print("   - Output SRT files identical (606 bytes)")
    print("   - Model files: INT16 ~2x larger than INT8")
    
    print("\nRECOMMENDATIONS:")
    print("=" * 60)
    
    print("\nFor NSIS PACKAGING:")
    print("Winner: INT8")
    print("Reasons:")
    print("  + 30% faster transcription")
    print("  + 9% faster loading")
    print("  + 50% smaller model size")
    print("  + Lower memory usage")
    print("  + Easier distribution")
    print("  = Same accuracy")
    
    print("\nFor MAXIMUM ACCURACY:")
    print("Winner: TIE (both identical)")
    print("  - Both achieve 100% language confidence")
    print("  - Identical text output")
    print("  - No meaningful accuracy difference")
    
    print("\nFor RESOURCE-CONSTRAINED ENVIRONMENTS:")
    print("Winner: INT8")
    print("  + Less RAM usage")
    print("  + Faster processing")
    print("  + Smaller storage requirement")
    
    print("\nFINAL VERDICT:")
    print("=" * 60)
    print("RECOMMENDED: INT8")
    print("")
    print("Why INT8 is better for your use case:")
    print("1. Significantly faster (30% speed improvement)")
    print("2. Much smaller model size (50% reduction)")
    print("3. Same accuracy as INT16")
    print("4. Perfect for NSIS packaging")
    print("5. Better user experience (faster loading/processing)")
    print("")
    print("INT16 offers no meaningful advantages over INT8")
    print("for Chinese subtitle generation.")
    
    return True

if __name__ == "__main__":
    success = analyze_results()
    print(f"\n{'='*80}")
    if success:
        print("Comparison analysis completed!")
    print(f"{'='*80}")
    sys.exit(0 if success else 1)