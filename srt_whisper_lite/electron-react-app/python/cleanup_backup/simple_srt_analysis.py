#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
簡化的SRT分析工具
專注於第12段問題分析
"""

import re
from pathlib import Path
import json

def parse_srt_simple(srt_path: str):
    """簡化的SRT解析"""
    segments = []
    try:
        content = Path(srt_path).read_text(encoding='utf-8-sig')
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    seq_num = int(lines[0])
                    
                    # 時間戳
                    time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', lines[1])
                    if time_match:
                        start_str, end_str = time_match.groups()
                        
                        # 解析時間
                        start_time = parse_time(start_str)
                        end_time = parse_time(end_str)
                        
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
        print(f"Parse error: {e}")
    
    return segments

def parse_time(time_str):
    """解析時間字符串"""
    try:
        h, m, s = time_str.split(':')
        s, ms = s.split(',')
        return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0
    except:
        return 0.0

def analyze_segment_12():
    """重點分析第12段問題"""
    print("DRLIN.mp4 Segment 12 Analysis")
    print("=" * 40)
    
    srt_file = "comparison_test/standard/DRLIN.srt"
    
    if not Path(srt_file).exists():
        print(f"File not found: {srt_file}")
        return
    
    segments = parse_srt_simple(srt_file)
    
    print(f"Total segments found: {len(segments)}")
    
    if len(segments) < 12:
        print("ERROR: Less than 12 segments found")
        return
    
    # 分析第12段
    seg12 = segments[11]  # 第12段 (0-indexed)
    
    print()
    print("Segment 12 Details:")
    print(f"  Text: \"{seg12['text']}\"")
    print(f"  Start: {seg12['start']:.3f}s")
    print(f"  End: {seg12['end']:.3f}s")
    print(f"  Duration: {seg12['duration']:.3f}s")
    print(f"  Text length: {len(seg12['text'])} characters")
    
    # 問題檢測
    expected_duration = len(seg12['text']) * 0.15  # 每字約0.15秒
    
    print()
    print("Issue Analysis:")
    print(f"  Expected duration: {expected_duration:.1f}s")
    print(f"  Actual duration: {seg12['duration']:.1f}s")
    print(f"  Excess time: {seg12['duration'] - expected_duration:.1f}s")
    
    if seg12['duration'] > expected_duration * 2:
        print("  STATUS: PROBLEMATIC - Contains music interlude")
        improvement_needed = True
    else:
        print("  STATUS: Normal")
        improvement_needed = False
    
    # 周圍段落分析
    print()
    print("Context Analysis (Segments 10-14):")
    for i in range(9, min(14, len(segments))):
        seg = segments[i]
        status = "PROBLEM" if i == 11 and improvement_needed else "OK"
        print(f"  Seg {seg['seq']:2d}: {seg['start']:6.1f}s-{seg['end']:6.1f}s ({seg['duration']:4.1f}s) [{status}] \"{seg['text'][:20]}...\"")
    
    # 建議修正
    if improvement_needed:
        print()
        print("Suggested Fix:")
        print(f"  Current: {seg12['start']:.3f}s -> {seg12['end']:.3f}s")
        
        # 建議的修正時間：從第11段結束後開始
        if len(segments) >= 11:
            prev_end = segments[10]['end']  # 第11段結束時間
            suggested_start = prev_end + 0.1  # 小間隔
            suggested_end = suggested_start + expected_duration
            
            print(f"  Suggested: {suggested_start:.3f}s -> {suggested_end:.3f}s")
            print(f"  Time saved: {seg12['duration'] - expected_duration:.1f}s ({((seg12['duration'] - expected_duration)/seg12['duration']*100):.1f}%)")
    
    # 生成對比數據
    analysis_data = {
        'segment_12_current': {
            'text': seg12['text'],
            'start': seg12['start'],
            'end': seg12['end'],
            'duration': seg12['duration']
        },
        'is_problematic': improvement_needed,
        'expected_duration': expected_duration,
        'excess_time': seg12['duration'] - expected_duration,
        'improvement_percentage': ((seg12['duration'] - expected_duration)/seg12['duration']*100) if improvement_needed else 0
    }
    
    # 保存結果
    with open('segment_12_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    
    print()
    print("Analysis saved to: segment_12_analysis.json")
    
    return analysis_data

if __name__ == "__main__":
    analyze_segment_12()