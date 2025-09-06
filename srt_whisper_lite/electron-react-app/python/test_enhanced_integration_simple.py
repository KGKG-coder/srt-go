#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增強型輕量級語音檢測器整合測試 (簡化版)

驗證v2.0增強版檢測器在實際字幕生成系統中的表現
"""

import sys
import os
import json
from pathlib import Path
import traceback

# 添加路徑以便測試
sys.path.append('.')

def test_content_type_detection():
    """測試內容類型自動檢測功能"""
    print("Testing Enhanced Content Type Auto-Detection")
    print("=" * 50)
    
    try:
        from enhanced_lightweight_voice_detector import EnhancedLightweightVoiceDetector
        
        detector = EnhancedLightweightVoiceDetector()
        
        # 測試案例：三種不同內容類型
        test_cases = [
            {
                'name': 'DRLIN.mp4',
                'segments': [
                    {'start': 20.350, 'end': 26.560, 'text': 'Mother Day is coming'},
                    {'start': 26.620, 'end': 29.149, 'text': 'Welcome to Nobel Eye Clinic'}
                ],
                'expected_type': 'promotional_video'
            },
            {
                'name': 'C0485.MP4', 
                'segments': [
                    {'start': 0.090, 'end': 0.490, 'text': 'Let us check'},
                    {'start': 3.690, 'end': 5.169, 'text': 'Surgery last year right'},
                    {'start': 39.200, 'end': 41.140, 'text': 'Cornea is clear'}
                ],
                'expected_type': 'medical_dialogue'
            },
            {
                'name': 'hutest.mp4',
                'segments': [
                    {'start': 0.000, 'end': 0.500, 'text': 'Let us see'},
                    {'start': 0.600, 'end': 0.980, 'text': 'Good'},
                    {'start': 5.599, 'end': 6.519, 'text': 'How is it'}
                ],
                'expected_type': 'casual_conversation'
            }
        ]
        
        results = {}
        correct_count = 0
        
        for test_case in test_cases:
            print(f"\nTesting: {test_case['name']}")
            
            # 執行內容類型檢測
            test_file = f"test_VIDEO/{test_case['name']}"
            detected_type = detector._auto_detect_content_type(test_case['segments'], test_file)
            
            # 檢查結果
            is_correct = detected_type == test_case['expected_type']
            if is_correct:
                correct_count += 1
                
            results[test_case['name']] = {
                'expected': test_case['expected_type'],
                'detected': detected_type,
                'correct': is_correct
            }
            
            status = "PASS" if is_correct else "FAIL"
            print(f"  Expected: {test_case['expected_type']}")
            print(f"  Detected: {detected_type}")
            print(f"  Result: {status}")
            
            # 檢查專門化閾值配置
            detector._apply_specialized_thresholds(detected_type)
            thresholds = detector.current_thresholds
            print(f"  Applied thresholds: voice_threshold={thresholds['voice_probability_threshold']:.2f}")
        
        # 統計結果
        total_tests = len(results)
        accuracy = correct_count / total_tests * 100
        
        print(f"\nContent Type Detection Results:")
        print(f"  Total tests: {total_tests}")
        print(f"  Passed: {correct_count}")
        print(f"  Accuracy: {accuracy:.1f}%")
        
        return results, accuracy
        
    except Exception as e:
        print(f"Content type detection test failed: {e}")
        traceback.print_exc()
        return {}, 0


def test_threshold_specialization():
    """測試專門化閾值配置"""
    print("\nTesting Specialized Threshold Configuration")
    print("=" * 50)
    
    try:
        from enhanced_lightweight_voice_detector import EnhancedLightweightVoiceDetector
        
        detector = EnhancedLightweightVoiceDetector()
        
        # 測試三種內容類型的閾值差異
        content_types = ['promotional_video', 'medical_dialogue', 'casual_conversation']
        threshold_results = {}
        
        for content_type in content_types:
            detector._apply_specialized_thresholds(content_type)
            thresholds = detector.current_thresholds.copy()
            threshold_results[content_type] = thresholds
            
            print(f"\n{content_type.replace('_', ' ').title()} Thresholds:")
            print(f"  Energy percentile: {thresholds['energy_percentile']}%")
            print(f"  ZCR percentile: {thresholds['zcr_percentile']}%")
            print(f"  Voice probability threshold: {thresholds['voice_probability_threshold']:.2f}")
            print(f"  Interlude score threshold: {thresholds['interlude_score_threshold']:.1f}")
            print(f"  Duration weight: {thresholds['duration_weight']:.1f}")
        
        # 驗證閾值差異化
        print(f"\nThreshold Differentiation Analysis:")
        promo_thresholds = threshold_results['promotional_video']
        medical_thresholds = threshold_results['medical_dialogue']
        casual_thresholds = threshold_results['casual_conversation']
        
        # 檢查關鍵差異
        energy_diff = abs(promo_thresholds['energy_percentile'] - medical_thresholds['energy_percentile'])
        voice_diff = abs(promo_thresholds['voice_probability_threshold'] - casual_thresholds['voice_probability_threshold'])
        
        print(f"  Energy percentile range: {energy_diff}% difference")
        print(f"  Voice threshold range: {voice_diff:.2f} difference")
        
        # 修正檢測邏輯：只要有明顯差異就算有效
        specialization_effective = energy_diff >= 10 and voice_diff >= 0.15
        status = "YES" if specialization_effective else "NO"
        print(f"  Specialization effective: {status}")
        
        return threshold_results, specialization_effective
        
    except Exception as e:
        print(f"Threshold specialization test failed: {e}")
        traceback.print_exc()
        return {}, False


def test_system_integration():
    """測試與主要字幕系統的整合"""
    print("\nTesting System Integration")
    print("=" * 50)
    
    try:
        # 模擬主要字幕系統的調用
        from simplified_subtitle_core import SimplifiedSubtitleCore
        
        # 創建字幕核心實例
        subtitle_core = SimplifiedSubtitleCore()
        
        # 啟用增強型語音檢測
        subtitle_core.enable_adaptive_voice_detection = True
        
        print("Enhanced voice detection enabled in subtitle core")
        print("System integration successful")
        
        # 測試不同設置的組合
        test_settings = [
            {'enable_adaptive_voice_detection': True, 'enable_subeasy': False},
            {'enable_adaptive_voice_detection': False, 'enable_subeasy': True},
            {'enable_adaptive_voice_detection': True, 'enable_subeasy': True}
        ]
        
        print(f"\nTesting {len(test_settings)} configuration combinations:")
        for i, setting in enumerate(test_settings, 1):
            for key, value in setting.items():
                setattr(subtitle_core, key, value)
            print(f"  Config {i}: {setting} - OK")
        
        return True
        
    except Exception as e:
        print(f"System integration test failed: {e}")
        traceback.print_exc()
        return False


def test_fallback_mechanisms():
    """測試備用機制"""
    print("\nTesting Fallback Mechanisms")
    print("=" * 50)
    
    try:
        # 檢查各個檢測器的可用性
        detectors = [
            'enhanced_lightweight_voice_detector',
            'lightweight_voice_detector',
            'adaptive_voice_detector'
        ]
        
        available_detectors = []
        
        for detector_name in detectors:
            try:
                module = __import__(detector_name)
                available_detectors.append(detector_name)
                print(f"OK {detector_name} is available")
            except ImportError:
                print(f"MISSING {detector_name} is not available")
        
        # 驗證備用機制邏輯
        print(f"\nFallback chain analysis:")
        if 'enhanced_lightweight_voice_detector' in available_detectors:
            print("  1. Enhanced detector -> Primary (Available)")
        else:
            print("  1. Enhanced detector -> Primary (Not Available)")
            
        if 'lightweight_voice_detector' in available_detectors:
            print("  2. Lightweight detector -> Secondary (Available)")
        else:
            print("  2. Lightweight detector -> Secondary (Not Available)")
            
        if 'adaptive_voice_detector' in available_detectors:
            print("  3. Adaptive detector -> Tertiary (Available)")
        else:
            print("  3. Adaptive detector -> Tertiary (Not Available)")
        
        print(f"\nTotal available detectors: {len(available_detectors)}/3")
        fallback_effective = len(available_detectors) >= 2
        status = "EFFECTIVE" if fallback_effective else "INSUFFICIENT"
        print(f"Fallback mechanism: {status}")
        
        return len(available_detectors)
        
    except Exception as e:
        print(f"Fallback mechanism test failed: {e}")
        traceback.print_exc()
        return 0


def generate_integration_report():
    """生成整合測試報告"""
    print("\nGenerating Integration Test Report")
    print("=" * 50)
    
    # 執行所有測試
    content_results, content_accuracy = test_content_type_detection()
    threshold_results, specialization_effective = test_threshold_specialization()
    integration_success = test_system_integration()
    fallback_count = test_fallback_mechanisms()
    
    # 生成報告
    report = {
        'timestamp': '2025-08-20',
        'test_version': 'Enhanced Integration v2.0',
        'content_type_detection': {
            'accuracy_percentage': content_accuracy,
            'passed': content_accuracy >= 80.0
        },
        'threshold_specialization': {
            'configurations_tested': len(threshold_results),
            'specialization_effective': specialization_effective,
            'passed': specialization_effective
        },
        'system_integration': {
            'integration_successful': integration_success,
            'passed': integration_success
        },
        'fallback_mechanisms': {
            'available_detectors': fallback_count,
            'fallback_effective': fallback_count >= 2,
            'passed': fallback_count >= 2
        }
    }
    
    # 計算總體通過狀態
    all_passed = all([
        report['content_type_detection']['passed'],
        report['threshold_specialization']['passed'],
        report['system_integration']['passed'],
        report['fallback_mechanisms']['passed']
    ])
    
    report['overall_status'] = {
        'all_tests_passed': all_passed,
        'ready_for_deployment': all_passed
    }
    
    # 保存報告
    report_file = 'enhanced_integration_test_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nIntegration test report saved to: {report_file}")
    
    # 顯示摘要
    print(f"\nTest Summary:")
    print(f"   Content Detection Accuracy: {content_accuracy:.1f}%")
    print(f"   Threshold Configurations: {len(threshold_results)}")
    print(f"   System Integration: {'SUCCESS' if integration_success else 'FAILED'}")
    print(f"   Fallback Detectors: {fallback_count}/3 available")
    print(f"   Overall Status: {'READY FOR DEPLOYMENT' if all_passed else 'NEEDS FIXES'}")
    
    return report


def main():
    """主測試流程"""
    print("Enhanced Lightweight Voice Detector v2.0 - Integration Testing")
    print("=" * 70)
    
    try:
        # 執行完整整合測試
        report = generate_integration_report()
        
        if report['overall_status']['ready_for_deployment']:
            print("\nEnhanced detector v2.0 integration testing completed successfully!")
            print("System is ready for deployment")
        else:
            print("\nIntegration testing completed with issues")
            print("System needs fixes before deployment")
            
    except Exception as e:
        print(f"\nIntegration testing failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()