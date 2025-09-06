#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化架構完整流程測試
"""

import sys
import os
import json
import subprocess
from pathlib import Path
import time

# 設置編碼
if sys.platform.startswith('win'):
    os.system('chcp 65001 > NUL 2>&1')

class SimplifiedArchitectureTest:
    """簡化架構測試類"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.results = {
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "python_version": sys.version,
            "tests": {}
        }
    
    def log(self, test_name, success, message, details=None):
        """記錄測試結果"""
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {test_name}: {message}")
        
        self.results["tests"][test_name] = {
            "success": success,
            "message": message,
            "details": details or {}
        }
        
        return success
    
    def test_file_structure(self):
        """測試檔案結構"""
        print("\n1. 檔案結構測試")
        print("-" * 40)
        
        required_files = {
            "main_simplified.js": "簡化版主程序",
            "python/electron_backend_simplified.py": "簡化版後端",
            "python/test_backend_minimal.py": "最簡測試後端",
            "mini_python/python.exe": "嵌入式 Python",
            "test_main_simplified.js": "主程序測試腳本",
            "package.json": "Node.js 配置"
        }
        
        all_exist = True
        missing_files = []
        
        for file_path, description in required_files.items():
            full_path = self.base_dir / file_path
            if full_path.exists():
                self.log(f"檔案存在_{file_path.replace('/', '_')}", True, f"{description} 存在")
            else:
                self.log(f"檔案存在_{file_path.replace('/', '_')}", False, f"{description} 不存在")
                missing_files.append(file_path)
                all_exist = False
        
        return self.log(
            "file_structure", 
            all_exist, 
            "所有必要檔案存在" if all_exist else f"缺少 {len(missing_files)} 個檔案",
            {"missing_files": missing_files}
        )
    
    def test_python_environment(self):
        """測試 Python 環境"""
        print("\n2. Python 環境測試")
        print("-" * 40)
        
        python_exe = self.base_dir / "mini_python" / "python.exe"
        
        if not python_exe.exists():
            return self.log("python_environment", False, "嵌入式 Python 不存在")
        
        try:
            # 測試基本執行
            result = subprocess.run(
                [str(python_exe), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log("python_version", True, f"Python 版本: {version}")
            else:
                return self.log("python_environment", False, "Python 無法執行")
            
            # 測試基本模組
            basic_modules = ["json", "pathlib", "sys", "os"]
            module_results = {}
            
            for module in basic_modules:
                test_result = subprocess.run(
                    [str(python_exe), "-c", f"import {module}; print('OK')"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                module_ok = test_result.returncode == 0
                module_results[module] = module_ok
                self.log(f"module_{module}", module_ok, f"{module} 模組可用" if module_ok else f"{module} 模組不可用")
            
            available_modules = sum(module_results.values())
            total_modules = len(module_results)
            
            return self.log(
                "python_environment",
                available_modules >= total_modules * 0.75,
                f"Python 環境基本可用 ({available_modules}/{total_modules} 模組)",
                {"modules": module_results}
            )
            
        except Exception as e:
            return self.log("python_environment", False, f"Python 測試失敗: {e}")
    
    def test_backend_execution(self):
        """測試後端執行"""
        print("\n3. 後端執行測試")
        print("-" * 40)
        
        python_exe = self.base_dir / "mini_python" / "python.exe"
        test_script = self.base_dir / "python" / "test_backend_minimal.py"
        
        if not python_exe.exists() or not test_script.exists():
            return self.log("backend_execution", False, "必要檔案不存在")
        
        try:
            # 測試最簡化後端
            cmd = [
                str(python_exe),
                str(test_script),
                "--files", json.dumps(["test1.mp4", "test2.mp4"]),
                "--settings", json.dumps({"model": "large", "language": "auto"}),
                "--corrections", "[]"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(python_exe.parent)
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # 檢查輸出格式
                has_progress = "PROGRESS:" in output
                has_result = "RESULT:" in output
                
                self.log("backend_progress", has_progress, "進度回調正常" if has_progress else "缺少進度回調")
                self.log("backend_result", has_result, "結果回傳正常" if has_result else "缺少結果回傳")
                
                success = has_progress and has_result
                return self.log(
                    "backend_execution",
                    success,
                    "後端執行成功" if success else "後端輸出格式不正確",
                    {"return_code": result.returncode, "has_progress": has_progress, "has_result": has_result}
                )
            else:
                return self.log(
                    "backend_execution",
                    False,
                    f"後端執行失敗 (返回碼: {result.returncode})",
                    {"return_code": result.returncode, "stderr": result.stderr[:500]}
                )
                
        except subprocess.TimeoutExpired:
            return self.log("backend_execution", False, "後端執行超時")
        except Exception as e:
            return self.log("backend_execution", False, f"後端執行異常: {e}")
    
    def test_nodejs_setup(self):
        """測試 Node.js 設置"""
        print("\n4. Node.js 設置測試")
        print("-" * 40)
        
        try:
            # 檢查 Node.js 版本
            node_result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if node_result.returncode == 0:
                version = node_result.stdout.strip()
                self.log("nodejs_version", True, f"Node.js 版本: {version}")
            else:
                return self.log("nodejs_setup", False, "Node.js 不可用")
            
            # 檢查 package.json
            package_json = self.base_dir / "package.json"
            if package_json.exists():
                with open(package_json, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                
                scripts = package_data.get("scripts", {})
                
                # 檢查簡化版腳本
                simplified_scripts = {
                    "start:simplified": "簡化版啟動腳本",
                    "dev:simplified": "簡化版開發腳本"
                }
                
                script_results = {}
                for script_name, description in simplified_scripts.items():
                    exists = script_name in scripts
                    script_results[script_name] = exists
                    self.log(f"script_{script_name.replace(':', '_')}", exists, f"{description}存在" if exists else f"{description}不存在")
                
                available_scripts = sum(script_results.values())
                total_scripts = len(script_results)
                
                return self.log(
                    "nodejs_setup",
                    available_scripts >= total_scripts,
                    f"Node.js 設置完成 ({available_scripts}/{total_scripts} 腳本)",
                    {"scripts": script_results}
                )
            else:
                return self.log("nodejs_setup", False, "package.json 不存在")
                
        except Exception as e:
            return self.log("nodejs_setup", False, f"Node.js 測試失敗: {e}")
    
    def test_integration(self):
        """整合測試"""
        print("\n5. 整合測試")
        print("-" * 40)
        
        try:
            # 執行 Node.js 路徑測試腳本
            test_script = self.base_dir / "test_main_simplified.js"
            
            if not test_script.exists():
                return self.log("integration", False, "整合測試腳本不存在")
            
            result = subprocess.run(
                ["node", str(test_script)],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=str(self.base_dir)
            )
            
            if result.returncode == 0:
                output = result.stdout
                success_indicators = [
                    "[OK] 找到嵌入式 Python",
                    "[OK] 找到測試腳本",
                    "[OK] 找到 main_simplified.js",
                    "[成功] 所有路徑和文件都正確"
                ]
                
                passed_checks = sum(1 for indicator in success_indicators if indicator in output)
                total_checks = len(success_indicators)
                
                integration_success = passed_checks >= total_checks * 0.75
                
                return self.log(
                    "integration",
                    integration_success,
                    f"整合測試通過 ({passed_checks}/{total_checks} 檢查)",
                    {"passed_checks": passed_checks, "total_checks": total_checks, "output": output[:1000]}
                )
            else:
                return self.log(
                    "integration",
                    False,
                    f"整合測試失敗 (返回碼: {result.returncode})",
                    {"stderr": result.stderr[:500]}
                )
                
        except Exception as e:
            return self.log("integration", False, f"整合測試異常: {e}")
    
    def generate_report(self):
        """生成測試報告"""
        print("\n" + "=" * 60)
        print("簡化架構完整測試報告")
        print("=" * 60)
        
        # 統計結果
        total_tests = len(self.results["tests"])
        passed_tests = sum(1 for test in self.results["tests"].values() if test["success"])
        
        print(f"\n測試時間: {self.results['test_time']}")
        print(f"Python 版本: {self.results['python_version'].split()[0]}")
        print(f"測試結果: {passed_tests}/{total_tests} 通過")
        
        # 詳細結果
        print(f"\n詳細結果:")
        for test_name, test_data in self.results["tests"].items():
            status = "✓" if test_data["success"] else "✗"
            print(f"  {status} {test_name}: {test_data['message']}")
        
        # 總結
        overall_success = passed_tests >= total_tests * 0.8
        
        if overall_success:
            print(f"\n[成功] 簡化架構測試通過！")
            print(f"系統已準備好使用簡化版後端。")
            print(f"\n建議下一步:")
            print(f"1. 執行: npm run dev:simplified")
            print(f"2. 安裝完整的 AI 依賴")
            print(f"3. 測試實際影片處理")
        else:
            print(f"\n[失敗] 簡化架構測試未完全通過")
            print(f"需要解決 {total_tests - passed_tests} 個問題")
        
        # 保存報告
        report_file = self.base_dir / "simplified_architecture_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n詳細報告已保存: {report_file}")
        
        return overall_success
    
    def run_all_tests(self):
        """執行所有測試"""
        print("簡化架構完整流程測試")
        print("版本: 2.2.1-simplified")
        
        # 執行測試
        tests = [
            self.test_file_structure,
            self.test_python_environment, 
            self.test_backend_execution,
            self.test_nodejs_setup,
            self.test_integration
        ]
        
        for test in tests:
            test()
        
        return self.generate_report()

def main():
    """主函數"""
    tester = SimplifiedArchitectureTest()
    success = tester.run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    input("\n按 Enter 鍵退出...")
    sys.exit(0 if success else 1)