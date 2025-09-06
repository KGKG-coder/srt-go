#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medium 模型極限優化測試
基於95.4%基礎，探索極端參數組合以達到98%+匹配度
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

# 極限優化配置 - 目標突破98%
EXTREME_MEDIUM_CONFIGS = [
    {
        "name": "Medium 極限分割",
        "description": "最極端的細分參數，追求100%匹配",
        "model": "medium",
        "vad_parameters": {
            "threshold": 0.01,              # 極極低閾值
            "min_speech_duration_ms": 30,   # 30ms極短語音
            "min_silence_duration_ms": 50,  # 50ms極短靜音
            "speech_pad_ms": 25             # 25ms最小填充
        },
        "whisper_params": {
            "beam_size": 1,                 # 最小beam（最敏感）
            "word_timestamps": True,
            "condition_on_previous_text": False,
            "compression_ratio_threshold": 1.5,  # 極低合併閾值
            "log_prob_threshold": -2.0,     # 極寬鬆概率
            "no_speech_threshold": 0.2      # 極敏感語音檢測
        }
    },
    {
        "name": "Medium 語氣詞專家",
        "description": "專門捕捉短語氣詞和感嘆詞",
        "model": "medium",
        "vad_parameters": {
            "threshold": 0.03,              # 極低但稍微穩定
            "min_speech_duration_ms": 40,   # 40ms短語音
            "min_silence_duration_ms": 80,  # 80ms短靜音
            "speech_pad_ms": 40             # 40ms填充
        },
        "whisper_params": {
            "beam_size": 2,                 # 超小beam
            "word_timestamps": True,
            "condition_on_previous_text": False,
            "compression_ratio_threshold": 1.6,
            "log_prob_threshold": -1.8,
            "no_speech_threshold": 0.3,
            "repetition_penalty": 1.0,     # 防止重複
            "length_penalty": 0.8           # 偏好短句
        }
    },
    {
        "name": "Medium 詞級精準",
        "description": "基於詞級時間戳的精準分割",
        "model": "medium",
        "vad_parameters": {
            "threshold": 0.08,              # 稍高穩定性
            "min_speech_duration_ms": 60,   # 稍長保證品質
            "min_silence_duration_ms": 120, # 稍長保證分割
            "speech_pad_ms": 30             # 小填充精準邊界
        },
        "whisper_params": {
            "beam_size": 3,
            "word_timestamps": True,
            "condition_on_previous_text": False,
            "compression_ratio_threshold": 1.7,
            "log_prob_threshold": -1.6,
            "no_speech_threshold": 0.35,
            "repetition_penalty": 1.1,
            "length_penalty": 0.9,
            "suppress_blank": True          # 抑制空白
        }
    },
    {
        "name": "Medium 混合策略",
        "description": "結合超敏感與詞級精準的混合策略",
        "model": "medium",
        "vad_parameters": {
            "threshold": 0.06,              # 混合閾值
            "min_speech_duration_ms": 45,   # 混合時長
            "min_silence_duration_ms": 90,  # 混合靜音
            "speech_pad_ms": 35             # 混合填充
        },
        "whisper_params": {
            "beam_size": 2,
            "word_timestamps": True,
            "condition_on_previous_text": False,
            "compression_ratio_threshold": 1.65,
            "log_prob_threshold": -1.7,
            "no_speech_threshold": 0.32,
            "repetition_penalty": 1.05,
            "length_penalty": 0.85
        }
    },
    {
        "name": "Medium 時間戳專家",
        "description": "專注於時間戳精度的極端優化",
        "model": "medium",
        "vad_parameters": {
            "threshold": 0.04,              # 超低閾值
            "min_speech_duration_ms": 35,   # 超短語音
            "min_silence_duration_ms": 70,  # 超短靜音
            "speech_pad_ms": 20             # 極小填充
        },
        "whisper_params": {
            "beam_size": 1,
            "word_timestamps": True,
            "condition_on_previous_text": False,
            "compression_ratio_threshold": 1.4,  # 極低閾值
            "log_prob_threshold": -2.2,     # 極寬鬆
            "no_speech_threshold": 0.25,    # 極敏感
            "temperature": 0.0              # 確定性輸出
        }
    },
    {
        "name": "Medium 深度細分",
        "description": "基於95.4%配置的深度優化版本",
        "model": "medium",
        "vad_parameters": {
            "threshold": 0.02,              # 比0.05更極端
            "min_speech_duration_ms": 25,   # 比50ms更短
            "min_silence_duration_ms": 60,  # 比100ms更短
            "speech_pad_ms": 30             # 比50ms更精準
        },
        "whisper_params": {
            "beam_size": 1,                 # 比3更敏感
            "word_timestamps": True,
            "condition_on_previous_text": False,
            "compression_ratio_threshold": 1.3,  # 比1.8更低
            "log_prob_threshold": -2.5,     # 比-1.5更寬鬆
            "no_speech_threshold": 0.15     # 比0.4更敏感
        }
    }
]

