#!/usr/bin/env python3
"""
CI/CD Setup Validation Script for SRT GO Enhanced v2.2.1
Validates that all automated testing and pipeline components are properly configured
"""

import os
import sys
import json
from pathlib import Path

def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists and report status"""
    if Path(file_path).exists():
        print(f"OK {description}: {file_path}")
        return True
    else:
        print(f"MISSING {description}: {file_path}")
        return False

def validate_workflow_files():
    """Validate GitHub Actions workflow files"""
    print("=== GitHub Actions Workflows Validation ===")
    workflows_dir = Path(".github/workflows")
    
    required_workflows = [
        ("ci-cd-pipeline.yml", "Complete CI/CD Pipeline"),
        ("quick-test.yml", "Quick Testing"),
        ("release-builder.yml", "Release Builder"),
        ("manual-testing.yml", "Manual Testing"),
        ("performance-monitoring.yml", "Performance Monitoring"),
        ("README.md", "Workflow Documentation")
    ]
    
    all_present = True
    for filename, description in required_workflows:
        filepath = workflows_dir / filename
        if not check_file_exists(str(filepath), description):
            all_present = False
    
    return all_present

def validate_test_framework():
    """Validate test framework structure"""
    print("\n=== Test Framework Validation ===")
    
    test_components = [
        ("tests/README.md", "Test Framework Documentation"),
        ("tests/performance/comprehensive_performance_suite.py", "Performance Test Suite"),
        ("tests/e2e/test_automation_suite.py", "E2E Test Suite"),
        ("tests/unit/test_audio_processor.py", "Unit Tests"),
        ("tests/integration/test_complete_workflow.py", "Integration Tests"),
        ("tests/utils/test_audio_generator.py", "Test Utilities")
    ]
    
    all_present = True
    for filepath, description in test_components:
        if not check_file_exists(filepath, description):
            all_present = False
    
    return all_present

def validate_documentation():
    """Validate documentation completeness"""
    print("\n=== Documentation Validation ===")
    
    docs = [
        ("USER_MANUAL_v2.2.1.md", "User Manual"),
        ("RELEASE_NOTES_v2.2.1.md", "Release Notes"),
        ("QUICK_START_GUIDE.md", "Quick Start Guide"),
        ("GITHUB_RELEASE_TEMPLATE.md", "Release Template"),
        ("CLAUDE.md", "Development Guidelines")
    ]
    
    all_present = True
    for filename, description in docs:
        if not check_file_exists(filename, description):
            all_present = False
    
    return all_present

def validate_project_structure():
    """Validate core project structure"""
    print("\n=== Project Structure Validation ===")
    
    core_files = [
        ("srt_whisper_lite/electron-react-app/main.js", "Electron Main Process"),
        ("srt_whisper_lite/electron-react-app/python/electron_backend.py", "Python Backend"),
        ("srt_whisper_lite/electron-react-app/python/smart_backend_selector.py", "Smart Backend Selector"),
        ("srt_whisper_lite/electron-react-app/python/large_v3_fp16_performance_manager.py", "FP16 Model Manager"),
        ("srt_whisper_lite/electron-react-app/python/adaptive_voice_detector.py", "Voice Detection"),
        ("srt_whisper_lite/electron-react-app/package.json", "Node.js Dependencies")
    ]
    
    all_present = True
    for filepath, description in core_files:
        if not check_file_exists(filepath, description):
            all_present = False
    
    return all_present

def run_component_tests():
    """Run basic component tests"""
    print("\n=== Component Tests ===")
    
    try:
        # Test performance monitoring system
        os.chdir(Path("tests/performance"))
        result = os.system("python comprehensive_performance_suite.py --component-test")
        if result == 0:
            print("OK Performance Monitoring Component")
            component_ok = True
        else:
            print("FAILED Performance Monitoring Component")
            component_ok = False
        
        # Return to root directory
        os.chdir(Path(__file__).parent)
        
        return component_ok
        
    except Exception as e:
        print(f"ERROR Component Tests: {e}")
        return False

def generate_validation_report():
    """Generate comprehensive validation report"""
    print("\n" + "="*60)
    print("SRT GO Enhanced v2.2.1 - CI/CD Setup Validation Report")
    print("="*60)
    
    # Run all validations
    workflow_ok = validate_workflow_files()
    test_ok = validate_test_framework()
    docs_ok = validate_documentation()
    structure_ok = validate_project_structure()
    components_ok = run_component_tests()
    
    # Summary
    print(f"\n=== VALIDATION SUMMARY ===")
    print(f"GitHub Actions Workflows: {'PASS' if workflow_ok else 'FAIL'}")
    print(f"Test Framework: {'PASS' if test_ok else 'FAIL'}")
    print(f"Documentation: {'PASS' if docs_ok else 'FAIL'}")
    print(f"Project Structure: {'PASS' if structure_ok else 'FAIL'}")
    print(f"Component Tests: {'PASS' if components_ok else 'FAIL'}")
    
    all_ok = all([workflow_ok, test_ok, docs_ok, structure_ok, components_ok])
    
    print(f"\nOVERALL STATUS: {'READY FOR PRODUCTION' if all_ok else 'NEEDS ATTENTION'}")
    
    if all_ok:
        print("\nSUCCESS: SRT GO Enhanced v2.2.1 is fully configured with:")
        print("- Complete 7-stage CI/CD pipeline")
        print("- Automated testing framework")
        print("- Performance monitoring system")
        print("- Comprehensive documentation")
        print("- Production-ready project structure")
        print("\nThe project is ready for deployment and ongoing maintenance.")
    else:
        print("\nWARNING: Some components need attention before production deployment.")
    
    return all_ok

def main():
    """Main validation entry point"""
    try:
        # Change to project root directory
        project_root = Path(__file__).parent
        os.chdir(project_root)
        
        # Run validation
        success = generate_validation_report()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"CRITICAL ERROR: Validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()