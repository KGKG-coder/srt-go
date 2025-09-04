#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
整合測試套件 - 智能FP16優先系統整合測試
專門測試智能模型選擇器和整個系統的整合功能
"""

import sys
import os
import json
import time
import subprocess
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "srt_whisper_lite" / "electron-react-app" / "python"))

def run_comprehensive_test():
    """運行綜合測試套件"""
    print("🔄 開始智能FP16優先系統整合測試")
    
    python_dir = project_root / "srt_whisper_lite" / "electron-react-app" / "python"
    test_script = python_dir / "comprehensive_test_suite.py"
    
    if not test_script.exists():
        print(f"❌ 測試腳本不存在: {test_script}")
        return False
    
    try:
        # 切換到Python目錄
        original_cwd = os.getcwd()
        os.chdir(python_dir)
        
        # 運行測試
        result = subprocess.run([
            sys.executable, "comprehensive_test_suite.py"
        ], capture_output=True, text=True, encoding='utf-8')
        
        os.chdir(original_cwd)
        
        if result.returncode == 0:
            print("✅ 智能FP16優先系統整合測試通過")
            print("📊 測試輸出:")
            print(result.stdout)
            return True
        else:
            print("❌ 智能FP16優先系統整合測試失敗")
            print("錯誤信息:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 測試執行異常: {str(e)}")
        return False

def run_ui_backend_integration():
    """運行UI-Backend整合測試"""
    print("\n🔄 開始UI-Backend整合測試")
    
    python_dir = project_root / "srt_whisper_lite" / "electron-react-app" / "python"
    test_script = python_dir / "test_ui_backend_integration.py"
    
    if not test_script.exists():
        print(f"❌ 測試腳本不存在: {test_script}")
        return False
    
    try:
        # 切換到Python目錄
        original_cwd = os.getcwd()
        os.chdir(python_dir)
        
        # 運行測試
        result = subprocess.run([
            sys.executable, "test_ui_backend_integration.py"
        ], capture_output=True, text=True, encoding='utf-8')
        
        os.chdir(original_cwd)
        
        if result.returncode == 0:
            print("✅ UI-Backend整合測試通過")
            print("📊 測試輸出:")
            print(result.stdout)
            return True
        else:
            print("❌ UI-Backend整合測試失敗")
            print("錯誤信息:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 測試執行異常: {str(e)}")
        return False

def generate_integration_report():
    """生成整合測試報告"""
    print("\n📊 生成整合測試報告")
    
    # 檢查測試結果文件
    python_dir = project_root / "srt_whisper_lite" / "electron-react-app" / "python"
    
    report_files = [
        python_dir / "comprehensive_test_report.json",
        python_dir / "ui_backend_integration_report.json"
    ]
    
    integration_report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'test_type': 'Integration Test Suite',
        'components_tested': [
            'IntelligentModelSelector',
            'PureFP16ModelManager', 
            'ElectronBackend Integration',
            'UI-Backend IPC Communication',
            'Auto Monitoring System'
        ],
        'test_results': {},
        'summary': {}
    }
    
    total_tests = 0
    passed_tests = 0
    
    for report_file in report_files:
        if report_file.exists():
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    file_name = report_file.stem
                    integration_report['test_results'][file_name] = data
                    
                    # 統計測試結果
                    if 'summary' in data:
                        if 'total_tests' in data['summary']:
                            total_tests += data['summary']['total_tests']
                        if 'passed_tests' in data['summary']:
                            passed_tests += data['summary']['passed_tests']
                    
            except Exception as e:
                print(f"⚠️  無法讀取報告文件 {report_file}: {str(e)}")
    
    # 生成摘要
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    integration_report['summary'] = {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': total_tests - passed_tests,
        'success_rate': f"{success_rate:.1f}%",
        'overall_status': '通過' if passed_tests == total_tests else '部分失敗'
    }
    
    # 保存整合報告
    output_file = Path(__file__).parent / "integration_test_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(integration_report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 整合測試報告已保存: {output_file}")
    
    # 打印摘要
    print("\n" + "="*50)
    print("📋 整合測試摘要")
    print("="*50)
    print(f"總測試數: {total_tests}")
    print(f"通過測試: {passed_tests}")
    print(f"失敗測試: {total_tests - passed_tests}")
    print(f"成功率: {integration_report['summary']['success_rate']}")
    print(f"整體狀態: {integration_report['summary']['overall_status']}")
    
    return integration_report['summary']['overall_status'] == '通過'

def main():
    print("🚀 SRT GO v2.2.1 整合測試套件")
    print("="*60)
    
    start_time = time.time()
    
    # 執行測試
    test1_success = run_comprehensive_test()
    test2_success = run_ui_backend_integration()
    
    # 等待一下確保所有文件都寫入完成
    time.sleep(2)
    
    # 生成整合報告
    report_success = generate_integration_report()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n⏱️  總執行時間: {duration:.2f} 秒")
    
    # 最終結果
    all_success = test1_success and test2_success and report_success
    
    if all_success:
        print("\n🎉 所有整合測試通過！系統可用於生產環境。")
        sys.exit(0)
    else:
        print("\n⚠️  部分整合測試失敗，請檢查日誌。")
        sys.exit(1)

if __name__ == '__main__':
    main()