#!/usr/bin/env python3
"""
商用級測試執行器
一鍵執行所有測試並生成完整報告
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import webbrowser

# 顏色輸出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_colored(text: str, color: str = Colors.WHITE):
    """列印有顏色的文字"""
    print(f"{color}{text}{Colors.END}")

def print_section(title: str):
    """列印區段標題"""
    print_colored(f"\n{'='*60}", Colors.CYAN)
    print_colored(f"  {title}", Colors.CYAN + Colors.BOLD)
    print_colored(f"{'='*60}", Colors.CYAN)

def run_command(cmd: List[str], description: str = None) -> Dict[str, Any]:
    """執行命令並回傳結果"""
    if description:
        print_colored(f"▶ {description}", Colors.BLUE)
    
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8'
        )
        
        duration = time.time() - start_time
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'duration': duration,
            'command': ' '.join(cmd)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'duration': time.time() - start_time,
            'command': ' '.join(cmd)
        }

class TestSuite:
    """測試套件管理器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
    def run_all_tests(self, args):
        """執行所有測試"""
        print_colored("🧪 SRT GO 商用級測試套件", Colors.BOLD + Colors.MAGENTA)
        print_colored(f"專案路徑: {self.project_root}", Colors.WHITE)
        print_colored(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.WHITE)
        
        self.start_time = time.time()
        
        # 檢查環境
        if not self.check_environment():
            return False
        
        # 執行測試階段
        test_phases = []
        
        if not args.skip_unit:
            test_phases.append(('unit_tests', '單元測試', self.run_unit_tests))
        
        if not args.skip_integration:
            test_phases.append(('integration_tests', '整合測試', self.run_integration_tests))
        
        if not args.skip_e2e:
            test_phases.append(('e2e_tests', 'E2E測試', self.run_e2e_tests))
        
        if not args.skip_performance:
            test_phases.append(('performance_tests', '效能測試', self.run_performance_tests))
        
        if not args.skip_security:
            test_phases.append(('security_tests', '安全測試', self.run_security_tests))
        
        # 執行測試
        all_passed = True
        for test_id, test_name, test_func in test_phases:
            print_section(test_name)
            result = test_func()
            self.test_results[test_id] = result
            
            if result['success']:
                print_colored(f"✅ {test_name} 通過 ({result['duration']:.1f}s)", Colors.GREEN)
            else:
                print_colored(f"❌ {test_name} 失敗 ({result['duration']:.1f}s)", Colors.RED)
                all_passed = False
                
                if not args.continue_on_failure:
                    break
        
        self.end_time = time.time()
        
        # 生成報告
        self.generate_report(args.report_format)
        
        # 顯示摘要
        self.show_summary()
        
        return all_passed
    
    def check_environment(self) -> bool:
        """檢查測試環境"""
        print_section("環境檢查")
        
        # 檢查 Python
        python_result = run_command([sys.executable, '--version'], "檢查 Python 版本")
        if not python_result['success']:
            print_colored("❌ Python 不可用", Colors.RED)
            return False
        
        print_colored(f"✅ {python_result['stdout'].strip()}", Colors.GREEN)
        
        # 檢查必需套件
        required_packages = [
            'pytest', 'pytest-cov', 'numpy', 'faster-whisper'
        ]
        
        for package in required_packages:
            result = run_command([sys.executable, '-c', f'import {package}'], f"檢查 {package}")
            if result['success']:
                print_colored(f"✅ {package} 可用", Colors.GREEN)
            else:
                print_colored(f"❌ {package} 不可用", Colors.RED)
                print_colored(f"請執行: pip install {package}", Colors.YELLOW)
                return False
        
        # 檢查測試檔案
        test_dirs = ['tests/unit', 'tests/integration', 'tests/e2e', 'tests/performance', 'tests/security']
        for test_dir in test_dirs:
            test_path = self.project_root / test_dir
            if test_path.exists():
                count = len(list(test_path.glob('test_*.py')))
                print_colored(f"✅ {test_dir}: {count} 個測試檔案", Colors.GREEN)
            else:
                print_colored(f"⚠️  {test_dir}: 目錄不存在", Colors.YELLOW)
        
        return True
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """執行單元測試"""
        cmd = [
            sys.executable, '-m', 'pytest',
            'tests/unit/',
            '--cov=srt_whisper_lite',
            '--cov-report=html:coverage/html',
            '--cov-report=xml:coverage/coverage.xml',
            '--cov-report=term-missing',
            '--junit-xml=reports/unit_tests.xml',
            '-v'
        ]
        
        return run_command(cmd, "執行單元測試")
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """執行整合測試"""
        cmd = [
            sys.executable, '-m', 'pytest',
            'tests/integration/',
            '--junit-xml=reports/integration_tests.xml',
            '-v'
        ]
        
        return run_command(cmd, "執行整合測試")
    
    def run_e2e_tests(self) -> Dict[str, Any]:
        """執行端到端測試"""
        # 先建置應用
        build_cmd = ['npm', 'run', 'build']
        build_result = run_command(build_cmd, "建置應用程式")
        
        if not build_result['success']:
            return build_result
        
        cmd = [
            sys.executable, '-m', 'pytest',
            'tests/e2e/',
            '--junit-xml=reports/e2e_tests.xml',
            '-v'
        ]
        
        return run_command(cmd, "執行 E2E 測試")
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """執行效能測試"""
        cmd = [
            sys.executable, '-m', 'pytest',
            'tests/performance/',
            '--benchmark-only',
            '--benchmark-json=reports/benchmark.json',
            '--benchmark-autosave',
            '--junit-xml=reports/performance_tests.xml',
            '-v'
        ]
        
        return run_command(cmd, "執行效能測試")
    
    def run_security_tests(self) -> Dict[str, Any]:
        """執行安全測試"""
        # 執行 Safety 檢查
        safety_cmd = ['safety', 'check', '--json']
        safety_result = run_command(safety_cmd, "執行 Safety 安全檢查")
        
        # 執行 Bandit 檢查
        bandit_cmd = ['bandit', '-r', 'srt_whisper_lite/', '-f', 'json', '-o', 'reports/bandit.json']
        bandit_result = run_command(bandit_cmd, "執行 Bandit 安全檢查")
        
        # 執行安全測試
        pytest_cmd = [
            sys.executable, '-m', 'pytest',
            'tests/security/',
            '--junit-xml=reports/security_tests.xml',
            '-v'
        ]
        
        pytest_result = run_command(pytest_cmd, "執行安全測試")
        
        # 結合所有結果
        success = all([
            safety_result.get('success', False),
            bandit_result.get('success', True),  # Bandit 可能報告問題但不算失敗
            pytest_result.get('success', False)
        ])
        
        return {
            'success': success,
            'duration': sum([
                safety_result.get('duration', 0),
                bandit_result.get('duration', 0),
                pytest_result.get('duration', 0)
            ]),
            'details': {
                'safety': safety_result,
                'bandit': bandit_result,
                'pytest': pytest_result
            }
        }
    
    def generate_report(self, format_type: str = 'html'):
        """生成測試報告"""
        print_section("生成測試報告")
        
        # 確保報告目錄存在
        reports_dir = self.project_root / 'reports'
        reports_dir.mkdir(exist_ok=True)
        
        # 收集測試結果
        total_duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'version': '2.2.1',
            'total_duration': total_duration,
            'test_results': self.test_results,
            'summary': self.calculate_summary()
        }
        
        # 生成 JSON 報告
        json_path = reports_dir / 'test_report.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print_colored(f"✅ JSON 報告: {json_path}", Colors.GREEN)
        
        # 生成 HTML 報告
        if format_type in ['html', 'all']:
            html_path = reports_dir / 'test_report.html'
            self.generate_html_report(report_data, html_path)
            print_colored(f"✅ HTML 報告: {html_path}", Colors.GREEN)
        
        return json_path, html_path if format_type in ['html', 'all'] else None
    
    def generate_html_report(self, data: Dict, output_path: Path):
        """生成 HTML 報告"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SRT GO 測試報告</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; padding: 20px; }}
        .metric {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }}
        .metric.success {{ border-left-color: #28a745; }}
        .metric.warning {{ border-left-color: #ffc107; }}
        .metric.danger {{ border-left-color: #dc3545; }}
        .test-results {{ padding: 20px; }}
        .test-item {{ margin-bottom: 15px; padding: 15px; border-radius: 5px; }}
        .test-item.passed {{ background: #d4edda; border-left: 4px solid #28a745; }}
        .test-item.failed {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
        .test-item.skipped {{ background: #fff3cd; border-left: 4px solid #ffc107; }}
        h1, h2, h3 {{ margin-top: 0; }}
        .timestamp {{ opacity: 0.7; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 SRT GO 測試報告</h1>
            <div class="timestamp">生成時間: {data['timestamp']}</div>
            <div class="timestamp">版本: v{data['version']}</div>
            <div class="timestamp">總執行時間: {data['total_duration']:.1f} 秒</div>
        </div>
        
        <div class="summary">
            <div class="metric success">
                <h3>通過測試</h3>
                <div style="font-size: 2em; font-weight: bold;">{data['summary']['passed']}</div>
            </div>
            <div class="metric danger">
                <h3>失敗測試</h3>
                <div style="font-size: 2em; font-weight: bold;">{data['summary']['failed']}</div>
            </div>
            <div class="metric warning">
                <h3>跳過測試</h3>
                <div style="font-size: 2em; font-weight: bold;">{data['summary']['skipped']}</div>
            </div>
            <div class="metric">
                <h3>成功率</h3>
                <div style="font-size: 2em; font-weight: bold;">{data['summary']['success_rate']:.1f}%</div>
            </div>
        </div>
        
        <div class="test-results">
            <h2>詳細結果</h2>
            {self.generate_test_items_html(data['test_results'])}
        </div>
    </div>
</body>
</html>"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def generate_test_items_html(self, test_results: Dict) -> str:
        """生成測試項目 HTML"""
        html_items = []
        
        for test_name, result in test_results.items():
            status = 'passed' if result['success'] else 'failed'
            status_icon = '✅' if result['success'] else '❌'
            
            html_items.append(f"""
            <div class="test-item {status}">
                <h3>{status_icon} {test_name.replace('_', ' ').title()}</h3>
                <p>執行時間: {result['duration']:.1f} 秒</p>
                {f'<p>錯誤: {result.get("stderr", "")}</p>' if not result['success'] else ''}
            </div>
            """)
        
        return ''.join(html_items)
    
    def calculate_summary(self) -> Dict[str, Any]:
        """計算測試摘要"""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results.values() if r.get('success', False))
        failed = sum(1 for r in self.test_results.values() if not r.get('success', True))
        skipped = total - passed - failed
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'success_rate': (passed / total * 100) if total > 0 else 0
        }
    
    def show_summary(self):
        """顯示測試摘要"""
        print_section("測試摘要")
        
        summary = self.calculate_summary()
        total_time = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        print_colored(f"總執行時間: {total_time:.1f} 秒", Colors.WHITE)
        print_colored(f"總測試套件: {summary['total']}", Colors.WHITE)
        print_colored(f"✅ 通過: {summary['passed']}", Colors.GREEN)
        print_colored(f"❌ 失敗: {summary['failed']}", Colors.RED)
        print_colored(f"⏭️  跳過: {summary['skipped']}", Colors.YELLOW)
        print_colored(f"📊 成功率: {summary['success_rate']:.1f}%", Colors.CYAN)
        
        if summary['success_rate'] >= 90:
            print_colored("🎉 測試品質: 優秀", Colors.GREEN + Colors.BOLD)
        elif summary['success_rate'] >= 80:
            print_colored("👍 測試品質: 良好", Colors.YELLOW + Colors.BOLD)
        else:
            print_colored("⚠️  測試品質: 需要改進", Colors.RED + Colors.BOLD)

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='SRT GO 商用級測試執行器')
    
    parser.add_argument('--skip-unit', action='store_true', help='跳過單元測試')
    parser.add_argument('--skip-integration', action='store_true', help='跳過整合測試')
    parser.add_argument('--skip-e2e', action='store_true', help='跳過 E2E 測試')
    parser.add_argument('--skip-performance', action='store_true', help='跳過效能測試')
    parser.add_argument('--skip-security', action='store_true', help='跳過安全測試')
    parser.add_argument('--continue-on-failure', action='store_true', help='測試失敗時繼續執行')
    parser.add_argument('--report-format', choices=['json', 'html', 'all'], default='html', help='報告格式')
    parser.add_argument('--open-report', action='store_true', help='自動開啟報告')
    
    args = parser.parse_args()
    
    # 取得專案根目錄
    project_root = Path(__file__).parent
    
    # 建立測試套件
    test_suite = TestSuite(project_root)
    
    # 執行測試
    success = test_suite.run_all_tests(args)
    
    # 開啟報告
    if args.open_report and args.report_format in ['html', 'all']:
        report_path = project_root / 'reports' / 'test_report.html'
        if report_path.exists():
            webbrowser.open(f'file://{report_path.absolute()}')
    
    # 設定退出碼
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()