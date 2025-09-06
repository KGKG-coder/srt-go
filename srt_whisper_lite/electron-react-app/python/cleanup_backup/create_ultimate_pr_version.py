#!/usr/bin/env python3
"""
創建終極PR兼容版本
解決重疊時間軸，確保完美切片
"""

def create_ultimate_pr_version():
    print("Creating ultimate PR-compatible version...")
    
    # 手動構建所有段落，修正重疊問題
    segments = [
        {"id": 1, "start": 0.110, "end": 0.889, "text": "母親節快到了"},
        {"id": 2, "start": 0.890, "end": 2.909, "text": "也許今年你可以來送點不一樣的"},
        {"id": 3, "start": 2.910, "end": 3.249, "text": "大家好"},
        {"id": 4, "start": 3.250, "end": 5.848, "text": "我是臺北戰前諾貝爾眼科診所院長"},
        {"id": 5, "start": 5.849, "end": 6.668, "text": "林一鴻醫師"},
        {"id": 6, "start": 6.669, "end": 8.948, "text": "我們人當過了40歲以後"},
        {"id": 7, "start": 8.949, "end": 10.928, "text": "我們就會開始產生所謂的老花眼"},
        {"id": 8, "start": 10.929, "end": 13.688, "text": "這個會讓你看近特別的喫力"},
        {"id": 9, "start": 13.689, "end": 15.368, "text": "造成你生活中的不方便"},
        {"id": 10, "start": 15.369, "end": 17.738, "text": "接下來就請大家一起到我的診間"},
        {"id": 11, "start": 17.739, "end": 20.670, "text": "讓我介紹一些老花眼相關的知識給你"},
        
        # 關鍵：第12段已修正，但要避免與第13段重疊
        {"id": 12, "start": 25.370, "end": 26.769, "text": "母親節快到了"},  # 修正時間軸，無重疊
        
        {"id": 13, "start": 26.770, "end": 29.099, "text": "歡迎帶你媽媽來諾貝爾眼科"},
        {"id": 14, "start": 29.100, "end": 30.259, "text": "找我們做諮詢"},
        {"id": 15, "start": 30.260, "end": 33.139, "text": "看看你媽媽適不適合做近視跟老花"},
        {"id": 16, "start": 33.140, "end": 35.019, "text": "一起處理的這種老花蕾色"},
        {"id": 17, "start": 35.020, "end": 38.479, "text": "讓我們給你媽媽一個清晰方便的視力"}
    ]
    
    print("\\n=== 檢查時間軸連續性 ===")
    
    # 檢查並報告任何問題
    for i in range(len(segments) - 1):
        curr = segments[i]
        next_seg = segments[i + 1]
        gap = next_seg['start'] - curr['end']
        
        if gap < 0:
            print(f"段落{curr['id']}-{next_seg['id']}: 重疊 {abs(gap):.3f}s")
        elif gap == 0:
            print(f"段落{curr['id']}-{next_seg['id']}: 無縫連接")
        elif gap > 5:
            print(f"段落{curr['id']}-{next_seg['id']}: 自然間隔 {gap:.3f}s")
        else:
            print(f"段落{curr['id']}-{next_seg['id']}: 正常間隔 {gap:.3f}s")
    
    def format_timestamp(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    # 生成標準SRT格式
    srt_lines = []
    
    for seg in segments:
        start_time = format_timestamp(seg['start'])
        end_time = format_timestamp(seg['end'])
        
        srt_lines.append(str(seg['id']))
        srt_lines.append(f"{start_time} --> {end_time}")
        srt_lines.append(seg['text'])
        srt_lines.append("")  # 空行分隔
    
    # 移除最後的空行
    if srt_lines and srt_lines[-1] == "":
        srt_lines.pop()
    
    # Windows CRLF格式
    srt_content = "\\r\\n".join(srt_lines) + "\\r\\n"
    
    output_file = "C:/Users/USER-ART0/Desktop/DRLIN_ULTIMATE_PR.srt"
    
    try:
        # 二進制寫入確保格式
        with open(output_file, 'wb') as f:
            f.write(srt_content.encode('utf-8'))
        
        print(f"\\n✅ 終極PR版本完成: {output_file}")
        print("特色:")
        print("  - 零重疊時間軸")
        print("  - 第12段語音對齊 (25.370s)")
        print("  - 完美CRLF格式")
        print("  - 17個獨立段落")
        
        # 驗證
        verify_ultimate_version(output_file)
        
    except Exception as e:
        print(f"ERROR: {e}")

def verify_ultimate_version(filename):
    """驗證終極版本"""
    try:
        with open(filename, 'rb') as f:
            raw_data = f.read()
        
        content = raw_data.decode('utf-8')
        
        print(f"\\n驗證結果:")
        print(f"  - 文件大小: {len(raw_data)} bytes")
        crlf_bytes = b'\r\n'
        correct_crlf = crlf_bytes in raw_data and raw_data.endswith(crlf_bytes)
        print(f"  - 正確CRLF: {correct_crlf}")
        print(f"  - 段落數量: {content.count('-->')}")
        
        # 檢查第12段
        if '00:00:25,370' in content:
            print("  - 第12段修正: 25.370s ✓")
        
        # 檢查重疊
        lines = content.splitlines()
        times = []
        for line in lines:
            if '-->' in line:
                start_str, end_str = line.split(' --> ')
                times.append((start_str, end_str))
        
        overlaps = 0
        for i in range(len(times) - 1):
            curr_end = times[i][1]
            next_start = times[i + 1][0]
            if curr_end > next_start:
                overlaps += 1
        
        print(f"  - 重疊段落: {overlaps} (應為0)")
        print(f"  - PR兼容性: {'✓' if overlaps == 0 else '✗'}")
        
    except Exception as e:
        print(f"驗證失敗: {e}")

if __name__ == "__main__":
    create_ultimate_pr_version()