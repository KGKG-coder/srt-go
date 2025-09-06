#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
創建綜合測試數據集
為性能監控系統建立多樣化的音頻測試集合，涵蓋不同時長、內容類型和品質
"""

import os
import sys
import json
import time
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# 設定控制台編碼
if sys.platform.startswith('win'):
    import os
    os.system('chcp 65001 > NUL')
    sys.stdout.reconfigure(encoding='utf-8')

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_dataset_creation.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveTestDatasetManager:
    """綜合測試數據集管理器"""
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            self.base_dir = Path(__file__).parent / "test_datasets"
        else:
            self.base_dir = Path(base_dir)
        
        # 確保基礎目錄存在
        self.base_dir.mkdir(exist_ok=True)
        
        # 測試分類目錄
        self.categories = {
            'short': self.base_dir / "short_clips",      # 短片段 (5-30秒)
            'medium': self.base_dir / "medium_clips",    # 中等長度 (30秒-5分鐘)
            'long': self.base_dir / "long_clips",        # 長音頻 (5-30分鐘)
            'very_long': self.base_dir / "very_long_clips", # 超長音頻 (30分鐘+)
            'multilingual': self.base_dir / "multilingual", # 多語言測試
            'quality_tests': self.base_dir / "quality_tests", # 品質測試
            'special_cases': self.base_dir / "special_cases"  # 特殊情況
        }
        
        # 創建分類目錄
        for category_path in self.categories.values():
            category_path.mkdir(exist_ok=True)
    
    def get_existing_test_files(self) -> Dict[str, List[str]]:
        """搜尋現有的測試音頻檔案"""
        logger.info("=== 掃描現有測試檔案 ===")
        
        # 搜尋路徑
        search_paths = [
            Path(__file__).parent.parent / "test_VIDEO",  # 主要測試目錄
            Path("C:/Users/USER-ART0/Desktop"),           # 桌面
            Path(__file__).parent,                        # 當前目錄
        ]
        
        existing_files = {}
        audio_extensions = {'.mp3', '.wav', '.mp4', '.m4a', '.flac', '.ogg', '.aac'}
        
        for search_path in search_paths:
            if search_path.exists():
                logger.info(f"搜尋路徑: {search_path}")
                files = []
                
                for file_path in search_path.rglob('*'):
                    if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
                        # 估算檔案大小和可能的時長
                        file_size = file_path.stat().st_size
                        estimated_duration = self._estimate_audio_duration(file_path)
                        
                        files.append({
                            'path': str(file_path),
                            'name': file_path.name,
                            'size': file_size,
                            'size_mb': round(file_size / (1024*1024), 2),
                            'estimated_duration': estimated_duration,
                            'extension': file_path.suffix.lower()
                        })
                
                if files:
                    existing_files[str(search_path)] = files
                    logger.info(f"  找到 {len(files)} 個音頻檔案")
        
        return existing_files
    
    def _estimate_audio_duration(self, file_path: Path) -> float:
        """估算音頻時長（基於檔案大小和類型）"""
        file_size = file_path.stat().st_size / (1024*1024)  # MB
        extension = file_path.suffix.lower()
        filename = file_path.name.lower()
        
        # 基於檔案名稱的啟發式估算
        if any(keyword in filename for keyword in ['short', 'test', 'sample']):
            return min(30, file_size * 8)  # 測試檔案通常較短
        elif any(keyword in filename for keyword in ['song', 'music', '音樂']):
            return min(300, file_size * 6)  # 音樂檔案
        elif 'interview' in filename or '訪談' in filename:
            return min(1800, file_size * 4)  # 訪談可能較長
        
        # 基於檔案大小的通用估算
        if extension == '.mp3':
            return file_size * 8  # 約1MB/min for 128kbps
        elif extension == '.wav':
            return file_size / 10  # 約10MB/min for CD quality
        elif extension == '.mp4':
            return file_size * 2  # 視頻檔案音軌估算
        else:
            return file_size * 6  # 一般壓縮音頻
    
    def categorize_existing_files(self, existing_files: Dict[str, List[str]]) -> Dict[str, List[Dict]]:
        """將現有檔案按照測試需求分類"""
        logger.info("=== 檔案分類處理 ===")
        
        categorized = {
            'short': [],      # 5-30秒
            'medium': [],     # 30秒-5分鐘
            'long': [],       # 5-30分鐘
            'very_long': [],  # 30分鐘+
            'multilingual': [],
            'quality_tests': [],
            'special_cases': []
        }
        
        for search_path, files in existing_files.items():
            for file_info in files:
                duration = file_info['estimated_duration']
                filename = file_info['name'].lower()
                
                # 時長分類
                if duration <= 30:
                    categorized['short'].append(file_info)
                elif duration <= 300:  # 5分鐘
                    categorized['medium'].append(file_info)
                elif duration <= 1800:  # 30分鐘
                    categorized['long'].append(file_info)
                else:
                    categorized['very_long'].append(file_info)
                
                # 多語言檢測
                if any(lang in filename for lang in ['en', 'english', 'jp', 'japanese', 'ko', 'korean']):
                    categorized['multilingual'].append(file_info)
                
                # 品質測試檢測
                if any(quality in filename for quality in ['hd', 'high', '高品質', 'lossless']):
                    categorized['quality_tests'].append(file_info)
                elif any(quality in filename for quality in ['low', '低品質', 'compressed']):
                    categorized['quality_tests'].append(file_info)
                
                # 特殊情況檢測
                if any(special in filename for special in ['noise', '雜音', 'echo', '回音', 'fast', '快速', 'slow', '慢速']):
                    categorized['special_cases'].append(file_info)
        
        # 輸出分類結果
        for category, files in categorized.items():
            logger.info(f"{category}: {len(files)} 個檔案")
            for file_info in files[:3]:  # 顯示前3個作為範例
                logger.info(f"  - {file_info['name']} ({file_info['estimated_duration']:.1f}s, {file_info['size_mb']}MB)")
        
        return categorized
    
    def create_test_dataset_manifest(self, categorized_files: Dict[str, List[Dict]]) -> Dict:
        """創建測試數據集清單"""
        logger.info("=== 創建測試數據集清單 ===")
        
        manifest = {
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_files': sum(len(files) for files in categorized_files.values()),
            'categories': {},
            'performance_test_plan': {},
            'recommended_test_sequence': []
        }
        
        # 處理各分類
        for category, files in categorized_files.items():
            if not files:
                continue
                
            manifest['categories'][category] = {
                'count': len(files),
                'files': files,
                'total_duration': sum(f['estimated_duration'] for f in files),
                'total_size_mb': sum(f['size_mb'] for f in files),
                'recommended_for_performance_testing': self._get_performance_test_recommendations(category, files)
            }
        
        # 性能測試計劃
        manifest['performance_test_plan'] = self._create_performance_test_plan(categorized_files)
        
        # 推薦測試順序
        manifest['recommended_test_sequence'] = self._create_test_sequence(categorized_files)
        
        return manifest
    
    def _get_performance_test_recommendations(self, category: str, files: List[Dict]) -> Dict:
        """獲取性能測試建議"""
        if category == 'short':
            return {
                'priority': 'high',
                'test_focus': 'latency_optimization',
                'expected_rtf_range': '0.05-0.2',
                'performance_modes': ['auto', 'gpu', 'cpu'],
                'notes': '短片段測試啟動延遲和最小處理單元效能'
            }
        elif category == 'medium':
            return {
                'priority': 'high',
                'test_focus': 'standard_performance',
                'expected_rtf_range': '0.1-0.5',
                'performance_modes': ['auto', 'gpu'],
                'notes': '標準性能基準測試，最常見的使用場景'
            }
        elif category == 'long':
            return {
                'priority': 'medium',
                'test_focus': 'memory_management',
                'expected_rtf_range': '0.2-0.8',
                'performance_modes': ['gpu', 'cpu'],
                'notes': '記憶體管理和長時間處理穩定性'
            }
        elif category == 'very_long':
            return {
                'priority': 'low',
                'test_focus': 'stress_testing',
                'expected_rtf_range': '0.5-1.5',
                'performance_modes': ['cpu'],
                'notes': '壓力測試，驗證系統極限和穩定性'
            }
        else:
            return {
                'priority': 'medium',
                'test_focus': 'specialized_scenarios',
                'expected_rtf_range': '0.1-1.0',
                'performance_modes': ['auto'],
                'notes': f'{category} 專用測試場景'
            }
    
    def _create_performance_test_plan(self, categorized_files: Dict[str, List[Dict]]) -> Dict:
        """創建綜合性能測試計劃"""
        plan = {
            'quick_validation': {
                'description': '快速驗證所有性能模式',
                'duration': '5-10分鐘',
                'files': []
            },
            'standard_benchmark': {
                'description': '標準性能基準測試',
                'duration': '15-30分鐘',
                'files': []
            },
            'comprehensive_test': {
                'description': '全面性能和穩定性測試',
                'duration': '1-2小時',
                'files': []
            },
            'stress_test': {
                'description': '壓力測試和極限情況',
                'duration': '2-4小時',
                'files': []
            }
        }
        
        # 快速驗證 - 選擇最短的檔案
        if categorized_files.get('short'):
            plan['quick_validation']['files'].extend(
                sorted(categorized_files['short'], key=lambda x: x['estimated_duration'])[:2]
            )
        
        # 標準基準 - 中等長度檔案
        if categorized_files.get('medium'):
            plan['standard_benchmark']['files'].extend(
                sorted(categorized_files['medium'], key=lambda x: x['estimated_duration'])[:3]
            )
        
        # 全面測試 - 各類型檔案
        for category in ['short', 'medium', 'long']:
            if categorized_files.get(category):
                plan['comprehensive_test']['files'].extend(
                    sorted(categorized_files[category], key=lambda x: x['estimated_duration'])[:2]
                )
        
        # 壓力測試 - 長音頻檔案
        if categorized_files.get('long'):
            plan['stress_test']['files'].extend(categorized_files['long'])
        if categorized_files.get('very_long'):
            plan['stress_test']['files'].extend(categorized_files['very_long'])
        
        return plan
    
    def _create_test_sequence(self, categorized_files: Dict[str, List[Dict]]) -> List[Dict]:
        """創建推薦的測試執行順序"""
        sequence = []
        
        # 1. 快速煙霧測試
        sequence.append({
            'phase': 'smoke_test',
            'description': '快速煙霧測試 - 驗證基本功能',
            'files': sorted(categorized_files.get('short', []), key=lambda x: x['estimated_duration'])[:1],
            'performance_modes': ['auto'],
            'expected_duration': '1-2分鐘'
        })
        
        # 2. 性能模式驗證
        sequence.append({
            'phase': 'performance_modes',
            'description': '性能模式驗證 - 測試所有模式',
            'files': sorted(categorized_files.get('medium', []), key=lambda x: x['estimated_duration'])[:1],
            'performance_modes': ['auto', 'gpu', 'cpu'],
            'expected_duration': '5-10分鐘'
        })
        
        # 3. 時長範圍測試
        sequence.append({
            'phase': 'duration_range',
            'description': '時長範圍測試 - 不同時長檔案',
            'files': self._select_representative_files(categorized_files),
            'performance_modes': ['auto'],
            'expected_duration': '10-20分鐘'
        })
        
        # 4. 品質和特殊情況
        sequence.append({
            'phase': 'quality_special',
            'description': '品質和特殊情況測試',
            'files': categorized_files.get('quality_tests', [])[:2] + categorized_files.get('special_cases', [])[:2],
            'performance_modes': ['auto'],
            'expected_duration': '5-15分鐘'
        })
        
        # 5. 多語言測試
        if categorized_files.get('multilingual'):
            sequence.append({
                'phase': 'multilingual',
                'description': '多語言支援測試',
                'files': categorized_files['multilingual'][:3],
                'performance_modes': ['auto'],
                'expected_duration': '10-30分鐘'
            })
        
        return sequence
    
    def _select_representative_files(self, categorized_files: Dict[str, List[Dict]]) -> List[Dict]:
        """選擇代表性檔案進行時長範圍測試"""
        representative = []
        
        # 每個時長分類選一個代表檔案
        for category in ['short', 'medium', 'long']:
            files = categorized_files.get(category, [])
            if files:
                # 選擇中位數時長的檔案
                sorted_files = sorted(files, key=lambda x: x['estimated_duration'])
                mid_index = len(sorted_files) // 2
                representative.append(sorted_files[mid_index])
        
        return representative
    
    def generate_performance_test_scripts(self, manifest: Dict) -> List[str]:
        """生成性能測試腳本"""
        logger.info("=== 生成性能測試腳本 ===")
        
        script_files = []
        
        # 為每個測試計劃生成腳本
        for plan_name, plan_config in manifest['performance_test_plan'].items():
            script_content = self._generate_test_script(plan_name, plan_config)
            script_file = self.base_dir / f"run_{plan_name}_test.py"
            
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            script_files.append(str(script_file))
            logger.info(f"生成測試腳本: {script_file.name}")
        
        return script_files
    
    def _generate_test_script(self, plan_name: str, plan_config: Dict) -> str:
        """生成單個測試計劃的腳本"""
        # 轉換檔案格式以便在腳本中使用
        test_files_str = json.dumps(plan_config['files'], ensure_ascii=False, indent=4)
        
        script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動生成的性能測試腳本: {plan_name}
{plan_config['description']}
預估執行時間: {plan_config['duration']}
"""

