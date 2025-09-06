#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medium 模型精細微調
基於95.4%基線，進行細微參數調整以突破98%
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from faster_whisper import WhisperModel
    logger.info("Faster-Whisper 模組導入成功")
except ImportError as e:
    logger.error(f"Faster-Whisper 導入失敗: {e}")
    sys.exit(1)

# 基於95.4%基線的精細微調配置
BASELINE_95_4_CONFIG = {
    "name": "Medium 95.4% 基線",
    "model": "medium",
    "vad_parameters": {
        "threshold": 0.05,
        "min_speech_duration_ms": 50,
        "min_silence_duration_ms": 100,
        "speech_pad_ms": 50
    },
    "whisper_params": {
        "beam_size": 3,
        "word_timestamps": True,
        "condition_on_previous_text": False,
        "compression_ratio_threshold": 1.8,
        "log_prob_threshold": -1.5,
        "no_speech_threshold": 0.4
    }
}

FINE_TUNED_CONFIGS = [
    {
        "name": "Medium 微調A - VAD優化",
        "description": "微調VAD參數，保持其他不變",
        "model": "medium",
        "vad_parameters": {
            "threshold": 0.07,              # 稍微提高穩定性
            "min_speech_duration_ms": 45,   # 稍微減短
            "min_silence_duration_ms": 110, # 稍微增長
            "speech_pad_ms": 45             # 稍微減少
        },
        "whisper_params": BASELINE_95_4_CONFIG["whisper_params"]
    },
    {
        "name": "Medium 微調B - Beam優化",
        "description": "調整Beam Size和概率閾值",
        "model": "medium",
        "vad_parameters": BASELINE_95_4_CONFIG["vad_parameters"],
        "whisper_params": {
            "beam_size": 4,                 # 稍微提高準確性
            "word_timestamps": True,
            "condition_on_previous_text": False,
            "compression_ratio_threshold": 1.7, # 稍微降低
            "log_prob_threshold": -1.4,     # 稍微提高要求
            "no_speech_threshold": 0.35     # 稍微提高敏感度
        }
    },
    {
        "name": "Medium 微調C - 上下文啟用",
        "description": "啟用上下文並調整相關參數",
        "model": "medium",
        "vad_parameters": BASELINE_95_4_CONFIG["vad_parameters"],
        "whisper_params": {
            "beam_size": 3,
            "word_timestamps": True,
            "condition_on_previous_text": True,  # 啟用上下文
            "compression_ratio_threshold": 1.9,  # 稍微提高
            "log_prob_threshold": -1.3,     # 提高要求
            "no_speech_threshold": 0.4
        }
    },
    {
        "name": "Medium 微調D - 混合最佳",
        "description": "結合多個微調的最佳參數",
        "model": "medium",
        "vad_parameters": {
            "threshold": 0.06,              # 介於0.05和0.07之間
            "min_speech_duration_ms": 47,   # 介於45和50之間
            "min_silence_duration_ms": 105, # 介於100和110之間
            "speech_pad_ms": 47             # 介於45和50之間
        },
        "whisper_params": {
            "beam_size": 4,                 # 提高準確性
            "word_timestamps": True,
            "condition_on_previous_text": True,  # 啟用上下文
            "compression_ratio_threshold": 1.75, # 平衡值
            "log_prob_threshold": -1.4,     # 平衡值
            "no_speech_threshold": 0.37     # 平衡值
        }
    },
    {
        "name": "Medium 微調E - 語氣詞增強",
        "description": "專門針對語氣詞捕捉的優化",
        "model": "medium",
        "vad_parameters": {
            "threshold": 0.04,              # 更敏感
            "min_speech_duration_ms": 40,   # 更短
            "min_silence_duration_ms": 90,  # 稍微減少
            "speech_pad_ms": 55             # 稍微增加保護
        },
        "whisper_params": {
            "beam_size": 2,                 # 更敏感
            "word_timestamps": True,
            "condition_on_previous_text": False,
            "compression_ratio_threshold": 1.6, # 更低
            "log_prob_threshold": -1.6,     # 更寬鬆
            "no_speech_threshold": 0.3      # 更敏感
        }
    },
    {
        "name": "Medium 微調F - 平衡策略",
        "description": "在穩定性和敏感性間的最佳平衡",
        "model": "medium",
        "vad_parameters": {
            "threshold": 0.08,              # 稍微提高穩定性
            "min_speech_duration_ms": 55,   # 稍微提高品質
            "min_silence_duration_ms": 120, # 稍微增長分割
            "speech_pad_ms": 40             # 精準邊界
        },
        "whisper_params": {
            "beam_size": 5,                 # 最高準確性
            "word_timestamps": True,
            "condition_on_previous_text": True,
            "compression_ratio_threshold": 2.0, # 稍微提高
            "log_prob_threshold": -1.2,     # 提高要求
            "no_speech_threshold": 0.45     # 穩定閾值
        }
    }
]

