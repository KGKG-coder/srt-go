#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
字幕檔對比分析工具
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

class SubtitleComparisonAnalyzer:
    """字幕檔對比分析器"""
    
    def __init__(self):
        self.test_files = [
            "test_VIDEO/DRLIN.mp4",
            "test_VIDEO/C0485.MP4", 
            "test_VIDEO/hutest.mp4"
        ]
        
        # 測試配置
        self.test_configs = {
            'standard': {
                'enable_adaptive_voice_detection': False,
                'enable_subeasy': False,
                'description': '標準Whisper輸出'
            },
            'subeasy': {
                'enable_adaptive_voice_detection': False,
                'enable_subeasy': True,
                'description': 'SubEasy濾波器'
            },
            'enhanced_detector': {
                'enable_adaptive_voice_detection': True,
                'enable_subeasy': False,
                'description': '增強型語音檢測器v2.0'
            },
            'combined': {
                'enable_adaptive_voice_detection': True,
                'enable_subeasy': True,
                'description': '增強檢測器 + SubEasy'
            }
        }
    
    def run_comparison_analysis(self):
        """執行完整的對比分析"""
        print("字幕檔對比分析工具")
        print("=" * 60)
        
        # 生成所有配置的字幕檔
        all_results = {}
        
        for test_file in self.test_files:
            filename = Path(test_file).stem
            print(f"\n處理檔案: {filename}")
            print("-" * 40)
            
            file_results = {}
            
            for config_name, config in self.test_configs.items():
                print(f"  生成 {config['description']} 字幕...")
                
                # 生成字幕檔
                output_dir = f"comparison_test/{filename}_{config_name}"
                os.makedirs(output_dir, exist_ok=True)
                
                result = self._generate_subtitle(test_file, config, output_dir)
                if result:
                    file_results[config_name] = result
                    print(f"    ✅ 完成: {result['segments_count']} 個段落")
                else:
                    print(f"    ❌ 失敗")
            
            all_results[filename] = file_results
        
        # 進行詳細對比分析
        comparison_report = self._analyze_differences(all_results)
        
        # 生成報告
        self._generate_comparison_report(comparison_report)
        
        return comparison_report
    
    def _generate_subtitle(self, audio_file: str, config: Dict, output_dir: str) -> Dict:
        """生成字幕檔"""
        try:
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
            
            # 執行命令
            result = subprocess.run(
                cmd, capture_output=True, text=True, 
                cwd=Path(__file__).parent, timeout=300
            )
            
            if result.returncode == 0:
                # 解析生成的SRT檔
                srt_file = Path(output_dir) / f"{Path(audio_file).stem}.srt"
                if srt_file.exists():
                    segments = self._parse_srt_file(srt_file)
                    return {
                        'srt_file': str(srt_file),
                        'segments': segments,
                        'segments_count': len(segments),
                        'total_duration': segments[-1]['end'] - segments[0]['start'] if segments else 0,
                        'config': config
                    }
            
            return None
            
        except Exception as e:
            print(f"      錯誤: {e}")
            return None
    
    def _parse_srt_file(self, srt_file: Path) -> List[Dict]:
        """解析SRT檔案"""
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
                        start_time = self._parse_timestamp(time_match.group(1))
                        end_time = self._parse_timestamp(time_match.group(2))
                        
                        # 文本內容
                        text = '\n'.join(lines[2:]).strip()
                        
                        segments.append({
                            'seq': seq_num,
                            'start': start_time,
                            'end': end_time,
                            'duration': end_time - start_time,
                            'text': text
                        })
        except Exception as e:
            print(f"SRT解析錯誤: {e}")
        
        return segments
    
    def _parse_timestamp(self, timestamp_str: str) -> float:
        """解析時間戳字符串為秒數"""
        parts = timestamp_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds_parts = parts[2].split(',')
        seconds = int(seconds_parts[0])
        milliseconds = int(seconds_parts[1])
        
        return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
    
    def _analyze_differences(self, all_results: Dict) -> Dict:
        """分析字幕檔差異"""
        comparison_report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_version': '1.0',
            'files_analyzed': [],
            'overall_improvements': {},
            'detailed_comparisons': {}
        }
        
        for filename, file_results in all_results.items():
            if not file_results:
                continue
                
            print(f"\n分析 {filename} 的差異:")
            print("-" * 50)
            
            file_analysis = self._analyze_single_file(filename, file_results)
            comparison_report['files_analyzed'].append(filename)
            comparison_report['detailed_comparisons'][filename] = file_analysis
            
            # 顯示主要改進
            improvements = file_analysis.get('improvements', {})
            for improvement_type, details in improvements.items():
                print(f"  {improvement_type}: {details}")
        
        # 計算整體改進統計
        comparison_report['overall_improvements'] = self._calculate_overall_improvements(
            comparison_report['detailed_comparisons']
        )
        
        return comparison_report
    
    def _analyze_single_file(self, filename: str, file_results: Dict) -> Dict:
        """分析單個檔案的差異"""
        analysis = {
            'filename': filename,
            'configurations': {},
            'improvements': {},
            'key_differences': []
        }
        
        # 基準：標準輸出
        baseline = file_results.get('standard')
        if not baseline:
            return analysis
        
        baseline_segments = baseline['segments']
        
        # 對比各種配置
        for config_name, result in file_results.items():
            if config_name == 'standard':
                continue
                
            config_analysis = self._compare_segments(
                baseline_segments, 
                result['segments'],
                config_name
            )
            
            analysis['configurations'][config_name] = config_analysis
        
        # 找出關鍵改進
        analysis['improvements'] = self._identify_improvements(analysis['configurations'])
        analysis['key_differences'] = self._find_key_differences(baseline_segments, file_results)
        
        return analysis
    
    def _compare_segments(self, baseline: List[Dict], comparison: List[Dict], config_name: str) -> Dict:
        """比較兩組段落"""
        return {
            'config_name': config_name,
            'baseline_count': len(baseline),
            'comparison_count': len(comparison),
            'count_difference': len(comparison) - len(baseline),
            'timing_adjustments': self._analyze_timing_changes(baseline, comparison),
            'content_changes': self._analyze_content_changes(baseline, comparison),
            'duration_changes': self._analyze_duration_changes(baseline, comparison)
        }
    
    def _analyze_timing_changes(self, baseline: List[Dict], comparison: List[Dict]) -> Dict:
        """分析時間戳變化"""
        timing_changes = {
            'total_adjustments': 0,
            'major_adjustments': [],  # 變化 > 1秒
            'average_adjustment': 0,
            'max_adjustment': 0
        }
        
        adjustments = []
        
        # 找到對應的段落進行比較
        for i, base_seg in enumerate(baseline):
            if i < len(comparison):
                comp_seg = comparison[i]
                
                # 計算開始時間調整
                start_diff = abs(comp_seg['start'] - base_seg['start'])
                end_diff = abs(comp_seg['end'] - base_seg['end'])
                
                max_diff = max(start_diff, end_diff)
                adjustments.append(max_diff)
                
                if max_diff > 1.0:  # 主要調整
                    timing_changes['major_adjustments'].append({
                        'segment': i + 1,
                        'text': base_seg['text'][:30] + '...',
                        'baseline_timing': f"{base_seg['start']:.3f}s → {base_seg['end']:.3f}s",
                        'adjusted_timing': f"{comp_seg['start']:.3f}s → {comp_seg['end']:.3f}s",
                        'adjustment': f"{max_diff:.3f}s"
                    })
        
        if adjustments:
            timing_changes['total_adjustments'] = len([a for a in adjustments if a > 0.1])
            timing_changes['average_adjustment'] = sum(adjustments) / len(adjustments)
            timing_changes['max_adjustment'] = max(adjustments)
        
        return timing_changes
    
    def _analyze_content_changes(self, baseline: List[Dict], comparison: List[Dict]) -> Dict:
        """分析內容變化"""
        return {
            'text_modifications': 0,  # 簡化版本，實際可以更詳細
            'removed_segments': max(0, len(baseline) - len(comparison)),
            'added_segments': max(0, len(comparison) - len(baseline))
        }
    
    def _analyze_duration_changes(self, baseline: List[Dict], comparison: List[Dict]) -> Dict:
        """分析時長變化"""
        baseline_total = sum(seg['duration'] for seg in baseline)
        comparison_total = sum(seg['duration'] for seg in comparison)
        
        return {
            'baseline_total_duration': baseline_total,
            'comparison_total_duration': comparison_total,
            'duration_difference': comparison_total - baseline_total,
            'duration_change_percentage': ((comparison_total - baseline_total) / baseline_total * 100) if baseline_total > 0 else 0
        }
    
    def _identify_improvements(self, configurations: Dict) -> Dict:
        """識別主要改進"""
        improvements = {}
        
        for config_name, config_analysis in configurations.items():
            config_improvements = []
            
            # 時間戳調整改進
            timing = config_analysis.get('timing_adjustments', {})
            if timing.get('total_adjustments', 0) > 0:
                config_improvements.append(
                    f"時間戳調整: {timing['total_adjustments']} 個段落"
                )
            
            # 主要調整
            major_adj = timing.get('major_adjustments', [])
            if major_adj:
                config_improvements.append(
                    f"重大調整: {len(major_adj)} 個段落 (>1秒)"
                )
            
            # 時長變化
            duration = config_analysis.get('duration_changes', {})
            duration_change = duration.get('duration_change_percentage', 0)
            if abs(duration_change) > 5:  # 5%以上變化
                config_improvements.append(
                    f"總時長變化: {duration_change:+.1f}%"
                )
            
            improvements[config_name] = config_improvements
        
        return improvements
    
    def _find_key_differences(self, baseline_segments: List[Dict], file_results: Dict) -> List[Dict]:
        """找出關鍵差異"""
        key_differences = []
        
        # 特別關注DRLIN.mp4的第12段問題
        if any('drlin' in str(result.get('srt_file', '')).lower() for result in file_results.values()):
            # 檢查第12段的變化
            if len(baseline_segments) >= 12:
                seg_12 = baseline_segments[11]  # 第12段 (0-indexed)
                
                enhanced_result = file_results.get('enhanced_detector')
                if enhanced_result and len(enhanced_result['segments']) >= 12:
                    enhanced_seg_12 = enhanced_result['segments'][11]
                    
                    if seg_12['duration'] > enhanced_seg_12['duration']:
                        key_differences.append({
                            'type': 'critical_fix',
                            'description': 'DRLIN第12段音樂間奏修正',
                            'segment': 12,
                            'before': f"{seg_12['start']:.3f}s → {seg_12['end']:.3f}s ({seg_12['duration']:.3f}s)",
                            'after': f"{enhanced_seg_12['start']:.3f}s → {enhanced_seg_12['end']:.3f}s ({enhanced_seg_12['duration']:.3f}s)",
                            'improvement': f"時長減少 {((seg_12['duration'] - enhanced_seg_12['duration']) / seg_12['duration'] * 100):.1f}%"
                        })
        
        return key_differences
    
    def _calculate_overall_improvements(self, detailed_comparisons: Dict) -> Dict:
        """計算整體改進統計"""
        overall = {
            'total_files_processed': len(detailed_comparisons),
            'configurations_tested': 4,
            'average_improvements': {},
            'success_rates': {}
        }
        
        # 統計各配置的改進情況
        for config_name in ['subeasy', 'enhanced_detector', 'combined']:
            config_improvements = []
            config_successes = 0
            
            for filename, file_analysis in detailed_comparisons.items():
                config_data = file_analysis.get('configurations', {}).get(config_name)
                if config_data:
                    timing_adj = config_data.get('timing_adjustments', {}).get('total_adjustments', 0)
                    if timing_adj > 0:
                        config_successes += 1
                    config_improvements.append(timing_adj)
            
            if config_improvements:
                overall['average_improvements'][config_name] = sum(config_improvements) / len(config_improvements)
                overall['success_rates'][config_name] = (config_successes / len(config_improvements)) * 100
        
        return overall
    
    def _generate_comparison_report(self, comparison_report: Dict):
        """生成對比報告"""
        report_file = "subtitle_comparison_report.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 對比分析報告已生成: {report_file}")
        
        # 顯示摘要
        self._display_summary(comparison_report)
    
    def _display_summary(self, report: Dict):
        """顯示分析摘要"""
        print("\n🎯 字幕檔對比分析摘要")
        print("=" * 50)
        
        overall = report.get('overall_improvements', {})
        
        print(f"📁 處理檔案數量: {overall.get('total_files_processed', 0)}")
        print(f"⚙️  測試配置數量: {overall.get('configurations_tested', 0)}")
        
        print("\n📈 各配置平均改進:")
        for config_name, avg_improvement in overall.get('average_improvements', {}).items():
            success_rate = overall.get('success_rates', {}).get(config_name, 0)
            config_desc = self.test_configs.get(config_name, {}).get('description', config_name)
            print(f"  {config_desc}: {avg_improvement:.1f} 個段落調整 ({success_rate:.0f}% 成功率)")
        
        # 顯示關鍵差異
        print("\n🔧 關鍵修正:")
        for filename, file_analysis in report.get('detailed_comparisons', {}).items():
            key_diffs = file_analysis.get('key_differences', [])
            for diff in key_diffs:
                if diff.get('type') == 'critical_fix':
                    print(f"  ✅ {diff['description']}")
                    print(f"     修正前: {diff['before']}")
                    print(f"     修正後: {diff['after']}")
                    print(f"     改進: {diff['improvement']}")


def main():
    """主程序"""
    analyzer = SubtitleComparisonAnalyzer()
    
    try:
        print("開始字幕檔對比分析...")
        report = analyzer.run_comparison_analysis()
        
        print("\n🎉 對比分析完成！")
        
    except KeyboardInterrupt:
        print("\n⏹️ 用戶中斷分析")
    except Exception as e:
        print(f"\n❌ 分析失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()