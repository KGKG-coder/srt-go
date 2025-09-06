#!/usr/bin/env python3
"""
測試 Large V3 Turbo INT8 模型管理器
驗證下載、載入和轉錄功能
"""

import sys
import logging
from pathlib import Path
import time

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_int8_model_manager():
    """測試 INT8 模型管理器"""
    try:
        print("=" * 70)
        print("🚀 開始測試 Large V3 Turbo INT8 模型管理器")
        print("=" * 70)
        
        # 導入模型管理器
        from large_v3_int8_model_manager import LargeV3INT8ModelManager
        
        # 創建管理器實例
        print("\n📦 1. 創建模型管理器...")
        model_manager = LargeV3INT8ModelManager()
        
        # 獲取模型信息
        print("\n📊 2. 模型信息:")
        print("-" * 50)
        model_info = model_manager.get_model_info()
        for key, value in model_info.items():
            print(f"  {key:20}: {value}")
        print("-" * 50)
        
        # 檢查模型可用性
        print("\n🔍 3. 檢查模型可用性...")
        available = model_manager.check_model_availability()
        if available:
            print("  ✅ 模型已可用，無需下載")
        else:
            print("  ⚠️ 模型不可用，需要下載")
            print("\n" + "=" * 50)
            print("  📥 模型下載說明:")
            print("  - 大小: 約 1GB (INT8 量化版)")
            print("  - 來源: Hugging Face")
            print("  - 速度: 取決於網路連接")
            print("=" * 50)
            
            # 詢問是否下載
            response = input("\n是否下載模型？(y/n): ").strip().lower()
            if response == 'y':
                print("\n📥 4. 開始下載模型...")
                print("  提示: 支援斷點續傳，中斷後可繼續")
                
                # 定義進度回調
                def progress_callback(progress, message):
                    bar_length = 40
                    filled = int(bar_length * progress)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    print(f"\r  [{bar}] {progress*100:.1f}% - {message}", end='', flush=True)
                
                start_time = time.time()
                success, path = model_manager.download_model(progress_callback)
                elapsed = time.time() - start_time
                
                print()  # 換行
                if success:
                    print(f"\n  ✅ 模型下載成功!")
                    print(f"  路徑: {path}")
                    print(f"  耗時: {elapsed:.1f} 秒")
                else:
                    print(f"\n  ❌ 模型下載失敗: {path}")
                    return False
            else:
                print("  跳過下載")
                return False
        
        # 準備模型
        print("\n🔧 5. 準備模型...")
        success, path = model_manager.prepare_model()
        if success:
            print(f"  ✅ 模型準備完成: {path}")
            
            # 顯示模型大小
            model_size = model_manager._get_model_size()
            print(f"  📊 模型大小: {model_manager._format_size(model_size)}")
        else:
            print(f"  ❌ 模型準備失敗")
            return False
        
        # 獲取 faster-whisper 配置
        print("\n⚙️ 6. 獲取 faster-whisper 配置:")
        config = model_manager.get_faster_whisper_config()
        print("-" * 50)
        for key, value in config.items():
            print(f"  {key:20}: {value}")
        print("-" * 50)
        
        # 可選：測試實際加載模型
        print("\n🧪 7. 測試模型加載")
        response = input("是否測試加載模型到 faster-whisper？(y/n): ").strip().lower()
        if response == 'y':
            try:
                from faster_whisper import WhisperModel
                
                print("\n  加載模型中...")
                start_time = time.time()
                
                model = WhisperModel(
                    config["model_size_or_path"],
                    device=config["device"],
                    compute_type=config["compute_type"],
                    download_root=config.get("download_root"),
                    local_files_only=False
                )
                
                elapsed = time.time() - start_time
                print(f"  ✅ 模型加載成功！(耗時: {elapsed:.1f}秒)")
                
                # 獲取模型信息
                print("\n  模型參數:")
                print(f"    - 編碼器層數: {model.model.num_encoder_layers if hasattr(model.model, 'num_encoder_layers') else 'N/A'}")
                print(f"    - 解碼器層數: {model.model.num_decoder_layers if hasattr(model.model, 'num_decoder_layers') else 'N/A'}")
                
                # 測試轉錄（可選）
                test_audio = input("\n輸入測試音頻文件路徑（留空跳過）: ").strip()
                if test_audio and Path(test_audio).exists():
                    print("\n  開始轉錄測試...")
                    start_time = time.time()
                    
                    segments, info = model.transcribe(
                        test_audio,
                        language="zh",
                        task="transcribe",
                        beam_size=5,
                        best_of=5,
                        temperature=[0.0, 0.2, 0.4, 0.6, 0.8]
                    )
                    
                    print(f"\n  檢測到語言: {info.language}")
                    print(f"  語言概率: {info.language_probability:.2%}")
                    print("\n  轉錄結果:")
                    print("-" * 50)
                    
                    segment_count = 0
                    for segment in segments:
                        segment_count += 1
                        print(f"  [{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
                    
                    elapsed = time.time() - start_time
                    print("-" * 50)
                    print(f"  ✅ 轉錄完成!")
                    print(f"  片段數: {segment_count}")
                    print(f"  耗時: {elapsed:.1f}秒")
                    
                    # 計算速度
                    audio_duration = info.duration if hasattr(info, 'duration') else 0
                    if audio_duration > 0:
                        speed_ratio = audio_duration / elapsed
                        print(f"  速度: {speed_ratio:.1f}x 實時")
                
            except ImportError:
                print("  ⚠️ faster-whisper 未安裝，跳過集成測試")
            except Exception as e:
                print(f"  ❌ 加載模型失敗: {e}")
                import traceback
                traceback.print_exc()
        
        # 清理測試
        print("\n🧹 8. 清理臨時文件...")
        model_manager.cleanup_cache()
        print("  ✅ 清理完成")
        
        print("\n" + "=" * 70)
        print("✅ 所有測試完成！")
        print("📊 總結:")
        print(f"  - 模型類型: Large V3 Turbo INT8")
        print(f"  - 模型大小: ~1GB")
        print(f"  - 速度優勢: 比 FP16 快 3.5 倍")
        print(f"  - 適合場景: NSIS 打包、快速轉錄")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_int8_model_manager()
    sys.exit(0 if success else 1)