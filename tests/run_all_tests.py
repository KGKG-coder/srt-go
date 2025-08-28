#!/usr/bin/env python3
"""
SRT GO v2.2.1 統一測試執行器
Unified Test Runner for SRT GO v2.2.1

執行所有測試類別並產生統一報告
Execute all test categories and generate unified reports.
"""

import sys
import os
import time
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any
import argparse

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SRTGOTestRunner:
    """SRT GO 統一測試執行器"""
    
    def __init__(self):
        self.test_root = Path(__file__).parent
        self.results = {}
        self.start_time = None
        self.total_time = 0
        
    def run_test_category(self, category: str, test_path: str, args: List[str] = None) -> Dict[str, Any]:
        """執行特定測試類別"""
        print(f"\\n{'='*60}")
        print(f"[TEST] 執行 {category} 測試")
        print(f"[PATH] 路徑: {test_path}")
        print(f"{'='*60}")
        
        if args is None:
            args = []
            
        full_path = self.test_root / test_path
        if not full_path.exists():
            return {
                "category": category,
                "success": False,
                "error": f"測試路徑不存在: {full_path}",
                "duration": 0,
                "test_count": 0
            }
        
        start_time = time.time()
        
        try:
            # 根據檔案類型選擇執行方式
            if test_path.endswith('.py'):
                # 直接執行Python腳本
                cmd = [sys.executable, str(full_path)] + args
            else:
                # 使用pytest執行目錄
                cmd = [sys.executable, '-m', 'pytest', str(full_path), '-v', '--tb=short'] + args
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                cwd=str(self.test_root)
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            # 解析測試結果
            test_count = self._extract_test_count(result.stdout)
            
            print(f"[TIME] 執行時間: {duration:.2f}秒")
            print(f"[STAT] 測試數量: {test_count}")
            print(f"{'[OK] 成功' if success else '[FAIL] 失敗'}")
            
            if not success and result.stderr:
                print(f"錯誤輸出: {result.stderr[:500]}...")
            
            return {
                "category": category,
                "success": success,
                "duration": duration,
                "test_count": test_count,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"[ERROR] 執行失敗: {e}")
            
            return {
                "category": category,
                "success": False,
                "error": str(e),
                "duration": duration,
                "test_count": 0
            }
    
    def _extract_test_count(self, output: str) -> int:
        """從輸出中提取測試數量"""
        try:
            # 查找pytest輸出中的測試統計
            lines = output.split('\\n')
            for line in lines:
                if 'passed' in line or 'failed' in line:
                    # 嘗試解析 "X passed, Y failed" 格式
                    words = line.split()
                    for i, word in enumerate(words):
                        if word.isdigit():
                            return int(word)
        except:
            pass
        return 0
    
    def run_all_tests(self, categories: List[str] = None):
        """執行所有測試"""
        print("[*] SRT GO v2.2.1 統一測試執行器")
        print("="*60)
        
        self.start_time = time.time()
        
        # 測試配置 - 按功能分類
        test_configs = {
            # 1. 單元測試
            "單元測試 - 音頻處理器": {
                "path": "unit/test_audio_processor.py",
                "args": ["-v"]
            },
            "單元測試 - 音頻處理器簡化版": {
                "path": "unit/test_audio_processor_simple.py", 
                "args": ["-v"]
            },
            
            # 2. 整合測試
            "整合測試 - 完整工作流程": {
                "path": "integration/test_complete_workflow.py",
                "args": ["-v"]
            },
            "整合測試 - 標準除錯": {
                "path": "debug_test_integration.py",
                "args": []
            },
            "整合測試 - 低VAD除錯": {
                "path": "debug_test_integration_low_vad.py",
                "args": []
            },
            
            # 3. 效能測試
            "效能測試 - 快速RTF測試": {
                "path": "performance/quick_rtf_test.py",
                "args": []
            },
            "效能測試 - RTF基準測試": {
                "path": "performance/test_rtf_benchmarks.py",
                "args": ["-v"]
            },
            "效能測試 - RTF監控系統": {
                "path": "performance/rtf_monitoring_system.py",
                "args": []
            },
            "效能測試 - 綜合效能套件": {
                "path": "performance/comprehensive_performance_suite.py",
                "args": []
            },
            
            # 4. E2E測試  
            "E2E測試 - 自動化測試套件": {
                "path": "e2e/test_automation_suite.py",
                "args": []
            },
        }
        
        # 如果指定了特定類別，只執行那些
        if categories:
            test_configs = {k: v for k, v in test_configs.items() if any(cat in k for cat in categories)}
        
        # 執行測試
        for category, config in test_configs.items():
            if categories and not any(cat in category for cat in categories):
                continue
                
            result = self.run_test_category(category, config["path"], config.get("args", []))
            self.results[category] = result
        
        self.total_time = time.time() - self.start_time
        
        # 生成報告
        self.generate_report()
        
        # 返回總體成功狀態
        return self.is_overall_success()
    
    def generate_report(self):
        """生成測試報告"""
        print("\\n" + "="*60)
        print("[SUMMARY] 測試結果統計")
        print("="*60)
        
        successful = [r for r in self.results.values() if r["success"]]
        failed = [r for r in self.results.values() if not r["success"]]
        total_tests = sum(r["test_count"] for r in self.results.values())
        
        print(f"總執行時間: {self.total_time:.2f}秒")
        print(f"測試類別數量: {len(self.results)}")
        print(f"成功類別: {len(successful)}")
        print(f"失敗類別: {len(failed)}")
        print(f"總測試數量: {total_tests}")
        print(f"成功率: {len(successful)/len(self.results)*100:.1f}%" if self.results else "0%")
        
        if successful:
            print("\\n[SUCCESS] 成功的測試類別:")
            for result in successful:
                print(f"  • {result['category']} ({result['test_count']}個測試, {result['duration']:.1f}秒)")
        
        if failed:
            print("\\n[FAILED] 失敗的測試類別:")  
            for result in failed:
                error_msg = result.get('error', '未知錯誤')
                print(f"  • {result['category']}: {error_msg}")
        
        # 效能統計
        print("\\n[PERF] 效能統計:")
        perf_results = [r for r in self.results.values() if "效能測試" in r["category"] and r["success"]]
        if perf_results:
            avg_duration = sum(r["duration"] for r in perf_results) / len(perf_results)
            print(f"  平均效能測試時間: {avg_duration:.2f}秒")
        
        # 生成JSON報告
        self.save_json_report()
        
        print("\\n" + "="*60)
        if self.is_overall_success():
            print("🎉 所有測試執行完成 - 整體狀態: 成功")
        else:
            print("⚠️  測試執行完成 - 發現問題需要處理")
        print("="*60)
    
    def save_json_report(self):
        """儲存JSON格式報告"""
        report_data = {
            "test_run_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_duration": self.total_time,
            "total_categories": len(self.results),
            "successful_categories": len([r for r in self.results.values() if r["success"]]),
            "failed_categories": len([r for r in self.results.values() if not r["success"]]),
            "total_tests": sum(r["test_count"] for r in self.results.values()),
            "overall_success": self.is_overall_success(),
            "results": self.results
        }
        
        report_file = self.test_root / "UNIFIED_TEST_REPORT.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\\n📄 詳細報告已儲存: {report_file}")
    
    def is_overall_success(self) -> bool:
        """判斷整體測試是否成功"""
        if not self.results:
            return False
        return all(r["success"] for r in self.results.values())


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="SRT GO v2.2.1 統一測試執行器")
    parser.add_argument(
        "--categories", "-c", 
        nargs='+',
        help="指定要執行的測試類別 (例如: --categories 單元測試 效能測試)"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true", 
        help="列出所有可用的測試類別"
    )
    parser.add_argument(
        "--quick-mode",
        action="store_true",
        help="快速測試模式（跳過耗時測試）"
    )
    parser.add_argument(
        "--intensive-mode", 
        action="store_true",
        help="密集測試模式（包含所有測試）"
    )
    parser.add_argument(
        "--component-test",
        action="store_true", 
        help="組件測試模式"
    )
    parser.add_argument(
        "--pre-build-check",
        action="store_true",
        help="預構建檢查模式"
    )
    
    args = parser.parse_args()
    
    runner = SRTGOTestRunner()
    
    if args.list:
        print("可用的測試類別:")
        categories = [
            "單元測試", "整合測試", "效能測試", "E2E測試"
        ]
        for i, category in enumerate(categories, 1):
            print(f"  {i}. {category}")
        return
    
    try:
        # 根據模式調整測試行為
        if args.quick_mode:
            print("[MODE] 快速測試模式 - 跳過耗時測試")
        elif args.intensive_mode:
            print("[MODE] 密集測試模式 - 包含所有測試")
        elif args.component_test:
            print("[MODE] 組件測試模式")
        elif args.pre_build_check:
            print("[MODE] 預構建檢查模式")
        
        success = runner.run_all_tests(args.categories)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n\\n[STOP] 測試執行被使用者中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\\n\\n[ERROR] 測試執行器發生錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()