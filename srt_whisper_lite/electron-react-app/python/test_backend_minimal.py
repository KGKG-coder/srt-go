#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最簡化的後端測試 - 跳過依賴檢查
"""

import sys
import json
import argparse
from pathlib import Path
import os

# 設定編碼
if sys.platform.startswith('win'):
    os.system('chcp 65001 > NUL')

def main():
    """主函數 - 測試參數解析和基本功能"""
    parser = argparse.ArgumentParser(description='簡化版字幕生成後端測試')
    parser.add_argument('--files', type=str, required=True, help='要處理的文件列表（JSON格式）')
    parser.add_argument('--settings', type=str, required=True, help='處理設置（JSON格式）')
    parser.add_argument('--corrections', type=str, default='[]', help='自定義校正（JSON格式）')
    
    args = parser.parse_args()
    
    try:
        # 解析參數
        files = json.loads(args.files)
        settings = json.loads(args.settings)
        corrections = json.loads(args.corrections)
        
        print("="*50)
        print("簡化版後端測試")
        print(f"Python版本: {sys.version}")
        print(f"執行路徑: {sys.executable}")
        print("="*50)
        
        print(f"文件數量: {len(files)}")
        print(f"設置: {settings}")
        print(f"校正數量: {len(corrections)}")
        
        # 模擬進度回調
        for i in range(0, 101, 20):
            progress_data = {
                "type": "progress",
                "percent": i,
                "filename": f"測試進度 {i}%",
                "message": f"處理中... {i}%"
            }
            print(f"PROGRESS:{json.dumps(progress_data, ensure_ascii=False)}")
        
        # 模擬成功結果
        success_data = {
            "type": "result",
            "data": {
                "success": True,
                "results": [{
                    "input": f"test_file_{i}.mp4",
                    "output": f"test_file_{i}.srt",
                    "success": True
                } for i in range(len(files))],
                "message": "測試完成（模擬）"
            }
        }
        print(f"RESULT:{json.dumps(success_data, ensure_ascii=False)}")
        
        return True
        
    except json.JSONDecodeError as e:
        error_data = {
            "type": "error",
            "data": {
                "success": False,
                "message": f"參數解析錯誤: {str(e)}",
                "code": "JSON_PARSE_ERROR"
            }
        }
        print(f"ERROR:{json.dumps(error_data, ensure_ascii=False)}")
        return False
        
    except Exception as e:
        error_data = {
            "type": "error",
            "data": {
                "success": False,
                "message": f"測試錯誤: {str(e)}",
                "code": "TEST_ERROR"
            }
        }
        print(f"ERROR:{json.dumps(error_data, ensure_ascii=False)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)