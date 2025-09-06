#!/usr/bin/env python3
"""
檢查 SRT 字幕文件的段落間隙
"""

import re
from pathlib import Path

def parse_srt(file_path):
    """解析 SRT 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    segments = []
    lines = content.strip().split('\n')
    current_segment = {}
    
    for line in lines:
        line = line.strip()
        if re.match(r'^\d+$', line):
            if current_segment:
                segments.append(current_segment)
            current_segment = {'id': int(line)}
        elif '-->' in line:
            start_str, end_str = line.split(' --> ')
            def parse_time(time_str):
                h, m, s = time_str.split(':')
                s, ms = s.split(',')
                return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0
            current_segment['start'] = parse_time(start_str)
            current_segment['end'] = parse_time(end_str)
        elif line and 'start' in current_segment and 'text' not in current_segment:
            current_segment['text'] = line
    
    if current_segment:
        segments.append(current_segment)
    
    return segments

def analyze_gaps(segments):
    """分析段落間隙"""
    print(f"分析 {len(segments)} 個段落的間隙:")
    print("-" * 60)
    
    overlaps = []
    small_gaps = []  # < 0.05秒
    perfect_gaps = []  # 0.008-0.012秒
    
    for i in range(len(segments) - 1):
        current = segments[i]
        next_seg = segments[i + 1]
        
        gap = next_seg['start'] - current['end']
        
        # 特別關注第11和第12段
        if i == 10:  # 第11段（索引10）
            print(f"\n[TARGET] 第11-12段重點分析:")
            print(f"   第11段: {current['start']:.3f}s -> {current['end']:.3f}s")
            print(f"   第12段: {next_seg['start']:.3f}s -> {next_seg['end']:.3f}s")
            print(f"   間隙: {gap:.3f}s")
            print(f"   第11段文本: {current['text'][:30]}...")
            print(f"   第12段文本: {next_seg['text']}")
            print()
        
        if gap < 0:
            overlaps.append((i+1, i+2, gap))
            print(f"[X] 重疊: 段落{i+1} 結束({current['end']:.3f}s) > 段落{i+2} 開始({next_seg['start']:.3f}s), 重疊{-gap:.3f}s")
        elif gap < 0.05:
            small_gaps.append((i+1, i+2, gap))
            if 0.008 <= gap <= 0.012:
                perfect_gaps.append((i+1, i+2, gap))
                print(f"[OK] 理想間隙: 段落{i+1}-{i+2}: {gap:.3f}s")
            else:
                print(f"[!] 小間隙: 段落{i+1}-{i+2}: {gap:.3f}s")
        else:
            print(f"   正常間隙: 段落{i+1}-{i+2}: {gap:.3f}s")
    
    print("\n" + "=" * 60)
    print("[STATS] 統計結果:")
    print(f"   重疊段落: {len(overlaps)} 個")
    print(f"   小間隙(<0.05s): {len(small_gaps)} 個")
    print(f"   理想間隙(~0.01s): {len(perfect_gaps)} 個")
    
    if overlaps:
        print("\n[WARNING] 重疊段落詳情:")
        for seg1, seg2, gap in overlaps:
            print(f"   段落{seg1}-{seg2}: 重疊{-gap:.3f}s")
    
    # 檢查第12段時間戳
    if len(segments) > 11:
        seg12 = segments[11]
        print(f"\n[TARGET] 第12段最終檢查:")
        print(f"   時間戳: {seg12['start']:.3f}s -> {seg12['end']:.3f}s")
        print(f"   文本: {seg12['text']}")
        
        if seg12['start'] >= 25.0:
            print("   [OK] 第12段時間戳已正確修正到語音位置！")
        else:
            print(f"   [X] 第12段時間戳仍有問題 (應該 >= 25.0s)")
    
    return len(overlaps) == 0

def main():
    # 檢查最新生成的字幕
    srt_path = Path("C:/Users/USER-ART0/Desktop/test_drlin_large/DRLIN.srt")
    
    if not srt_path.exists():
        print(f"文件不存在: {srt_path}")
        return
    
    print(f"檢查字幕文件: {srt_path}")
    print("=" * 60)
    
    segments = parse_srt(srt_path)
    no_overlaps = analyze_gaps(segments)
    
    print("\n" + "=" * 60)
    if no_overlaps:
        print("[SUCCESS] 所有段落間隙正常，無重疊！")
        print("字幕可以在 Premiere Pro 中正確切片。")
    else:
        print("[WARNING] 存在重疊段落，需要進一步優化。")

if __name__ == "__main__":
    main()