#!/usr/bin/env python3
"""
性能基準測試 - RTF (Real-Time Factor) 測量
測量 SRT GO 在不同條件下的處理速度性能
"""

import pytest
import time
import sys
import json
import subprocess
from pathlib import Path
import tempfile
from typing import Dict, List, Tuple

# 設置路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "python"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.ultra_realistic_speech_generator import create_ultra_realistic_test_audio


class RTFBenchmark:
    """RTF 性能基準測試類"""
    
    def __init__(self):
        self.results = []
        # 修復到實際的工作backend路徑
        self.backend_script = Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "dist" / "win-unpacked" / "resources" / "resources" / "python" / "electron_backend.py"
        
        # 檢查backend腳本是否存在，否則使用備用路徑
        if not self.backend_script.exists():
            alt_backend = Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "python" / "electron_backend.py"
            if alt_backend.exists():
                self.backend_script = alt_backend
            else:
                print(f"WARNING: Backend script not found at expected locations")
                print(f"Primary: {self.backend_script}")
                print(f"Alternative: {alt_backend}")
        
        print(f"Using backend script: {self.backend_script}")
        print(f"Backend exists: {self.backend_script.exists()}")
    
    def create_test_audio(self, duration: float, temp_dir: Path) -> str:
        """創建指定長度的測試音頻"""
        from utils.ultra_realistic_speech_generator import UltraRealisticSpeechGenerator, save_audio_wav
        
        generator = UltraRealisticSpeechGenerator()
        audio = generator.create_whisper_optimized_speech(duration=duration)
        
        audio_path = temp_dir / f"test_audio_{duration}s.wav"
        save_audio_wav(audio, str(audio_path))
        return str(audio_path)
    
    def measure_processing_time(self, audio_file: str, settings: Dict) -> Tuple[float, bool]:
        """測量音頻處理時間"""
        output_dir = Path(tempfile.mkdtemp(prefix="rtf_test_"))
        settings["customDir"] = str(output_dir)
        
        # 使用打包版本的Python解釋器
        python_exe = Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "dist" / "win-unpacked" / "resources" / "resources" / "mini_python" / "python.exe"
        
        if not python_exe.exists():
            # 備用：尋找其他可能的Python路徑
            alt_python = Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "mini_python" / "python.exe"
            if alt_python.exists():
                python_exe = alt_python
            else:
                python_exe = sys.executable  # 最後備用：系統Python
        
        cmd = [
            str(python_exe),
            str(self.backend_script),
            "--files", json.dumps([audio_file]),
            "--settings", json.dumps(settings),
            "--corrections", json.dumps([])
        ]
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=300  # 5分鐘超時
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # 檢查是否成功
            success = result.returncode == 0
            if success:
                # 檢查是否有輸出文件
                srt_files = list(output_dir.glob("*.srt"))
                success = len(srt_files) > 0 and any(f.stat().st_size > 0 for f in srt_files)
            
            return processing_time, success
            
        except subprocess.TimeoutExpired:
            return 300.0, False  # 超時視為失敗
    
    def calculate_rtf(self, audio_duration: float, processing_time: float) -> float:
        """計算 RTF (Real-Time Factor)"""
        return processing_time / audio_duration
    
    def run_benchmark_suite(self) -> List[Dict]:
        """運行完整的 RTF 基準測試套件"""
        print("=== SRT GO RTF Performance Benchmark ===")
        print()
        
        # 測試配置
        test_configs = [
            # 不同音頻長度測試
            {"duration": 5.0, "model": "medium", "gpu": False, "name": "Short_CPU_Medium"},
            {"duration": 15.0, "model": "medium", "gpu": False, "name": "Medium_CPU_Medium"},
            {"duration": 30.0, "model": "medium", "gpu": False, "name": "Long_CPU_Medium"},
            
            # 不同模型測試
            {"duration": 15.0, "model": "small", "gpu": False, "name": "Medium_CPU_Small"},
            {"duration": 15.0, "model": "large", "gpu": False, "name": "Medium_CPU_Large"},
            
            # GPU測試 (如果可用)
            {"duration": 15.0, "model": "medium", "gpu": True, "name": "Medium_GPU_Medium"},
            {"duration": 15.0, "model": "large", "gpu": True, "name": "Medium_GPU_Large"},
        ]
        
        results = []
        
        with tempfile.TemporaryDirectory(prefix="rtf_benchmark_") as temp_dir:
            temp_path = Path(temp_dir)
            
            for i, config in enumerate(test_configs, 1):
                print(f"[{i}/{len(test_configs)}] Test: {config['name']}")
                print(f"  Duration: {config['duration']}s")
                print(f"  Model: {config['model']}")
                print(f"  GPU: {'Enabled' if config['gpu'] else 'Disabled'}")
                
                # 創建測試音頻
                audio_file = self.create_test_audio(config["duration"], temp_path)
                
                # 準備設置
                settings = {
                    "model": config["model"],
                    "language": "auto",
                    "outputFormat": "srt",
                    "enable_gpu": config["gpu"],
                    "enablePureVoiceMode": False,  # 關閉以獲得穩定性能
                    "vad_threshold": 0.35
                }
                
                # 執行測試 (3次取平均)
                times = []
                successes = []
                
                for attempt in range(3):
                    print(f"  Attempt {attempt + 1}/3...", end=" ")
                    processing_time, success = self.measure_processing_time(audio_file, settings)
                    times.append(processing_time)
                    successes.append(success)
                    
                    if success:
                        rtf = self.calculate_rtf(config["duration"], processing_time)
                        print(f"Complete ({processing_time:.1f}s, RTF: {rtf:.3f})")
                    else:
                        print("Failed")
                
                # 計算結果
                avg_time = sum(times) / len(times) if times else 0
                success_rate = sum(successes) / len(successes) if successes else 0
                avg_rtf = self.calculate_rtf(config["duration"], avg_time) if avg_time > 0 else float('inf')
                
                result = {
                    "name": config["name"],
                    "duration": config["duration"],
                    "model": config["model"],
                    "gpu": config["gpu"],
                    "avg_processing_time": avg_time,
                    "avg_rtf": avg_rtf,
                    "success_rate": success_rate,
                    "attempts": len(times)
                }
                
                results.append(result)
                
                # 顯示結果
                if success_rate > 0:
                    print(f"  > Avg Processing Time: {avg_time:.1f}s")
                    print(f"  > Avg RTF: {avg_rtf:.3f}")
                    print(f"  > Success Rate: {success_rate*100:.0f}%")
                    
                    # RTF 性能評級
                    if avg_rtf <= 0.2:
                        rating = "Excellent (RTF <= 0.2)"
                    elif avg_rtf <= 0.5:
                        rating = "Good (RTF <= 0.5)"
                    elif avg_rtf <= 1.0:
                        rating = "Acceptable (RTF <= 1.0)"
                    else:
                        rating = "Needs Improvement (RTF > 1.0)"
                    
                    print(f"  > Performance Rating: {rating}")
                else:
                    print(f"  > Test FAILED (Success Rate: 0%)")
                
                print()
        
        return results
    
    def generate_performance_report(self, results: List[Dict]) -> str:
        """生成性能報告"""
        report = ["# SRT GO RTF 性能基準測試報告", ""]
        report.append(f"測試時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"測試案例: {len(results)} 個")
        report.append("")
        
        # 成功的測試結果
        successful_results = [r for r in results if r["success_rate"] > 0]
        
        if successful_results:
            report.append("## 📊 性能統計")
            report.append("")
            
            # 最佳性能
            best_rtf = min(r["avg_rtf"] for r in successful_results)
            best_config = next(r for r in successful_results if r["avg_rtf"] == best_rtf)
            report.append(f"**最佳 RTF**: {best_rtf:.3f} ({best_config['name']})")
            
            # CPU vs GPU 比較 (如果有 GPU 測試)
            cpu_results = [r for r in successful_results if not r["gpu"]]
            gpu_results = [r for r in successful_results if r["gpu"]]
            
            if cpu_results:
                avg_cpu_rtf = sum(r["avg_rtf"] for r in cpu_results) / len(cpu_results)
                report.append(f"**CPU 平均 RTF**: {avg_cpu_rtf:.3f}")
            
            if gpu_results:
                avg_gpu_rtf = sum(r["avg_rtf"] for r in gpu_results) / len(gpu_results)
                report.append(f"**GPU 平均 RTF**: {avg_gpu_rtf:.3f}")
                
                if cpu_results and gpu_results:
                    speedup = avg_cpu_rtf / avg_gpu_rtf
                    report.append(f"**GPU 加速比**: {speedup:.1f}x")
            
            report.append("")
            
            # 詳細結果表格
            report.append("## 📋 詳細測試結果")
            report.append("")
            report.append("| 測試名稱 | 音頻長度 | 模型 | GPU | 處理時間 | RTF | 成功率 | 評級 |")
            report.append("|---------|---------|------|-----|---------|-----|--------|------|")
            
            for r in results:
                if r["success_rate"] > 0:
                    if r["avg_rtf"] <= 0.2:
                        rating = "優秀"
                    elif r["avg_rtf"] <= 0.5:
                        rating = "良好"
                    elif r["avg_rtf"] <= 1.0:
                        rating = "可接受"
                    else:
                        rating = "需改進"
                    
                    gpu_text = "✓" if r["gpu"] else "✗"
                    report.append(f"| {r['name']} | {r['duration']:.0f}s | {r['model']} | {gpu_text} | {r['avg_processing_time']:.1f}s | {r['avg_rtf']:.3f} | {r['success_rate']*100:.0f}% | {rating} |")
                else:
                    report.append(f"| {r['name']} | {r['duration']:.0f}s | {r['model']} | {'✓' if r['gpu'] else '✗'} | - | - | 0% | 失敗 |")
        
        else:
            report.append("## ❌ 所有測試均失敗")
            report.append("請檢查系統配置和依賴項。")
        
        report.append("")
        report.append("## 📈 性能目標")
        report.append("")
        report.append("- **RTF ≤ 0.2**: 優秀 (適合實時應用)")
        report.append("- **RTF ≤ 0.5**: 良好 (適合批量處理)")
        report.append("- **RTF ≤ 1.0**: 可接受 (基本要求)")
        report.append("- **RTF > 1.0**: 需改進 (性能不足)")
        
        return "\n".join(report)


@pytest.fixture
def rtf_benchmark():
    """RTF 基準測試 fixture"""
    return RTFBenchmark()


def test_rtf_performance_suite(rtf_benchmark):
    """RTF 性能測試套件"""
    results = rtf_benchmark.run_benchmark_suite()
    
    # 驗證至少有一些測試成功
    successful_tests = [r for r in results if r["success_rate"] > 0]
    assert len(successful_tests) > 0, "沒有任何 RTF 測試成功"
    
    # 檢查性能是否符合基本要求 (RTF < 2.0)
    acceptable_performance = [r for r in successful_tests if r["avg_rtf"] < 2.0]
    assert len(acceptable_performance) > 0, "沒有測試達到基本性能要求 (RTF < 2.0)"
    
    # 生成性能報告
    report = rtf_benchmark.generate_performance_report(results)
    
    # 保存報告
    report_file = Path(__file__).parent / "RTF_BENCHMARK_REPORT.md"
    report_file.write_text(report, encoding='utf-8')
    
    print(f"性能報告已保存至: {report_file}")


if __name__ == "__main__":
    # 直接運行基準測試
    benchmark = RTFBenchmark()
    results = benchmark.run_benchmark_suite()
    
    # 生成並保存報告
    report = benchmark.generate_performance_report(results)
    report_file = Path(__file__).parent / "RTF_BENCHMARK_REPORT.md"
    report_file.parent.mkdir(exist_ok=True)
    report_file.write_text(report, encoding='utf-8')
    
    print("=" * 50)
    print("RTF Performance Benchmark Complete!")
    print(f"Report saved to: {report_file}")
    print("=" * 50)