#!/usr/bin/env python3
"""
End-to-End Test Automation Suite for SRT GO v2.2.1
Comprehensive automated testing covering full application workflow
"""

import pytest
import time
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import tempfile

# Add test utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.ultra_realistic_speech_generator import create_ultra_realistic_test_audio


class SRTGOTestAutomation:
    """Complete E2E test automation for SRT GO application"""
    
    def __init__(self):
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_results = []
        self.backend_script = self._find_backend_script()
        self.test_audio_files = {}
        
        # Create test data directory
        self.test_data_dir.mkdir(exist_ok=True)
        
    def _find_backend_script(self) -> Optional[Path]:
        """Locate the backend script"""
        possible_paths = [
            Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "python" / "electron_backend.py",
            Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "dist" / "win-unpacked" / "resources" / "resources" / "python" / "electron_backend.py"
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def setup_test_environment(self) -> bool:
        """Set up test environment and generate test audio files"""
        print("=== Setting up E2E Test Environment ===")
        
        if not self.backend_script:
            print("ERROR: Backend script not found")
            return False
        
        print(f"Backend script: {self.backend_script}")
        
        # Generate test audio files
        try:
            print("Generating synthetic test audio...")
            audio_files = create_ultra_realistic_test_audio(str(self.test_data_dir / "audio"))
            
            # Also check for existing real test files
            real_test_dir = Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "test_VIDEO"
            if real_test_dir.exists():
                for video_file in real_test_dir.glob("*.mp4"):
                    audio_files[f"real_{video_file.stem}"] = str(video_file)
            
            self.test_audio_files = audio_files
            print(f"Available test audio files: {list(audio_files.keys())}")
            
        except Exception as e:
            print(f"Warning: Could not generate synthetic audio: {e}")
            # Try to use existing test files only
            real_test_dir = Path(__file__).parent.parent.parent / "srt_whisper_lite" / "electron-react-app" / "test_VIDEO"
            if real_test_dir.exists():
                for video_file in real_test_dir.glob("*.mp4"):
                    self.test_audio_files[f"real_{video_file.stem}"] = str(video_file)
            
        return len(self.test_audio_files) > 0
    
    def run_backend_test(self, audio_file: str, settings: Dict, test_name: str) -> Dict:
        """Run a single backend test"""
        output_dir = self.test_data_dir / f"output_{test_name}"
        output_dir.mkdir(exist_ok=True)
        
        settings["customDir"] = str(output_dir)
        
        cmd = [
            sys.executable,
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
                timeout=180
            )
            
            processing_time = time.time() - start_time
            
            # Analyze results
            success = result.returncode == 0
            output_files = list(output_dir.glob("*.srt"))
            
            test_result = {
                "test_name": test_name,
                "audio_file": Path(audio_file).name,
                "settings": settings,
                "processing_time": processing_time,
                "success": success,
                "return_code": result.returncode,
                "output_files": len(output_files),
                "errors": []
            }
            
            if success and output_files:
                srt_file = output_files[0]
                file_size = srt_file.stat().st_size
                
                if file_size > 0:
                    # Analyze SRT content
                    try:
                        content = srt_file.read_text(encoding='utf-8')
                        subtitle_count = content.count('-->')
                        
                        test_result.update({
                            "file_size": file_size,
                            "subtitle_count": subtitle_count,
                            "content_sample": content[:200] + "..." if len(content) > 200 else content
                        })
                        
                        # Calculate RTF if we have duration info
                        if "duration" in settings:
                            rtf = processing_time / settings["duration"]
                            test_result["rtf"] = rtf
                            
                    except Exception as e:
                        test_result["errors"].append(f"Content analysis failed: {e}")
                
                else:
                    test_result["errors"].append("Empty output file")
                    test_result["success"] = False
            
            else:
                test_result["errors"].append("No output files generated")
                if result.stderr:
                    test_result["errors"].append(f"stderr: {result.stderr[:300]}")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            return {
                "test_name": test_name,
                "success": False,
                "errors": ["Test timeout (180s exceeded)"],
                "processing_time": 180
            }
        except Exception as e:
            return {
                "test_name": test_name,
                "success": False,
                "errors": [f"Test execution error: {e}"],
                "processing_time": time.time() - start_time
            }
    
    def test_core_functionality(self):
        """Test core subtitle generation functionality"""
        print("\n=== Core Functionality Tests ===")
        
        if not self.test_audio_files:
            print("No test audio files available")
            return
        
        # Use the first available audio file
        audio_file = list(self.test_audio_files.values())[0]
        
        core_tests = [
            {
                "name": "basic_medium_cpu",
                "settings": {
                    "model": "medium",
                    "language": "auto",
                    "outputFormat": "srt",
                    "enable_gpu": False,
                    "enablePureVoiceMode": True
                }
            },
            {
                "name": "small_model_test", 
                "settings": {
                    "model": "small",
                    "language": "auto",
                    "outputFormat": "srt",
                    "enable_gpu": False,
                    "enablePureVoiceMode": True
                }
            },
            {
                "name": "gpu_acceleration_test",
                "settings": {
                    "model": "medium",
                    "language": "auto", 
                    "outputFormat": "srt",
                    "enable_gpu": True,
                    "enablePureVoiceMode": True
                }
            }
        ]
        
        for test_config in core_tests:
            print(f"Running test: {test_config['name']}")
            result = self.run_backend_test(audio_file, test_config["settings"], test_config["name"])
            self.test_results.append(result)
            
            if result["success"]:
                print(f"  [+] SUCCESS: {result['processing_time']:.1f}s")
                if "subtitle_count" in result:
                    print(f"  [+] Generated {result['subtitle_count']} subtitles")
                if "rtf" in result:
                    print(f"  [+] RTF: {result['rtf']:.3f}")
            else:
                print(f"  [-] FAILED: {', '.join(result['errors'])}")
    
    def test_format_outputs(self):
        """Test different output formats"""
        print("\n=== Output Format Tests ===")
        
        if not self.test_audio_files:
            return
            
        audio_file = list(self.test_audio_files.values())[0]
        
        format_tests = [
            {"format": "srt", "name": "srt_format"},
            {"format": "vtt", "name": "vtt_format"}, 
            {"format": "txt", "name": "txt_format"}
        ]
        
        for test_config in format_tests:
            settings = {
                "model": "small",  # Use small model for speed
                "language": "auto",
                "outputFormat": test_config["format"],
                "enable_gpu": False,
                "enablePureVoiceMode": True
            }
            
            print(f"Testing format: {test_config['format']}")
            result = self.run_backend_test(audio_file, settings, test_config["name"])
            self.test_results.append(result)
            
            if result["success"]:
                print(f"  [+] SUCCESS: {test_config['format']} format")
            else:
                print(f"  [-] FAILED: {test_config['format']} format")
    
    def test_language_detection(self):
        """Test language detection and processing"""
        print("\n=== Language Detection Tests ===")
        
        if not self.test_audio_files:
            return
            
        # Test with different language settings
        language_tests = [
            {"language": "auto", "name": "auto_detect"},
            {"language": "en", "name": "english_forced"},
            {"language": "zh", "name": "chinese_forced"}
        ]
        
        audio_file = list(self.test_audio_files.values())[0]
        
        for test_config in language_tests:
            settings = {
                "model": "small",
                "language": test_config["language"],
                "outputFormat": "srt",
                "enable_gpu": False,
                "enablePureVoiceMode": True
            }
            
            print(f"Testing language: {test_config['language']}")
            result = self.run_backend_test(audio_file, settings, test_config["name"])
            self.test_results.append(result)
            
            if result["success"]:
                print(f"  [+] SUCCESS: {test_config['language']}")
            else:
                print(f"  [-] FAILED: {test_config['language']}")
    
    def test_advanced_features(self):
        """Test advanced features like Pure Voice Mode"""
        print("\n=== Advanced Features Tests ===")
        
        if not self.test_audio_files:
            return
            
        audio_file = list(self.test_audio_files.values())[0]
        
        advanced_tests = [
            {
                "name": "pure_voice_mode",
                "settings": {
                    "model": "medium",
                    "language": "auto",
                    "outputFormat": "srt", 
                    "enable_gpu": False,
                    "enablePureVoiceMode": True
                }
            },
            {
                "name": "traditional_subeasy",
                "settings": {
                    "model": "medium", 
                    "language": "auto",
                    "outputFormat": "srt",
                    "enable_gpu": False,
                    "enableSubEasy": True
                }
            }
        ]
        
        for test_config in advanced_tests:
            print(f"Testing feature: {test_config['name']}")
            result = self.run_backend_test(audio_file, test_config["settings"], test_config["name"])
            self.test_results.append(result)
            
            if result["success"]:
                print(f"  [+] SUCCESS: {test_config['name']}")
            else:
                print(f"  [-] FAILED: {test_config['name']}")
    
    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        successful_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        success_rate = len(successful_tests) / len(self.test_results) * 100 if self.test_results else 0
        
        report = [
            "# SRT GO E2E Test Automation Report",
            "",
            f"**Test Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Test Suite**: End-to-End Automation",
            f"**Total Tests**: {len(self.test_results)}",
            f"**Successful**: {len(successful_tests)}",
            f"**Failed**: {len(failed_tests)}",
            f"**Success Rate**: {success_rate:.1f}%",
            "",
            "## Test Results Summary",
            ""
        ]
        
        if successful_tests:
            report.append("### ✅ Successful Tests")
            report.append("")
            report.append("| Test Name | Processing Time | Subtitles | File Size |")
            report.append("|-----------|----------------|-----------|-----------|")
            
            for result in successful_tests:
                subtitles = result.get("subtitle_count", "N/A")
                file_size = f"{result.get('file_size', 0)} bytes"
                report.append(f"| {result['test_name']} | {result['processing_time']:.1f}s | {subtitles} | {file_size} |")
            
            report.append("")
        
        if failed_tests:
            report.append("### ❌ Failed Tests")
            report.append("")
            
            for result in failed_tests:
                report.append(f"**{result['test_name']}**:")
                for error in result.get("errors", []):
                    report.append(f"  - {error}")
                report.append("")
        
        # Performance analysis
        if successful_tests:
            avg_time = sum(r["processing_time"] for r in successful_tests) / len(successful_tests)
            
            report.extend([
                "## Performance Analysis",
                "",
                f"**Average Processing Time**: {avg_time:.1f}s",
                f"**Fastest Test**: {min(successful_tests, key=lambda x: x['processing_time'])['test_name']} ({min(r['processing_time'] for r in successful_tests):.1f}s)",
                f"**Slowest Test**: {max(successful_tests, key=lambda x: x['processing_time'])['test_name']} ({max(r['processing_time'] for r in successful_tests):.1f}s)",
                ""
            ])
        
        report.extend([
            "## Test Environment",
            "",
            f"**Backend Script**: {self.backend_script}",
            f"**Test Audio Files**: {len(self.test_audio_files)}",
            f"**Python Version**: {sys.version.split()[0]}",
            "",
            "## Recommendations",
            ""
        ])
        
        if success_rate >= 90:
            report.append("✅ **System Status**: Excellent - Ready for production deployment")
        elif success_rate >= 70:
            report.append("⚠️ **System Status**: Good - Minor issues to address")
        else:
            report.append("❌ **System Status**: Needs attention - Multiple failures detected")
        
        return "\\n".join(report)
    
    def run_complete_test_suite(self):
        """Execute the complete E2E test suite"""
        print("=" * 60)
        print("SRT GO E2E Test Automation Suite")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_environment():
            print("ERROR: Test environment setup failed")
            return
        
        # Run all test categories
        self.test_core_functionality()
        self.test_format_outputs()
        self.test_language_detection()
        self.test_advanced_features()
        
        # Generate and save report
        report = self.generate_test_report()
        report_file = self.test_data_dir / "E2E_TEST_AUTOMATION_REPORT.md"
        report_file.write_text(report, encoding='utf-8')
        
        print()
        print("=" * 60)
        print("E2E Test Automation Complete")
        print("=" * 60)
        print(f"Report saved to: {report_file}")
        
        # Summary
        successful_tests = len([r for r in self.test_results if r["success"]])
        total_tests = len(self.test_results)
        success_rate = successful_tests / total_tests * 100 if total_tests else 0
        
        print(f"Results: {successful_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        return success_rate >= 70  # Return True if success rate >= 70%


# Pytest integration
@pytest.fixture
def e2e_automation():
    """E2E automation fixture"""
    return SRTGOTestAutomation()


def test_e2e_automation_suite(e2e_automation):
    """Complete E2E test suite"""
    success = e2e_automation.run_complete_test_suite()
    assert success, "E2E test automation suite failed"


if __name__ == "__main__":
    # Direct execution
    automation = SRTGOTestAutomation()
    automation.run_complete_test_suite()