def analyze_segment_similarity_advanced(generated_segments, reference_file, max_segments=34):
    """高級相似度分析，更精確的匹配度計算"""
    
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
        
        # 分析相似度 - 更精確的算法
        ref_total_time = ref_segments[-1]['end'] if ref_segments else 0
        gen_relevant_segments = [seg for seg in generated_segments if seg['start'] <= ref_total_time]
        
        # 1. 段落數匹配度 (40%)
        segment_ratio = len(gen_relevant_segments) / len(ref_segments) if ref_segments else 0
        segment_score = 100 - min(100, abs(1 - segment_ratio) * 100)
        
        # 2. 時長分布匹配度 (30%)
        ref_durations = [seg['end'] - seg['start'] for seg in ref_segments]
        gen_durations = [seg['duration'] for seg in gen_relevant_segments]
        
        ref_avg_dur = sum(ref_durations) / len(ref_durations) if ref_durations else 0
        gen_avg_dur = sum(gen_durations) / len(gen_durations) if gen_durations else 0
        duration_diff = abs(ref_avg_dur - gen_avg_dur)
        duration_score = max(0, 100 - (duration_diff * 100))
        
        # 3. 短段落捕捉匹配度 (20%)
        ref_short = sum(1 for d in ref_durations if d < 1.0)
        gen_short = sum(1 for d in gen_durations if d < 1.0)
        short_ratio = gen_short / ref_short if ref_short > 0 else 1.0
        short_score = 100 - min(100, abs(1 - short_ratio) * 50)
        
        # 4. 語氣詞專業匹配度 (10%)
        particles = ['好', '恩', '嗯', '哇', '啊', '喔', '嘿', '欸']
        ref_particles = sum(1 for seg in ref_segments if len(seg['text'].strip()) <= 3 and 
                           any(p in seg['text'] for p in particles))
        gen_particles = sum(1 for seg in gen_relevant_segments if len(seg['text'].strip()) <= 3 and 
                           any(p in seg['text'] for p in particles))
        
        particle_ratio = gen_particles / ref_particles if ref_particles > 0 else 1.0
        particle_score = 100 - min(100, abs(1 - particle_ratio) * 30)
        
        # 5. 時間戳精度 (權重計算)
        # 檢查前10段的時間戳精度
        timestamp_accuracy = 100
        for i in range(min(10, len(ref_segments), len(gen_relevant_segments))):
            ref_start_diff = abs(ref_segments[i]['start'] - gen_relevant_segments[i]['start'])
            if ref_start_diff > 0.5:  # 超過500ms差異
                timestamp_accuracy -= 5
        
        # 綜合評分
        overall_score = (
            segment_score * 0.40 + 
            duration_score * 0.30 + 
            short_score * 0.20 + 
            particle_score * 0.10
        )
        
        # 時間戳精度加成/扣分
        final_score = overall_score * (timestamp_accuracy / 100)
        
        detailed_metrics = {
            'reference_segments': len(ref_segments),
            'generated_segments': len(gen_relevant_segments),
            'segment_ratio': round(segment_ratio, 3),
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
            'time_coverage': round(ref_total_time, 3)
        }
        
        return detailed_metrics
        
    except Exception as e:
        logger.error(f"高級參考檔案分析失敗: {e}")
        return {}

