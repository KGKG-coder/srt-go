#!/usr/bin/env python3
"""
Download standard Large-v3 INT8 model instead of turbo version
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_standard_int8():
    """Download standard large-v3 int8 model"""
    try:
        print("=" * 80)
        print("Download Standard Large-v3 INT8 Model")
        print("=" * 80)
        
        # Use huggingface-hub to download
        try:
            from huggingface_hub import snapshot_download
            import shutil
            
            # Download to temp directory first
            cache_dir = Path("H:/字幕程式設計環境/SRT-GO-Development/models")
            temp_dir = cache_dir / "temp_download"
            final_dir = cache_dir / "large-v3-int8"
            
            print(f"Downloading standard large-v3 int8 model...")
            print(f"This may take a while (about 1GB)...")
            
            # Try different repositories
            repos_to_try = [
                "guillaumekln/faster-whisper-large-v3",  # Official conversion
                "Systran/faster-whisper-large-v3",       # Systran version
            ]
            
            success = False
            for repo in repos_to_try:
                try:
                    print(f"\nTrying repository: {repo}")
                    
                    downloaded_path = snapshot_download(
                        repo_id=repo,
                        cache_dir=temp_dir,
                        local_files_only=False,
                        allow_patterns=["*.json", "*.bin", "*.txt"]
                    )
                    
                    print(f"Downloaded to: {downloaded_path}")
                    
                    # Move to final location
                    if final_dir.exists():
                        shutil.rmtree(final_dir)
                    shutil.move(downloaded_path, final_dir)
                    
                    print(f"Model moved to: {final_dir}")
                    success = True
                    break
                    
                except Exception as e:
                    print(f"Failed with {repo}: {e}")
                    continue
            
            if not success:
                print("All repositories failed, trying direct faster-whisper download...")
                
                # Let faster-whisper handle the download
                from faster_whisper import WhisperModel
                
                print("Creating model with faster-whisper (auto-download)...")
                model = WhisperModel(
                    "large-v3",
                    device="cpu",
                    compute_type="int8",
                    download_root=str(cache_dir)
                )
                
                print("Model downloaded successfully via faster-whisper")
                return True
            
            # Verify downloaded files
            required_files = ["model.bin", "config.json"]
            print(f"\nVerifying downloaded files:")
            
            for file_name in required_files:
                file_path = final_dir / file_name
                if file_path.exists():
                    size_mb = file_path.stat().st_size / (1024**2)
                    print(f"  SUCCESS: {file_name} ({size_mb:.1f} MB)")
                else:
                    print(f"  WARNING: Missing {file_name}")
            
            return True
            
        except ImportError:
            print("ERROR: huggingface-hub not installed")
            print("Please install: pip install huggingface-hub")
            return False
            
    except Exception as e:
        print(f"ERROR: Download failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = download_standard_int8()
    print(f"\n{'='*80}")
    if success:
        print("Standard INT8 model download completed!")
    else:
        print("Standard INT8 model download failed!")
    print(f"{'='*80}")
    sys.exit(0 if success else 1)