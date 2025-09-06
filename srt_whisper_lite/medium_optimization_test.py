#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medium 模型最佳參數調教腳本
目標：匹配手動編輯的test1.srt前34段的細緻分割風格
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

# Medium 模型調教配置
MEDIUM_TEST_CONFIGS = [
    {
        "name": "Medium 超敏感配置",
        "description": "極低VAD閾值，捕捉所有語音",
        "model": "medium",
        "vad_parameters": {
            "threshold": 0.05,              # 極低閾值
            "min_speech_duration_ms": 50,   # 極短語音
            "min_silence_duration_ms": 100, # 極短靜音
            "speech_pad_ms": 50             # 短填充
        },
        "whisper_params": {
            "beam_size": 3,                 # 較低beam size提高分割敏感度
            "word_timestamps": True,
            "condition_on_previous_text": False,  # 減少上下文依賴
            "compression_ratio_threshold": 1.8,  # 更低閾值
            "log_prob_threshold": -1.5,     # 更低閾值
            "no_speech_threshold": 0.4      # 更低閾值
        }
    },
    {
        "name": "Medium 細分配置",
        "description": "針對細緻分割優化",
        "model": "medium",
        "vad_parameters": {
            "threshold": 0.10,              # 低閾值
            "min_speech_duration_ms": 100,  # 短語音
            "min_silence_duration_ms": 150, # 短靜音
            "speech_pad_ms": 75             # 中等填充
        },
        "whisper_params": {
            "beam_size": 5,
            "word_timestamps": True,
            "condition_on_previous_text": True,
            "compression_ratio_threshold": 2.0,
            "log_prob_threshold": -1.2,
            "no_speech_threshold": 0.5
        }
    },
    {
        "name": "Medium 平衡配置",
        "description": "平衡準確性與細分度",
        "model": "medium",
        "vad_parameters": {
            "threshold": 0.20,              # 中等閾值
            "min_speech_duration_ms": 150,  # 標準語音
            "min_silence_duration_ms": 250, # 標準靜音
            "speech_pad_ms": 100            # 標準填充
        },
        "whisper_params": {
            "beam_size": 5,
            "word_timestamps": True,
            "condition_on_previous_text": True,
            "compression_ratio_threshold": 2.4,
            "log_prob_threshold": -1.0,
            "no_speech_threshold": 0.6
        }
    }
]

def analyze_segment_similarity(generated_segments, reference_file, max_segments=34):
    """分析與參考檔案的相似度"""
    
    # 讀取參考檔案前34段
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
        
        logger.info(f"參考檔案載入成功，前{max_segments}段共 {len(ref_segments)} 個段落")
        
        # 分析相似度
        ref_total_time = ref_segments[-1]['end'] if ref_segments else 0
        gen_relevant_segments = [seg for seg in generated_segments if seg['start'] <= ref_total_time]
        
        similarity_metrics = {
            'reference_segments': len(ref_segments),
            'generated_segments': len(gen_relevant_segments),
            'segment_ratio': len(gen_relevant_segments) / len(ref_segments) if ref_segments else 0,
            'avg_ref_duration': sum(seg['end'] - seg['start'] for seg in ref_segments) / len(ref_segments) if ref_segments else 0,
            'avg_gen_duration': sum(seg['duration'] for seg in gen_relevant_segments) / len(gen_relevant_segments) if gen_relevant_segments else 0,
            'time_coverage': ref_total_time,
            'short_segments_ref': sum(1 for seg in ref_segments if (seg['end'] - seg['start']) < 1.0),
            'short_segments_gen': sum(1 for seg in gen_relevant_segments if seg['duration'] < 1.0)
        }
        
        # 計算匹配度分數 (0-100)
        segment_score = min(100, (similarity_metrics['segment_ratio'] * 100))
        duration_score = 100 - min(100, abs(similarity_metrics['avg_ref_duration'] - similarity_metrics['avg_gen_duration']) * 100)
        short_seg_score = min(100, (similarity_metrics['short_segments_gen'] / similarity_metrics['short_segments_ref'] * 100)) if similarity_metrics['short_segments_ref'] > 0 else 50
        
        overall_score = (segment_score * 0.4 + duration_score * 0.3 + short_seg_score * 0.3)
        similarity_metrics['match_score'] = round(overall_score, 1)
        
        return similarity_metrics
        
    except Exception as e:
        logger.error(f"參考檔案分析失敗: {e}")
        return {}