def test_extreme_config(audio_file, output_file, config):
    """測試極端配置"""
    try:
        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 測試 {config['name']}")
        logger.info(f"📝 {config['description']}")
        logger.info(f"🎵 音頻檔案: {Path(audio_file).name}")
        logger.info(f"{'='*80}")
        
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
        
        # 高級相似度分析
        similarity = analyze_segment_similarity_advanced(segment_list, "C:/Users/USER-ART0/Desktop/test1.srt")
        
        # 基本統計
        if segment_list:
            total_speech_time = sum(seg['duration'] for seg in segment_list)
            avg_segment_duration = total_speech_time / len(segment_list)
            segments_per_second = len(segment_list) / info.duration
        else:
            total_speech_time = avg_segment_duration = segments_per_second = 0
        
        result = {
            'success': True,
            'config_name': config['name'],
            'model': config['model'],
            'vad_config': config['vad_parameters'],
            'whisper_config': config['whisper_params'],
            
            'audio_duration': round(info.duration, 2),
            'segment_count': len(segment_list),
            'segments_per_second': round(segments_per_second, 3),
            'avg_segment_duration': round(avg_segment_duration, 3),
            
            'similarity_analysis': similarity,
            
            'language': info.language,
            'language_probability': round(info.language_probability, 4),
            
            'model_load_time': round(model_load_time, 2),
            'transcribe_time': round(transcribe_time, 2),
            'real_time_factor': round(transcribe_time / info.duration, 2),
            
            'output_file': str(output_file)
        }
        
        # 結果摘要
        logger.info(f"\n📊 極端配置測試結果:")
        logger.info(f"  🎯 段落數: {len(segment_list)}段")
        logger.info(f"  ⚡ 段落密度: {segments_per_second:.3f}段/秒")
        logger.info(f"  ⏱️ 平均時長: {avg_segment_duration:.3f}秒")
        logger.info(f"  🚀 處理速度: {result['real_time_factor']:.2f}x實時")
        logger.info(f"  🗣️ 語言: {info.language} (信心度: {info.language_probability:.3f})")
        
        if similarity:
            logger.info(f"  📈 匹配度: {similarity.get('match_score', 0):.1f}%")
            logger.info(f"    - 段落匹配: {similarity.get('segment_score', 0):.1f}%")
            logger.info(f"    - 時長匹配: {similarity.get('duration_score', 0):.1f}%")
            logger.info(f"    - 短段捕捉: {similarity.get('short_score', 0):.1f}%")
            logger.info(f"    - 語氣詞匹配: {similarity.get('particle_score', 0):.1f}%")
            logger.info(f"    - 時間戳精度: {similarity.get('timestamp_accuracy', 0):.1f}%")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 極端配置測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'config_name': config['name'],
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

