#!/usr/bin/env python3
"""
Check actual model sizes - INT8 vs INT16
Analyze disk usage and memory impact
"""

import sys
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    
    return f"{size:.2f} {units[unit_index]}"

def get_directory_size(directory):
    """Calculate total size of directory"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    except Exception as e:
        logger.error(f"Error calculating directory size: {e}")
    
    return total_size

def check_huggingface_cache():
    """Check HuggingFace cache for whisper models"""
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    whisper_models = {}
    
    if cache_dir.exists():
        for model_dir in cache_dir.iterdir():
            if "whisper" in model_dir.name.lower():
                size = get_directory_size(model_dir)
                whisper_models[model_dir.name] = size
    
    return whisper_models

def check_model_sizes():
    """Check actual model sizes"""
    try:
        print("=" * 80)
        print("Model Size Analysis - INT8 vs INT16")
        print("=" * 80)
        
        # 1. Check local models directory
        models_dir = Path("H:/字幕程式設計環境/SRT-GO-Development/models")
        print(f"\n1. LOCAL MODELS DIRECTORY: {models_dir}")
        print("-" * 60)
        
        if models_dir.exists():
            total_local_size = 0
            for model_subdir in models_dir.iterdir():
                if model_subdir.is_dir() and model_subdir.name != "temp":
                    size = get_directory_size(model_subdir)
                    total_local_size += size
                    print(f"  {model_subdir.name:<30}: {format_size(size)}")
                    
                    # Show individual files
                    if size > 0:
                        for file in model_subdir.glob("*"):
                            if file.is_file():
                                file_size = file.stat().st_size
                                print(f"    - {file.name:<25}: {format_size(file_size)}")
            
            print(f"  {'TOTAL LOCAL MODELS':<30}: {format_size(total_local_size)}")
        else:
            print("  No local models directory found")
        
        # 2. Check HuggingFace cache
        print(f"\n2. HUGGINGFACE CACHE:")
        print("-" * 60)
        
        hf_models = check_huggingface_cache()
        total_hf_size = 0
        
        if hf_models:
            for model_name, size in hf_models.items():
                total_hf_size += size
                print(f"  {model_name:<50}: {format_size(size)}")
        else:
            print("  No HuggingFace whisper models found in cache")
        
        if total_hf_size > 0:
            print(f"  {'TOTAL HF CACHE':<50}: {format_size(total_hf_size)}")
        
        # 3. Test model loading and memory usage
        print(f"\n3. MODEL LOADING TEST:")
        print("-" * 60)
        
        try:
            from faster_whisper import WhisperModel
            import psutil
            import time
            
            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss
            
            print(f"Initial memory usage: {format_size(initial_memory)}")
            
            # Test INT8 model
            print(f"\nLoading INT8 model...")
            start_time = time.time()
            int8_model = WhisperModel("large-v3", device="cpu", compute_type="int8")
            int8_load_time = time.time() - start_time
            int8_memory = process.memory_info().rss
            int8_memory_usage = int8_memory - initial_memory
            
            print(f"  Load time: {int8_load_time:.1f} seconds")
            print(f"  Memory usage: {format_size(int8_memory_usage)}")
            print(f"  Total memory: {format_size(int8_memory)}")
            
            del int8_model  # Free memory
            time.sleep(2)   # Wait for cleanup
            
            # Test INT16 model
            print(f"\nLoading INT16 model...")
            start_time = time.time()
            int16_model = WhisperModel("large-v3", device="cpu", compute_type="int16")
            int16_load_time = time.time() - start_time
            int16_memory = process.memory_info().rss
            int16_memory_usage = int16_memory - initial_memory
            
            print(f"  Load time: {int16_load_time:.1f} seconds")
            print(f"  Memory usage: {format_size(int16_memory_usage)}")
            print(f"  Total memory: {format_size(int16_memory)}")
            
            del int16_model  # Free memory
            
            # Compare memory usage
            memory_diff = int16_memory_usage - int8_memory_usage
            memory_ratio = int16_memory_usage / int8_memory_usage if int8_memory_usage > 0 else 0
            
            print(f"\nMemory Usage Comparison:")
            print(f"  INT8  memory: {format_size(int8_memory_usage)}")
            print(f"  INT16 memory: {format_size(int16_memory_usage)}")
            print(f"  Difference  : {format_size(memory_diff)} ({memory_ratio:.1f}x)")
            
        except ImportError:
            print("  faster-whisper not available for memory testing")
        except Exception as e:
            print(f"  Memory test failed: {e}")
        
        # 4. NSIS Packaging Analysis
        print(f"\n4. NSIS PACKAGING ANALYSIS:")
        print("-" * 60)
        
        # Estimate model sizes for packaging
        int8_model_size = 800 * 1024 * 1024    # ~800MB
        int16_model_size = 1600 * 1024 * 1024  # ~1.6GB
        app_size = 50 * 1024 * 1024            # ~50MB for app
        
        int8_total = int8_model_size + app_size
        int16_total = int16_model_size + app_size
        
        print(f"Estimated NSIS package sizes:")
        print(f"  App files only    : {format_size(app_size)}")
        print(f"  INT8 + App        : {format_size(int8_total)}")
        print(f"  INT16 + App       : {format_size(int16_total)}")
        print(f"  Size difference   : {format_size(int16_total - int8_total)}")
        
        # Distribution considerations
        print(f"\nDistribution Impact:")
        
        # Download time estimates (10 Mbps connection)
        download_speed_mbps = 10
        download_speed_bps = download_speed_mbps * 1024 * 1024 / 8  # bytes per second
        
        int8_download_time = int8_total / download_speed_bps
        int16_download_time = int16_total / download_speed_bps
        
        print(f"  Download time (10 Mbps):")
        print(f"    INT8 package  : {int8_download_time/60:.1f} minutes")
        print(f"    INT16 package : {int16_download_time/60:.1f} minutes")
        print(f"    Time difference: {(int16_download_time - int8_download_time)/60:.1f} minutes")
        
        # Storage requirements
        print(f"\n  Storage requirements:")
        print(f"    INT8 package  : {format_size(int8_total)}")
        print(f"    INT16 package : {format_size(int16_total)}")
        print(f"    Extra storage : {format_size(int16_total - int8_total)}")
        
        # 5. Final Recommendations
        print(f"\n5. FINAL RECOMMENDATIONS:")
        print("=" * 60)
        
        size_ratio = int16_total / int8_total
        
        print(f"File Size Impact:")
        print(f"  INT16 is {size_ratio:.1f}x larger than INT8")
        print(f"  Extra {format_size(int16_total - int8_total)} for potential quality gains")
        
        print(f"\nFor NSIS Packaging:")
        if size_ratio > 1.5:
            print(f"  ✅ RECOMMEND INT8 - Significantly smaller package")
            print(f"  ⚠️  INT16 creates {size_ratio:.1f}x larger installer")
        else:
            print(f"  ⚖️ Size difference manageable")
        
        print(f"\nDistribution Concerns:")
        if int8_download_time < 300:  # 5 minutes
            print(f"  ✅ INT8: Quick download ({int8_download_time/60:.1f} min)")
        else:
            print(f"  ⚠️ INT8: Long download ({int8_download_time/60:.1f} min)")
            
        if int16_download_time < 600:  # 10 minutes
            print(f"  ⚖️ INT16: Acceptable download ({int16_download_time/60:.1f} min)")
        else:
            print(f"  ❌ INT16: Very long download ({int16_download_time/60:.1f} min)")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Size analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_model_sizes()
    print(f"\n{'='*80}")
    if success:
        print("Model size analysis completed!")
    else:
        print("Model size analysis failed!")
    print(f"{'='*80}")
    sys.exit(0 if success else 1)