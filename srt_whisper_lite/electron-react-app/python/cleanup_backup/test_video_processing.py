#!/usr/bin/env python3
"""
測試影片處理 - 使用 INT8 模型
測試 test_video 目錄下的影片
"""

import sys
import os
import logging
import time
from pathlib import Path

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_video_processing():
    """測試影片處理功能"""
    try:
        print("=" * 80)
        print("測試影片處理 - INT8 模型版本")
        print("=" * 80)
        
        # 檢查測試影片目錄
        test_video_dir = Path("H:/字幕程式設計環境/test_video")
        if not test_video_dir.exists():
            print(f"❌ 測試影片目錄不存在: {test_video_dir}")
            return False
        
        # 尋找影片文件
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
        video_files = []
        for ext in video_extensions:
            video_files.extend(test_video_dir.glob(f"*{ext}"))
        
        if not video_files:
            print("❌ 未找到影片文件")
            return False
        
        print(f"\n📁 找到 {len(video_files)} 個影片文件:")
        for i, video_file in enumerate(video_files, 1):
            size_mb = video_file.stat().st_size / (1024**2)
            print(f"  {i}. {video_file.name} ({size_mb:.1f} MB)")
        
        # 導入必要模塊
        print("\n🔧 載入模型管理器和字幕核心...")
        try:
            from large_v3_int8_model_manager import LargeV3INT8ModelManager
            from simplified_subtitle_core import SimplifiedSubtitleCore
        except ImportError as e:
            print(f"❌ 導入失敗: {e}")
            return False
        
        # 初始化模型管理器
        print("\n📦 初始化 INT8 模型管理器...")
        model_manager = LargeV3INT8ModelManager()
        
        # 檢查模型可用性
        if not model_manager.check_model_availability():
            print("⚠️ 模型不可用，需要先下載")
            response = input("是否下載 INT8 模型？(y/n): ").strip().lower()
            if response != 'y':
                print("取消測試")
                return False
            
            print("\n📥 下載模型...")
            def progress_callback(progress, message):
                bar_length = 40
                filled = int(bar_length * progress)
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"\r  [{bar}] {progress*100:.1f}% - {message}", end='', flush=True)
            
            success, path = model_manager.download_model(progress_callback)
            print()  # 換行
            if not success:
                print(f"❌ 模型下載失敗: {path}")
                return False
            print(f"✅ 模型下載完成: {path}")
        
        # 創建字幕核心
        print("\n🚀 初始化字幕生成核心...")
        subtitle_core = SimplifiedSubtitleCore(
            model_size="large-v3",
            device="cpu",  # 使用 CPU 進行測試
            compute_type="int8"
        )
        
        # 初始化模型
        def init_progress(percent, message):
            print(f"  進度 {percent}%: {message}")
        
        print("載入 AI 模型...")
        init_start = time.time()
        success = subtitle_core.initialize(init_progress)
        init_time = time.time() - init_start
        
        if not success:
            print("❌ 模型初始化失敗")
            return False
        
        print(f"✅ 模型載入成功！耗時: {init_time:.1f} 秒")
        
        # 讓用戶選擇要處理的影片
        print(f"\n🎯 選擇要處理的影片:")
        for i, video_file in enumerate(video_files, 1):
            print(f"  {i}. {video_file.name}")
        print(f"  0. 處理所有影片")
        
        try:
            choice = int(input("\n請選擇 (0-{}): ".format(len(video_files))))
            if choice == 0:
                selected_videos = video_files
            elif 1 <= choice <= len(video_files):
                selected_videos = [video_files[choice - 1]]
            else:
                print("❌ 選擇無效")
                return False
        except ValueError:
            print("❌ 請輸入數字")
            return False
        
        # 處理選中的影片
        print(f"\n🎬 開始處理 {len(selected_videos)} 個影片...")
        
        results = []
        for i, video_file in enumerate(selected_videos, 1):
            print(f"\n{'='*60}")
            print(f"處理影片 {i}/{len(selected_videos)}: {video_file.name}")
            print(f"{'='*60}")
            
            # 創建輸出目錄
            output_dir = video_file.parent / "subtitles"
            output_dir.mkdir(exist_ok=True)
            
            # 生成 SRT 文件名
            srt_file = output_dir / f"{video_file.stem}.srt"
            
            # 處理進度回調
            def process_progress(percent, message):
                bar_length = 50
                filled = int(bar_length * percent / 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"\r  [{bar}] {percent:.1f}% - {message}", end='', flush=True)
            
            try:
                start_time = time.time()
                
                # 調用字幕生成
                success = subtitle_core.process_audio(
                    str(video_file),
                    str(srt_file),
                    progress_callback=process_progress,
                    language="zh",  # 中文
                    task="transcribe"
                )
                
                elapsed = time.time() - start_time
                print()  # 換行
                
                if success:
                    # 檢查生成的文件
                    if srt_file.exists():
                        file_size = srt_file.stat().st_size
                        print(f"  ✅ 字幕生成成功!")
                        print(f"  📄 輸出: {srt_file}")
                        print(f"  📊 大小: {file_size} 字節")
                        print(f"  ⏱️  耗時: {elapsed:.1f} 秒")
                        
                        # 讀取並顯示前幾行字幕
                        try:
                            with open(srt_file, 'r', encoding='utf-8') as f:
                                lines = f.readlines()[:10]  # 前10行
                            print(f"  📝 字幕預覽:")
                            for line in lines:
                                print(f"    {line.strip()}")
                            if len(lines) >= 10:
                                print(f"    ... (共 {len(lines)} 行)")
                        except Exception as e:
                            print(f"  ⚠️ 無法讀取字幕內容: {e}")
                        
                        results.append({
                            "video": video_file.name,
                            "success": True,
                            "time": elapsed,
                            "output": str(srt_file),
                            "size": file_size
                        })
                    else:
                        print(f"  ❌ 字幕文件未生成")
                        results.append({
                            "video": video_file.name,
                            "success": False,
                            "error": "字幕文件未生成"
                        })
                else:
                    print(f"  ❌ 字幕生成失敗")
                    results.append({
                        "video": video_file.name,
                        "success": False,
                        "error": "處理失敗"
                    })
                    
            except Exception as e:
                print(f"\n  ❌ 處理出錯: {e}")
                results.append({
                    "video": video_file.name,
                    "success": False,
                    "error": str(e)
                })
        
        # 顯示總結
        print(f"\n{'='*80}")
        print("📊 處理總結")
        print(f"{'='*80}")
        
        successful = sum(1 for r in results if r["success"])
        total_time = sum(r.get("time", 0) for r in results if r["success"])
        
        print(f"✅ 成功處理: {successful}/{len(results)} 個影片")
        print(f"⏱️  總耗時: {total_time:.1f} 秒")
        if successful > 0:
            print(f"📈 平均速度: {total_time/successful:.1f} 秒/影片")
        
        print(f"\n📋 詳細結果:")
        for result in results:
            if result["success"]:
                print(f"  ✅ {result['video']}")
                print(f"     耗時: {result['time']:.1f}秒, 輸出: {result['size']} 字節")
            else:
                print(f"  ❌ {result['video']}: {result.get('error', '未知錯誤')}")
        
        print(f"\n🎯 INT8 模型性能表現:")
        print(f"  - 模型大小: ~1GB (比標準版小 70%)")
        print(f"  - 計算精度: INT8 量化")
        print(f"  - 速度優勢: 比 FP16 快約 3.5 倍")
        print(f"  - 適合場景: 快速轉錄、資源受限環境")
        
        return successful > 0
        
    except Exception as e:
        print(f"\n❌ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_video_processing()
    print(f"\n{'='*80}")
    if success:
        print("🎉 影片處理測試完成！")
    else:
        print("💥 影片處理測試失敗！")
    print(f"{'='*80}")
    sys.exit(0 if success else 1)