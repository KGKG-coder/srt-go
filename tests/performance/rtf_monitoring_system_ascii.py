#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RTF Performance Monitoring System
Continuous tracking and monitoring of SRT GO performance baselines
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
    """RTF test result data structure"""
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
    """RTF Performance Monitoring System"""
    
    def __init__(self, baseline_file: Path = None):
        self.results_file = Path(__file__).parent / "rtf_monitoring_results.json"
        self.baseline_file = baseline_file or Path(__file__).parent / "RTF_PERFORMANCE_BASELINE_REPORT.md"
        self.alerts_file = Path(__file__).parent / "performance_alerts.json"
        self.setup_logging()
        self.load_baselines()
        
    def setup_logging(self):
        """Setup logging system"""
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
        """Load baseline performance data"""
        self.baselines = {
            "Medium_GPU": {"rtf": 0.736, "tolerance": 0.2},  # ±20% tolerance
            "Medium_CPU": {"rtf": 2.012, "tolerance": 0.3},  # ±30% tolerance
            "Small_CPU": {"rtf": 2.012, "tolerance": 0.3}
        }
        self.logger.info(f"Loaded baselines: {self.baselines}")
    
    def get_git_info(self) -> Tuple[str, str]:
        """Get current Git information"""
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
        """Execute RTF benchmark tests"""
        self.logger.info("Starting RTF benchmark tests...")
        
        # Test configurations
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
                
        self.logger.info(f"RTF benchmark completed, {len(results)} results")
        return results
    
    def _run_single_test(self, config: Dict, commit_hash: str, branch: str) -> Optional[RTFResult]:
        """Execute single configuration test"""
        try:
            # Find available backend
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
                self.logger.error("Cannot find electron_backend.py")
                return None
            
            # Test audio file
            test_audio = Path(__file__).parent / "test_data" / "ultra_realistic_english.wav"
            if not test_audio.exists():
                # Use E2E test audio file
                test_audio = Path(__file__).parent.parent / "e2e" / "test_data" / "audio" / "ultra_realistic_english.wav"
            
            if not test_audio.exists():
                self.logger.warning(f"Test audio file not found, skipping: {config['name']}")
                return None
            
            # Build test command
            settings = {
                "model": config["model"],
                "language": "auto", 
                "outputFormat": "srt",
                "customDir": str(Path(__file__).parent / "temp_output"),
                "enable_gpu": config["gpu"]
            }
            
            # Ensure output directory exists
            Path(settings["customDir"]).mkdir(exist_ok=True)
            
            cmd = [
                "python", str(backend_script),
                "--files", json.dumps([str(test_audio)]),
                "--settings", json.dumps(settings),
                "--corrections", "[]"
            ]
            
            self.logger.info(f"Running test: {config['name']}")
            start_time = time.time()
            
            # Execute test
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=300  # 5 minutes timeout
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Calculate audio duration (assume 5 seconds)
            audio_duration = 5.0
            rtf_score = processing_time / audio_duration
            
            # Check if successful
            success = result.returncode == 0 and "COMPLETE" in result.stdout
            
            if success:
                self.logger.info(f"Test successful: {config['name']}, RTF: {rtf_score:.3f}")
            else:
                self.logger.warning(f"Test failed: {config['name']}, error: {result.stderr}")
            
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
            self.logger.error(f"Test timeout: {config['name']}")
            return None
        except Exception as e:
            self.logger.error(f"Test execution error: {config['name']}, {e}")
            return None
    
    def save_results(self, results: List[RTFResult]):
        """Save test results"""
        # Load existing results
        existing_results = []
        if self.results_file.exists():
            try:
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    existing_results = existing_data.get('results', [])
            except:
                existing_results = []
        
        # Add new results
        new_results = [asdict(result) for result in results]
        all_results = existing_results + new_results
        
        # Keep latest 100 records
        if len(all_results) > 100:
            all_results = all_results[-100:]
        
        # Save results
        data = {
            "last_updated": datetime.now().isoformat(),
            "total_tests": len(all_results),
            "results": all_results
        }
        
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Saved {len(results)} new test results")
    
    def check_performance_regression(self, results: List[RTFResult]) -> List[Dict]:
        """Check performance regression"""
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
            
            # Calculate performance change percentage
            change_percent = ((current_rtf - baseline_rtf) / baseline_rtf) * 100
            
            # Check if beyond tolerance range
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
                    self.logger.warning(f"Performance regression: {result.model_config}, RTF {baseline_rtf:.3f} -> {current_rtf:.3f} ({change_percent:+.1f}%)")
                else:
                    self.logger.info(f"Performance improvement: {result.model_config}, RTF {baseline_rtf:.3f} -> {current_rtf:.3f} ({change_percent:+.1f}%)")
        
        # Save alerts
        if alerts:
            self._save_alerts(alerts)
        
        return alerts
    
    def _save_alerts(self, alerts: List[Dict]):
        """Save performance alerts"""
        existing_alerts = []
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    existing_alerts = json.load(f)
            except:
                existing_alerts = []
        
        all_alerts = existing_alerts + alerts
        
        # Keep latest 50 alerts
        if len(all_alerts) > 50:
            all_alerts = all_alerts[-50:]
        
        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump(all_alerts, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Saved {len(alerts)} performance alerts")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RTF Performance Monitoring System")
    parser.add_argument('--run-benchmark', action='store_true', help='Run RTF benchmark tests')
    parser.add_argument('--generate-report', action='store_true', help='Generate monitoring report')
    parser.add_argument('--check-regression', action='store_true', help='Check performance regression')
    parser.add_argument('--baseline-file', type=str, help='Baseline file path')
    
    args = parser.parse_args()
    
    # Create monitoring system
    baseline_file = Path(args.baseline_file) if args.baseline_file else None
    monitoring = RTFMonitoringSystem(baseline_file)
    
    if args.run_benchmark:
        # Run benchmark tests
        results = monitoring.run_rtf_benchmark()
        if results:
            monitoring.save_results(results)
            alerts = monitoring.check_performance_regression(results)
            print(f"[+] RTF benchmark completed, {len(results)} results")
            if alerts:
                print(f"[!] Detected {len(alerts)} performance alerts")
        else:
            print("[-] RTF benchmark failed")
    
    if args.generate_report:
        # Generate report (placeholder)
        print("[+] Monitoring report generation - feature coming soon")
    
    if args.check_regression:
        # Check regression (placeholder)  
        print("[+] Performance regression check - feature coming soon")

if __name__ == "__main__":
    main()