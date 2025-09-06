#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
複雜音頻VAD參數測試
測試背景音樂、多語言、低音質等複雜環境下的VAD參數效果
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
    import numpy as np
    logger.info("Faster-Whisper 模組導入成功")
except ImportError as e:
    logger.error(f"Faster-Whisper 導入失敗: {e}")
    sys.exit(1)

def test_complex_audio_vad(audio_file, output_dir):
    """
    測試複雜音頻環境下的VAD參數效果
    """
    
    # 確保輸出目錄存在
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 針對複雜音頻的VAD配置
    complex_vad_configs = [
        {
            'name': 'Large_V3_Ultra_Sensitive',
            'model': 'large-v3',
            'vad': {
                "threshold": 0.15,
                "min_speech_duration_ms": 100,
                "min_silence_duration_ms": 300,
                "speech_pad_ms": 100
            }
        },
        {
            'name': 'Large_V3_Extreme_001',
            'model': 'large-v3',
            'vad': {
                "threshold": 0.01,  # 極限敏感
                "min_speech_duration_ms": 30,
                "min_silence_duration_ms": 100,
                "speech_pad_ms": 30
            }
        },
        {
            'name': 'Large_V3_Conservative',
            'model': 'large-v3',
            'vad': {
                "threshold": 0.5,   # 保守設定
                "min_speech_duration_ms": 300,
                "min_silence_duration_ms": 800,
                "speech_pad_ms": 250
            }
        },
        {
            'name': 'Large_V2_Ultra_Sensitive',
            'model': 'large-v2',
            'vad': {
                "threshold": 0.15,
                "min_speech_duration_ms": 100,
                "min_silence_duration_ms": 300,
                "speech_pad_ms": 100
            }
        },
        {
            'name': 'Large_V2_Extreme_001',
            'model': 'large-v2',
            'vad': {
                "threshold": 0.01,
                "min_speech_duration_ms": 30,
                "min_silence_duration_ms": 100,
                "speech_pad_ms": 30
            }
        },
        {
            'name': 'Medium_Ultra_Sensitive',
            'model': 'medium',
            'vad': {
                "threshold": 0.15,
                "min_speech_duration_ms": 100,
                "min_silence_duration_ms": 300,
                "speech_pad_ms": 100
            }
        }
    ]
    
    logger.info(f"🎵 開始複雜音頻VAD測試: {audio_file}")
    logger.info(f"🔬 測試 {len(complex_vad_configs)} 種配置")
    
    results = []
    
    for i, config in enumerate(complex_vad_configs):
        logger.info(f"\n=== 測試 {i+1}/{len(complex_vad_configs)}: {config['name']} ===")
        
        try:
            start_time = time.time()
            
            # 載入模型
            model = WhisperModel(config['model'], device="cpu", compute_type="int8")
            load_time = time.time() - start_time
            
            # 執行轉錄
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
            
            # 生成SRT
            srt_content = generate_srt_from_segments(segment_list)
            output_file = output_path / f"{config['name']}_complex_result.srt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            # 計算統計信息
            total_speech_duration = sum(seg.end - seg.start for seg in segment_list)
            avg_segment_duration = total_speech_duration / len(segment_list) if segment_list else 0
            
            result = {
                'success': True,
                'config_name': config['name'],
                'model': config['model'],
                'vad_threshold': config['vad']['threshold'],
                'segment_count': len(segment_list),
                'total_duration': info.duration,
                'total_speech_duration': round(total_speech_duration, 2),
                'avg_segment_duration': round(avg_segment_duration, 2),
                'language': info.language,
                'language_probability': round(info.language_probability, 4),
                'load_time': round(load_time, 2),
                'transcribe_time': round(transcribe_time, 2),
                'segments_per_minute': round(len(segment_list) / (info.duration / 60), 1),
                'output_file': str(output_file)
            }
            
            logger.info(f"✅ {config['name']}: {len(segment_list)}段, {transcribe_time:.1f}s, 信心度:{info.language_probability:.3f}")
            logger.info(f"   平均段落長度: {avg_segment_duration:.2f}s, 段落密度: {result['segments_per_minute']:.1f}段/分鐘")
            
            results.append(result)
            
        except Exception as e:
            logger.error(f"❌ {config['name']} 測試失敗: {e}")
            results.append({
                'success': False,
                'config_name': config['name'],
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

def main():
    """主函數"""
    
    # 測試多種複雜音頻文件
    test_files = [
        {
            'file': "C:/Users/USER-ART0/Desktop/DRLIN.mp4",
            'description': "廣告影片 (背景音樂)",
            'output_suffix': "background_music"
        },
        {
            'file': "C:/Users/USER-ART0/Desktop/C0485.MP4", 
            'description': "醫療對話 (對話間隙)",
            'output_suffix': "medical_dialogue"
        }
    ]
    
    all_results = {}
    
    for test_file in test_files:
        file_path = test_file['file']
        if not Path(file_path).exists():
            logger.warning(f"測試文件不存在: {file_path}")
            continue
            
        logger.info(f"\n🎯 開始測試: {test_file['description']}")
        logger.info(f"檔案: {file_path}")
        
        output_dir = f"C:/Users/USER-ART0/Desktop/complex_vad_tests_{test_file['output_suffix']}"
        
        try:
            results = test_complex_audio_vad(file_path, output_dir)
            all_results[test_file['output_suffix']] = {
                'file_info': test_file,
                'results': results
            }
            
            # 生成該檔案的報告
            successful_results = [r for r in results if r.get('success', False)]
            if successful_results:
                logger.info(f"\n📊 {test_file['description']} 測試結果:")
                sorted_results = sorted(successful_results, key=lambda x: x['segment_count'], reverse=True)
                
                for i, result in enumerate(sorted_results):
                    logger.info(f"{i+1:2d}. {result['config_name']:25s}: {result['segment_count']:3d}段, VAD:{result['vad_threshold']:5.2f}, 信心度:{result['language_probability']:.3f}")
            
        except Exception as e:
            logger.error(f"❌ {test_file['description']} 測試失敗: {e}")
    
    # 生成綜合報告
    if all_results:
        comprehensive_report = {
            'test_summary': {
                'total_files': len(test_files),
                'completed_files': len(all_results),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'detailed_results': all_results
        }
        
        report_file = Path("C:/Users/USER-ART0/Desktop/Complex_Audio_VAD_Comprehensive_Report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n✅ 複雜音頻VAD測試完成！")
        logger.info(f"📋 綜合報告: {report_file}")
        
        return comprehensive_report
    
    return None

if __name__ == "__main__":
    try:
        report = main()
        if report:
            print(f"\n🎉 複雜音頻VAD測試成功完成！")
        else:
            print(f"\n💥 測試失敗或無可用測試檔案！")
    except Exception as e:
        logger.error(f"❌ 主程序失敗: {e}")
        sys.exit(1)