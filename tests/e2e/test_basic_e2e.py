"""
Basic End-to-End Tests for SRT GO
Simple E2E tests that can run in CI environment
"""

import pytest
import sys
import subprocess
import os
from pathlib import Path


def test_python_executable():
    """Test if Python executable works"""
    result = subprocess.run([
        sys.executable, "--version"
    ], capture_output=True, text=True)
    
    assert result.returncode == 0, "Python executable not working"
    assert "Python" in result.stdout, "Invalid Python version output"


def test_pip_available():
    """Test if pip is available"""
    result = subprocess.run([
        sys.executable, "-m", "pip", "--version"
    ], capture_output=True, text=True)
    
    assert result.returncode == 0, "pip not available"
    assert "pip" in result.stdout, "Invalid pip output"


def test_pytest_available():
    """Test if pytest is available and working"""
    result = subprocess.run([
        sys.executable, "-m", "pytest", "--version"
    ], capture_output=True, text=True)
    
    assert result.returncode == 0, "pytest not available"
    assert "pytest" in result.stdout, "Invalid pytest output"


def test_basic_module_availability():
    """Test if basic modules can be imported via subprocess"""
    modules_to_test = ["json", "pathlib", "subprocess", "sys", "os"]
    
    for module in modules_to_test:
        result = subprocess.run([
            sys.executable, "-c", f"import {module}; print('OK')"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Module {module} not available"
        assert "OK" in result.stdout, f"Module {module} import failed"


@pytest.mark.skip(reason="Requires full application build")
def test_electron_app_startup():
    """Test Electron app startup (requires full build)"""
    pytest.skip("E2E testing requires full application build")


@pytest.mark.skip(reason="Requires audio files")
def test_full_workflow():
    """Test full subtitle generation workflow (requires audio files)"""
    pytest.skip("Full workflow testing requires audio files and complete system")


def test_project_configuration():
    """Test if project configuration files are valid"""
    project_root = Path(__file__).parent.parent.parent
    
    # Test if package.json exists and is valid JSON
    electron_dir = project_root / "srt_whisper_lite" / "electron-react-app"
    package_json = electron_dir / "package.json"
    
    if package_json.exists():
        import json
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            assert "name" in package_data, "package.json missing name field"
        except json.JSONDecodeError:
            pytest.fail("package.json is not valid JSON")


def test_github_actions_compatibility():
    """Test GitHub Actions environment compatibility"""
    # Check if running in GitHub Actions
    github_actions = os.environ.get('GITHUB_ACTIONS', 'false') == 'true'
    
    if github_actions:
        # Verify GitHub Actions environment variables
        required_vars = ['GITHUB_WORKSPACE', 'GITHUB_REPOSITORY']
        for var in required_vars:
            assert os.environ.get(var), f"Missing GitHub Actions env var: {var}"