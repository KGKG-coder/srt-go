#!/usr/bin/env python3
"""
SRT GO v2.2.1 Deployment Verification Script
用於驗證部署準備狀態的腳本
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

class DeploymentVerification:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "version": "2.2.1",
            "checks": {},
            "ready_for_deployment": False
        }
        
    def check_github_workflows(self):
        """檢查 GitHub Actions workflows"""
        print("📋 Checking GitHub Actions workflows...")
        workflows_dir = self.root_dir / ".github" / "workflows"
        
        if not workflows_dir.exists():
            self.results["checks"]["github_workflows"] = {
                "status": "ERROR",
                "message": ".github/workflows directory not found"
            }
            return False
            
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        
        workflow_status = []
        for wf in workflow_files:
            try:
                with open(wf, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'name:' in content and 'on:' in content:
                        workflow_status.append({
                            "file": wf.name,
                            "valid": True
                        })
                        print(f"  ✅ {wf.name} - Valid")
                    else:
                        workflow_status.append({
                            "file": wf.name,
                            "valid": False
                        })
                        print(f"  ❌ {wf.name} - Invalid structure")
            except Exception as e:
                workflow_status.append({
                    "file": wf.name,
                    "valid": False,
                    "error": str(e)
                })
                print(f"  ❌ {wf.name} - Error: {e}")
                
        all_valid = all(w["valid"] for w in workflow_status)
        self.results["checks"]["github_workflows"] = {
            "status": "PASS" if all_valid else "FAIL",
            "total_workflows": len(workflow_files),
            "valid_workflows": sum(1 for w in workflow_status if w["valid"]),
            "workflows": workflow_status
        }
        return all_valid
        
    def check_test_suite(self):
        """檢查測試套件狀態"""
        print("\n🧪 Checking test suite...")
        tests_dir = self.root_dir / "tests"
        
        if not tests_dir.exists():
            self.results["checks"]["test_suite"] = {
                "status": "ERROR",
                "message": "tests directory not found"
            }
            return False
            
        test_categories = ["unit", "integration", "performance", "e2e"]
        test_status = {}
        
        for category in test_categories:
            category_dir = tests_dir / category
            if category_dir.exists():
                test_files = list(category_dir.glob("test_*.py"))
                test_status[category] = {
                    "exists": True,
                    "test_files": len(test_files)
                }
                print(f"  ✅ {category}: {len(test_files)} test files")
            else:
                test_status[category] = {
                    "exists": False,
                    "test_files": 0
                }
                print(f"  ⚠️ {category}: Directory not found")
                
        # 檢查測試配置文件
        conftest = tests_dir / "conftest.py"
        has_conftest = conftest.exists()
        
        self.results["checks"]["test_suite"] = {
            "status": "PASS" if has_conftest else "WARNING",
            "has_conftest": has_conftest,
            "categories": test_status,
            "total_categories": len(test_categories),
            "existing_categories": sum(1 for c in test_status.values() if c["exists"])
        }
        return True
        
    def check_application_structure(self):
        """檢查應用程式結構"""
        print("\n🏗️ Checking application structure...")
        app_dir = self.root_dir / "srt_whisper_lite" / "electron-react-app"
        
        critical_files = {
            "main.js": app_dir / "main.js",
            "package.json": app_dir / "package.json",
            "electron_backend.py": app_dir / "python" / "electron_backend.py",
            "smart_backend_selector.py": app_dir / "python" / "smart_backend_selector.py"
        }
        
        file_status = {}
        all_exist = True
        
        for name, path in critical_files.items():
            exists = path.exists()
            file_status[name] = exists
            if exists:
                print(f"  ✅ {name} - Found")
            else:
                print(f"  ❌ {name} - Missing")
                all_exist = False
                
        self.results["checks"]["application_structure"] = {
            "status": "PASS" if all_exist else "FAIL",
            "critical_files": file_status,
            "app_directory_exists": app_dir.exists()
        }
        return all_exist
        
    def check_models(self):
        """檢查 AI 模型狀態"""
        print("\n🤖 Checking AI models...")
        
        # 檢查 HuggingFace 緩存
        hf_cache = Path.home() / ".cache" / "huggingface" / "hub"
        model_paths = []
        
        if hf_cache.exists():
            whisper_models = list(hf_cache.glob("models--*whisper*"))
            for model in whisper_models:
                model_name = model.name.replace("models--", "").replace("--", "/")
                model_paths.append(model_name)
                print(f"  ✅ Found cached model: {model_name}")
                
        # 檢查本地模型目錄
        local_models = self.root_dir / "srt_whisper_lite" / "electron-react-app" / "models"
        has_local_models = local_models.exists() and any(local_models.iterdir())
        
        self.results["checks"]["ai_models"] = {
            "status": "PASS" if model_paths or has_local_models else "WARNING",
            "cached_models": model_paths,
            "has_local_models": has_local_models,
            "total_models": len(model_paths)
        }
        return True
        
    def check_dependencies(self):
        """檢查 Python 依賴"""
        print("\n📦 Checking dependencies...")
        
        required_packages = [
            "numpy",
            "pytest"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"  ✅ {package} - Installed")
            except ImportError:
                missing_packages.append(package)
                print(f"  ❌ {package} - Missing")
                
        self.results["checks"]["dependencies"] = {
            "status": "PASS" if not missing_packages else "WARNING",
            "required_packages": required_packages,
            "missing_packages": missing_packages
        }
        return len(missing_packages) == 0
        
    def check_git_status(self):
        """檢查 Git 狀態"""
        print("\n🔄 Checking Git status...")
        
        try:
            # 獲取當前分支
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.root_dir
            )
            current_branch = branch_result.stdout.strip()
            
            # 獲取未跟踪文件數量
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.root_dir
            )
            untracked_files = len([l for l in status_result.stdout.splitlines() if l.startswith("??")])
            
            # 獲取最後提交
            last_commit = subprocess.run(
                ["git", "log", "-1", "--format=%h %s"],
                capture_output=True,
                text=True,
                cwd=self.root_dir
            )
            
            self.results["checks"]["git_status"] = {
                "status": "PASS",
                "current_branch": current_branch,
                "untracked_files": untracked_files,
                "last_commit": last_commit.stdout.strip()
            }
            
            print(f"  📌 Current branch: {current_branch}")
            print(f"  📁 Untracked files: {untracked_files}")
            print(f"  💾 Last commit: {last_commit.stdout.strip()}")
            
            return True
        except Exception as e:
            self.results["checks"]["git_status"] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"  ❌ Git check failed: {e}")
            return False
            
    def generate_report(self):
        """生成部署報告"""
        print("\n" + "="*50)
        print("📊 DEPLOYMENT READINESS REPORT")
        print("="*50)
        
        all_checks_passed = all(
            check.get("status") in ["PASS", "WARNING"] 
            for check in self.results["checks"].values()
        )
        
        critical_checks_passed = all(
            self.results["checks"].get(key, {}).get("status") == "PASS"
            for key in ["github_workflows", "application_structure"]
        )
        
        self.results["ready_for_deployment"] = critical_checks_passed
        
        # 計算統計
        total_checks = len(self.results["checks"])
        passed_checks = sum(1 for c in self.results["checks"].values() if c.get("status") == "PASS")
        warning_checks = sum(1 for c in self.results["checks"].values() if c.get("status") == "WARNING")
        failed_checks = sum(1 for c in self.results["checks"].values() if c.get("status") in ["FAIL", "ERROR"])
        
        print(f"\n📈 Summary:")
        print(f"  ✅ Passed: {passed_checks}/{total_checks}")
        print(f"  ⚠️ Warnings: {warning_checks}/{total_checks}")
        print(f"  ❌ Failed: {failed_checks}/{total_checks}")
        
        if self.results["ready_for_deployment"]:
            print("\n🎉 DEPLOYMENT STATUS: READY ✅")
            print("The system is ready for deployment to production!")
        else:
            print("\n⚠️ DEPLOYMENT STATUS: NOT READY")
            print("Critical checks have failed. Please fix issues before deployment.")
            
        # 保存報告
        report_file = self.root_dir / "deployment_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return self.results["ready_for_deployment"]
        
    def run_verification(self):
        """執行所有驗證檢查"""
        print("🚀 Starting SRT GO v2.2.1 Deployment Verification...")
        print("="*50)
        
        # 執行所有檢查
        self.check_github_workflows()
        self.check_test_suite()
        self.check_application_structure()
        self.check_models()
        self.check_dependencies()
        self.check_git_status()
        
        # 生成報告
        ready = self.generate_report()
        
        return ready

def main():
    verifier = DeploymentVerification()
    ready = verifier.run_verification()
    
    # 返回適當的退出碼
    sys.exit(0 if ready else 1)

if __name__ == "__main__":
    main()