def test_medium_config(audio_file, output_file, config):
    """測試Medium配置"""
    try:
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
        
        # 分析與參考檔案的相似度
        similarity = analyze_segment_similarity(segment_list, "C:/Users/USER-ART0/Desktop/test1.srt")
        
        # 基本統計
        if segment_list:
            total_speech_time = sum(seg['duration'] for seg in segment_list)
            avg_segment_duration = total_speech_time / len(segment_list)
            segments_per_second = len(segment_list) / info.duration
            speech_ratio = total_speech_time / info.duration
        else:
            total_speech_time = avg_segment_duration = segments_per_second = speech_ratio = 0
        
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
            
            # 相似度分析
            'similarity_analysis': similarity,
            
            # 語言檢測
            'language': info.language,
            'language_probability': round(info.language_probability, 4),
            
            # 性能統計
            'model_load_time': round(model_load_time, 2),
            'transcribe_time': round(transcribe_time, 2),
            'total_time': round(total_time, 2),
            'real_time_factor': round(transcribe_time / info.duration, 2),
            
            # 檔案資訊
            'output_file': str(output_file),
            'first_10_segments': segment_list[:10]  # 前10段詳情
        }
        
        # 輸出結果摘要
        logger.info(f"\n📊 測試結果:")
        logger.info(f"  ✅ 段落數: {len(segment_list)}段")
        logger.info(f"  ✅ 段落密度: {segments_per_second:.3f}段/秒")
        logger.info(f"  ✅ 平均段落時長: {avg_segment_duration:.3f}秒")
        logger.info(f"  ✅ 處理速度: {result['real_time_factor']:.2f}x實時")
        logger.info(f"  ✅ 語言: {info.language} (信心度: {info.language_probability:.3f})")
        
        if similarity:
            logger.info(f"  📈 與參考檔案匹配度: {similarity.get('match_score', 0):.1f}%")
            logger.info(f"    - 段落數比例: {similarity.get('segment_ratio', 0):.2f}")
            logger.info(f"    - 平均時長差異: {abs(similarity.get('avg_ref_duration', 0) - similarity.get('avg_gen_duration', 0)):.3f}秒")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
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
    
    # 測試檔案
    test_file = "C:/Users/USER-ART0/Desktop/C0485.MP4"
    output_dir = Path("C:/Users/USER-ART0/Desktop/medium_optimization_tests")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not Path(test_file).exists():
        logger.error(f"❌ 測試檔案不存在: {test_file}")
        return None
    
    logger.info(f"🚀 Medium 模型最佳化參數測試")
    logger.info(f"📁 測試檔案: {Path(test_file).name}")
    logger.info(f"💾 輸出目錄: {output_dir}")
    logger.info(f"📋 配置數量: {len(MEDIUM_TEST_CONFIGS)}")
    
    all_results = []
    
    for i, config in enumerate(MEDIUM_TEST_CONFIGS):
        logger.info(f"\n{'='*80}")
        logger.info(f"📝 測試 {i+1}/{len(MEDIUM_TEST_CONFIGS)}")
        
        # 生成輸出檔名
        config_name_safe = config['name'].replace(' ', '_').replace('：', '_')
        output_file = output_dir / f"C0485_{config_name_safe}.srt"
        
        # 執行測試
        result = test_medium_config(test_file, output_file, config)
        result['test_file'] = str(test_file)
        result['config_index'] = i + 1
        
        all_results.append(result)
        
        # 短暫延遲
        time.sleep(1)
    
    # 分析所有結果
    logger.info(f"\n{'='*80}")
    logger.info(f"📊 Medium 模型測試結果分析")
    logger.info(f"{'='*80}")
    
    successful_results = [r for r in all_results if r.get('success', False)]
    
    if successful_results:
        # 按匹配度排序
        successful_results.sort(key=lambda x: x.get('similarity_analysis', {}).get('match_score', 0), reverse=True)
        
        logger.info(f"\n🏆 最佳配置排名:")
        for i, result in enumerate(successful_results):
            match_score = result.get('similarity_analysis', {}).get('match_score', 0)
            logger.info(f"  {i+1}. {result['config_name']}: {match_score:.1f}% 匹配度")
            logger.info(f"     段落數: {result['segment_count']}, 密度: {result['segments_per_second']:.3f}段/秒")
            logger.info(f"     處理速度: {result['real_time_factor']:.2f}x實時")
        
        # 詳細分析最佳配置
        best_config = successful_results[0]
        logger.info(f"\n🎯 最佳配置詳細分析: {best_config['config_name']}")
        sim = best_config.get('similarity_analysis', {})
        if sim:
            logger.info(f"  參考檔案前34段: {sim.get('reference_segments', 0)} 段")
            logger.info(f"  生成對應區間: {sim.get('generated_segments', 0)} 段")
            logger.info(f"  段落數比例: {sim.get('segment_ratio', 0):.2f}")
            logger.info(f"  平均時長 - 參考: {sim.get('avg_ref_duration', 0):.3f}秒")
            logger.info(f"  平均時長 - 生成: {sim.get('avg_gen_duration', 0):.3f}秒")
    
    # 保存完整報告
    report = {
        'test_metadata': {
            'test_file': test_file,
            'total_configs': len(MEDIUM_TEST_CONFIGS),
            'successful_configs': len(successful_results),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        'test_results': all_results,
        'best_config': successful_results[0] if successful_results else None
    }
    
    report_file = output_dir / 'medium_optimization_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n✅ Medium 最佳化測試完成！")
    logger.info(f"📋 詳細報告已保存: {report_file}")
    
    return report

if __name__ == "__main__":
    try:
        report = main()
        if report and report['test_metadata']['successful_configs'] > 0:
            print(f"\n🎉 Medium 最佳化測試成功完成！")
            print(f"成功測試: {report['test_metadata']['successful_configs']}/{report['test_metadata']['total_configs']}")
            best = report['best_config']
            if best:
                print(f"最佳配置: {best['config_name']} (匹配度: {best.get('similarity_analysis', {}).get('match_score', 0):.1f}%)")
        else:
            print(f"\n💥 測試失敗！")
    except Exception as e:
        logger.error(f"❌ 主程序失敗: {e}")
        sys.exit(1)