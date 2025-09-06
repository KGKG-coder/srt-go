#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
簡化版字幕檔對比分析工具
對比使用增強型語音檢測器v2.0前後產出的字幕檔差異
"""

import sys
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
import subprocess
from datetime import datetime

# 添加路徑
sys.path.append('.')

class SimpleSubtitleComparator:
    """簡化版字幕檔對比器"""
    
    def __init__(self):
        # 測試配置：只比較關鍵的兩種模式
        self.test_configs = {
            'standard': {
                'enable_adaptive_voice_detection': False,
                'enable_subeasy': False,
                'description': 'Standard Whisper Output'
            },
            'enhanced': {
                'enable_adaptive_voice_detection': True,
                'enable_subeasy': False,
                'description': 'Enhanced Voice Detector v2.0'
            }
        }
    
    def compare_subtitle_files(self):
        """執行字幕檔對比"""
        print("Subtitle Comparison Analysis Tool")
        print("=" * 50)
        
        # 針對DRLIN.mp4進行重點分析
        test_file = "test_VIDEO/DRLIN.mp4"
        filename = Path(test_file).stem
        
        print(f"Processing file: {filename}")
        print("-" * 30)
        
        results = {}
        
        # 生成標準版本字幕
        print("Generating standard subtitle...")
        standard_result = self._generate_single_subtitle(
            test_file, self.test_configs['standard'], 
            f"comparison_output/{filename}_standard"
        )
        
        if standard_result:
            results['standard'] = standard_result
            print(f"  Standard: {standard_result['segments_count']} segments")
        
        # 生成增強版本字幕
        print("Generating enhanced subtitle...")
        enhanced_result = self._generate_single_subtitle(
            test_file, self.test_configs['enhanced'],
            f"comparison_output/{filename}_enhanced"
        )
        
        if enhanced_result:
            results['enhanced'] = enhanced_result
            print(f"  Enhanced: {enhanced_result['segments_count']} segments")
        
        # 進行對比分析
        if len(results) == 2:
            analysis = self._analyze_differences_simple(results)
            self._display_analysis_results(analysis)
            return analysis
        else:
            print("ERROR: Failed to generate both subtitle versions for comparison")
            return None
    
    def _generate_single_subtitle(self, audio_file: str, config: Dict, output_dir: str) -> Dict:
        """生成單個字幕檔"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # 構建設置參數
            settings = {
                "model": "large",
                "language": "auto",
                "outputFormat": "srt",
                "customDir": output_dir,
                "enable_gpu": False,
                **{k: v for k, v in config.items() if k.startswith('enable')}
            }
            
            # 構建命令
            cmd = [
                "python", "electron_backend.py",
                "--files", f'["{audio_file}"]',
                "--settings", json.dumps(settings),
                "--corrections", "[]"
            ]
            
            # 執行命令（增加超時時間）
            result = subprocess.run(
                cmd, capture_output=True, text=True, 
                cwd=Path(__file__).parent, timeout=300,
                encoding='utf-8', errors='ignore'
            )
            
            if result.returncode == 0:
                # 解析生成的SRT檔
                srt_file = Path(output_dir) / f"{Path(audio_file).stem}.srt"
                if srt_file.exists():
                    segments = self._parse_srt_simple(srt_file)
                    return {
                        'srt_file': str(srt_file),
                        'segments': segments,
                        'segments_count': len(segments),
                        'config_name': config.get('description', 'Unknown')
                    }
            else:
                print(f"  Command failed with return code: {result.returncode}")
                if result.stderr:
                    print(f"  Error: {result.stderr[:200]}...")
            
            return None
            
        except Exception as e:
            print(f"  Generation error: {str(e)[:100]}...")
            return None
    
    def _parse_srt_simple(self, srt_file: Path) -> List[Dict]:
        """簡化版SRT檔案解析"""
        segments = []
        try:
            content = srt_file.read_text(encoding='utf-8')
            blocks = re.split(r'\n\s*\n', content.strip())
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    # 序號
                    try:
                        seq_num = int(lines[0])
                    except ValueError:
                        continue
                    
                    # 時間戳
                    time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', lines[1])
                    if time_match:
                        start_time = self._parse_timestamp_simple(time_match.group(1))
                        end_time = self._parse_timestamp_simple(time_match.group(2))
                        
                        # 文本內容
                        text = ' '.join(lines[2:]).strip()
                        
                        segments.append({
                            'seq': seq_num,
                            'start': start_time,
                            'end': end_time,
                            'duration': end_time - start_time,
                            'text': text
                        })
        except Exception as e:
            print(f"SRT parsing error: {e}")
        
        return segments
    
    def _parse_timestamp_simple(self, timestamp_str: str) -> float:
        """簡化版時間戳解析"""
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
    
    def _analyze_differences_simple(self, results: Dict) -> Dict:
        """簡化版差異分析"""
        standard = results['standard']
        enhanced = results['enhanced']
        
        standard_segments = standard['segments']
        enhanced_segments = enhanced['segments']
        
        analysis = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'file_analyzed': 'DRLIN.mp4',
            'standard_output': {
                'segments_count': len(standard_segments),
                'total_duration': sum(s['duration'] for s in standard_segments),
                'config': standard['config_name']
            },
            'enhanced_output': {
                'segments_count': len(enhanced_segments),
                'total_duration': sum(s['duration'] for s in enhanced_segments),
                'config': enhanced['config_name']
            },
            'differences': {},
            'key_improvements': []
        }
        
        # 計算基本差異
        count_diff = len(enhanced_segments) - len(standard_segments)
        duration_diff = analysis['enhanced_output']['total_duration'] - analysis['standard_output']['total_duration']
        duration_change_pct = (duration_diff / analysis['standard_output']['total_duration']) * 100 if analysis['standard_output']['total_duration'] > 0 else 0
        
        analysis['differences'] = {
            'segment_count_change': count_diff,
            'total_duration_change': duration_diff,
            'duration_change_percentage': duration_change_pct
        }
        
        # 檢查第12段的關鍵修正
        if len(standard_segments) >= 12 and len(enhanced_segments) >= 12:
            std_seg12 = standard_segments[11]  # 第12段 (0-indexed)
            enh_seg12 = enhanced_segments[11]
            
            seg12_improvement = {
                'segment_number': 12,
                'text': std_seg12['text'],
                'standard_timing': f"{std_seg12['start']:.3f}s -> {std_seg12['end']:.3f}s",
                'enhanced_timing': f"{enh_seg12['start']:.3f}s -> {enh_seg12['end']:.3f}s",
                'standard_duration': std_seg12['duration'],
                'enhanced_duration': enh_seg12['duration'],
                'duration_reduction': std_seg12['duration'] - enh_seg12['duration'],
                'duration_reduction_pct': ((std_seg12['duration'] - enh_seg12['duration']) / std_seg12['duration']) * 100 if std_seg12['duration'] > 0 else 0
            }
            
            analysis['key_improvements'].append(seg12_improvement)
        
        # 檢查其他顯著的時間戳調整
        timing_adjustments = []
        min_segments = min(len(standard_segments), len(enhanced_segments))
        
        for i in range(min_segments):
            std_seg = standard_segments[i]
            enh_seg = enhanced_segments[i]
            
            start_diff = abs(enh_seg['start'] - std_seg['start'])
            end_diff = abs(enh_seg['end'] - std_seg['end'])
            duration_diff = abs(enh_seg['duration'] - std_seg['duration'])
            
            if start_diff > 0.5 or end_diff > 0.5 or duration_diff > 0.5:
                timing_adjustments.append({
                    'segment': i + 1,
                    'text_preview': std_seg['text'][:30] + '...',
                    'start_adjustment': start_diff,
                    'end_adjustment': end_diff,
                    'duration_change': duration_diff
                })
        
        analysis['timing_adjustments'] = {
            'total_count': len(timing_adjustments),
            'adjustments': timing_adjustments[:5]  # 只保留前5個
        }
        
        return analysis
    
    def _display_analysis_results(self, analysis: Dict):
        """顯示分析結果"""
        print("\nComparison Analysis Results")
        print("=" * 40)
        
        # 基本統計
        print(f"File: {analysis['file_analyzed']}")
        print(f"Analysis Time: {analysis['timestamp']}")
        
        standard = analysis['standard_output']
        enhanced = analysis['enhanced_output']
        diff = analysis['differences']
        
        print(f"\nSegment Count:")
        print(f"  Standard: {standard['segments_count']}")
        print(f"  Enhanced: {enhanced['segments_count']}")
        print(f"  Change: {diff['segment_count_change']:+d}")
        
        print(f"\nTotal Duration:")
        print(f"  Standard: {standard['total_duration']:.3f}s")
        print(f"  Enhanced: {enhanced['total_duration']:.3f}s")
        print(f"  Change: {diff['total_duration_change']:+.3f}s ({diff['duration_change_percentage']:+.1f}%)")
        
        # 關鍵改進
        key_improvements = analysis.get('key_improvements', [])
        if key_improvements:
            print(f"\nKey Improvements:")
            for improvement in key_improvements:
                print(f"  Segment {improvement['segment_number']}: \"{improvement['text'][:40]}...\"")
                print(f"    Before: {improvement['standard_timing']} ({improvement['standard_duration']:.3f}s)")
                print(f"    After:  {improvement['enhanced_timing']} ({improvement['enhanced_duration']:.3f}s)")
                print(f"    Reduction: {improvement['duration_reduction']:.3f}s ({improvement['duration_reduction_pct']:.1f}%)")
        
        # 時間戳調整
        timing_adj = analysis.get('timing_adjustments', {})
        print(f"\nTiming Adjustments: {timing_adj.get('total_count', 0)} segments modified")
        
        if timing_adj.get('adjustments'):
            print("  Sample adjustments:")
            for adj in timing_adj['adjustments'][:3]:
                print(f"    Segment {adj['segment']}: {adj['text_preview']}")
                print(f"      Start: {adj['start_adjustment']:.3f}s, End: {adj['end_adjustment']:.3f}s")
        
        # 保存結果
        self._save_analysis_results(analysis)
    
    def _save_analysis_results(self, analysis: Dict):
        """保存分析結果"""
        output_file = "subtitle_comparison_results.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            print(f"\nAnalysis results saved to: {output_file}")
        except Exception as e:
            print(f"Failed to save results: {e}")


def main():
    """主程序"""
    comparator = SimpleSubtitleComparator()
    
    try:
        print("Starting subtitle comparison analysis...")
        analysis = comparator.compare_subtitle_files()
        
        if analysis:
            print("\nComparison analysis completed successfully!")
        else:
            print("\nComparison analysis failed!")
            
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
    except Exception as e:
        print(f"\nAnalysis failed: {e}")


if __name__ == "__main__":
    main()