import sys
import os
import time
import subprocess
import json
from pathlib import Path

# 添加父目錄到路徑以便導入
sys.path.append(str(Path(__file__).parent.parent))

def run_performance_test():
    """執行性能測試"""
    print("=== {plan_name} 性能測試 ===")
    print("描述: {plan_config['description']}")
    print("預估時間: {plan_config['duration']}")
    print()
    
    test_files = {test_files_str}
    performance_modes = ['auto', 'gpu', 'cpu']
    
    results = []
    
    for file_info in test_files:
        file_path = file_info['path']
        if not Path(file_path).exists():
            print(f"警告: 檔案不存在 {{file_path}}")
            continue
            
        print(f"測試檔案: {{file_info['name']}} ({{file_info['estimated_duration']:.1f}}s)")
        
        for mode in performance_modes:
            print(f"  測試模式: {{mode}}")
            
            # 構建測試命令
            cmd = [
                "python",
                str(Path(__file__).parent.parent / "electron_backend.py"),
                "--files", f'["{{file_path}}"]',
                "--settings", f'{{"model":"large","language":"auto","performanceMode":"{{mode}}","outputFormat":"srt","customDir":"C:/temp/test_results","enable_gpu":{{"true" if mode=="gpu" else "false"}}}}',
                "--corrections", "[]"
            ]
            
            # 執行測試
            start_time = time.time()
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                end_time = time.time()
                
                processing_time = end_time - start_time
                rtf = processing_time / file_info['estimated_duration']
                
                test_result = {{
                    'file': file_info['name'],
                    'mode': mode,
                    'processing_time': processing_time,
                    'audio_duration': file_info['estimated_duration'],
                    'rtf': rtf,
                    'success': result.returncode == 0,
                    'stdout': result.stdout[:500],  # 前500字符
                    'stderr': result.stderr[:500] if result.stderr else None
                }}
                
                results.append(test_result)
                
                print(f"    處理時間: {{processing_time:.1f}}s")
                print(f"    RTF: {{rtf:.3f}}")
                print(f"    狀態: {{'成功' if test_result['success'] else '失敗'}}")
                
                if not test_result['success']:
                    print(f"    錯誤: {{result.stderr[:200]}}")
                
            except subprocess.TimeoutExpired:
                print(f"    超時 (>10分鐘)")
                results.append({{'file': file_info['name'], 'mode': mode, 'status': 'timeout'}})
            except Exception as e:
                print(f"    異常: {{e}}")
                results.append({{'file': file_info['name'], 'mode': mode, 'status': 'error', 'error': str(e)}})
            
            print()
    
    # 保存結果
    result_file = Path(__file__).parent / "{plan_name}_results.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({{'test_name': '{plan_name}', 'results': results, 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')}}, f, ensure_ascii=False, indent=2)
    
    print(f"測試結果已保存至: {{result_file}}")
    return results

