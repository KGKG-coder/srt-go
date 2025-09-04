#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
統一測試執行器 - SRT GO v2.2.1
支援快速測試、完整測試和CI/CD模式
"""

import os
import sys
import json
import argparse
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple

class TestRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.test_root = Path(__file__).parent.parent
        self.results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_results': {},
            'summary': {}
        }
        
    def run_python_test(self, test_path: Path, test_name: str) -> Tuple[bool, Dict]:
        """執行Python測試並返回結果"""
        print(f"\n🔄 運行測試: {test_name}")
        print(f"   路徑: {test_path}")
        
        try:
            # 切換到測試文件所在目錄
            original_cwd = os.getcwd()
            os.chdir(test_path.parent)
            
            # 執行測試
            result = subprocess.run([
                sys.executable, str(test_path.name)
            ], capture_output=True, text=True, encoding='utf-8')
            
            os.chdir(original_cwd)
            
            success = result.returncode == 0
            
            test_result = {
                'success': success,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time': time.time()
            }
            
            if success:
                print(f"   ✅ {test_name} - 測試通過")
                self.results['passed_tests'] += 1
            else:
                print(f"   ❌ {test_name} - 測試失敗")
                print(f"      錯誤: {result.stderr}")
                self.results['failed_tests'] += 1
            
            self.results['total_tests'] += 1
            self.results['test_results'][test_name] = test_result
            
            return success, test_result
            
        except Exception as e:
            print(f"   ❌ {test_name} - 執行異常: {str(e)}")
            self.results['failed_tests'] += 1
            self.results['total_tests'] += 1
            
            error_result = {
                'success': False,
                'error': str(e),
                'execution_time': time.time()
            }
            self.results['test_results'][test_name] = error_result
            return False, error_result
    
    def run_quick_tests(self):
        """快速測試套件 - 核心功能驗證"""
        print("🚀 執行快速測試套件")
        print("=" * 60)
        
        # 核心測試路徑
        python_dir = self.project_root / "srt_whisper_lite" / "electron-react-app" / "python"
        
        quick_tests = [
            (python_dir / "comprehensive_test_suite.py", "智能FP16優先系統測試"),
            (python_dir / "test_ui_backend_integration.py", "UI-Backend整合測試"),
        ]
        
        for test_path, test_name in quick_tests:
            if test_path.exists():
                self.run_python_test(test_path, test_name)
            else:
                print(f"⚠️  測試文件不存在: {test_path}")
                self.results['failed_tests'] += 1
                self.results['total_tests'] += 1
    
    def run_full_tests(self):
        """完整測試套件 - 包含所有測試"""
        print("🔬 執行完整測試套件")
        print("=" * 60)
        
        # 先執行快速測試
        self.run_quick_tests()
        
        # 額外的完整測試
        python_dir = self.project_root / "srt_whisper_lite" / "electron-react-app" / "python"
        
        additional_tests = [
            # 可以添加更多測試文件
        ]
        
        for test_path, test_name in additional_tests:
            if test_path.exists():
                self.run_python_test(test_path, test_name)
    
    def run_ci_tests(self):
        """CI/CD模式測試 - 適合GitHub Actions"""
        print("🔧 執行CI/CD測試套件")
        print("=" * 60)
        
        # CI環境的特殊設置
        os.environ['CI_MODE'] = '1'
        os.environ['DISABLE_GPU'] = '1'  # CI環境通常無GPU
        
        self.run_quick_tests()
    
    def generate_report(self, output_file: str = None):
        """生成測試報告"""
        self.results['summary'] = {
            'success_rate': f"{(self.results['passed_tests'] / self.results['total_tests'] * 100):.1f}%" if self.results['total_tests'] > 0 else "0%",
            'overall_status': '通過' if self.results['failed_tests'] == 0 else '失敗',
            'total_duration': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 打印摘要
        print("\n" + "=" * 60)
        print("📊 測試結果摘要")
        print("=" * 60)
        print(f"總測試數: {self.results['total_tests']}")
        print(f"通過測試: {self.results['passed_tests']}")
        print(f"失敗測試: {self.results['failed_tests']}")
        print(f"成功率: {self.results['summary']['success_rate']}")
        print(f"整體狀態: {self.results['summary']['overall_status']}")
        
        # 保存報告
        if output_file:
            report_path = Path(output_file)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            print(f"\n📄 測試報告已保存: {report_path}")
        
        return self.results

def main():
    parser = argparse.ArgumentParser(description='SRT GO 統一測試執行器')
    parser.add_argument('--quick', action='store_true', help='執行快速測試套件')
    parser.add_argument('--full', action='store_true', help='執行完整測試套件')
    parser.add_argument('--ci-mode', action='store_true', help='CI/CD模式測試')
    parser.add_argument('--output', '-o', help='測試報告輸出文件')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.ci_mode:
        runner.run_ci_tests()
    elif args.full:
        runner.run_full_tests()
    elif args.quick:
        runner.run_quick_tests()
    else:
        # 預設執行快速測試
        runner.run_quick_tests()
    
    # 生成報告
    output_file = args.output or f"test_results_{int(time.time())}.json"
    runner.generate_report(output_file)
    
    # 根據結果設置退出碼
    sys.exit(0 if runner.results['failed_tests'] == 0 else 1)

if __name__ == '__main__':
    main()