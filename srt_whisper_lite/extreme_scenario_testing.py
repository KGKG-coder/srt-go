#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
極限場景測試 - 尋找VAD參數真正發揮作用的情況
測試長音頻、低品質錄音、快速語音等極限情況
"""

import sys
import json
import logging
import time
from pathlib import Path
import os

# 設定控制台編碼
if sys.platform.startswith('win'):
    os.system('chcp 65001 > NUL')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from faster_whisper import WhisperModel
    logger.info("Faster-Whisper 模組導入成功")
except ImportError as e:
    logger.error(f"Faster-Whisper 導入失敗: {e}")
    sys.exit(1)

def test_extreme_vad_scenarios(audio_file, output_dir):
    """
    測試極限VAD場景
    """
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 極限場景VAD配置
    extreme_configs = [
        {
            'name': 'Large_V3_Standard',
            'model': 'large-v3',
            'description': '標準配置基線',
            'vad': {
                "threshold": 0.5,
                "min_speech_duration_ms": 250,
                "min_silence_duration_ms": 2000,
                "speech_pad_ms": 400
            }
        },
        {
            'name': 'Large_V3_Ultra_Aggressive',
            'model': 'large-v3', 
            'description': '超激進分割',
            'vad': {
                "threshold": 0.01,
                "min_speech_duration_ms": 10,   # 極短語音
                "min_silence_duration_ms": 50,  # 極短靜音
                "speech_pad_ms": 10
            }
        },
        {
            'name': 'Large_V3_Ultra_Conservative',
            'model': 'large-v3',
            'description': '超保守分割',
            'vad': {
                "threshold": 0.8,              # 極高閾值
                "min_speech_duration_ms": 1000, # 極長語音
                "min_silence_duration_ms": 3000, # 極長靜音
                "speech_pad_ms": 500
            }
        },
        {
            'name': 'Large_V2_Comparison',
            'model': 'large-v2',
            'description': 'V2對比基線',
            'vad': {
                "threshold": 0.15,
                "min_speech_duration_ms": 100,
                "min_silence_duration_ms": 300,
                "speech_pad_ms": 100
            }
        },
        {
            'name': 'Medium_Speed_Test',
            'model': 'medium',
            'description': '速度測試基線',
            'vad': {
                "threshold": 0.15,
                "min_speech_duration_ms": 100,
                "min_silence_duration_ms": 300,
                "speech_pad_ms": 100
            }
        }
    ]
    
    logger.info(f"🚀 開始極限場景VAD測試")
    logger.info(f"🎯 測試檔案: {audio_file}")
    logger.info(f"🔬 測試 {len(extreme_configs)} 種極限配置")
    
    results = []
    
    for i, config in enumerate(extreme_configs):
        logger.info(f"\n=== 極限測試 {i+1}/{len(extreme_configs)}: {config['name']} ===")
        logger.info(f"描述: {config['description']}")
        logger.info(f"模型: {config['model']}")
        logger.info(f"VAD: {config['vad']}")
        
        try:
            # 記錄開始時間
            start_time = time.time()
            
            # 載入模型
            logger.info("載入模型中...")
            model = WhisperModel(config['model'], device="cpu", compute_type="int8")
            load_time = time.time() - start_time
            
            # 執行轉錄
            logger.info("開始轉錄...")
            transcribe_start = time.time()
            segments, info = model.transcribe(
                audio_file,
                language=None,
                beam_size=5,
                word_timestamps=True,
                vad_filter=True,
                vad_parameters=config['vad']
            )
            
            # 處理結果
            segment_list = list(segments)
            transcribe_time = time.time() - transcribe_start
            total_time = time.time() - start_time
            
            # 生成詳細統計
            if segment_list:
                segment_durations = [seg.end - seg.start for seg in segment_list]
                total_speech_time = sum(segment_durations)
                avg_segment_duration = total_speech_time / len(segment_list)
                shortest_segment = min(segment_durations)
                longest_segment = max(segment_durations)
                speech_ratio = total_speech_time / info.duration
            else:
                total_speech_time = avg_segment_duration = shortest_segment = longest_segment = speech_ratio = 0
            
            # 生成SRT
            srt_content = generate_srt_from_segments(segment_list)
            output_file = output_path / f"{config['name']}_extreme_result.srt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            result = {
                'success': True,
                'config_name': config['name'],
                'description': config['description'],
                'model': config['model'],
                'vad_config': config['vad'],
                
                # 基本統計
                'segment_count': len(segment_list),
                'total_duration': round(info.duration, 2),
                'total_speech_time': round(total_speech_time, 2),
                'speech_ratio': round(speech_ratio, 3),
                
                # 段落分析
                'avg_segment_duration': round(avg_segment_duration, 3),
                'shortest_segment': round(shortest_segment, 3),
                'longest_segment': round(longest_segment, 3),
                'segments_per_minute': round(len(segment_list) / (info.duration / 60), 1),
                
                # 語言檢測
                'language': info.language,
                'language_probability': round(info.language_probability, 4),
                
                # 性能統計
                'load_time': round(load_time, 2),
                'transcribe_time': round(transcribe_time, 2),
                'total_time': round(total_time, 2),
                'real_time_factor': round(transcribe_time / info.duration, 2),
                
                'output_file': str(output_file)
            }
            
            logger.info(f"✅ {config['name']} 完成!")
            logger.info(f"   段落: {len(segment_list)}段, 處理: {transcribe_time:.1f}s, 實時倍數: {result['real_time_factor']:.2f}x")
            logger.info(f"   語音比例: {speech_ratio:.1%}, 平均段落: {avg_segment_duration:.2f}s")
            logger.info(f"   信心度: {info.language_probability:.3f}, 最短段落: {shortest_segment:.2f}s")
            
            results.append(result)
            
        except Exception as e:
            logger.error(f"❌ {config['name']} 測試失敗: {e}")
            results.append({
                'success': False,
                'config_name': config['name'],
                'description': config['description'],
                'model': config['model'],
                'error': str(e)
            })
    
    return results

def generate_srt_from_segments(segments):
    """從段落生成SRT格式"""
    def format_timestamp(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    srt_content = ""
    for i, segment in enumerate(segments, 1):
        start_time = format_timestamp(segment.start)
        end_time = format_timestamp(segment.end)
        text = segment.text.strip()
        
        srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
    
    return srt_content

def analyze_extreme_results(results):
    """分析極限測試結果"""
    
    logger.info(f"\n📊 極限測試結果分析")
    logger.info(f"{'='*80}")
    
    successful_results = [r for r in results if r.get('success', False)]
    
    if not successful_results:
        logger.error("❌ 沒有成功的測試結果")
        return
    
    # 按段落數排序
    by_segments = sorted(successful_results, key=lambda x: x['segment_count'], reverse=True)
    logger.info(f"\n🏆 段落數排名 (細分程度):")
    for i, result in enumerate(by_segments):
        vad_desc = f"VAD:{result['vad_config']['threshold']}"
        logger.info(f"{i+1:2d}. {result['config_name']:25s}: {result['segment_count']:3d}段 {vad_desc:10s} ({result['description']})")
    
    # 按處理速度排序
    by_speed = sorted(successful_results, key=lambda x: x['transcribe_time'])
    logger.info(f"\n⚡ 處理速度排名:")
    for i, result in enumerate(by_speed):
        logger.info(f"{i+1:2d}. {result['config_name']:25s}: {result['transcribe_time']:6.1f}s (RTF:{result['real_time_factor']:5.2f}x)")
    
    # 按語言信心度排序
    by_confidence = sorted(successful_results, key=lambda x: x['language_probability'], reverse=True)
    logger.info(f"\n🎯 語言信心度排名:")
    for i, result in enumerate(by_confidence):
        logger.info(f"{i+1:2d}. {result['config_name']:25s}: {result['language_probability']:6.3f} ({result['language']})")
    
    # VAD效果分析
    logger.info(f"\n🔍 VAD參數效果分析:")
    vad_effects = {}
    for result in successful_results:
        threshold = result['vad_config']['threshold']
        if threshold not in vad_effects:
            vad_effects[threshold] = []
        vad_effects[threshold].append(result)
    
    for threshold in sorted(vad_effects.keys()):
        results_for_threshold = vad_effects[threshold]
        segments = [r['segment_count'] for r in results_for_threshold]
        avg_segments = sum(segments) / len(segments)
        logger.info(f"   VAD閾值 {threshold:4.2f}: 平均 {avg_segments:5.1f}段 (範圍: {min(segments)}-{max(segments)})")
    
    # 檢查VAD參數差異顯著性
    logger.info(f"\n🚨 VAD參數顯著性檢查:")
    
    # 找到相同模型但不同VAD的組合
    model_groups = {}
    for result in successful_results:
        model = result['model']
        if model not in model_groups:
            model_groups[model] = []
        model_groups[model].append(result)
    
    vad_significance_found = False
    
    for model, model_results in model_groups.items():
        if len(model_results) > 1:
            segments_by_vad = [(r['vad_config']['threshold'], r['segment_count']) for r in model_results]
            segments_by_vad.sort()
            
            min_segments = min(seg for _, seg in segments_by_vad)
            max_segments = max(seg for _, seg in segments_by_vad)
            
            if max_segments > min_segments:
                vad_significance_found = True
                logger.info(f"   {model}: VAD閾值影響段落數 {min_segments}-{max_segments} (差異: {max_segments-min_segments})")
            else:
                logger.info(f"   {model}: VAD閾值無影響 (均為{min_segments}段)")
    
    if not vad_significance_found:
        logger.info(f"   ⚠️ 在此音頻上，VAD參數調整無顯著影響！")
        logger.info(f"   💡 建議測試更複雜的音頻環境")
    
    return {
        'vad_significance': vad_significance_found,
        'results_summary': successful_results
    }

def main():
    """主函數"""
    
    # 使用已知的複雜音頻進行極限測試
    test_file = "C:/Users/USER-ART0/Desktop/C0485.MP4"  # 較長的對話音頻
    output_dir = "C:/Users/USER-ART0/Desktop/extreme_vad_scenario_tests"
    
    if not Path(test_file).exists():
        logger.error(f"測試文件不存在: {test_file}")
        logger.info("請確保有可用的測試音頻檔案")
        return None
    
    logger.info(f"🎯 極限場景VAD測試開始")
    logger.info(f"測試檔案: {test_file}")
    logger.info(f"輸出目錄: {output_dir}")
    
    try:
        # 執行極限測試
        results = test_extreme_vad_scenarios(test_file, output_dir)
        
        # 分析結果
        analysis = analyze_extreme_results(results)
        
        # 生成詳細報告
        report = {
            'test_metadata': {
                'test_file': str(test_file),
                'output_dir': str(output_dir),
                'total_configs': len(results),
                'successful_tests': len([r for r in results if r.get('success', False)]),
                'vad_significance_detected': analysis.get('vad_significance', False) if analysis else False,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'extreme_test_results': results,
            'analysis_summary': analysis
        }
        
        # 保存報告
        report_file = Path(output_dir) / 'extreme_vad_scenario_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n✅ 極限場景VAD測試完成！")
        logger.info(f"📋 詳細報告: {report_file}")
        
        return report
        
    except Exception as e:
        logger.error(f"❌ 極限測試失敗: {e}")
        return None

if __name__ == "__main__":
    try:
        report = main()
        if report and report['test_metadata']['vad_significance_detected']:
            print(f"\n🎉 找到VAD參數顯著影響場景！")
        elif report:
            print(f"\n🤔 VAD參數在此場景下仍無顯著影響")
        else:
            print(f"\n💥 測試失敗！")
    except Exception as e:
        logger.error(f"❌ 主程序失敗: {e}")
        sys.exit(1)