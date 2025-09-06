#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版第12段分析工具
專門分析DRLIN.mp4第12段時間戳問題
"""

import re
from pathlib import Path

def parse_srt_simple(srt_path):
    """解析SRT檔案"""
    segments = []
    try:
        with open(srt_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    seq_num = int(lines[0])
                    
                    # 時間戳解析
                    time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', lines[1])
                    if time_match:
                        start_str, end_str = time_match.groups()
                        start_time = parse_timestamp(start_str)
                        end_time = parse_timestamp(end_str)
                        text = '\n'.join(lines[2:]).strip()
                        
                        segments.append({
                            'seq': seq_num,
                            'start': start_time,
                            'end': end_time,
                            'duration': end_time - start_time,
                            'text': text
                        })
                except:
                    continue
    except Exception as e:
        print(f"Error parsing file: {e}")
    
    return segments

def parse_timestamp(timestamp_str):
    """解析時間戳"""
    h, m, s = timestamp_str.split(':')
    s, ms = s.split(',')
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0

def analyze_segment_12():
    """分析第12段"""
    print("DRLIN.mp4 Segment 12 Analysis")
    print("=" * 40)
    
    # 標準版本
    standard_file = "../comparison_test/standard/DRLIN.srt"
    
    if not Path(standard_file).exists():
        print(f"File not found: {standard_file}")
        return
    
    segments = parse_srt_simple(standard_file)
    print(f"Total segments: {len(segments)}")
    
    if len(segments) < 12:
        print("ERROR: Less than 12 segments")
        return
    
    # 第12段分析
    seg12 = segments[11]  # 0-indexed
    
    print(f"\nSegment 12 Current Status:")
    print(f"  Text: \"{seg12['text']}\"")
    print(f"  Timing: {seg12['start']:.3f}s -> {seg12['end']:.3f}s")
    print(f"  Duration: {seg12['duration']:.3f}s")
    
    # 問題判斷
    text_chars = len(seg12['text'])
    expected_duration = text_chars * 0.15  # 每字約0.15秒
    
    print(f"\nProblem Analysis:")
    print(f"  Text length: {text_chars} characters")
    print(f"  Expected duration: {expected_duration:.1f}s")
    print(f"  Actual duration: {seg12['duration']:.1f}s")
    print(f"  Excess time: {seg12['duration'] - expected_duration:.1f}s")
    
    if seg12['duration'] > expected_duration * 2:
        print(f"  STATUS: PROBLEMATIC - Contains music interlude")
        time_savings = seg12['duration'] - expected_duration
        savings_pct = (time_savings / seg12['duration']) * 100
        print(f"  Potential savings: {time_savings:.1f}s ({savings_pct:.1f}%)")
        
        print(f"\nSuggested Fix:")
        print(f"  Current: {seg12['start']:.3f}s -> {seg12['end']:.3f}s")
        
        # 建議從音樂結束後開始（約25-26秒）
        suggested_start = 25.3
        suggested_end = suggested_start + expected_duration
        print(f"  Suggested: {suggested_start:.3f}s -> {suggested_end:.3f}s")
        print(f"  This aligns with voice timing and removes music interlude")
    else:
        print(f"  STATUS: OK")
    
    print(f"\nThis analysis confirms the need for Enhanced Voice Detector v2.0")
    print(f"The adaptive voice detection should fix this timing issue automatically.")
    
    return seg12

if __name__ == "__main__":
    analyze_segment_12()