#!/usr/bin/env python3
"""
終極時間戳修正器 - 基於市場成功方案的激進解決方案
專門用於修復 Whisper 包含間奏和靜音時間的問題
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def aggressive_timing_fix(srt_content: str) -> str:
    """
    激進的時間戳修正，基於市場成功產品的經驗
    
    專門處理以下問題：
    1. 段落包含間奏時間（如段落12的20s-25s間奏問題）
    2. 時間戳前擴問題
    3. 靜音時間被誤包含
    """
    
    # 解析 SRT 內容
    segments = parse_srt(srt_content)
    if not segments:
        return srt_content
    
    logger.info(f"開始激進時間戳修正，共 {len(segments)} 個段落")
    
    # 分析段落模式，識別異常
    corrected_segments = []
    
    for i, segment in enumerate(segments):
        original_start = segment['start']
        original_end = segment['end']
        duration = original_end - original_start
        text = segment['text'].strip()
        
        # 規則1：檢測異常長的段落（可能包含間奏）
        if duration > 4.0:  # 超過4秒的段落需要檢查
            # 估算正常語音時間（基於字符數）
            char_count = len(text)
            estimated_speech_time = max(1.5, char_count * 0.15)  # 每字符約0.15秒
            
            if duration > estimated_speech_time * 2.5:  # 如果實際時間是估算時間的2.5倍以上
                # 激進修正：縮短段落到合理長度
                new_duration = estimated_speech_time * 1.3  # 加30%緩衝
                new_start = original_end - new_duration
                
                # 確保不會與前一段重疊
                if i > 0:
                    prev_end = corrected_segments[i-1]['end']
                    if new_start < prev_end + 0.3:
                        new_start = prev_end + 0.3
                
                logger.info(f"激進修正段落 {i+1}: '{text[:20]}...' 時間 {original_start:.3f}s -> {new_start:.3f}s (縮短 {original_start - new_start:.3f}s)")
                segment['start'] = new_start
        
        # 規則2：檢測重複內容（如"母親節快到了"出現兩次）
        if i > 0 and text in [s['text'] for s in corrected_segments]:
            # 對於重複內容，確保時間戳緊貼語音
            if duration > 3.0:  # 如果重複內容的段落異常長
                # 向後調整開始時間
                char_count = len(text)
                reasonable_duration = max(1.2, char_count * 0.12)  # 更緊密的時間估算
                new_start = original_end - reasonable_duration
                
                logger.info(f"修正重複內容段落 {i+1}: '{text[:20]}...' 時間 {original_start:.3f}s -> {new_start:.3f}s")
                segment['start'] = new_start
        
        # 規則3：檢測段落間的異常間隙
        if i > 0:
            prev_segment = corrected_segments[i-1]
            gap = segment['start'] - prev_segment['end']
            
            # 如果間隙太大（超過2秒），可能前一段包含了間奏
            if gap > 2.0:
                # 檢查前一段是否可以縮短
                prev_duration = prev_segment['end'] - prev_segment['start']
                prev_char_count = len(prev_segment['text'])
                prev_estimated_time = max(1.2, prev_char_count * 0.12)
                
                if prev_duration > prev_estimated_time * 1.5:
                    # 縮短前一段
                    new_prev_end = prev_segment['start'] + prev_estimated_time * 1.2
                    logger.info(f"縮短前段落以減少間隙: 段落{i} 結束時間 {prev_segment['end']:.3f}s -> {new_prev_end:.3f}s")
                    corrected_segments[i-1]['end'] = new_prev_end
        
        corrected_segments.append(segment)
    
    # 轉換回 SRT 格式
    result = generate_srt(corrected_segments)
    logger.info("激進時間戳修正完成")
    return result

def parse_srt(content: str) -> List[Dict]:
    """解析 SRT 內容為段落列表"""
    segments = []
    pattern = r'(\d+)\s+(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\s+(.+?)(?=\n\n|\n\d+\s+\d{2}:|\Z)'
    
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        index = int(match[0])
        start_time = srt_time_to_seconds(match[1])
        end_time = srt_time_to_seconds(match[2])
        text = match[3].strip().replace('\n', ' ')
        
        segments.append({
            'index': index,
            'start': start_time,
            'end': end_time,
            'text': text
        })
    
    return segments

def srt_time_to_seconds(time_str: str) -> float:
    """將 SRT 時間格式轉換為秒"""
    h, m, s_ms = time_str.split(':')
    s, ms = s_ms.split(',')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

def seconds_to_srt_time(seconds: float) -> str:
    """將秒轉換為 SRT 時間格式"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def generate_srt(segments: List[Dict]) -> str:
    """生成 SRT 內容"""
    result = []
    for seg in segments:
        result.append(str(seg['index']))
        result.append(f"{seconds_to_srt_time(seg['start'])} --> {seconds_to_srt_time(seg['end'])}")
        result.append(seg['text'])
        result.append("")
    
    return '\n'.join(result)

if __name__ == "__main__":
    # 測試用途
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 讀取 SRT 文件
    srt_file = r"C:\Users\USER-ART0\Desktop\DRLIN.srt"
    
    # 如果桌面上沒有，檢查其他位置
    import os
    if not os.path.exists(srt_file):
        # 檢查新增資料夾(2)
        alt_file = r"C:\Users\USER-ART0\Desktop\新增資料夾 (2)\DRLIN.srt"
        if os.path.exists(alt_file):
            srt_file = alt_file
    try:
        with open(srt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 應用修正
        fixed_content = aggressive_timing_fix(content)
        
        # 保存修正結果
        output_file = srt_file.replace('.srt', '_fixed.srt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"修正完成，輸出文件: {output_file}")
        
    except Exception as e:
        print(f"處理失敗: {e}")