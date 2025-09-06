#!/usr/bin/env python3
"""
智能字幕生成器 - 主程序
基於 Faster-Whisper 引擎的極簡版本
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('subtitle_generator.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# 添加當前目錄到 Python 路徑
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from simplified_subtitle_core import SimplifiedSubtitleCore
    from subtitle_formatter import SubtitleFormatter
    from audio_processor import AudioProcessor
except ImportError as e:
    logger.error(f"模組導入失敗: {e}")
    sys.exit(1)


class SubtitleGenerator:
    """字幕生成器主類別"""
    
    def __init__(self, model_size="medium", device="auto", compute_type="auto"):
        self.subtitle_core = None
        self.audio_processor = AudioProcessor()
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.initialized = False
        
    def initialize(self, progress_callback: Optional[callable] = None) -> bool:
        """初始化核心組件"""
        try:
            if progress_callback:
                progress_callback(5, "初始化字幕生成引擎...")
            
            # 初始化字幕生成核心
            self.subtitle_core = SimplifiedSubtitleCore(
                model_size=self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            
            # 載入模型
            success = self.subtitle_core.initialize(progress_callback)
            if not success:
                logger.error("字幕生成模型初始化失敗")
                return False
            
            self.initialized = True
            logger.info("字幕生成器初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"初始化失敗: {e}")
            return False
    
    def generate_subtitle(self, 
                         input_file: str,
                         output_file: str,
                         language: Optional[str] = None,
                         format: str = "srt",
                         progress_callback: Optional[callable] = None) -> bool:
        """
        生成字幕
        
        Args:
            input_file: 輸入音視頻文件
            output_file: 輸出字幕文件
            language: 語言代碼（None為自動檢測）
            format: 輸出格式（srt, vtt, txt）
            progress_callback: 進度回調函數
            
        Returns:
            bool: 是否成功
        """
        try:
            # 檢查初始化
            if not self.initialized:
                if not self.initialize(progress_callback):
                    return False
            
            # 檢查輸入文件
            if not os.path.exists(input_file):
                logger.error(f"輸入文件不存在: {input_file}")
                return False
            
            logger.info(f"開始處理: {input_file}")
            
            # 直接使用字幕核心進行處理（包含音頻預處理和語音識別）
            success = self.subtitle_core.generate_subtitle(
                input_file,
                output_file,
                language=language,
                format=format,
                progress_callback=progress_callback
            )
            
            if success:
                logger.info(f"字幕生成完成: {output_file}")
                return True
            else:
                logger.error("字幕生成失敗")
                return False
                
        except Exception as e:
            logger.error(f"字幕生成失敗: {e}")
            return False
        
        finally:
            # 清理臨時文件
            if hasattr(self, 'audio_processor'):
                self.audio_processor.cleanup_temp_files()


def process_file_callback(input_file: str, output_file: str, 
                         language: Optional[str], format: str,
                         progress_callback: callable,
                         model_size: str = "medium") -> bool:
    """GUI 處理回調函數"""
    generator = SubtitleGenerator(model_size=model_size)
    return generator.generate_subtitle(
        input_file, output_file, language, format, progress_callback
    )


def main():
    """主函數"""
    logger.info("智能字幕生成器啟動")
    
    try:
        # 檢查 GUI 模式
        if len(sys.argv) == 1 or '--gui' in sys.argv:
            logger.info("啟動 GUI 模式")
            
            # 優先使用 Electron React GUI
            try:
                import subprocess
                
                # 檢查已打包的 Electron 應用
                electron_exe_path = current_dir / "electron-react-app" / "dist" / "win-unpacked" / "SRT GO - AI 字幕生成工具.exe"
                
                if electron_exe_path.exists():
                    logger.info("啟動 Electron React GUI...")
                    subprocess.Popen([str(electron_exe_path)], cwd=str(electron_exe_path.parent))
                    return
                else:
                    # 備用：開發模式啟動 Electron
                    electron_app_path = current_dir / "electron-react-app"
                    
                    if electron_app_path.exists():
                        # 檢查是否已安裝依賴
                        if not (electron_app_path / "node_modules").exists():
                            logger.info("首次運行，正在安裝依賴...")
                            subprocess.run(["npm", "run", "install:all"], cwd=str(electron_app_path), shell=True)
                        
                        # 啟動 Electron 開發模式
                        logger.info("正在啟動 SRT GO - AI 字幕生成工具...")
                        subprocess.run(["npm", "start"], cwd=str(electron_app_path), shell=True)
                        return
                    else:
                        # 最後備用：本地 GUI
                        logger.warning("Electron 不可用，嘗試本地 GUI...")
                        try:
                            from local_gui import main as gui_main
                            logger.info("啟動本地 GUI 界面...")
                            gui_main()
                            return
                        except ImportError:
                            logger.error("GUI 界面不可用，請使用命令行模式")
                            print("GUI 界面不可用。請使用命令行模式：")
                            print("SubtitleGenerator.exe input_video.mp4")
                            return
            except Exception as e:
                logger.error(f"啟動 GUI 失敗: {e}")
                print("GUI 界面不可用。請使用命令行模式：")
                print("SubtitleGenerator.exe input_video.mp4")
                return
            
        else:
            # 命令行模式
            import argparse
            
            parser = argparse.ArgumentParser(description="智能字幕生成器")
            parser.add_argument("input", help="輸入音視頻文件")
            parser.add_argument("-o", "--output", help="輸出字幕文件")
            parser.add_argument("-l", "--language", help="語言代碼")
            parser.add_argument("-f", "--format", default="srt", 
                              choices=["srt", "vtt", "txt"], help="輸出格式")
            parser.add_argument("-m", "--model", default="medium",
                              choices=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"],
                              help="Whisper 模型大小")
            parser.add_argument("-d", "--device", default="auto",
                              choices=["auto", "cpu", "cuda"],
                              help="計算設備")
            
            args = parser.parse_args()
            
            # 設定輸出文件
            if not args.output:
                input_path = Path(args.input)
                args.output = str(input_path.with_suffix(f".{args.format}"))
            
            # 生成字幕
            generator = SubtitleGenerator(
                model_size=args.model,
                device=args.device
            )
            success = generator.generate_subtitle(
                args.input,
                args.output,
                args.language,
                args.format
            )
            
            if success:
                print(f"字幕生成成功: {args.output}")
            else:
                print("字幕生成失敗")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("用戶中斷操作")
    except Exception as e:
        logger.error(f"程序執行失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()