#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RTF 效能監控系統
持續追蹤和監控 SRT GO 的效能基準，檢測效能回歸
"""

import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import statistics
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
import sys

@dataclass
class RTFResult:
    """RTF 測試結果數據結構"""
    timestamp: str
    model_config: str
    gpu_enabled: bool
    rtf_score: float
    processing_time: float
    audio_duration: float
    success: bool
    commit_hash: Optional[str] = None
    branch: Optional[str] = None

class RTFMonitoringSystem:
    """RTF 效能監控系統"""
    
    def __init__(self, baseline_file: Path = None):
        self.results_file = Path(__file__).parent / "rtf_monitoring_results.json"
        self.baseline_file = baseline_file or Path(__file__).parent / "RTF_PERFORMANCE_BASELINE_REPORT.md"
        self.alerts_file = Path(__file__).parent / "performance_alerts.json"
        self.setup_logging()
        self.load_baselines()
        
    def setup_logging(self):
        """設置日誌系統"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(Path(__file__).parent / "rtf_monitoring.log", encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_baselines(self):
        """載入基準效能數據"""
        self.baselines = {
            "Medium_GPU": {"rtf": 0.736, "tolerance": 0.2},  # ±20% 容忍度
            "Medium_CPU": {"rtf": 2.012, "tolerance": 0.3},  # ±30% 容忍度
            "Small_CPU": {"rtf": 2.012, "tolerance": 0.3}
        }
        self.logger.info(f"載入基準數據: {self.baselines}")
    
    def get_git_info(self) -> Tuple[str, str]:
        """取得當前 Git 資訊"""
        try:
            commit_hash = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'], 
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            return commit_hash[:8], branch
        except:
            return None, None
    
    def run_rtf_benchmark(self) -> List[RTFResult]:
        """執行 RTF 基準測試"""
        self.logger.info("開始執行 RTF 基準測試...")
        
        # 測試配置
        test_configs = [
            {"model": "medium", "gpu": False, "name": "Medium_CPU"},
            {"model": "medium", "gpu": True, "name": "Medium_GPU"},
            {"model": "small", "gpu": False, "name": "Small_CPU"}
        ]
        
        results = []
        commit_hash, branch = self.get_git_info()
        
        for config in test_configs:
            result = self._run_single_test(config, commit_hash, branch)
            if result:
                results.append(result)
                
        self.logger.info(f"RTF 基準測試完成，共 {len(results)} 個結果")
        return results
    
    def _run_single_test(self, config: Dict, commit_hash: str, branch: str) -> Optional[RTFResult]:
        """執行單一配置的測試"""
        try:
            # 尋找可用的後端
            backend_paths = [
                Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "python" / "electron_backend.py",
                Path(__file__).parent.parent.parent / "electron-react-app" / "python" / "electron_backend.py"
            ]
            
            backend_script = None
            for path in backend_paths:
                if path.exists():
                    backend_script = path
                    break
            
            if not backend_script:
                self.logger.error("找不到 electron_backend.py")
                return None
            
            # 測試音頻檔案
            test_audio = Path(__file__).parent / "test_data" / "ultra_realistic_english.wav"
            if not test_audio.exists():
                # 使用 E2E 測試的音頻檔案
                test_audio = Path(__file__).parent.parent / "e2e" / "test_data" / "audio" / "ultra_realistic_english.wav"
            
            if not test_audio.exists():
                self.logger.warning(f"測試音頻檔案不存在，跳過測試: {config['name']}")
                return None
            
            # 建構測試命令
            settings = {
                "model": config["model"],
                "language": "auto",
                "outputFormat": "srt",
                "customDir": str(Path(__file__).parent / "temp_output"),
                "enable_gpu": config["gpu"]
            }
            
            # 確保輸出目錄存在
            Path(settings["customDir"]).mkdir(exist_ok=True)
            
            cmd = [
                "python", str(backend_script),
                "--files", json.dumps([str(test_audio)]),
                "--settings", json.dumps(settings),
                "--corrections", "[]"
            ]
            
            self.logger.info(f"執行測試: {config['name']}")
            start_time = time.time()
            
            # 執行測試
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=300  # 5分鐘超時
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # 計算音頻持續時間（假設 5 秒）
            audio_duration = 5.0
            rtf_score = processing_time / audio_duration
            
            # 檢查是否成功
            success = result.returncode == 0 and "COMPLETE" in result.stdout
            
            if success:
                self.logger.info(f"測試成功: {config['name']}, RTF: {rtf_score:.3f}")
            else:
                self.logger.warning(f"測試失敗: {config['name']}, 錯誤: {result.stderr}")
            
            return RTFResult(
                timestamp=datetime.now().isoformat(),
                model_config=config["name"],
                gpu_enabled=config["gpu"],
                rtf_score=rtf_score,
                processing_time=processing_time,
                audio_duration=audio_duration,
                success=success,
                commit_hash=commit_hash,
                branch=branch
            )
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"測試超時: {config['name']}")
            return None
        except Exception as e:
            self.logger.error(f"測試執行錯誤: {config['name']}, {e}")
            return None
    
    def save_results(self, results: List[RTFResult]):
        """儲存測試結果"""
        # 載入現有結果
        existing_results = []
        if self.results_file.exists():
            try:
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    existing_results = existing_data.get('results', [])
            except:
                existing_results = []
        
        # 添加新結果
        new_results = [asdict(result) for result in results]
        all_results = existing_results + new_results
        
        # 保留最近 100 筆記錄
        if len(all_results) > 100:
            all_results = all_results[-100:]
        
        # 儲存結果
        data = {
            "last_updated": datetime.now().isoformat(),
            "total_tests": len(all_results),
            "results": all_results
        }
        
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"儲存 {len(results)} 筆新測試結果")
    
    def check_performance_regression(self, results: List[RTFResult]) -> List[Dict]:
        """檢查效能回歸"""
        alerts = []
        
        for result in results:
            if not result.success:
                continue
                
            baseline = self.baselines.get(result.model_config)
            if not baseline:
                continue
            
            baseline_rtf = baseline["rtf"]
            tolerance = baseline["tolerance"]
            current_rtf = result.rtf_score
            
            # 計算效能變化百分比
            change_percent = ((current_rtf - baseline_rtf) / baseline_rtf) * 100
            
            # 檢查是否超出容忍範圍
            if abs(change_percent) > tolerance * 100:
                alert_type = "regression" if change_percent > 0 else "improvement"
                
                alert = {
                    "timestamp": result.timestamp,
                    "type": alert_type,
                    "model_config": result.model_config,
                    "baseline_rtf": baseline_rtf,
                    "current_rtf": current_rtf,
                    "change_percent": change_percent,
                    "severity": "high" if abs(change_percent) > tolerance * 200 else "medium",
                    "commit_hash": result.commit_hash,
                    "branch": result.branch
                }
                
                alerts.append(alert)
                
                if alert_type == "regression":
                    self.logger.warning(f"效能回歸檢測: {result.model_config}, RTF {baseline_rtf:.3f} → {current_rtf:.3f} ({change_percent:+.1f}%)")
                else:
                    self.logger.info(f"效能改善檢測: {result.model_config}, RTF {baseline_rtf:.3f} → {current_rtf:.3f} ({change_percent:+.1f}%)")
        
        # 儲存警報
        if alerts:
            self._save_alerts(alerts)
        
        return alerts
    
    def _save_alerts(self, alerts: List[Dict]):
        """儲存效能警報"""
        existing_alerts = []
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    existing_alerts = json.load(f)
            except:
                existing_alerts = []
        
        all_alerts = existing_alerts + alerts
        
        # 保留最近 50 筆警報
        if len(all_alerts) > 50:
            all_alerts = all_alerts[-50:]
        
        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump(all_alerts, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"儲存 {len(alerts)} 筆效能警報")
    
    def generate_monitoring_report(self) -> str:
        """生成監控報告"""
        if not self.results_file.exists():
            return "尚無監控數據"
        
        with open(self.results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = data.get('results', [])
        if not results:
            return "尚無監控數據"
        
        # 分析最近的結果
        recent_results = results[-10:]  # 最近 10 筆
        
        report_lines = [
            "# RTF 效能監控報告",
            f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**總測試次數**: {len(results)}",
            f"**最近測試**: {len(recent_results)} 筆",
            "",
            "## 最新效能數據",
            ""
        ]
        
        # 按配置分組分析
        config_groups = {}
        for result in recent_results:
            config = result['model_config']
            if config not in config_groups:
                config_groups[config] = []
            config_groups[config].append(result)
        
        for config, config_results in config_groups.items():
            if not config_results:
                continue
                
            rtf_scores = [r['rtf_score'] for r in config_results if r['success']]
            if not rtf_scores:
                continue
            
            avg_rtf = statistics.mean(rtf_scores)
            baseline = self.baselines.get(config, {}).get('rtf', 0)
            change = ((avg_rtf - baseline) / baseline * 100) if baseline > 0 else 0
            
            status = "✅" if change <= 10 else "⚠️" if change <= 30 else "❌"
            
            report_lines.extend([
                f"### {config} {status}",
                f"- **平均 RTF**: {avg_rtf:.3f}",
                f"- **基準 RTF**: {baseline:.3f}",
                f"- **變化**: {change:+.1f}%",
                f"- **最新測試**: {config_results[-1]['timestamp'][:19]}",
                ""
            ])
        
        # 檢查警報
        alerts_summary = self._get_recent_alerts_summary()
        if alerts_summary:
            report_lines.extend([
                "## 效能警報",
                "",
                alerts_summary
            ])
        
        return '\n'.join(report_lines)
    
    def _get_recent_alerts_summary(self) -> str:
        """取得最近警報摘要"""
        if not self.alerts_file.exists():
            return ""
        
        try:
            with open(self.alerts_file, 'r', encoding='utf-8') as f:
                alerts = json.load(f)
        except:
            return ""
        
        if not alerts:
            return ""
        
        # 最近 24 小時的警報
        recent_alerts = []
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for alert in alerts:
            alert_time = datetime.fromisoformat(alert['timestamp'].replace('Z', '+00:00').replace('+00:00', ''))
            if alert_time > cutoff_time:
                recent_alerts.append(alert)
        
        if not recent_alerts:
            return "✅ 最近 24 小時無效能警報"
        
        summary_lines = []
        for alert in recent_alerts:
            icon = "❌" if alert['type'] == "regression" else "✅"
            summary_lines.append(
                f"{icon} {alert['model_config']}: RTF {alert['baseline_rtf']:.3f} → {alert['current_rtf']:.3f} ({alert['change_percent']:+.1f}%)"
            )
        
        return '\n'.join(summary_lines)

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RTF 效能監控系統")
    parser.add_argument('--run-benchmark', action='store_true', help='執行 RTF 基準測試')
    parser.add_argument('--generate-report', action='store_true', help='生成監控報告')
    parser.add_argument('--check-regression', action='store_true', help='檢查效能回歸')
    parser.add_argument('--baseline-file', type=str, help='基準檔案路徑')
    
    args = parser.parse_args()
    
    # 建立監控系統
    baseline_file = Path(args.baseline_file) if args.baseline_file else None
    monitoring = RTFMonitoringSystem(baseline_file)
    
    if args.run_benchmark:
        # 執行基準測試
        results = monitoring.run_rtf_benchmark()
        if results:
            monitoring.save_results(results)
            alerts = monitoring.check_performance_regression(results)
            print(f"✅ RTF 基準測試完成，共 {len(results)} 個結果")
            if alerts:
                print(f"⚠️ 檢測到 {len(alerts)} 個效能警報")
        else:
            print("❌ RTF 基準測試失敗")
    
    if args.generate_report:
        # 生成報告
        report = monitoring.generate_monitoring_report()
        report_file = Path(__file__).parent / "RTF_MONITORING_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ 監控報告已生成: {report_file}")
        print("\n" + report)
    
    if args.check_regression:
        # 檢查回歸（基於最新結果）
        if monitoring.results_file.exists():
            with open(monitoring.results_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            recent_results = data.get('results', [])[-3:]  # 最近 3 筆
            if recent_results:
                results = [RTFResult(**r) for r in recent_results]
                alerts = monitoring.check_performance_regression(results)
                if alerts:
                    print(f"⚠️ 檢測到 {len(alerts)} 個效能變化")
                    for alert in alerts:
                        print(f"  {alert['type']}: {alert['model_config']} ({alert['change_percent']:+.1f}%)")
                else:
                    print("✅ 無效能回歸檢測")
        else:
            print("❌ 尚無監控數據")

if __name__ == "__main__":
    main()