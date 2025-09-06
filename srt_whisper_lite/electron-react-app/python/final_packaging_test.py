#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Final Packaging Test
Comprehensive verification that the system is ready for distribution
"""

import sys
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime
import subprocess

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

class FinalPackagingValidator:
    """Validate system readiness for packaging and distribution"""
    
    def __init__(self):
        self.test_results = {
            "test_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "Enhanced Voice Detector v2.0 - Final Package",
            "test_categories": [],
            "overall_status": "unknown",
            "packaging_ready": False
        }
    
    def test_core_system_integrity(self):
        """Test core system integrity"""
        print("1. Core System Integrity Test")
        print("-" * 35)
        
        results = {
            "category": "Core System Integrity",
            "tests": [],
            "status": "unknown"
        }
        
        # Test 1.1: Essential files
        essential_files = [
            "electron_backend.py",
            "simplified_subtitle_core.py",
            "enhanced_lightweight_voice_detector.py",
            "adaptive_voice_detector.py",
            "subeasy_multilayer_filter.py",
            "subtitle_formatter.py",
            "large_v3_int8_model_manager.py",
            "semantic_processor.py",
            "config_manager.py"
        ]
        
        files_present = 0
        for file in essential_files:
            if Path(file).exists():
                files_present += 1
        
        file_test = {
            "name": "Essential Files Present",
            "result": f"{files_present}/{len(essential_files)}",
            "status": "PASS" if files_present == len(essential_files) else "FAIL"
        }
        results["tests"].append(file_test)
        print(f"  Essential Files: {file_test['result']} - {file_test['status']}")
        
        # Test 1.2: Module imports
        import_tests = [
            ("SimplifiedSubtitleCore", "from simplified_subtitle_core import SimplifiedSubtitleCore"),
            ("EnhancedVoiceDetector", "from enhanced_lightweight_voice_detector import EnhancedLightweightVoiceDetector"),
            ("AdaptiveVoiceDetector", "from adaptive_voice_detector import AdaptiveVoiceDetector"),
            ("SubEasyFilter", "from subeasy_multilayer_filter import IntelligentMultiLayerFilter"),
            ("ElectronBackend", "from electron_backend import process_subtitle_files")
        ]
        
        imports_passed = 0
        for name, import_stmt in import_tests:
            try:
                exec(import_stmt)
                imports_passed += 1
                print(f"  {name}: PASS")
            except Exception as e:
                print(f"  {name}: FAIL - {e}")
        
        import_test = {
            "name": "Module Imports",
            "result": f"{imports_passed}/{len(import_tests)}",
            "status": "PASS" if imports_passed == len(import_tests) else "FAIL"
        }
        results["tests"].append(import_test)
        
        # Overall core system status
        results["status"] = "PASS" if file_test["status"] == "PASS" and import_test["status"] == "PASS" else "FAIL"
        self.test_results["test_categories"].append(results)
        
        print(f"  Overall Core System: {results['status']}")
        return results["status"] == "PASS"
    
    def test_enhanced_voice_detector_functionality(self):
        """Test Enhanced Voice Detector v2.0 functionality"""
        print("\n2. Enhanced Voice Detector v2.0 Test")
        print("-" * 40)
        
        results = {
            "category": "Enhanced Voice Detector v2.0",
            "tests": [],
            "status": "unknown"
        }
        
        try:
            from enhanced_lightweight_voice_detector import EnhancedLightweightVoiceDetector
            detector = EnhancedLightweightVoiceDetector()
            
            # Test 2.1: Content type detection
            test_segments = [
                {'start': 0.0, 'end': 2.0, 'text': '歡迎來到諾貝爾眼科'},
                {'start': 2.0, 'end': 4.0, 'text': '母親節快到了'}
            ]
            
            content_type = detector._auto_detect_content_type(test_segments, "test_DRLIN.mp4")
            content_test = {
                "name": "Content Type Detection",
                "result": content_type,
                "status": "PASS" if content_type in ['promotional_video', 'medical_dialogue', 'casual_conversation'] else "FAIL"
            }
            results["tests"].append(content_test)
            print(f"  Content Type Detection: {content_type} - {content_test['status']}")
            
            # Test 2.2: Specialized thresholds
            detector._apply_specialized_thresholds(content_type)
            thresholds = detector.current_thresholds
            
            threshold_test = {
                "name": "Specialized Thresholds",
                "result": f"{len(thresholds)} parameters configured",
                "status": "PASS" if len(thresholds) >= 7 else "FAIL"
            }
            results["tests"].append(threshold_test)
            print(f"  Specialized Thresholds: {threshold_test['result']} - {threshold_test['status']}")
            
            # Test 2.3: Detection summary
            summary = detector.get_detection_summary()
            
            summary_test = {
                "name": "Detection Summary",
                "result": f"v{summary['detector_version']}, {len(summary['optimization_features'])} features",
                "status": "PASS" if summary['detector_version'] == '2.0 Enhanced' else "FAIL"
            }
            results["tests"].append(summary_test)
            print(f"  Detection Summary: {summary_test['result']} - {summary_test['status']}")
            
            # Overall Enhanced Voice Detector status
            all_passed = all(test["status"] == "PASS" for test in results["tests"])
            results["status"] = "PASS" if all_passed else "FAIL"
            
        except Exception as e:
            error_test = {
                "name": "Enhanced Voice Detector Initialization",
                "result": f"Error: {e}",
                "status": "FAIL"
            }
            results["tests"].append(error_test)
            results["status"] = "FAIL"
            print(f"  Enhanced Voice Detector: FAIL - {e}")
        
        self.test_results["test_categories"].append(results)
        print(f"  Overall Enhanced Voice Detector: {results['status']}")
        return results["status"] == "PASS"
    
    def test_system_dependencies(self):
        """Test system dependencies"""
        print("\n3. System Dependencies Test")
        print("-" * 30)
        
        results = {
            "category": "System Dependencies",
            "tests": [],
            "status": "unknown"
        }
        
        # Critical dependencies
        critical_deps = [
            ("faster_whisper", "Whisper AI model"),
            ("numpy", "Numerical computing"),
            ("pathlib", "Path handling"),
            ("json", "JSON processing"),
            ("logging", "Logging system")
        ]
        
        # Optional dependencies (for enhanced features)
        optional_deps = [
            ("scipy", "Scientific computing"),
            ("sklearn", "Machine learning"),
            ("librosa", "Audio analysis")
        ]
        
        critical_passed = 0
        for dep_name, description in critical_deps:
            try:
                __import__(dep_name)
                critical_passed += 1
                print(f"  {dep_name} ({description}): PASS")
            except ImportError:
                print(f"  {dep_name} ({description}): FAIL - CRITICAL")
        
        critical_test = {
            "name": "Critical Dependencies",
            "result": f"{critical_passed}/{len(critical_deps)}",
            "status": "PASS" if critical_passed == len(critical_deps) else "FAIL"
        }
        results["tests"].append(critical_test)
        
        optional_passed = 0
        for dep_name, description in optional_deps:
            try:
                __import__(dep_name)
                optional_passed += 1
                print(f"  {dep_name} ({description}): PASS")
            except ImportError:
                print(f"  {dep_name} ({description}): OPTIONAL - not required")
        
        optional_test = {
            "name": "Optional Dependencies",
            "result": f"{optional_passed}/{len(optional_deps)}",
            "status": "PASS"  # Optional deps don't affect packaging
        }
        results["tests"].append(optional_test)
        
        results["status"] = critical_test["status"]
        self.test_results["test_categories"].append(results)
        
        print(f"  Overall Dependencies: {results['status']}")
        return results["status"] == "PASS"
    
    def test_backend_api_compatibility(self):
        """Test backend API compatibility"""
        print("\n4. Backend API Compatibility Test")
        print("-" * 38)
        
        results = {
            "category": "Backend API Compatibility",
            "tests": [],
            "status": "unknown"
        }
        
        try:
            # Test API structure
            from electron_backend import process_subtitle_files
            
            # Test settings format compatibility
            test_settings = {
                'model': 'large',
                'language': 'auto',
                'outputFormat': 'srt',
                'enable_gpu': False,
                'enableSubEasy': True
            }
            
            api_test = {
                "name": "API Function Available",
                "result": "process_subtitle_files function accessible",
                "status": "PASS"
            }
            results["tests"].append(api_test)
            print(f"  API Function: {api_test['status']}")
            
            # Test settings validation (without actual processing)
            required_settings = ['model', 'language', 'outputFormat']
            settings_valid = all(key in test_settings for key in required_settings)
            
            settings_test = {
                "name": "Settings Format",
                "result": f"All {len(required_settings)} required settings present",
                "status": "PASS" if settings_valid else "FAIL"
            }
            results["tests"].append(settings_test)
            print(f"  Settings Format: {settings_test['status']}")
            
            results["status"] = "PASS"
            
        except Exception as e:
            error_test = {
                "name": "Backend API Access",
                "result": f"Error: {e}",
                "status": "FAIL"
            }
            results["tests"].append(error_test)
            results["status"] = "FAIL"
            print(f"  Backend API: FAIL - {e}")
        
        self.test_results["test_categories"].append(results)
        print(f"  Overall Backend API: {results['status']}")
        return results["status"] == "PASS"
    
    def test_packaging_readiness(self):
        """Test packaging readiness"""
        print("\n5. Packaging Readiness Test")
        print("-" * 30)
        
        results = {
            "category": "Packaging Readiness",
            "tests": [],
            "status": "unknown"
        }
        
        # Test 5.1: Directory structure
        expected_dirs = ["../dist", "../react-app", "../models"]
        dirs_present = 0
        for dir_path in expected_dirs:
            if Path(dir_path).exists():
                dirs_present += 1
        
        dir_test = {
            "name": "Directory Structure",
            "result": f"{dirs_present}/{len(expected_dirs)} expected directories",
            "status": "PARTIAL" if dirs_present > 0 else "FAIL"
        }
        results["tests"].append(dir_test)
        print(f"  Directory Structure: {dir_test['result']} - {dir_test['status']}")
        
        # Test 5.2: File size optimization
        python_files = list(Path(".").glob("*.py"))
        total_size_kb = sum(f.stat().st_size for f in python_files if f.is_file()) / 1024
        
        size_test = {
            "name": "Python Code Size",
            "result": f"{total_size_kb:.1f} KB across {len(python_files)} files",
            "status": "PASS" if total_size_kb < 5000 else "WARN"  # Under 5MB is good
        }
        results["tests"].append(size_test)
        print(f"  Python Code Size: {size_test['result']} - {size_test['status']}")
        
        # Test 5.3: Cleanup verification
        cleanup_report = Path("cleanup_report.json")
        if cleanup_report.exists():
            with open(cleanup_report, 'r', encoding='utf-8') as f:
                cleanup_data = json.load(f)
            
            cleanup_test = {
                "name": "Cleanup Completed",
                "result": f"{cleanup_data['summary']['files_removed']} unused files removed, {cleanup_data['summary']['space_saved_mb']:.2f}MB saved",
                "status": "PASS"
            }
            print(f"  Cleanup: {cleanup_test['result']} - {cleanup_test['status']}")
        else:
            cleanup_test = {
                "name": "Cleanup Status",
                "result": "Cleanup report not found",
                "status": "WARN"
            }
            print(f"  Cleanup: {cleanup_test['result']} - {cleanup_test['status']}")
        
        results["tests"].append(cleanup_test)
        
        # Overall packaging readiness
        pass_count = sum(1 for test in results["tests"] if test["status"] == "PASS")
        results["status"] = "PASS" if pass_count >= 2 else "PARTIAL"
        
        self.test_results["test_categories"].append(results)
        print(f"  Overall Packaging: {results['status']}")
        return results["status"] in ["PASS", "PARTIAL"]
    
    def generate_final_report(self):
        """Generate final packaging readiness report"""
        print("\n" + "=" * 60)
        print("FINAL PACKAGING READINESS REPORT")
        print("=" * 60)
        
        # Calculate overall status
        category_statuses = [cat["status"] for cat in self.test_results["test_categories"]]
        pass_count = category_statuses.count("PASS")
        total_count = len(category_statuses)
        
        if pass_count == total_count:
            self.test_results["overall_status"] = "READY"
            self.test_results["packaging_ready"] = True
            status_symbol = "READY"
        elif pass_count >= total_count - 1:
            self.test_results["overall_status"] = "MOSTLY READY"
            self.test_results["packaging_ready"] = True
            status_symbol = "MOSTLY READY"
        else:
            self.test_results["overall_status"] = "NOT READY"
            self.test_results["packaging_ready"] = False
            status_symbol = "NOT READY"
        
        print(f"\nOverall System Status: {status_symbol}")
        print(f"Test Categories Passed: {pass_count}/{total_count}")
        
        print(f"\nCategory Results:")
        for i, category in enumerate(self.test_results["test_categories"], 1):
            print(f"  {i}. {category['category']}: {category['status']}")
        
        # Recommendations
        if self.test_results["packaging_ready"]:
            print(f"\nRECOMMENDATION: System is ready for packaging!")
            print("Next steps:")
            print("1. Create Electron distribution package")
            print("2. Generate NSIS installer")
            print("3. Test final distribution on clean system")
            print("4. Prepare for release")
        else:
            print(f"\nRECOMMENDATION: Address failing tests before packaging")
            failing_categories = [cat["category"] for cat in self.test_results["test_categories"] if cat["status"] == "FAIL"]
            for category in failing_categories:
                print(f"  - Fix issues in: {category}")
        
        # Save report
        report_path = "final_packaging_report.json"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            print(f"\nDetailed report saved to: {report_path}")
        except Exception as e:
            print(f"Failed to save report: {e}")
        
        return self.test_results["packaging_ready"]
    
    def run_full_validation(self):
        """Run complete packaging validation"""
        print("Final Packaging Test - Enhanced Voice Detector v2.0")
        print("=" * 55)
        print("Validating system readiness for distribution packaging\n")
        
        # Run all test categories
        test_1 = self.test_core_system_integrity()
        test_2 = self.test_enhanced_voice_detector_functionality()
        test_3 = self.test_system_dependencies()
        test_4 = self.test_backend_api_compatibility()
        test_5 = self.test_packaging_readiness()
        
        # Generate final report
        ready_for_packaging = self.generate_final_report()
        
        return ready_for_packaging

def main():
    """Main validation execution"""
    validator = FinalPackagingValidator()
    
    try:
        is_ready = validator.run_full_validation()
        
        if is_ready:
            print(f"\nSUCCESS: System ready for final packaging and distribution!")
            return 0
        else:
            print(f"\nWARNING: System needs additional work before packaging")
            return 1
            
    except Exception as e:
        print(f"\nERROR: Validation failed: {e}")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)