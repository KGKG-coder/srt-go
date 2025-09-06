#!/usr/bin/env python3
"""
簡單音頻生成和字幕測試
"""

import sys
import os
import numpy as np
import wave
from pathlib import Path
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_audio():
    """創建一個簡單的測試音頻文件"""
    try:
        # 生成 3 秒的正弦波音頻（440Hz A音）
        sample_rate = 16000
        duration = 3.0
        frequency = 440.0
        
        # 生成音頻數據
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t)
        
        # 添加一些變化以模擬語音
        audio_data = audio_data * np.exp(-t / 2)  # 衰減
        audio_data = audio_data * 0.3  # 降低音量
        
        # 轉換為16位整數
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # 保存為 WAV 文件
        output_file = "test_simple_audio.wav"
        with wave.open(output_file, 'w') as wav_file:
            wav_file.setnchannels(1)  # 單聲道
            wav_file.setsampwidth(2)  # 16位
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        logger.info(f"✅ 測試音頻文件已創建: {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"❌ 創建測試音頻失敗: {e}")
        return None

def test_subtitle_generation():
    """測試字幕生成功能"""
    try:
        from simplified_subtitle_core import SimplifiedSubtitleCore
        
        # 創建測試音頻
        audio_file = create_test_audio()
        if not audio_file:
            return False
        
        logger.info("正在初始化字幕生成核心...")
        core = SimplifiedSubtitleCore(model_size="tiny", device="cpu")
        success = core.initialize()
        
        if not success:
            logger.error("❌ 核心初始化失敗")
            return False
        
        logger.info("正在生成字幕...")
        output_file = "test_output.srt"
        
        # 嘗試生成字幕
        result = core.generate_subtitles(
            audio_file=audio_file,
            output_file=output_file,
            language="auto"
        )
        
        if result and os.path.exists(output_file):
            logger.info(f"✅ 字幕生成成功: {output_file}")
            
            # 讀取並顯示生成的字幕
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f"生成的字幕內容:\n{content}")
            
            return True
        else:
            logger.error("❌ 字幕生成失敗")
            return False
            
    except Exception as e:
        logger.error(f"❌ 字幕生成測試異常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_command_line():
    """測試命令行功能"""
    try:
        # 創建測試音頻
        audio_file = create_test_audio()
        if not audio_file:
            return False
        
        logger.info("測試命令行功能...")
        
        # 構建命令
        cmd = f'py -3.11 main.py "{audio_file}" -o "test_cmd_output.srt" -m tiny -d cpu'
        
        logger.info(f"執行命令: {cmd}")
        
        import subprocess
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info("✅ 命令行執行成功")
            if os.path.exists("test_cmd_output.srt"):
                logger.info("✅ 輸出文件已生成")
                return True
            else:
                logger.warning("⚠️ 命令執行成功但沒有輸出文件")
                return False
        else:
            logger.error(f"❌ 命令行執行失敗: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ 命令執行超時")
        return False
    except Exception as e:
        logger.error(f"❌ 命令行測試異常: {e}")
        return False

def main():
    """運行測試"""
    logger.info("=== 開始字幕生成功能測試 ===")
    
    tests = [
        ("字幕生成功能", test_subtitle_generation),
        ("命令行功能", test_command_line),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- 測試: {test_name} ---")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} - 通過")
            else:
                logger.error(f"❌ {test_name} - 失敗")
        except Exception as e:
            logger.error(f"❌ {test_name} - 異常: {e}")
    
    logger.info(f"\n=== 測試結果 ===")
    logger.info(f"通過: {passed}/{total}")
    logger.info(f"成功率: {(passed/total)*100:.1f}%")
    
    # 清理測試文件
    for file in ["test_simple_audio.wav", "test_output.srt", "test_cmd_output.srt"]:
        if os.path.exists(file):
            try:
                os.remove(file)
                logger.info(f"清理測試文件: {file}")
            except:
                pass
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)