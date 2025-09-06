#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Large V2 最優化參數測試腳本
基於完整研究結果，測試Large V2作為單一模型解決方案的效果
重點驗證時間軸準確性和處理效率
"""

import sys
import json
import logging
import time
from pathlib import Path
import os
import re

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

# Large V2 最優化配置
LARGE_V2_OPTIMAL_CONFIG = {
    "name": "Large V2 生產環境最優配置",
    "description": "時間軸準確、速度快、穩定可靠",
    "model": "large-v2",
    
    # 最優VAD參數（基於實測）
    "vad_parameters": {
        "threshold": 0.15,              # 平衡設定，適用99%場景
        "min_speech_duration_ms": 100,  # 100ms最短語音
        "min_silence_duration_ms": 300, # 300ms最短靜音
        "speech_pad_ms": 100            # 100ms語音填充
    },
    
    # Whisper優化參數
    "whisper_params": {
        "beam_size": 5,                 # 平衡速度與準確性
        "word_timestamps": True,         # 啟用詞級時間戳
        "condition_on_previous_text": True,  # 上下文增強
        "compression_ratio_threshold": 2.4,  # 壓縮比閾值
        "log_prob_threshold": -1.0,     # 對數概率閾值
        "no_speech_threshold": 0.6      # 無語音閾值
    },
    
    # 預期性能指標
    "expected_performance": {
        "時間軸準確度": "95%+",
        "處理速度": "0.8-1.2x實時",
        "語言信心度": "99%+",
        "段落密度": "0.4-0.8段/秒"
    }
}

def analyze_timestamp_accuracy(segments):
    """分析時間軸準確性"""
    if not segments:
        return {}
    
    # 計算時間軸特徵
    gaps = []
    overlaps = 0
    short_segments = 0
    
    for i in range(len(segments) - 1):
        gap = segments[i+1]['start'] - segments[i]['end']
        if gap < 0:
            overlaps += 1
        else:
            gaps.append(gap)
        
        duration = segments[i]['end'] - segments[i]['start']
        if duration < 0.5:  # 小於0.5秒視為過短
            short_segments += 1
    
    avg_gap = sum(gaps) / len(gaps) if gaps else 0
    
    return {
        'total_segments': len(segments),
        'overlapping_segments': overlaps,
        'short_segments': short_segments,
        'average_gap': round(avg_gap, 3),
        'min_gap': round(min(gaps), 3) if gaps else 0,
        'max_gap': round(max(gaps), 3) if gaps else 0,
        'timestamp_quality': 'Excellent' if overlaps == 0 and short_segments < 3 else 
                           'Good' if overlaps <= 2 else 'Poor'
    }

def test_large_v2_optimal(audio_file, output_file):
    """測試Large V2最優化配置"""
    try:
        config = LARGE_V2_OPTIMAL_CONFIG
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🎯 測試 {config['name']}")
        logger.info(f"📝 {config['description']}")
        logger.info(f"🎵 音頻檔案: {Path(audio_file).name}")
        logger.info(f"{'='*80}")
        
        # 記錄開始時間
        start_time = time.time()
        
        # 載入模型
        logger.info(f"⏳ 載入 {config['model']} 模型...")
        model_load_start = time.time()
        model = WhisperModel(
            config['model'], 
            device="cpu", 
            compute_type="int8"
        )
        model_load_time = time.time() - model_load_start
        logger.info(f"✅ 模型載入完成 ({model_load_time:.2f}秒)")
        
        # 執行轉錄
        logger.info("🎤 開始轉錄...")
        transcribe_start = time.time()
        
        segments, info = model.transcribe(
            audio_file,
            language=None,  # 自動檢測
            vad_filter=True,
            vad_parameters=config['vad_parameters'],
            **config['whisper_params']
        )
        
        # 處理結果
        segment_list = []
        for segment in segments:
            segment_data = {
                'id': len(segment_list) + 1,
                'start': segment.start,
                'end': segment.end,
                'text': segment.text.strip(),
                'duration': segment.end - segment.start
            }
            
            # 如果有詞級時間戳
            if hasattr(segment, 'words') and segment.words:
                segment_data['word_count'] = len(segment.words)
                segment_data['words'] = [
                    {
                        'word': w.word,
                        'start': w.start,
                        'end': w.end,
                        'probability': w.probability
                    } for w in segment.words
                ]
            
            segment_list.append(segment_data)
        
        transcribe_time = time.time() - transcribe_start
        total_time = time.time() - start_time
        
        # 生成SRT
        srt_content = generate_srt_from_segments(segment_list)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        # 分析時間軸準確性
        timestamp_analysis = analyze_timestamp_accuracy(segment_list)
        
        # 計算詳細統計
        if segment_list:
            segment_durations = [seg['duration'] for seg in segment_list]
            total_speech_time = sum(segment_durations)
            avg_segment_duration = total_speech_time / len(segment_list)
            segments_per_second = len(segment_list) / info.duration
            speech_ratio = total_speech_time / info.duration
            
            # 計算語言信心度統計
            if segment_list[0].get('words'):
                all_probs = []
                for seg in segment_list:
                    if seg.get('words'):
                        all_probs.extend([w['probability'] for w in seg['words']])
                avg_word_confidence = sum(all_probs) / len(all_probs) if all_probs else 0
            else:
                avg_word_confidence = 0
        else:
            total_speech_time = avg_segment_duration = segments_per_second = speech_ratio = 0
            avg_word_confidence = 0
        
        # 結果彙總
        result = {
            'success': True,
            'config_name': config['name'],
            'model': config['model'],
            'vad_config': config['vad_parameters'],
            
            # 基本統計
            'audio_duration': round(info.duration, 2),
            'segment_count': len(segment_list),
            'segments_per_second': round(segments_per_second, 3),
            'avg_segment_duration': round(avg_segment_duration, 3),
            'speech_ratio': round(speech_ratio, 3),
            
            # 時間軸分析
            'timestamp_analysis': timestamp_analysis,
            
            # 語言檢測
            'language': info.language,
            'language_probability': round(info.language_probability, 4),
            'avg_word_confidence': round(avg_word_confidence, 4),
            
            # 性能統計
            'model_load_time': round(model_load_time, 2),
            'transcribe_time': round(transcribe_time, 2),
            'total_time': round(total_time, 2),
            'real_time_factor': round(transcribe_time / info.duration, 2),
            
            # 檔案資訊
            'output_file': str(output_file),
            'segment_details': segment_list[:5]  # 前5個段落詳情
        }
        
        # 輸出結果摘要
        logger.info(f"\n📊 測試結果:")
        logger.info(f"  ✅ 段落數: {len(segment_list)}段")
        logger.info(f"  ✅ 段落密度: {segments_per_second:.2f}段/秒")
        logger.info(f"  ✅ 平均段落時長: {avg_segment_duration:.2f}秒")
        logger.info(f"  ✅ 處理速度: {result['real_time_factor']:.2f}x實時")
        logger.info(f"  ✅ 語言: {info.language} (信心度: {info.language_probability:.3f})")
        logger.info(f"  ✅ 時間軸品質: {timestamp_analysis['timestamp_quality']}")
        logger.info(f"  ✅ 重疊段落: {timestamp_analysis['overlapping_segments']}個")
        logger.info(f"  ✅ 過短段落: {timestamp_analysis['short_segments']}個")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }

def generate_srt_from_segments(segments):
    """從段落生成SRT格式"""
    def format_timestamp(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    srt_content = ""
    for segment in segments:
        segment_id = segment.get('id', len(srt_content.split('\n\n')) + 1)
        start_time = format_timestamp(segment['start'])
        end_time = format_timestamp(segment['end'])
        text = segment['text']
        
        srt_content += f"{segment_id}\n{start_time} --> {end_time}\n{text}\n\n"
    
    return srt_content

def run_comprehensive_v2_testing(test_files, output_dir):
    """執行全面的Large V2測試"""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"🚀 開始 Large V2 最優化參數測試")
    logger.info(f"📁 測試檔案數: {len(test_files)}")
    logger.info(f"💾 輸出目錄: {output_dir}")
    
    all_results = []
    
    for i, test_file in enumerate(test_files):
        if not Path(test_file).exists():
            logger.warning(f"⚠️ 測試檔案不存在: {test_file}")
            continue
        
        logger.info(f"\n{'='*80}")
        logger.info(f"📝 測試 {i+1}/{len(test_files)}")
        
        # 生成輸出檔名
        file_stem = Path(test_file).stem
        output_file = output_path / f"{file_stem}_v2_optimal.srt"
        
        # 執行測試
        result = test_large_v2_optimal(test_file, output_file)
        result['test_file'] = str(test_file)
        result['file_name'] = Path(test_file).name
        
        all_results.append(result)
        
        # 短暫延遲避免資源衝突
        time.sleep(1)
    
    return all_results

def analyze_v2_results(results):
    """分析V2測試結果"""
    
    logger.info(f"\n{'='*80}")
    logger.info(f"📊 Large V2 最優化測試結果分析")
    logger.info(f"{'='*80}")
    
    successful_results = [r for r in results if r.get('success', False)]
    
    if not successful_results:
        logger.error("❌ 沒有成功的測試結果")
        return
    
    # 總體統計
    logger.info(f"\n🎯 總體統計:")
    logger.info(f"  成功測試: {len(successful_results)}/{len(results)}")
    
    avg_rtf = sum(r['real_time_factor'] for r in successful_results) / len(successful_results)
    avg_segments_per_sec = sum(r['segments_per_second'] for r in successful_results) / len(successful_results)
    avg_confidence = sum(r['language_probability'] for r in successful_results) / len(successful_results)
    
    logger.info(f"  平均處理速度: {avg_rtf:.2f}x實時")
    logger.info(f"  平均段落密度: {avg_segments_per_sec:.3f}段/秒")
    logger.info(f"  平均語言信心度: {avg_confidence:.3f}")
    
    # 時間軸品質統計
    excellent_count = sum(1 for r in successful_results 
                         if r['timestamp_analysis']['timestamp_quality'] == 'Excellent')
    logger.info(f"  時間軸品質優秀: {excellent_count}/{len(successful_results)}")
    
    # 個別檔案結果
    logger.info(f"\n📋 個別檔案結果:")
    for result in successful_results:
        logger.info(f"\n  {result['file_name']}:")
        logger.info(f"    段落數: {result['segment_count']}段")
        logger.info(f"    處理速度: {result['real_time_factor']:.2f}x實時")
        logger.info(f"    時間軸品質: {result['timestamp_analysis']['timestamp_quality']}")
        logger.info(f"    語言信心度: {result['language_probability']:.3f}")
        
        # 顯示前3個段落作為樣本
        if result.get('segment_details'):
            logger.info(f"    前3個段落樣本:")
            for seg in result['segment_details'][:3]:
                logger.info(f"      [{seg['start']:.2f}-{seg['end']:.2f}] \"{seg['text'][:30]}...\"")

def main():
    """主函數"""
    
    # 測試檔案清單
    test_files = [
        "C:/Users/USER-ART0/Desktop/hutest.mp3",        # 短音頻 (~11秒)
        "C:/Users/USER-ART0/Desktop/DRLIN.mp4",         # 中音頻 (~40秒)  
        "C:/Users/USER-ART0/Desktop/C0485.MP4"          # 長音頻 (~140秒)
    ]
    
    output_dir = "C:/Users/USER-ART0/Desktop/large_v2_optimal_validation"
    
    # 檢查測試檔案
    available_files = [f for f in test_files if Path(f).exists()]
    if not available_files:
        logger.error("❌ 沒有可用的測試檔案")
        return None
    
    logger.info(f"🎯 Large V2 最優化參數驗證測試")
    logger.info(f"✅ 可用測試檔案: {len(available_files)}/{len(test_files)}")
    
    try:
        # 執行測試
        results = run_comprehensive_v2_testing(available_files, output_dir)
        
        # 分析結果
        analyze_v2_results(results)
        
        # 生成詳細報告
        report = {
            'test_metadata': {
                'model': 'large-v2',
                'config': LARGE_V2_OPTIMAL_CONFIG,
                'test_files': available_files,
                'total_tests': len(results),
                'successful_tests': len([r for r in results if r.get('success', False)]),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'test_results': results,
            'summary': {
                'average_rtf': sum(r['real_time_factor'] for r in results if r.get('success')) / 
                              len([r for r in results if r.get('success')]) if results else 0,
                'average_segments_per_second': sum(r['segments_per_second'] for r in results if r.get('success')) / 
                                              len([r for r in results if r.get('success')]) if results else 0,
                'timestamp_quality': {
                    'excellent': sum(1 for r in results if r.get('success') and 
                                   r['timestamp_analysis']['timestamp_quality'] == 'Excellent'),
                    'good': sum(1 for r in results if r.get('success') and 
                              r['timestamp_analysis']['timestamp_quality'] == 'Good'),
                    'poor': sum(1 for r in results if r.get('success') and 
                              r['timestamp_analysis']['timestamp_quality'] == 'Poor')
                }
            }
        }
        
        # 保存報告
        report_file = Path(output_dir) / 'large_v2_optimal_test_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n✅ Large V2 最優化測試完成！")
        logger.info(f"📋 詳細報告已保存: {report_file}")
        
        # 結論
        logger.info(f"\n{'='*80}")
        logger.info(f"🏆 結論")
        logger.info(f"{'='*80}")
        logger.info(f"Large V2 配置表現:")
        
        if report['summary']['timestamp_quality']['excellent'] == len(available_files):
            logger.info(f"  ✅ 時間軸品質: 完美 (所有檔案都達到Excellent)")
        else:
            logger.info(f"  ⚠️ 時間軸品質: 良好 (部分檔案需要注意)")
        
        if report['summary']['average_rtf'] < 1.5:
            logger.info(f"  ✅ 處理速度: 優秀 (平均 {report['summary']['average_rtf']:.2f}x實時)")
        else:
            logger.info(f"  ⚠️ 處理速度: 可接受 (平均 {report['summary']['average_rtf']:.2f}x實時)")
        
        logger.info(f"  ✅ 段落密度: {report['summary']['average_segments_per_second']:.3f}段/秒")
        
        return report
        
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
        return None

if __name__ == "__main__":
    try:
        report = main()
        if report and report['test_metadata']['successful_tests'] > 0:
            print(f"\n🎉 Large V2 最優化測試成功完成！")
            print(f"成功測試: {report['test_metadata']['successful_tests']}/{report['test_metadata']['total_tests']}")
        else:
            print(f"\n💥 測試失敗！")
    except Exception as e:
        logger.error(f"❌ 主程序失敗: {e}")
        sys.exit(1)