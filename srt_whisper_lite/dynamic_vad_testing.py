#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動態VAD參數測試
直接調用Faster-Whisper進行多種VAD參數測試
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
    import numpy as np
    logger.info("Faster-Whisper 模組導入成功")
except ImportError as e:
    logger.error(f"Faster-Whisper 導入失敗: {e}")
    sys.exit(1)

def test_vad_configuration(audio_file, model_size, vad_config, output_file):
    """
    測試特定VAD配置
    """
    try:
        logger.info(f"測試VAD配置: {vad_config}")
        
        # 載入模型
        start_time = time.time()
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        load_time = time.time() - start_time
        
        # 執行轉錄
        transcribe_start = time.time()
        segments, info = model.transcribe(
            audio_file,
            language=None,  # 自動檢測
            beam_size=5,
            word_timestamps=True,
            vad_filter=True,
            vad_parameters=vad_config
        )
        
        # 處理結果
        segment_list = []
        for segment in segments:
            segment_data = {
                'start': segment.start,
                'end': segment.end,
                'text': segment.text.strip(),
                'words': []
            }
            
            if hasattr(segment, 'words') and segment.words:
                for word in segment.words:
                    segment_data['words'].append({
                        'start': word.start,
                        'end': word.end,
                        'word': word.word,
                        'probability': word.probability
                    })
            
            segment_list.append(segment_data)
        
        transcribe_time = time.time() - transcribe_start
        
        # 生成SRT格式
        srt_content = generate_srt_from_segments(segment_list)
        
        # 保存結果
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        # 返回統計信息
        return {
            'success': True,
            'segment_count': len(segment_list),
            'total_duration': info.duration,
            'language': info.language,
            'language_probability': info.language_probability,
            'load_time': round(load_time, 2),
            'transcribe_time': round(transcribe_time, 2),
            'vad_config': vad_config,
            'output_file': str(output_file)
        }
        
    except Exception as e:
        logger.error(f"VAD測試失敗: {e}")
        return {
            'success': False,
            'error': str(e),
            'vad_config': vad_config
        }

def generate_srt_from_segments(segments):
    """
    從段落生成SRT格式字幕
    """
    def format_timestamp(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    srt_content = ""
    for i, segment in enumerate(segments, 1):
        start_time = format_timestamp(segment['start'])
        end_time = format_timestamp(segment['end'])
        text = segment['text']
        
        srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
    
    return srt_content

def run_comprehensive_vad_tests(audio_file, output_dir):
    """
    執行全面的VAD參數測試
    """
    
    # 確保輸出目錄存在
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 定義測試配置
    test_configs = [
        {
            'name': 'Current_Ultra_Sensitive',
            'model': 'large-v2', 
            'vad': {
                "threshold": 0.15,
                "min_speech_duration_ms": 100,
                "min_silence_duration_ms": 300,
                "speech_pad_ms": 100
            }
        },
        {
            'name': 'Extreme_Sensitive_005',
            'model': 'large-v2',
            'vad': {
                "threshold": 0.05,
                "min_speech_duration_ms": 50,
                "min_silence_duration_ms": 200,
                "speech_pad_ms": 50
            }
        },
        {
            'name': 'Extreme_Sensitive_001',
            'model': 'large-v2',
            'vad': {
                "threshold": 0.01,
                "min_speech_duration_ms": 30,
                "min_silence_duration_ms": 100,
                "speech_pad_ms": 30
            }
        },
        {
            'name': 'Ultra_Conservative',
            'model': 'large-v2',
            'vad': {
                "threshold": 0.5,
                "min_speech_duration_ms": 300,
                "min_silence_duration_ms": 800,
                "speech_pad_ms": 250
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
        },
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
            'name': 'Balanced_Enhanced',
            'model': 'large-v2',
            'vad': {
                "threshold": 0.25,
                "min_speech_duration_ms": 120,
                "min_silence_duration_ms": 400,
                "speech_pad_ms": 120
            }
        },
        {
            'name': 'Whisper_Default',
            'model': 'large-v2',
            'vad': {
                "threshold": 0.5,
                "min_speech_duration_ms": 250,
                "min_silence_duration_ms": 2000,
                "speech_pad_ms": 400
            }
        }
    ]
    
    logger.info(f"🔬 開始執行 {len(test_configs)} 項VAD參數測試")
    
    results = []
    
    for i, config in enumerate(test_configs):
        logger.info(f"\n=== 測試 {i+1}/{len(test_configs)}: {config['name']} ===")
        logger.info(f"模型: {config['model']}")
        logger.info(f"VAD: threshold={config['vad']['threshold']}, speech={config['vad']['min_speech_duration_ms']}ms, silence={config['vad']['min_silence_duration_ms']}ms")
        
        output_file = output_path / f"{config['name']}_result.srt"
        
        result = test_vad_configuration(
            audio_file,
            config['model'],
            config['vad'],
            output_file
        )
        
        result['config_name'] = config['name']
        result['model'] = config['model']
        results.append(result)
        
        if result['success']:
            logger.info(f"✅ {config['name']}: {result['segment_count']}段, {result['transcribe_time']}s, 信心度:{result['language_probability']:.4f}")
        else:
            logger.error(f"❌ {config['name']}: {result.get('error', '未知錯誤')}")
    
    # 生成詳細報告
    report = {
        'test_metadata': {
            'audio_file': str(audio_file),
            'total_configs': len(test_configs),
            'successful_tests': len([r for r in results if r['success']]),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        'test_results': results
    }
    
    # 保存報告
    report_file = output_path / 'comprehensive_vad_test_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n📊 測試完成！詳細報告: {report_file}")
    
    # 輸出排名
    successful_results = [r for r in results if r['success']]
    if successful_results:
        logger.info(f"\n🏆 測試結果排名 (按段落數排序):")
        sorted_results = sorted(successful_results, key=lambda x: x['segment_count'], reverse=True)
        
        for i, result in enumerate(sorted_results[:8]):
            logger.info(f"{i+1:2d}. {result['config_name']:25s}: {result['segment_count']:3d}段, {result['transcribe_time']:5.1f}s, 信心度:{result['language_probability']:.3f}")
    
    return report

def main():
    """主函數"""
    
    # 測試文件
    audio_file = "C:/Users/USER-ART0/Desktop/hutest.mp3"
    output_dir = "C:/Users/USER-ART0/Desktop/comprehensive_vad_tests"
    
    if not Path(audio_file).exists():
        logger.error(f"測試文件不存在: {audio_file}")
        return
    
    logger.info(f"🎯 開始全面VAD參數測試")
    logger.info(f"測試文件: {audio_file}")
    logger.info(f"輸出目錄: {output_dir}")
    
    try:
        report = run_comprehensive_vad_tests(audio_file, output_dir)
        logger.info(f"\n✅ 全面VAD測試完成！")
        return report
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
        return None

if __name__ == "__main__":
    report = main()
    if report:
        print(f"\n🎉 測試成功完成！")
    else:
        print(f"\n💥 測試失敗！")
        sys.exit(1)