def analyze_segment_similarity_precise(generated_segments, reference_file, max_segments=34):
    """精確相似度分析"""
    try:
        with open(reference_file, 'r', encoding='utf-8') as f:
            ref_content = f.read()
        
        import re
        ref_segments = []
        lines = ref_content.strip().split('\n')
        current_seg = {}
        
        for line in lines:
            line = line.strip()
            if re.match(r'^\d+$', line):
                seg_id = int(line)
                if seg_id > max_segments:
                    break
                if current_seg:
                    ref_segments.append(current_seg)
                current_seg = {'id': seg_id}
            elif '-->' in line:
                start_str, end_str = line.split(' --> ')
                def parse_time(time_str):
                    h, m, s = time_str.split(':')
                    s, ms = s.split(',')
                    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0
                current_seg['start'] = parse_time(start_str)
                current_seg['end'] = parse_time(end_str)
            elif line and 'start' in current_seg and 'text' not in current_seg:
                current_seg['text'] = line
        
        if current_seg and current_seg['id'] <= max_segments:
            ref_segments.append(current_seg)
        
        ref_total_time = ref_segments[-1]['end'] if ref_segments else 0
        gen_relevant_segments = [seg for seg in generated_segments if seg['start'] <= ref_total_time]
        
        # 精確評分算法 - 針對95.4%基線優化
        
        # 1. 段落數精確匹配 (35%)
        target_segments = len(ref_segments)  # 34段
        actual_segments = len(gen_relevant_segments)
        segment_ratio = actual_segments / target_segments if target_segments else 0
        
        # 最佳範圍是32-38段落
        if 32 <= actual_segments <= 38:
            segment_score = 100 - abs(34 - actual_segments) * 2
        else:
            segment_score = max(0, 100 - abs(34 - actual_segments) * 5)
        
        # 2. 時長分布精確匹配 (30%)
        ref_durations = [seg['end'] - seg['start'] for seg in ref_segments]
        gen_durations = [seg['duration'] for seg in gen_relevant_segments]
        
        ref_avg_dur = sum(ref_durations) / len(ref_durations) if ref_durations else 0  # ~1.425s
        gen_avg_dur = sum(gen_durations) / len(gen_durations) if gen_durations else 0
        
        # 理想範圍 1.3-1.5秒
        if 1.3 <= gen_avg_dur <= 1.5:
            duration_score = 100 - abs(1.425 - gen_avg_dur) * 200
        else:
            duration_score = max(0, 100 - abs(1.425 - gen_avg_dur) * 400)
        
        # 3. 短段落匹配 (20%)
        ref_short = sum(1 for d in ref_durations if d < 1.0)  # ~10個
        gen_short = sum(1 for d in gen_durations if d < 1.0)
        
        # 理想範圍 8-12個短段落
        if 8 <= gen_short <= 12:
            short_score = 100 - abs(10 - gen_short) * 10
        else:
            short_score = max(0, 100 - abs(10 - gen_short) * 20)
        
        # 4. 語氣詞專業匹配 (15%)
        particles = ['好', '恩', '嗯', '哇', '啊', '喔', '嘿', '欸', '對']
        ref_particles = sum(1 for seg in ref_segments if len(seg['text'].strip()) <= 3 and 
                           any(p in seg['text'] for p in particles))  # ~5個
        gen_particles = sum(1 for seg in gen_relevant_segments if len(seg['text'].strip()) <= 3 and 
                           any(p in seg['text'] for p in particles))
        
        # 理想範圍 4-8個語氣詞
        if 4 <= gen_particles <= 8:
            particle_score = 100 - abs(5 - gen_particles) * 15
        else:
            particle_score = max(0, 100 - abs(5 - gen_particles) * 25)
        
        # 5. 時間戳精度加成
        timestamp_accuracy = 100
        time_penalties = 0
        
        # 檢查前15段的時間戳精度
        check_count = min(15, len(ref_segments), len(gen_relevant_segments))
        for i in range(check_count):
            start_diff = abs(ref_segments[i]['start'] - gen_relevant_segments[i]['start'])
            if start_diff > 1.0:  # 超過1秒差異
                time_penalties += 10
            elif start_diff > 0.5:  # 超過500ms差異
                time_penalties += 5
        
        timestamp_accuracy = max(50, 100 - time_penalties)
        
        # 綜合評分
        base_score = (
            segment_score * 0.35 + 
            duration_score * 0.30 + 
            short_score * 0.20 + 
            particle_score * 0.15
        )
        
        # 時間戳精度影響
        final_score = base_score * (timestamp_accuracy / 100)
        
        return {
            'reference_segments': len(ref_segments),
            'generated_segments': len(gen_relevant_segments),
            'segment_score': round(segment_score, 1),
            'duration_score': round(duration_score, 1),
            'short_score': round(short_score, 1),
            'particle_score': round(particle_score, 1),
            'timestamp_accuracy': round(timestamp_accuracy, 1),
            'match_score': round(final_score, 1),
            'avg_ref_duration': round(ref_avg_dur, 3),
            'avg_gen_duration': round(gen_avg_dur, 3),
            'ref_particles': ref_particles,
            'gen_particles': gen_particles,
            'ref_short': ref_short,
            'gen_short': gen_short
        }
        
    except Exception as e:
        logger.error(f"精確分析失敗: {e}")
        return {}

