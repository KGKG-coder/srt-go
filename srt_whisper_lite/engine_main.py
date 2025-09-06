#!/usr/bin/env python3
"""
SRT Whisper Lite CLI Wrapper
極薄命令行包裝 - 重用現有 electron_backend.py 邏輯
供自動化/CI/腳本使用
"""

import sys
import argparse
import json
from pathlib import Path

# 添加 electron-react-app/python 到路徑
sys.path.insert(0, str(Path(__file__).parent / "electron-react-app" / "python"))

try:
    from official_model_manager import OfficialModelManager
    from simplified_subtitle_core import SimplifiedSubtitleCore
    from electron_backend import process_files_internal
except ImportError as e:
    print(f"❌ 導入錯誤: {e}")
    print("請確認在 srt_whisper_lite 目錄中執行此腳本")
    sys.exit(1)

def ensure_model():
    """確保模型準備就緒"""
    print("🔄 檢查模型狀態...")
    
    model_manager = OfficialModelManager()
    info = model_manager.get_model_info()
    
    print(f"模型: {info['name']}")
    print(f"狀態: {info['status_text']}")
    
    if not info['available']:
        print("📥 開始下載模型...")
        
        def progress_callback(percent, stage, message):
            print(f"  [{stage}] {percent:.1%} - {message}")
        
        success, result = model_manager.download_model(progress_callback)
        if success:
            print(f"✅ 模型準備完成: {result}")
            return True
        else:
            print(f"❌ 模型準備失敗: {result}")
            return False
    else:
        print(f"✅ 模型已就緒: {info['path']}")
        print(f"   大小: {info['actual_size']}")
        return True

def transcribe_files(input_files, **kwargs):
    """轉錄文件"""
    if not ensure_model():
        return False
    
    # 構造設置
    settings = {
        'model': 'large',  # 固定使用 large
        'language': kwargs.get('language', 'auto'),
        'outputLanguage': kwargs.get('output_language', 'same'),
        'outputFormat': kwargs.get('format', 'srt'),
        'customDir': kwargs.get('output_dir', ''),
        'enableCorrections': True,
        'enable_gpu': kwargs.get('enable_gpu', True)
    }
    
    # 文件清單
    files = []
    for input_file in input_files:
        file_path = Path(input_file)
        if not file_path.exists():
            print(f"❌ 文件不存在: {input_file}")
            return False
        
        files.append({
            'path': str(file_path.absolute()),
            'name': file_path.name,
            'size': file_path.stat().st_size
        })
    
    # 使用現有的後端邏輯
    try:
        print(f"🔄 開始處理 {len(files)} 個文件...")
        
        result = process_files_internal(files, settings, [])
        
        if result.get('success', False):
            print(f"✅ 成功生成 {result.get('successful', 0)} 個字幕文件")
            if 'results' in result:
                for r in result['results']:
                    if r.get('success'):
                        print(f"   {r['input']} → {r['output']}")
            return True
        else:
            print(f"❌ 處理失敗: {result.get('message', '未知錯誤')}")
            return False
            
    except Exception as e:
        print(f"❌ 處理異常: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='SRT Whisper Lite CLI - 極薄命令行包裝',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python engine_main.py ensure-model
  python engine_main.py transcribe input.mp4
  python engine_main.py transcribe input.mp4 --language zh --format srt
  python engine_main.py transcribe *.mp4 --output-dir ./subtitles
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # ensure-model 子命令
    subparsers.add_parser('ensure-model', help='確保模型準備就緒')
    
    # transcribe 子命令
    transcribe_parser = subparsers.add_parser('transcribe', help='轉錄音訊/視頻文件')
    transcribe_parser.add_argument('input', nargs='+', help='輸入文件路徑')
    transcribe_parser.add_argument('--language', '-l', 
                                 choices=['auto', 'zh', 'en', 'ja', 'ko'],
                                 default='auto', help='輸入語言 (默認: auto)')
    transcribe_parser.add_argument('--output-language', '--output-lang',
                                 choices=['same', 'zh-TW', 'zh-CN'],
                                 default='same', help='輸出語言 (默認: same)')
    transcribe_parser.add_argument('--format', '-f',
                                 choices=['srt', 'vtt', 'txt'],
                                 default='srt', help='輸出格式 (默認: srt)')
    transcribe_parser.add_argument('--output-dir', '-o',
                                 default='', help='輸出目錄 (默認: 與輸入文件同目錄)')
    transcribe_parser.add_argument('--no-gpu', action='store_true',
                                 help='禁用 GPU 加速')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'ensure-model':
        success = ensure_model()
        sys.exit(0 if success else 1)
    
    elif args.command == 'transcribe':
        success = transcribe_files(
            args.input,
            language=args.language,
            output_language=args.output_language,
            format=args.format,
            output_dir=args.output_dir,
            enable_gpu=not args.no_gpu
        )
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()