def main():
    """主函數"""
    
    test_file = "C:/Users/USER-ART0/Desktop/C0485.MP4"
    output_dir = Path("C:/Users/USER-ART0/Desktop/medium_extreme_tests")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not Path(test_file).exists():
        logger.error(f"❌ 測試檔案不存在: {test_file}")
        return None
    
    logger.info(f"🚀 Medium 極限優化測試")
    logger.info(f"📁 測試檔案: {Path(test_file).name}")
    logger.info(f"💾 輸出目錄: {output_dir}")
    logger.info(f"🎯 目標: 突破95.4%，達到98%+匹配度")
    logger.info(f"📋 極限配置數量: {len(EXTREME_MEDIUM_CONFIGS)}")
    
    all_results = []
    
    for i, config in enumerate(EXTREME_MEDIUM_CONFIGS):
        logger.info(f"\n{'='*80}")
        logger.info(f"📝 極限測試 {i+1}/{len(EXTREME_MEDIUM_CONFIGS)}")
        
        config_name_safe = config['name'].replace(' ', '_').replace('：', '_')
        output_file = output_dir / f"C0485_{config_name_safe}.srt"
        
        result = test_extreme_config(test_file, output_file, config)
        result['test_file'] = str(test_file)
        result['config_index'] = i + 1
        
        all_results.append(result)
        
        # 如果達到98%以上，特別標註
        if result.get('success') and result.get('similarity_analysis', {}).get('match_score', 0) >= 98:
            logger.info(f"🏆 發現突破性配置！匹配度: {result['similarity_analysis']['match_score']:.1f}%")
        
        time.sleep(1)
    
    # 最終分析
    logger.info(f"\n{'='*80}")
    logger.info(f"🏆 Medium 極限優化測試結果分析")
    logger.info(f"{'='*80}")
    
    successful_results = [r for r in all_results if r.get('success', False)]
    
    if successful_results:
        # 按匹配度排序
        successful_results.sort(key=lambda x: x.get('similarity_analysis', {}).get('match_score', 0), reverse=True)
        
        logger.info(f"\n🥇 極限配置排行榜:")
        for i, result in enumerate(successful_results):
            match_score = result.get('similarity_analysis', {}).get('match_score', 0)
            symbol = "🔥" if match_score >= 98 else "⭐" if match_score >= 96 else "✓"
            logger.info(f"  {symbol} {i+1}. {result['config_name']}: {match_score:.1f}%")
            logger.info(f"      段落數: {result['segment_count']}, 處理速度: {result['real_time_factor']:.2f}x")
        
        # 冠軍配置詳細分析
        champion = successful_results[0]
        logger.info(f"\n🏆 冠軍配置分析: {champion['config_name']}")
        sim = champion.get('similarity_analysis', {})
        if sim:
            logger.info(f"  📊 詳細得分:")
            logger.info(f"    - 總匹配度: {sim.get('match_score', 0):.1f}%")
            logger.info(f"    - 段落匹配: {sim.get('segment_score', 0):.1f}% (權重40%)")
            logger.info(f"    - 時長匹配: {sim.get('duration_score', 0):.1f}% (權重30%)")
            logger.info(f"    - 短段捕捉: {sim.get('short_score', 0):.1f}% (權重20%)")
            logger.info(f"    - 語氣詞匹配: {sim.get('particle_score', 0):.1f}% (權重10%)")
            logger.info(f"    - 時間戳精度: {sim.get('timestamp_accuracy', 0):.1f}%")
            
            logger.info(f"  📈 數據對比:")
            logger.info(f"    - 參考段落: {sim.get('reference_segments', 0)} vs 生成: {sim.get('generated_segments', 0)}")
            logger.info(f"    - 段落比例: {sim.get('segment_ratio', 0):.3f}")
            logger.info(f"    - 平均時長: 參考{sim.get('avg_ref_duration', 0):.3f}s vs 生成{sim.get('avg_gen_duration', 0):.3f}s")
    
    # 保存極限測試報告
    report = {
        'test_metadata': {
            'test_type': 'extreme_optimization',
            'test_file': test_file,
            'baseline_score': 95.4,
            'target_score': 98.0,
            'total_configs': len(EXTREME_MEDIUM_CONFIGS),
            'successful_configs': len(successful_results),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        'test_results': all_results,
        'champion_config': successful_results[0] if successful_results else None,
        'breakthrough_configs': [r for r in successful_results 
                               if r.get('similarity_analysis', {}).get('match_score', 0) >= 98]
    }
    
    report_file = output_dir / 'medium_extreme_optimization_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n✅ Medium 極限優化測試完成！")
    logger.info(f"📋 詳細報告: {report_file}")
    
    # 最終結論
    if successful_results:
        best_score = successful_results[0].get('similarity_analysis', {}).get('match_score', 0)
        if best_score >= 98:
            logger.info(f"🎉 突破成功！最佳匹配度: {best_score:.1f}%")
        elif best_score > 95.4:
            logger.info(f"📈 優化成功！提升至: {best_score:.1f}% (基線: 95.4%)")
        else:
            logger.info(f"📊 測試完成，最佳: {best_score:.1f}% (仍需優化)")
    
    return report

if __name__ == "__main__":
    try:
        report = main()
        if report and report['test_metadata']['successful_configs'] > 0:
            best = report['champion_config']
            best_score = best.get('similarity_analysis', {}).get('match_score', 0) if best else 0
            breakthrough_count = len(report.get('breakthrough_configs', []))
            
            print(f"\n🎯 Medium 極限優化測試完成！")
            print(f"成功配置: {report['test_metadata']['successful_configs']}/{report['test_metadata']['total_configs']}")
            print(f"最佳匹配度: {best_score:.1f}%")
            if breakthrough_count > 0:
                print(f"🔥 突破性配置: {breakthrough_count}個 (≥98%)")
        else:
            print(f"\n💥 極限測試失敗！")
    except Exception as e:
        logger.error(f"❌ 主程序失敗: {e}")
        sys.exit(1)