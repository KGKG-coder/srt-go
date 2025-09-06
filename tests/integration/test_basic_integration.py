"""
Basic Integration Tests for SRT GO
Simple integration tests that can run in CI environment
"""

import pytest
import sys
from pathlib import Path


def test_python_version():
    """Test Python version compatibility"""
    assert sys.version_info >= (3, 8), "Python 3.8+ required"


def test_basic_imports():
    """Test if basic Python libraries are available"""
    try:
        import json
        import pathlib
        import subprocess
        assert True
    except ImportError as e:
        pytest.fail(f"Basic import failed: {e}")


def test_project_structure():
    """Test if project structure exists"""
    project_root = Path(__file__).parent.parent.parent
    
    # Check main directories
    assert (project_root / "srt_whisper_lite").exists(), "Main project directory missing"
    assert (project_root / "tests").exists(), "Tests directory missing"
    
    # Check if electron app directory exists
    electron_dir = project_root / "srt_whisper_lite" / "electron-react-app"
    if electron_dir.exists():
        assert (electron_dir / "package.json").exists(), "package.json missing"


def test_requirements_files():
    """Test if requirements files exist"""
    project_root = Path(__file__).parent.parent.parent
    
    # Check for at least one requirements file
    req_files = [
        project_root / "srt_whisper_lite" / "requirements.txt",
        project_root / "srt_whisper_lite" / "electron-react-app" / "python" / "requirements.txt",
        project_root / "tests" / "requirements-ci.txt"
    ]
    
    existing_files = [f for f in req_files if f.exists()]
    assert len(existing_files) > 0, "No requirements files found"


def test_git_repository():
    """Test if this is a git repository"""
    project_root = Path(__file__).parent.parent.parent
    git_dir = project_root / ".git"
    
    assert git_dir.exists(), "Not a git repository"