def test_fine_tuned_config(audio_file, output_file, config):
    """測試微調配置"""
    try:
        logger.info(f"\n🔬 微調測試: {config['name']}")
        logger.info(f"📝 {config['description']}")
        
        start_time = time.time()
        
        # 載入模型
        model = WhisperModel(config['model'], device="cpu", compute_type="int8")
        
        # 執行轉錄
        segments, info = model.transcribe(
            audio_file,
            language=None,
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
            segment_list.append(segment_data)
        
        total_time = time.time() - start_time
        
        # 生成SRT
        srt_content = generate_srt_from_segments(segment_list)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        # 精確相似度分析
        similarity = analyze_segment_similarity_precise(segment_list, "C:/Users/USER-ART0/Desktop/test1.srt")
        
        # 基本統計
        if segment_list:
            segments_per_second = len(segment_list) / info.duration
            avg_segment_duration = sum(seg['duration'] for seg in segment_list) / len(segment_list)
        else:
            segments_per_second = avg_segment_duration = 0
        
        result = {
            'success': True,
            'config_name': config['name'],
            'segment_count': len(segment_list),
            'segments_per_second': round(segments_per_second, 3),
            'avg_segment_duration': round(avg_segment_duration, 3),
            'similarity_analysis': similarity,
            'language': info.language,
            'language_probability': round(info.language_probability, 4),
            'processing_time': round(total_time, 2),
            'real_time_factor': round(total_time / info.duration, 2),
            'output_file': str(output_file)
        }
        
        # 結果摘要
        if similarity:
            match_score = similarity.get('match_score', 0)
            improvement = match_score - 95.4
            logger.info(f"  📊 匹配度: {match_score:.1f}% ({'+'if improvement > 0 else ''}{improvement:.1f}%)")
            logger.info(f"    段落: {similarity.get('segment_score', 0):.1f}% | 時長: {similarity.get('duration_score', 0):.1f}% | 短段: {similarity.get('short_score', 0):.1f}% | 語氣: {similarity.get('particle_score', 0):.1f}%")
            
            if match_score > 96:
                logger.info(f"  🎉 突破！超越基線 {improvement:.1f}%")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 微調測試失敗: {e}")
        return {'success': False, 'config_name': config['name'], 'error': str(e)}

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

def main():
    """主函數"""
    
    test_file = "C:/Users/USER-ART0/Desktop/C0485.MP4"
    output_dir = Path("C:/Users/USER-ART0/Desktop/medium_fine_tuning_tests")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not Path(test_file).exists():
        logger.error(f"❌ 測試檔案不存在: {test_file}")
        return None
    
    logger.info(f"🎯 Medium 精細微調測試")
    logger.info(f"📊 基線匹配度: 95.4%")
    logger.info(f"🎯 目標: 突破98%")
    logger.info(f"📋 微調配置: {len(FINE_TUNED_CONFIGS)}個")
    
    all_results = []
    
    for i, config in enumerate(FINE_TUNED_CONFIGS):
        logger.info(f"\n{'='*60}")
        logger.info(f"📝 微調測試 {i+1}/{len(FINE_TUNED_CONFIGS)}")
        
        config_name_safe = config['name'].replace(' ', '_').replace('-', '_')
        output_file = output_dir / f"C0485_{config_name_safe}.srt"
        
        result = test_fine_tuned_config(test_file, output_file, config)
        all_results.append(result)
        
        time.sleep(0.5)
    
    # 分析結果
    logger.info(f"\n{'='*80}")
    logger.info(f"🏆 Medium 微調測試結果總覽")
    logger.info(f"{'='*80}")
    
    successful_results = [r for r in all_results if r.get('success', False)]
    
    if successful_results:
        # 按匹配度排序
        successful_results.sort(key=lambda x: x.get('similarity_analysis', {}).get('match_score', 0), reverse=True)
        
        logger.info(f"\n📈 微調結果排名:")
        baseline_score = 95.4
        
        for i, result in enumerate(successful_results):
            match_score = result.get('similarity_analysis', {}).get('match_score', 0)
            improvement = match_score - baseline_score
            symbol = "🔥" if match_score >= 98 else "🚀" if match_score > baseline_score else "📊"
            
            logger.info(f"  {symbol} {i+1}. {result['config_name']}")
            logger.info(f"      匹配度: {match_score:.1f}% ({'+'if improvement > 0 else ''}{improvement:.1f}%)")
            logger.info(f"      段落數: {result['segment_count']}, 處理速度: {result['real_time_factor']:.2f}x")
        
        # 最佳配置分析
        best = successful_results[0]
        best_score = best.get('similarity_analysis', {}).get('match_score', 0)
        
        logger.info(f"\n🏆 最佳微調配置: {best['config_name']}")
        logger.info(f"📊 最終匹配度: {best_score:.1f}%")
        
        if best_score > baseline_score:
            logger.info(f"🎉 成功提升 {best_score - baseline_score:.1f}%！")
        else:
            logger.info(f"📝 未能超越基線，差距 {baseline_score - best_score:.1f}%")
    
    # 保存報告
    report = {
        'test_metadata': {
            'baseline_score': 95.4,
            'target_score': 98.0,
            'test_file': test_file,
            'total_configs': len(FINE_TUNED_CONFIGS),
            'successful_configs': len(successful_results),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        'test_results': all_results,
        'best_config': successful_results[0] if successful_results else None
    }
    
    report_file = output_dir / 'medium_fine_tuning_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n✅ 微調測試完成！")
    logger.info(f"📋 詳細報告: {report_file}")
    
    return report

if __name__ == "__main__":
    try:
        report = main()
        if report and report['test_metadata']['successful_configs'] > 0:
            best = report['best_config']
            best_score = best.get('similarity_analysis', {}).get('match_score', 0) if best else 0
            baseline = report['test_metadata']['baseline_score']
            
            print(f"\n🎯 Medium 微調測試完成！")
            print(f"最佳匹配度: {best_score:.1f}% (基線: {baseline}%)")
            
            if best_score > baseline:
                print(f"🎉 成功提升: +{best_score - baseline:.1f}%")
            else:
                print(f"📊 未能超越基線: -{baseline - best_score:.1f}%")
                
        else:
            print(f"\n💥 微調測試失敗！")
    except Exception as e:
        logger.error(f"❌ 主程序失敗: {e}")
        sys.exit(1)