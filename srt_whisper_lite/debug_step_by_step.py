#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逐步調試腳本，模擬 Electron 調用
"""

import sys
import json
import logging
from pathlib import Path
import os

# 設定控制台編碼為UTF-8
if sys.platform.startswith('win'):
    os.system('chcp 65001 > NUL')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 設定簡化日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_electron_backend():
    """測試 Electron 後端"""
    
    # 測試用的虛擬檔案 - 創建一個小的音頻檔案
    test_audio_file = "C:/Users/USER-ART0/Desktop/hutest.mp4"
    
    if not os.path.exists(test_audio_file):
        logger.error(f"測試檔案不存在: {test_audio_file}")
        return False
    
    # 構建命令參數
    files = [test_audio_file]
    settings = {
        "model": "tiny",
        "language": "auto",
        "outputFormat": "srt",
        "customDir": "C:/Users/USER-ART0/Desktop"
    }
    corrections = []
    
    # 轉換為 JSON 字符串
    files_json = json.dumps(files)
    settings_json = json.dumps(settings)
    corrections_json = json.dumps(corrections)
    
    logger.info("準備測試參數:")
    logger.info(f"Files: {files_json}")
    logger.info(f"Settings: {settings_json}")
    
    # 執行 electron_backend.py
    import subprocess
    
    mini_python = Path("mini_python/python.exe")
    electron_backend = Path("electron_backend.py")
    
    if not mini_python.exists():
        logger.error(f"mini_python 不存在: {mini_python}")
        return False
        
    if not electron_backend.exists():
        logger.error(f"electron_backend 不存在: {electron_backend}")
        return False
    
    cmd = [
        str(mini_python.absolute()),
        str(electron_backend.absolute()),
        "--files", files_json,
        "--settings", settings_json,
        "--corrections", corrections_json
    ]
    
    logger.info(f"執行命令: {' '.join(cmd)}")
    
    try:
        # 啟動進程
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            bufsize=1,
            universal_newlines=True
        )
        
        logger.info("進程已啟動，開始監控輸出...")
        
        # 實時讀取輸出
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                logger.info(f"STDOUT: {output.strip()}")
                
        # 讀取錯誤輸出
        stderr_output = process.stderr.read()
        if stderr_output:
            logger.error(f"STDERR: {stderr_output}")
            
        # 等待進程結束
        return_code = process.poll()
        logger.info(f"進程結束，返回碼: {return_code}")
        
        return return_code == 0
        
    except Exception as e:
        logger.error(f"執行過程中發生錯誤: {e}")
        return False

if __name__ == "__main__":
    logger.info("開始逐步調試測試")
    success = test_electron_backend()
    
    if success:
        logger.info("✅ 測試成功")
    else:
        logger.error("❌ 測試失敗")
    
    input("按 Enter 鍵退出...")