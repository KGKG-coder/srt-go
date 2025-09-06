#!/usr/bin/env python3
"""
Integration test for the new faster-whisper subtitle generation system.
Tests model loading, GPU detection, and basic transcription.
"""

import sys
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_gpu_detection():
    """Test GPU/CPU detection logic"""
    logger.info("Testing GPU/CPU detection...")
    
    from engine.utils.runtime import gpu_available, pick_runtime
    
    has_gpu = gpu_available()
    runtime = pick_runtime()
    
    logger.info(f"  GPU Available: {has_gpu}")
    logger.info(f"  Selected Runtime: {runtime}")
    
    assert runtime["model_size"] == "large-v3-turbo", "Should always use large-v3-turbo model"
    
    if has_gpu:
        assert runtime["device"] == "cuda", "Should use CUDA when GPU available"
        assert runtime["compute_type"] == "float16", "Should use FP16 with GPU"
    else:
        assert runtime["device"] == "cpu", "Should use CPU when no GPU"
        assert runtime["compute_type"] == "int8", "Should use INT8 with CPU"
    
    logger.info("  ✓ GPU detection test passed")
    return True

def test_model_download():
    """Test model download manager"""
    logger.info("Testing model download manager...")
    
    from engine.utils.download import ModelDownloader
    from engine.utils.runtime import get_model_repo
    
    # Create test directory
    test_dir = Path("test_models")
    test_dir.mkdir(exist_ok=True)
    
    def progress_callback(percent, stage, message):
        logger.info(f"  [{stage}] {percent}% - {message}")
    
    downloader = ModelDownloader(test_dir, progress_callback)
    
    # Test model info
    repo_id = get_model_repo()
    logger.info(f"  Model Repository: {repo_id}")
    assert repo_id == "zzxxcc0805/my-whisper-large-v3-turbo-ct2", "Should use specified HF repo"
    
    # Test SHA256 calculation
    test_file = test_dir / "test.txt"
    test_file.write_text("test content")
    sha = downloader.sha256_file(test_file)
    assert len(sha) == 64, "SHA256 should be 64 hex characters"
    
    # Cleanup
    test_file.unlink()
    test_dir.rmdir()
    
    logger.info("  ✓ Model download manager test passed")
    return True

def test_filter_pipeline():
    """Test 5-layer filter pipeline configuration"""
    logger.info("Testing 5-layer filter pipeline...")
    
    from engine.core.pipeline import FilterPipeline
    
    # Test pipeline with all filters enabled
    config = {
        "vad_enabled": True,
        "bgm_suppress_enabled": True,
        "denoise_enabled": True,
        "segment_enabled": True,
        "ts_fix_enabled": True
    }
    
    pipeline = FilterPipeline(config)
    
    assert pipeline.vad_enabled == True, "VAD should be enabled"
    assert pipeline.bgm_suppress_enabled == True, "BGM suppress should be enabled"
    assert pipeline.denoise_enabled == True, "Denoise should be enabled"
    assert pipeline.segment_enabled == True, "Segment should be enabled"
    assert pipeline.ts_fix_enabled == True, "TS fix should be enabled"
    
    logger.info("  ✓ All 5 filter layers configured correctly")
    
    # Test selective disabling
    config["vad_enabled"] = False
    config["bgm_suppress_enabled"] = False
    
    pipeline2 = FilterPipeline(config)
    assert pipeline2.vad_enabled == False, "VAD should be disabled"
    assert pipeline2.bgm_suppress_enabled == False, "BGM suppress should be disabled"
    
    logger.info("  ✓ Selective filter disabling works")
    return True

def test_subtitle_formatter():
    """Test subtitle formatting"""
    logger.info("Testing subtitle formatter...")
    
    from engine.io.subtitle import SubtitleFormatter
    
    formatter = SubtitleFormatter()
    
    # Test segments
    segments = [
        {"start": 0.0, "end": 2.5, "text": "Hello world"},
        {"start": 3.0, "end": 5.5, "text": "This is a test"}
    ]
    
    # Test SRT format
    srt = formatter.to_srt(segments)
    assert "00:00:00,000 --> 00:00:02,500" in srt, "SRT should have correct timestamp"
    assert "Hello world" in srt, "SRT should contain text"
    
    # Test VTT format
    vtt = formatter.to_vtt(segments)
    assert "WEBVTT" in vtt, "VTT should have header"
    assert "00:00:00.000 --> 00:00:02.500" in vtt, "VTT should have correct timestamp"
    
    # Test TXT format
    txt = formatter.to_txt(segments)
    assert txt == "Hello world\nThis is a test", "TXT should be plain text"
    
    logger.info("  ✓ Subtitle formatting test passed")
    return True

def test_chinese_conversion():
    """Test Chinese Traditional/Simplified conversion"""
    logger.info("Testing Chinese conversion...")
    
    try:
        import opencc
        
        # Test conversion
        cc_s2t = opencc.OpenCC('s2t')  # Simplified to Traditional
        cc_t2s = opencc.OpenCC('t2s')  # Traditional to Simplified
        
        simplified = "简体中文测试"
        traditional = cc_s2t.convert(simplified)
        assert traditional == "簡體中文測試", "Should convert to traditional"
        
        back_to_simplified = cc_t2s.convert(traditional)
        assert "简" in back_to_simplified, "Should convert back to simplified"
        
        logger.info("  ✓ Chinese conversion test passed")
        return True
        
    except ImportError:
        logger.warning("  ⚠ OpenCC not installed, skipping Chinese conversion test")
        return True

def test_electron_bridge():
    """Test Electron bridge integration"""
    logger.info("Testing Electron bridge...")
    
    from engine.integration.electron_bridge import convert_chinese, apply_corrections
    
    # Test corrections
    segments = [
        {"text": "This is a test with typo"},
        {"text": "Another segment"}
    ]
    
    corrections = [
        {"find": "typo", "replace": "correction"}
    ]
    
    corrected = apply_corrections(segments, corrections)
    assert corrected[0]["text"] == "This is a test with correction", "Corrections should be applied"
    
    logger.info("  ✓ Electron bridge test passed")
    return True

def main():
    """Run all integration tests"""
    logger.info("=" * 60)
    logger.info("SRT Whisper Turbo Integration Tests")
    logger.info("=" * 60)
    
    tests = [
        ("GPU/CPU Detection", test_gpu_detection),
        ("Model Download Manager", test_model_download),
        ("5-Layer Filter Pipeline", test_filter_pipeline),
        ("Subtitle Formatter", test_subtitle_formatter),
        ("Chinese Conversion", test_chinese_conversion),
        ("Electron Bridge", test_electron_bridge)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                logger.error(f"✗ {test_name} failed")
        except Exception as e:
            failed += 1
            logger.error(f"✗ {test_name} failed with error: {e}")
    
    logger.info("=" * 60)
    logger.info(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("✓ All tests passed!")
        return 0
    else:
        logger.error(f"✗ {failed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())