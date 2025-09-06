#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
直接SRT檔案對比分析工具
分析現有的字幕檔差異
"""

import re
from pathlib import Path
from typing import List, Dict
import json

def parse_srt_file(srt_path: str) -> List[Dict]:
    """解析SRT檔案"""
    segments = []
    try:
        content = Path(srt_path).read_text(encoding='utf-8-sig')  # 處理BOM
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    seq_num = int(lines[0])
                    
                    # 解析時間戳
                    time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', lines[1])
                    if time_match:
                        start_time = parse_timestamp(time_match.group(1))
                        end_time = parse_timestamp(time_match.group(2))
                        
                        # 文本內容
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
        print(f"Error parsing {srt_path}: {e}")
    
    return segments

def parse_timestamp(timestamp_str: str) -> float:
    """解析時間戳為秒數"""
    try:
        parts = timestamp_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds_parts = parts[2].split(',')
        seconds = int(seconds_parts[0])
        milliseconds = int(seconds_parts[1])
        
        return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
    except:
        return 0.0

def analyze_current_subtitle():
    """分析現有的字幕檔"""
    print("Direct SRT File Comparison Analysis")
    print("=" * 50)
    
    # 分析標準版本字幕檔
    standard_srt = "../comparison_test/standard/DRLIN.srt"
    
    if not Path(standard_srt).exists():
        print(f"Standard file not found: {standard_srt}")
        return
    
    segments = parse_srt_file(standard_srt)
    
    print(f"Analyzing: {standard_srt}")
    print(f"Total segments: {len(segments)}")
    print()
    
    # 詳細分析每個段落
    print("Detailed Segment Analysis:")
    print("-" * 40)
    
    total_duration = 0
    problematic_segments = []
    
    for i, seg in enumerate(segments):
        duration = seg['duration']
        total_duration += duration
        
        print(f"Segment {seg['seq']:2d}: {seg['start']:7.3f}s → {seg['end']:7.3f}s ({duration:5.3f}s)")
        print(f"             Text: \"{seg['text']}\"")
        
        # 識別問題段落
        text_length = len(seg['text'])
        words_per_second = text_length / duration if duration > 0 else 0
        
        # 檢測可能的問題
        issues = []
        if duration > 5.0 and text_length < 10:  # 長時間但文本很短
            issues.append(f"Long duration ({duration:.1f}s) with short text")
        if duration > 3.0 and words_per_second < 2:  # 語速太慢
            issues.append(f"Very slow speech rate ({words_per_second:.1f} chars/s)")
        if text_length < 5 and duration > 2.0:  # 極短文本但時間較長
            issues.append("Suspiciously short text for duration")
        
        if issues:
            problematic_segments.append({
                'segment': seg['seq'],
                'text': seg['text'],
                'duration': duration,
                'start': seg['start'],
                'end': seg['end'],
                'issues': issues
            })
            print(f"             ⚠️ Issues: {'; '.join(issues)}")
        
        print()
    
    print("Summary Analysis:")
    print("=" * 30)
    print(f"Total segments: {len(segments)}")
    print(f"Total duration: {total_duration:.3f}s")
    print(f"Average segment length: {total_duration/len(segments):.3f}s")
    print(f"Problematic segments: {len(problematic_segments)}")
    
    print()
    print("Problematic Segments Details:")
    print("-" * 35)
    
    for prob_seg in problematic_segments:
        print(f"Segment {prob_seg['segment']}: \"{prob_seg['text']}\"")
        print(f"  Timing: {prob_seg['start']:.3f}s → {prob_seg['end']:.3f}s ({prob_seg['duration']:.3f}s)")
        print(f"  Issues: {', '.join(prob_seg['issues'])}")
        print()
    
    # 特別關注第12段
    if len(segments) >= 12:
        seg12 = segments[11]  # 第12段 (0-indexed)
        print("Focus: Segment 12 Analysis (Known Issue)")
        print("-" * 40)
        print(f"Text: \"{seg12['text']}\"")
        print(f"Timing: {seg12['start']:.3f}s → {seg12['end']:.3f}s")
        print(f"Duration: {seg12['duration']:.3f}s")
        print(f"Text length: {len(seg12['text'])} characters")
        print(f"Characters per second: {len(seg12['text'])/seg12['duration']:.2f}")
        
        if seg12['duration'] > 4.0:
            print("❌ ISSUE CONFIRMED: Segment 12 has excessive duration")
            print("   This segment likely contains music interlude")
            print("   Expected duration for this text: ~1.5-2.0 seconds")
            expected_duration = len(seg12['text']) * 0.15  # 約每字0.15秒
            time_savings = seg12['duration'] - expected_duration
            print(f"   Potential time savings: {time_savings:.1f}s ({time_savings/seg12['duration']*100:.1f}%)")
        else:
            print("✅ Segment 12 appears normal")
    
    # 保存分析結果
    analysis_result = {
        'file_analyzed': standard_srt,
        'total_segments': len(segments),
        'total_duration': total_duration,
        'average_duration': total_duration/len(segments) if segments else 0,
        'problematic_segments_count': len(problematic_segments),
        'problematic_segments': problematic_segments,
        'segment_12_analysis': {
            'text': segments[11]['text'] if len(segments) >= 12 else None,
            'duration': segments[11]['duration'] if len(segments) >= 12 else None,
            'start': segments[11]['start'] if len(segments) >= 12 else None,
            'end': segments[11]['end'] if len(segments) >= 12 else None,
            'is_problematic': segments[11]['duration'] > 4.0 if len(segments) >= 12 else False
        }
    }
    
    # 保存分析結果
    with open('srt_analysis_result.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, indent=2, ensure_ascii=False)
    
    print(f"\nAnalysis results saved to: srt_analysis_result.json")
    return analysis_result

if __name__ == "__main__":
    analyze_current_subtitle()