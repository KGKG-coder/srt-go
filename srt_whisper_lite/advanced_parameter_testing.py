#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
進階參數測試腳本
測試多種VAD參數組合、模型配置和處理策略
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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('advanced_testing.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# 添加當前目錄到路徑
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from simplified_subtitle_core import SimplifiedSubtitleCore
    from subtitle_formatter import SubtitleFormatter
    logger.info("核心模組導入成功")
except ImportError as e:
    logger.error(f"模組導入失敗: {e}")
    sys.exit(1)

def run_vad_parameter_test(test_file, output_base, vad_configs):
    """
    測試多種VAD參數配置
    """
    results = []
    
    for i, config in enumerate(vad_configs):
        logger.info(f"\n=== VAD測試 {i+1}/{len(vad_configs)}: {config['name']} ===")
        
        try:
            # 創建輸出目錄
            output_dir = Path(output_base) / f"vad_test_{i+1}_{config['name'].replace(' ', '_')}"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 記錄開始時間
            start_time = time.time()
            
            # 修改VAD參數的臨時實現
            # 由於需要深度修改，我們通過環境變數傳遞參數
            os.environ['CUSTOM_VAD_THRESHOLD'] = str(config['threshold'])
            os.environ['CUSTOM_VAD_MIN_SPEECH'] = str(config['min_speech_duration'])
            os.environ['CUSTOM_VAD_MIN_SILENCE'] = str(config['min_silence_duration'])
            os.environ['CUSTOM_VAD_SPEECH_PAD'] = str(config['speech_pad'])
            os.environ['ENABLE_ULTRA_SENSITIVE'] = str(config.get('ultra_sensitive', True))
            
            # 創建核心實例
            core = SimplifiedSubtitleCore(
                model_size=config.get('model', 'large-v2'),
                device='cpu',
                compute_type='int8'
            )
            
            # 初始化模型
            if not core.initialize():
                logger.error(f"模型初始化失敗: {config['name']}")
                continue
            
            # 生成字幕
            output_file = output_dir / f"{Path(test_file).stem}.srt"
            success = core.generate_subtitle(
                test_file,
                str(output_file),
                language=None,
                output_language=None,
                format='srt'
            )
            
            # 記錄結果
            end_time = time.time()
            processing_time = end_time - start_time
            
            if success and output_file.exists():
                # 分析生成的字幕
                srt_content = output_file.read_text(encoding='utf-8')
                segments = len([line for line in srt_content.split('\n') if line.strip() and '-->' in line])
                
                result = {
                    'config_name': config['name'],
                    'vad_threshold': config['threshold'],
                    'min_speech_duration': config['min_speech_duration'],
                    'min_silence_duration': config['min_silence_duration'], 
                    'speech_pad': config['speech_pad'],
                    'model': config.get('model', 'large-v2'),
                    'segments_count': segments,
                    'processing_time': round(processing_time, 2),
                    'success': True,
                    'output_file': str(output_file)
                }
                
                logger.info(f"✅ {config['name']}: {segments}段, {processing_time:.2f}秒")
                
            else:
                result = {
                    'config_name': config['name'],
                    'success': False,
                    'error': '字幕生成失敗'
                }
                logger.error(f"❌ {config['name']}: 生成失敗")
            
            results.append(result)
            
        except Exception as e:
            logger.error(f"❌ {config['name']} 測試失敗: {e}")
            results.append({
                'config_name': config['name'],
                'success': False,
                'error': str(e)
            })
        
        finally:
            # 清理環境變數
            for env_var in ['CUSTOM_VAD_THRESHOLD', 'CUSTOM_VAD_MIN_SPEECH', 
                           'CUSTOM_VAD_MIN_SILENCE', 'CUSTOM_VAD_SPEECH_PAD', 'ENABLE_ULTRA_SENSITIVE']:
                if env_var in os.environ:
                    del os.environ[env_var]
    
    return results

def main():
    """主測試函數"""
    logger.info("🔬 開始進階參數測試")
    
    # 測試檔案
    test_file = "C:/Users/USER-ART0/Desktop/hutest.mp3"
    output_base = "C:/Users/USER-ART0/Desktop/advanced_parameter_tests"
    
    # 定義測試配置
    vad_test_configs = [
        {
            'name': 'Ultra_Sensitive_Current',
            'threshold': 0.15,
            'min_speech_duration': 100,
            'min_silence_duration': 300,
            'speech_pad': 100,
            'model': 'large-v2',
            'ultra_sensitive': True
        },
        {
            'name': 'Extreme_Sensitive_005',
            'threshold': 0.05,  # 極限敏感
            'min_speech_duration': 50,   # 極短語音
            'min_silence_duration': 200,  # 極短靜音
            'speech_pad': 50,
            'model': 'large-v2',
            'ultra_sensitive': True
        },
        {
            'name': 'Extreme_Sensitive_001',
            'threshold': 0.01,  # 最極限敏感
            'min_speech_duration': 30,
            'min_silence_duration': 100,
            'speech_pad': 30,
            'model': 'large-v2',
            'ultra_sensitive': True
        },
        {
            'name': 'Balanced_Enhanced',
            'threshold': 0.25,
            'min_speech_duration': 120,
            'min_silence_duration': 400,
            'speech_pad': 120,
            'model': 'large-v2',
            'ultra_sensitive': True
        },
        {
            'name': 'Large_V3_Ultra',
            'threshold': 0.15,
            'min_speech_duration': 100,
            'min_silence_duration': 300,
            'speech_pad': 100,
            'model': 'large-v3',
            'ultra_sensitive': True
        },
        {
            'name': 'Medium_Ultra', 
            'threshold': 0.15,
            'min_speech_duration': 100,
            'min_silence_duration': 300,
            'speech_pad': 100,
            'model': 'medium',
            'ultra_sensitive': True
        },
        {
            'name': 'Conservative_High_Quality',
            'threshold': 0.4,
            'min_speech_duration': 200,
            'min_silence_duration': 600,
            'speech_pad': 200,
            'model': 'large-v2',
            'ultra_sensitive': False
        }
    ]
    
    # 執行VAD參數測試
    logger.info(f"🎯 測試 {len(vad_test_configs)} 種VAD配置")
    vad_results = run_vad_parameter_test(test_file, output_base, vad_test_configs)
    
    # 生成測試報告
    report = {
        'test_summary': {
            'total_configs': len(vad_test_configs),
            'successful_tests': len([r for r in vad_results if r.get('success', False)]),
            'test_file': test_file,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        'vad_parameter_tests': vad_results
    }
    
    # 保存測試報告
    report_file = Path(output_base) / 'advanced_parameter_test_report.json'
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 輸出簡要統計
    logger.info(f"\n📊 測試完成統計:")
    logger.info(f"總配置數: {report['test_summary']['total_configs']}")
    logger.info(f"成功測試: {report['test_summary']['successful_tests']}")
    logger.info(f"詳細報告: {report_file}")
    
    # 輸出最佳結果排序
    successful_results = [r for r in vad_results if r.get('success', False)]
    if successful_results:
        logger.info(f"\n🏆 段落數排序 (細分程度):")
        sorted_by_segments = sorted(successful_results, key=lambda x: x.get('segments_count', 0), reverse=True)
        for i, result in enumerate(sorted_by_segments[:5]):
            logger.info(f"{i+1}. {result['config_name']}: {result.get('segments_count', 0)}段 ({result.get('processing_time', 0):.2f}s)")
    
    return report

if __name__ == "__main__":
    try:
        report = main()
        print(f"\n✅ 進階參數測試完成！")
        print(f"測試報告已保存")
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
        sys.exit(1)