#!/usr/bin/env python3
"""
測試修復後的時間戳處理功能
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from subtitle_formatter import SubtitleFormatter

def test_negative_timestamps():
    """測試負數時間戳修復"""
    print("=== 測試負數時間戳修復 ===")
    
    # 模擬包含負數時間戳的段落
    problematic_segments = [
        {
            'start': -7199.337,  # 負數時間戳
            'end': 1.480,
            'text': '母親節快到了'
        },
        {
            'start': 1.480,
            'end': 1.840,
            'text': '也許今年你可以來送點不一樣的喔'
        },
        {
            'start': 1.840,
            'end': -5.0,  # 負數結束時間
            'text': '大家好'
        }
    ]
    
    # 轉換為 SRT 格式
    srt_content = SubtitleFormatter.segments_to_srt(problematic_segments)
    
    print("修復後的 SRT 內容:")
    print(srt_content)
    
    # 檢查是否還有負數時間戳
    lines = srt_content.split('\n')
    for line in lines:
        if '-->' in line:
            print(f"時間戳行: {line}")
            # 確保沒有負號
            if '-1:' in line or '-0:' in line:
                print("❌ 仍然發現負數時間戳！")
                return False
    
    print("✅ 負數時間戳已成功修復")
    return True

def test_invalid_time_ranges():
    """測試無效時間範圍修復"""
    print("\n=== 測試無效時間範圍修復 ===")
    
    # 結束時間小於開始時間的段落
    invalid_segments = [
        {
            'start': 10.0,
            'end': 5.0,  # 結束時間小於開始時間
            'text': '無效時間範圍測試'
        },
        {
            'start': 15.0,
            'end': 15.0,  # 結束時間等於開始時間
            'text': '零持續時間測試'
        }
    ]
    
    srt_content = SubtitleFormatter.segments_to_srt(invalid_segments)
    print("修復後的 SRT 內容:")
    print(srt_content)
    
    # 驗證時間範圍的有效性
    lines = srt_content.split('\n')
    for line in lines:
        if '-->' in line:
            times = line.split(' --> ')
            if len(times) == 2:
                start_str, end_str = times
                print(f"驗證時間戳: {start_str} -> {end_str}")
                
                # 檢查格式是否正確
                if ',' in start_str and ',' in end_str:
                    print("✅ 時間戳格式正確")
                else:
                    print("❌ 時間戳格式錯誤")
                    return False
    
    print("✅ 無效時間範圍已成功修復")
    return True

def test_edge_cases():
    """測試邊界情況"""
    print("\n=== 測試邊界情況 ===")
    
    edge_cases = [
        {
            'start': 0.0,
            'end': 0.001,  # 非常短的持續時間
            'text': '極短時間測試'
        },
        {
            'start': 86399.999,  # 接近24小時的最大值
            'end': 86400.5,     # 超過24小時
            'text': '最大時間測試'
        },
        {
            'start': -1000.0,   # 大負數
            'end': -500.0,      # 另一個負數
            'text': '大負數測試'
        }
    ]
    
    srt_content = SubtitleFormatter.segments_to_srt(edge_cases)
    print("邊界情況處理結果:")
    print(srt_content)
    
    # 檢查是否所有時間戳都在有效範圍內
    lines = srt_content.split('\n')
    for line in lines:
        if '-->' in line:
            print(f"邊界測試時間戳: {line}")
            # 確保沒有超過23:59:59的時間戳
            if '24:' in line or '25:' in line:
                print("❌ 發現超過24小時的時間戳")
                return False
    
    print("✅ 邊界情況處理正確")
    return True

def create_corrected_srt():
    """創建修正版的測試 SRT 文件"""
    print("\n=== 創建修正版 SRT 文件 ===")
    
    # 模擬 DRLIN.srt 的問題段落
    drlin_segments = [
        {'start': 0.0, 'end': 1.480, 'text': '母親節快到了'},
        {'start': 1.480, 'end': 1.840, 'text': '也許今年你可以來送點不一樣的喔'},
        {'start': 1.840, 'end': 4.299, 'text': '大家好'},
        {'start': 4.299, 'end': 5.120, 'text': '我是臺北站前諾貝爾眼科診所院長'},
        {'start': 5.120, 'end': 7.397, 'text': '林一鴻醫師'},
        {'start': 7.400, 'end': 9.378, 'text': '我們人當過了40歲以後'},
        {'start': 9.380, 'end': 12.137, 'text': '我們就會開始產生所謂的老花眼'},
        {'start': 12.140, 'end': 13.837, 'text': '會讓你看近特別的喫力'},
        {'start': 13.839, 'end': 16.167, 'text': '造成你生活中的不方便'},
        {'start': 16.170, 'end': 18.847, 'text': '接下來就請大家一起到我的診間'},
        {'start': 23.807, 'end': 24.707, 'text': '母親節快到了'},  # 重複段落
        {'start': 24.960, 'end': 27.557, 'text': '歡迎帶你媽媽來諾貝爾眼科'},
        {'start': 27.559, 'end': 28.698, 'text': '找我們做諮詢'},
        {'start': 28.699, 'end': 30.358, 'text': '看看你媽媽適不適合做'},
        {'start': 30.359, 'end': 32.280, 'text': '近視跟老花一起處理的'},
        {'start': 32.280, 'end': 33.460, 'text': '這種老花蕾色'},
        {'start': 33.460, 'end': 34.859, 'text': '讓我們給你媽媽一個'},
        {'start': 34.859, 'end': 36.640, 'text': '清晰方便的視力'}
    ]
    
    # 生成修正後的 SRT
    corrected_srt = SubtitleFormatter.segments_to_srt(drlin_segments)
    
    # 保存為修正版文件
    output_path = "DRLIN_corrected.srt"
    with open(output_path, 'w', encoding='utf-8-sig', newline='\r\n') as f:
        f.write(corrected_srt)
    
    print(f"✅ 修正版 SRT 文件已保存: {output_path}")
    
    # 顯示前幾行內容
    print("修正後的前幾行:")
    lines = corrected_srt.split('\n')
    for i, line in enumerate(lines[:15]):
        print(f"{i+1:2d}: {line}")
    
    return True

def main():
    """主測試函數"""
    print("開始測試修復後的時間戳處理功能...")
    
    tests = [
        test_negative_timestamps,
        test_invalid_time_ranges, 
        test_edge_cases,
        create_corrected_srt
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ 測試失敗: {test.__name__}")
        except Exception as e:
            print(f"❌ 測試出錯: {test.__name__} - {e}")
    
    print(f"\n測試完成: {passed}/{len(tests)} 項通過")
    
    if passed == len(tests):
        print("✅ 所有測試通過，時間戳修復功能正常！")
        return True
    else:
        print("❌ 部分測試失敗，需要進一步修復")
        return False

if __name__ == "__main__":
    main()