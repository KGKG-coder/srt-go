#!/usr/bin/env python3
"""
Setup script for SRT Whisper Turbo.
Handles installation, dependency checking, and first-run setup.
"""

import sys
import subprocess
import json
import os
from pathlib import Path

# Fix console encoding on Windows
if sys.platform.startswith('win'):
    os.system('chcp 65001 > NUL')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version < (3, 8) or version >= (3, 12):
        print(f"WARNING: Python {version.major}.{version.minor} detected")
        print("   Recommended: Python 3.8-3.11 for best compatibility")
        print("   Python 3.12+ may have dependency issues")
    else:
        print(f"OK: Python {version.major}.{version.minor} is compatible")

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements.txt", 
            "--upgrade"
        ], check=True)
        print("OK: Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        return False

def test_installation():
    """Test the installation"""
    print("Testing installation...")
    
    try:
        # Test core imports
        from engine.utils.runtime import gpu_available, pick_runtime
        from engine.core.model import ModelManager
        from engine.core.pipeline import FilterPipeline
        
        print("OK: Core modules imported successfully")
        
        # Test GPU detection
        has_gpu = gpu_available()
        runtime = pick_runtime()
        print(f"Runtime: {runtime['device']} ({runtime['compute_type']})")
        
        # Test model repository
        from engine.utils.runtime import get_model_repo
        repo = get_model_repo()
        print(f"Model source: {repo}")
        
        return True
    except ImportError as e:
        print(f"ERROR: Import failed: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        return False

def run_integration_tests():
    """Run integration tests if available"""
    test_file = Path("test_integration.py")
    if test_file.exists():
        print("Running integration tests...")
        try:
            result = subprocess.run([sys.executable, str(test_file)], check=True)
            print("OK: Integration tests passed")
            return True
        except subprocess.CalledProcessError:
            print("WARNING: Some integration tests failed (this may be expected)")
            return False
    else:
        print("INFO: Integration tests not found, skipping")
        return True

def create_config():
    """Create default configuration"""
    print("Creating default configuration...")
    
    config = {
        "version": "1.0.0",
        "model_repo": "zzxxcc0805/my-whisper-large-v3-turbo-ct2",
        "default_settings": {
            "language": "auto",
            "zh_output": "traditional",
            "output_format": "srt",
            "filters": {
                "vad_enabled": True,
                "bgm_suppress_enabled": True,
                "denoise_enabled": True,
                "segment_enabled": True,
                "ts_fix_enabled": True
            }
        }
    }
    
    config_file = Path("config.json")
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"OK: Configuration saved to {config_file}")
    return True

def main():
    """Main setup process"""
    print("=" * 60)
    print("SRT Whisper Turbo Setup")
    print("=" * 60)
    
    # Check Python version
    check_python_version()
    print()
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed at dependency installation")
        return 1
    print()
    
    # Test installation
    if not test_installation():
        print("\n❌ Setup failed at installation test")
        return 1
    print()
    
    # Run integration tests
    run_integration_tests()
    print()
    
    # Create config
    create_config()
    print()
    
    print("=" * 60)
    print("✅ Setup completed successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Run CLI: python engine_main.py transcribe your_audio.mp4")
    print("2. Import offline model: python engine_main.py import-model-pack model.zip")
    print("3. Check system info: python engine_main.py info")
    print()
    print("For Electron integration:")
    print("1. Navigate to electron-react-app directory")
    print("2. Update main.js to use engine/integration/electron_bridge.py")
    print("3. Update React components with app/renderer/SettingsUpdate.js")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())