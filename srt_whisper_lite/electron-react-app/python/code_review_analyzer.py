#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代碼審查分析器
檢查項目中的代碼質量、依賴使用和清理需求
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class CodeReviewAnalyzer:
    """代碼審查分析器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.python_files = []
        self.js_files = []
        self.analysis_results = {
            "timestamp": str(Path().absolute()),
            "python_analysis": {},
            "javascript_analysis": {},
            "dependency_analysis": {},
            "cleanup_recommendations": []
        }
    
    def run_comprehensive_review(self):
        """執行全面代碼審查"""
        print("Code Review and Cleanup Analysis")
        print("=" * 50)
        
        # 1. 掃描所有代碼文件
        self.scan_code_files()
        
        # 2. 分析Python代碼
        self.analyze_python_code()
        
        # 3. 分析JavaScript代碼
        self.analyze_javascript_code()
        
        # 4. 分析依賴項
        self.analyze_dependencies()
        
        # 5. 生成清理建議
        self.generate_cleanup_recommendations()
        
        # 6. 生成報告
        self.generate_review_report()
        
        return self.analysis_results
    
    def scan_code_files(self):
        """掃描所有代碼文件"""
        print("1. Scanning code files...")
        
        # Python文件
        for py_file in self.project_root.glob("**/*.py"):
            if not any(skip in str(py_file) for skip in ["node_modules", "__pycache__", ".git"]):
                self.python_files.append(py_file)
        
        # JavaScript文件
        for js_file in self.project_root.glob("**/*.js"):
            if not any(skip in str(js_file) for skip in ["node_modules", ".git"]):
                self.js_files.append(js_file)
        
        print(f"   Found {len(self.python_files)} Python files")
        print(f"   Found {len(self.js_files)} JavaScript files")
    
    def analyze_python_code(self):
        """分析Python代碼"""
        print("2. Analyzing Python code...")
        
        python_analysis = {
            "total_files": len(self.python_files),
            "imports_analysis": self.analyze_python_imports(),
            "unused_files": self.find_unused_python_files(),
            "code_quality_issues": self.check_python_code_quality(),
            "function_analysis": self.analyze_python_functions()
        }
        
        self.analysis_results["python_analysis"] = python_analysis
        
        print(f"   Analyzed {python_analysis['total_files']} Python files")
        print(f"   Found {len(python_analysis['unused_files'])} potentially unused files")
    
    def analyze_python_imports(self) -> Dict:
        """分析Python導入"""
        all_imports = defaultdict(set)
        import_usage = defaultdict(int)
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 找到import語句
                import_lines = []
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('import ') or line.startswith('from '):
                        import_lines.append(line)
                
                # 記錄導入
                for import_line in import_lines:
                    if 'import' in import_line:
                        # 提取模組名
                        if import_line.startswith('from '):
                            # from module import something
                            module = import_line.split(' import ')[0].replace('from ', '').strip()
                        else:
                            # import module
                            module = import_line.replace('import ', '').split(' as ')[0].strip()
                        
                        all_imports[str(py_file)].add(module)
                        import_usage[module] += 1
                        
            except Exception as e:
                print(f"   Warning: Could not analyze {py_file}: {e}")
        
        return {
            "unique_imports": len(set().union(*all_imports.values())),
            "most_used_imports": dict(sorted(import_usage.items(), key=lambda x: x[1], reverse=True)[:10]),
            "single_use_imports": [imp for imp, count in import_usage.items() if count == 1]
        }
    
    def find_unused_python_files(self) -> List[str]:
        """找到可能未使用的Python文件"""
        unused_files = []
        
        # 主要入口點
        main_files = [
            "electron_backend.py",
            "simplified_subtitle_core.py",
            "main.py"
        ]
        
        # 檢查每個文件是否被其他文件導入
        for py_file in self.python_files:
            filename = py_file.name
            stem = py_file.stem
            
            # 跳過主要入口點和測試文件
            if any(main in filename for main in main_files) or filename.startswith('test_'):
                continue
            
            # 檢查是否被其他文件引用
            is_referenced = False
            for other_file in self.python_files:
                if other_file == py_file:
                    continue
                
                try:
                    with open(other_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # 檢查import語句
                    if f"import {stem}" in content or f"from {stem}" in content:
                        is_referenced = True
                        break
                        
                except Exception:
                    continue
            
            if not is_referenced:
                unused_files.append(str(py_file.relative_to(self.project_root)))
        
        return unused_files
    
    def check_python_code_quality(self) -> Dict:
        """檢查Python代碼質量"""
        issues = {
            "long_functions": [],
            "high_complexity_files": [],
            "deprecated_patterns": [],
            "encoding_issues": []
        }
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # 檢查長函數
                current_function = None
                function_lines = 0
                
                for i, line in enumerate(lines):
                    if line.strip().startswith('def '):
                        if current_function and function_lines > 50:
                            issues["long_functions"].append({
                                "file": str(py_file.relative_to(self.project_root)),
                                "function": current_function,
                                "lines": function_lines
                            })
                        
                        current_function = line.strip().split('(')[0].replace('def ', '')
                        function_lines = 0
                    elif current_function:
                        function_lines += 1
                
                # 檢查文件複雜度（基於行數）
                if len(lines) > 500:
                    issues["high_complexity_files"].append({
                        "file": str(py_file.relative_to(self.project_root)),
                        "lines": len(lines)
                    })
                
                # 檢查已棄用模式
                if "#!/usr/bin/env python" in content and "python3" not in content:
                    issues["deprecated_patterns"].append({
                        "file": str(py_file.relative_to(self.project_root)),
                        "issue": "Using python instead of python3 in shebang"
                    })
                
                # 檢查編碼問題
                if "# -*- coding: utf-8 -*-" not in content[:100]:
                    issues["encoding_issues"].append({
                        "file": str(py_file.relative_to(self.project_root)),
                        "issue": "Missing UTF-8 encoding declaration"
                    })
                        
            except Exception as e:
                print(f"   Warning: Could not analyze {py_file}: {e}")
        
        return issues
    
    def analyze_python_functions(self) -> Dict:
        """分析Python函數"""
        function_stats = {
            "total_functions": 0,
            "classes": 0,
            "average_function_length": 0,
            "function_distribution": defaultdict(int)
        }
        
        total_function_lines = 0
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 使用AST分析
                try:
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            function_stats["total_functions"] += 1
                            # 估算函數長度
                            func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 10
                            total_function_lines += func_lines
                            
                            if func_lines < 10:
                                function_stats["function_distribution"]["short"] += 1
                            elif func_lines < 30:
                                function_stats["function_distribution"]["medium"] += 1
                            else:
                                function_stats["function_distribution"]["long"] += 1
                        
                        elif isinstance(node, ast.ClassDef):
                            function_stats["classes"] += 1
                            
                except SyntaxError:
                    # 跳過語法錯誤的文件
                    continue
                    
            except Exception:
                continue
        
        if function_stats["total_functions"] > 0:
            function_stats["average_function_length"] = total_function_lines / function_stats["total_functions"]
        
        return function_stats
    
    def analyze_javascript_code(self):
        """分析JavaScript代碼"""
        print("3. Analyzing JavaScript code...")
        
        js_analysis = {
            "total_files": len(self.js_files),
            "unused_files": self.find_unused_js_files(),
            "package_json_analysis": self.analyze_package_json()
        }
        
        self.analysis_results["javascript_analysis"] = js_analysis
        print(f"   Analyzed {js_analysis['total_files']} JavaScript files")
    
    def find_unused_js_files(self) -> List[str]:
        """找到未使用的JavaScript文件"""
        # 簡化版本：檢查明顯的測試或實驗性文件
        unused_files = []
        
        for js_file in self.js_files:
            filename = js_file.name
            
            # 檢查明顯的測試文件
            if any(pattern in filename.lower() for pattern in [
                'test_', 'debug_', 'experiment_', 'backup_', '.backup', '.test'
            ]):
                unused_files.append(str(js_file.relative_to(self.project_root)))
        
        return unused_files
    
    def analyze_package_json(self) -> Dict:
        """分析package.json"""
        package_json_files = list(self.project_root.glob("**/package.json"))
        analysis = {
            "package_json_count": len(package_json_files),
            "dependencies_summary": {},
            "potential_unused_deps": []
        }
        
        for pkg_file in package_json_files:
            try:
                with open(pkg_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                deps = data.get("dependencies", {})
                dev_deps = data.get("devDependencies", {})
                
                analysis["dependencies_summary"][str(pkg_file.relative_to(self.project_root))] = {
                    "dependencies": len(deps),
                    "devDependencies": len(dev_deps),
                    "total": len(deps) + len(dev_deps)
                }
                
            except Exception as e:
                print(f"   Warning: Could not analyze {pkg_file}: {e}")
        
        return analysis
    
    def analyze_dependencies(self):
        """分析依賴項"""
        print("4. Analyzing dependencies...")
        
        dependency_analysis = {
            "python_requirements": self.analyze_python_requirements(),
            "node_modules_size": self.estimate_node_modules_size(),
            "duplicate_dependencies": self.find_duplicate_dependencies()
        }
        
        self.analysis_results["dependency_analysis"] = dependency_analysis
    
    def analyze_python_requirements(self) -> Dict:
        """分析Python依賴需求"""
        requirements_files = list(self.project_root.glob("**/requirements*.txt"))
        
        analysis = {
            "requirements_files": len(requirements_files),
            "total_requirements": 0,
            "requirements_details": []
        }
        
        for req_file in requirements_files:
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                requirements = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
                analysis["total_requirements"] += len(requirements)
                analysis["requirements_details"].append({
                    "file": str(req_file.relative_to(self.project_root)),
                    "count": len(requirements)
                })
                
            except Exception as e:
                print(f"   Warning: Could not analyze {req_file}: {e}")
        
        return analysis
    
    def estimate_node_modules_size(self) -> Dict:
        """估算node_modules大小"""
        node_modules_dirs = list(self.project_root.glob("**/node_modules"))
        
        total_estimated_size = 0
        for nm_dir in node_modules_dirs:
            # 簡單估算：假設每個package平均1MB
            try:
                package_count = len([d for d in nm_dir.iterdir() if d.is_dir()])
                estimated_size = package_count * 1  # MB
                total_estimated_size += estimated_size
            except Exception:
                continue
        
        return {
            "node_modules_directories": len(node_modules_dirs),
            "estimated_total_size_mb": total_estimated_size
        }
    
    def find_duplicate_dependencies(self) -> List[str]:
        """找到重複的依賴項"""
        # 簡化版本：比較不同package.json中的依賴
        all_deps = defaultdict(list)
        package_files = list(self.project_root.glob("**/package.json"))
        
        for pkg_file in package_files:
            try:
                with open(pkg_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                deps = data.get("dependencies", {})
                for dep, version in deps.items():
                    all_deps[dep].append((str(pkg_file), version))
                    
            except Exception:
                continue
        
        duplicates = []
        for dep, locations in all_deps.items():
            if len(locations) > 1:
                versions = set(loc[1] for loc in locations)
                if len(versions) > 1:  # 不同版本
                    duplicates.append(f"{dep} (multiple versions: {list(versions)})")
        
        return duplicates
    
    def generate_cleanup_recommendations(self):
        """生成清理建議"""
        print("5. Generating cleanup recommendations...")
        
        recommendations = []
        
        # Python文件清理
        python_analysis = self.analysis_results["python_analysis"]
        if python_analysis["unused_files"]:
            recommendations.append({
                "category": "Python Files",
                "action": "Remove unused Python files",
                "files": python_analysis["unused_files"][:5],  # 只顯示前5個
                "impact": "Reduce package size and complexity"
            })
        
        # JavaScript文件清理
        js_analysis = self.analysis_results["javascript_analysis"]
        if js_analysis["unused_files"]:
            recommendations.append({
                "category": "JavaScript Files",
                "action": "Remove test/debug JavaScript files",
                "files": js_analysis["unused_files"][:5],
                "impact": "Clean up development artifacts"
            })
        
        # 依賴項清理
        dep_analysis = self.analysis_results["dependency_analysis"]
        if dep_analysis["duplicate_dependencies"]:
            recommendations.append({
                "category": "Dependencies",
                "action": "Resolve duplicate dependencies",
                "details": dep_analysis["duplicate_dependencies"][:3],
                "impact": "Reduce package size and conflicts"
            })
        
        # 代碼質量改進
        quality_issues = python_analysis["code_quality_issues"]
        if quality_issues["long_functions"]:
            recommendations.append({
                "category": "Code Quality",
                "action": "Refactor long functions",
                "details": f"Found {len(quality_issues['long_functions'])} functions >50 lines",
                "impact": "Improve maintainability"
            })
        
        self.analysis_results["cleanup_recommendations"] = recommendations
        print(f"   Generated {len(recommendations)} cleanup recommendations")
    
    def generate_review_report(self):
        """生成審查報告"""
        print("\n" + "="*50)
        print("CODE REVIEW SUMMARY")
        print("="*50)
        
        # Python分析摘要
        py_analysis = self.analysis_results["python_analysis"]
        print(f"\nPython Code Analysis:")
        print(f"  Total files: {py_analysis['total_files']}")
        print(f"  Unique imports: {py_analysis['imports_analysis']['unique_imports']}")
        print(f"  Functions: {py_analysis['function_analysis']['total_functions']}")
        print(f"  Classes: {py_analysis['function_analysis']['classes']}")
        print(f"  Potentially unused files: {len(py_analysis['unused_files'])}")
        
        # JavaScript分析摘要
        js_analysis = self.analysis_results["javascript_analysis"]
        print(f"\nJavaScript Code Analysis:")
        print(f"  Total files: {js_analysis['total_files']}")
        print(f"  Package.json files: {js_analysis['package_json_analysis']['package_json_count']}")
        print(f"  Unused files: {len(js_analysis['unused_files'])}")
        
        # 依賴項分析摘要
        dep_analysis = self.analysis_results["dependency_analysis"]
        print(f"\nDependency Analysis:")
        print(f"  Requirements files: {dep_analysis['python_requirements']['requirements_files']}")
        print(f"  Total Python requirements: {dep_analysis['python_requirements']['total_requirements']}")
        print(f"  Node.js directories: {dep_analysis['node_modules_size']['node_modules_directories']}")
        print(f"  Duplicate dependencies: {len(dep_analysis['duplicate_dependencies'])}")
        
        # 清理建議摘要
        recommendations = self.analysis_results["cleanup_recommendations"]
        print(f"\nCleanup Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec['category']}: {rec['action']}")
            print(f"     Impact: {rec['impact']}")
        
        # 保存詳細報告
        self.save_detailed_report()
    
    def save_detailed_report(self):
        """保存詳細報告"""
        try:
            with open("code_review_report.json", "w", encoding="utf-8") as f:
                json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
            print(f"\nDetailed report saved to: code_review_report.json")
        except Exception as e:
            print(f"Failed to save detailed report: {e}")

if __name__ == "__main__":
    analyzer = CodeReviewAnalyzer()
    analyzer.run_comprehensive_review()