if __name__ == "__main__":
    results = run_performance_test()
    print(f"\\n{plan_name} 測試完成，共執行 {{len(results)}} 個測試案例")
'''
        
        return script_content
    
    def save_manifest(self, manifest: Dict) -> str:
        """保存測試數據集清單"""
        manifest_file = self.base_dir / "test_dataset_manifest.json"
        
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        
        logger.info(f"測試數據集清單已保存至: {manifest_file}")
        return str(manifest_file)
    
    def create_readme(self, manifest: Dict) -> str:
        """創建測試數據集說明文檔"""
        readme_content = f"""# 綜合測試數據集

建立時間: {manifest['created_at']}
總檔案數: {manifest['total_files']} 個

## 檔案分類

"""
        
        for category, info in manifest['categories'].items():
            readme_content += f"### {category.upper()} ({info['count']} 個檔案)\n"
            readme_content += f"- 總時長: {info['total_duration']:.1f}秒 ({info['total_duration']/60:.1f}分鐘)\n"
            readme_content += f"- 總大小: {info['total_size_mb']:.1f}MB\n"
            
            if info.get('recommended_for_performance_testing'):
                rec = info['recommended_for_performance_testing']
                readme_content += f"- 測試重點: {rec['test_focus']}\n"
                readme_content += f"- 預期RTF範圍: {rec['expected_rtf_range']}\n"
                readme_content += f"- 建議模式: {', '.join(rec['performance_modes'])}\n"
            
            readme_content += "\n代表性檔案:\n"
            for file_info in info['files'][:3]:
                readme_content += f"- {file_info['name']} ({file_info['estimated_duration']:.1f}s, {file_info['size_mb']}MB)\n"
            readme_content += "\n"
        
        readme_content += "## 測試計劃\n\n"
        for plan_name, plan_config in manifest['performance_test_plan'].items():
            readme_content += f"### {plan_name.upper()}\n"
            readme_content += f"- {plan_config['description']}\n"
            readme_content += f"- 預估時間: {plan_config['duration']}\n"
            readme_content += f"- 測試檔案: {len(plan_config['files'])} 個\n\n"
        
        readme_content += "## 推薦測試順序\n\n"
        for i, phase in enumerate(manifest['recommended_test_sequence'], 1):
            readme_content += f"{i}. **{phase['phase'].upper()}** - {phase['description']}\n"
            readme_content += f"   - 預估時間: {phase['expected_duration']}\n"
            readme_content += f"   - 測試檔案: {len(phase['files'])} 個\n"
            readme_content += f"   - 性能模式: {', '.join(phase['performance_modes'])}\n\n"
        
        readme_content += """## 使用方法

### 執行快速驗證測試
```bash
python run_quick_validation_test.py
```

### 執行標準基準測試
```bash
python run_standard_benchmark_test.py
```

### 執行全面性能測試
```bash
python run_comprehensive_test_test.py
```

### 執行壓力測試
```bash
python run_stress_test_test.py
```

## 結果分析

測試結果將保存為JSON格式，包含：
- 處理時間和RTF值
- 性能等級分類
- 成功/失敗狀態
- 詳細的錯誤信息（如有）

結果檔案位置：
- quick_validation_results.json
- standard_benchmark_results.json
- comprehensive_test_results.json
- stress_test_results.json
"""
        
        readme_file = self.base_dir / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        logger.info(f"測試說明文檔已創建: {readme_file}")
        return str(readme_file)

def main():
    """主函數 - 建立綜合測試數據集"""
    logger.info("開始建立綜合測試數據集...")
    logger.info("=" * 60)
    
    try:
        # 1. 初始化管理器
        dataset_manager = ComprehensiveTestDatasetManager()
        
        # 2. 掃描現有檔案
        existing_files = dataset_manager.get_existing_test_files()
        
        if not existing_files:
            logger.warning("未找到任何測試音頻檔案！")
            logger.info("請將測試檔案放置在以下位置之一：")
            logger.info("- test_VIDEO/ 目錄")
            logger.info("- C:/Users/USER-ART0/Desktop/")
            logger.info("- 當前 python/ 目錄")
            return False
        
        # 3. 分類檔案
        categorized_files = dataset_manager.categorize_existing_files(existing_files)
        
        # 4. 創建測試清單
        manifest = dataset_manager.create_test_dataset_manifest(categorized_files)
        
        # 5. 生成測試腳本
        script_files = dataset_manager.generate_performance_test_scripts(manifest)
        
        # 6. 保存清單和說明
        manifest_file = dataset_manager.save_manifest(manifest)
        readme_file = dataset_manager.create_readme(manifest)
        
        # 7. 輸出摘要
        logger.info("")
        logger.info("=" * 60)
        logger.info("🎉 綜合測試數據集建立完成！")
        logger.info("")
        logger.info(f"📁 基礎目錄: {dataset_manager.base_dir}")
        logger.info(f"📊 總檔案數: {manifest['total_files']} 個")
        logger.info(f"📝 測試清單: {Path(manifest_file).name}")
        logger.info(f"📚 說明文檔: {Path(readme_file).name}")
        logger.info(f"🔧 測試腳本: {len(script_files)} 個")
        logger.info("")
        logger.info("檔案分佈：")
        for category, info in manifest['categories'].items():
            if info['count'] > 0:
                logger.info(f"  {category}: {info['count']} 個檔案 ({info['total_duration']/60:.1f}分鐘)")
        
        logger.info("")
        logger.info("🚀 建議開始測試順序：")
        logger.info("1. python run_quick_validation_test.py")
        logger.info("2. python run_standard_benchmark_test.py")
        logger.info("3. python run_comprehensive_test_test.py")
        
        return True
        
    except Exception as e:
        logger.error(f"建立測試數據集時發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)