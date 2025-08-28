"""
Basic Performance Tests for SRT GO
Simple performance tests that can run in CI environment
"""

import pytest
import time
import sys
import json
from pathlib import Path


def test_import_performance():
    """Test import performance"""
    start_time = time.time()
    
    # Import basic modules
    import json
    import pathlib
    import subprocess
    
    import_time = time.time() - start_time
    
    # Imports should be fast (less than 1 second)
    assert import_time < 1.0, f"Imports too slow: {import_time:.2f}s"


def test_file_system_performance():
    """Test file system operations performance"""
    project_root = Path(__file__).parent.parent.parent
    
    start_time = time.time()
    
    # Test directory traversal
    files = list(project_root.rglob("*.py"))
    
    traversal_time = time.time() - start_time
    
    # Directory traversal should be reasonable
    assert traversal_time < 5.0, f"File system traversal too slow: {traversal_time:.2f}s"
    assert len(files) > 0, "No Python files found"


def test_json_processing_performance():
    """Test JSON processing performance"""
    # Create test data
    test_data = {
        "files": [f"file_{i}.mp4" for i in range(100)],
        "settings": {
            "model": "large",
            "language": "auto",
            "output_format": "srt"
        },
        "metadata": {
            "version": "2.2.1",
            "timestamp": "2025-08-28"
        }
    }
    
    start_time = time.time()
    
    # Test JSON serialization/deserialization
    json_str = json.dumps(test_data)
    parsed_data = json.loads(json_str)
    
    json_time = time.time() - start_time
    
    # JSON operations should be fast
    assert json_time < 0.1, f"JSON processing too slow: {json_time:.2f}s"
    assert parsed_data == test_data, "JSON data corrupted"


@pytest.mark.skip(reason="Requires psutil")
def test_memory_usage_basic():
    """Test basic memory usage"""
    # Skip if psutil not available
    try:
        import psutil
        import os
        
        # Get current process memory
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        # Memory usage should be reasonable for tests (less than 500MB)
        memory_mb = memory_info.rss / 1024 / 1024
        assert memory_mb < 500, f"Memory usage too high: {memory_mb:.1f}MB"
    except ImportError:
        pytest.skip("psutil not available")


@pytest.mark.skip(reason="Requires actual audio files")
def test_rtf_baseline():
    """Test Real-Time Factor baseline (requires actual implementation)"""
    # This would test actual RTF performance but requires audio files
    # and the actual subtitle generation system
    pytest.skip("RTF testing requires audio files and full system")