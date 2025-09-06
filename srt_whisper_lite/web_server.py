#!/usr/bin/env python3
"""
Web GUI 服務器
使用 Flask 提供 Web 界面服務
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional
import tempfile
import threading
import time

try:
    from flask import Flask, render_template, request, jsonify, send_from_directory
    from flask_cors import CORS
    import werkzeug.utils
except ImportError:
    print("缺少依賴: pip install flask flask-cors")
    sys.exit(1)

# 添加當前目錄到路徑
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from faster_whisper_core import FasterWhisperCore
    from subtitle_formatter import SubtitleFormatter
    from audio_processor import AudioProcessor
except ImportError as e:
    print(f"模組導入失敗: {e}")
    sys.exit(1)

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 全局變量
subtitle_generator = None
processing_status = {"status": "idle", "progress": 0, "message": ""}

class WebSubtitleGenerator:
    """Web 版字幕生成器"""
    
    def __init__(self):
        self.whisper_core = None
        self.audio_processor = AudioProcessor()
        self.initialized = False
        
    def initialize(self) -> bool:
        """初始化核心組件"""
        try:
            logger.info("初始化 Faster-Whisper 核心...")
            
            self.whisper_core = FasterWhisperCore(
                model_size="medium",
                device="auto",
                compute_type="auto"
            )
            
            success = self.whisper_core.initialize()
            if success:
                self.initialized = True
                logger.info("字幕生成器初始化完成")
            
            return success
            
        except Exception as e:
            logger.error(f"初始化失敗: {e}")
            return False
    
    def generate_subtitle(self, 
                         input_file: str,
                         language: Optional[str] = None,
                         format: str = "srt") -> dict:
        """
        生成字幕
        
        Returns:
            dict: 結果字典 {"success": bool, "output_file": str, "error": str}
        """
        try:
            global processing_status
            processing_status = {"status": "processing", "progress": 0, "message": "初始化..."}
            
            # 檢查初始化
            if not self.initialized:
                processing_status["message"] = "正在初始化 AI 引擎..."
                if not self.initialize():
                    return {"success": False, "error": "初始化失敗"}
            
            # 設定輸出文件
            input_path = Path(input_file)
            output_file = str(input_path.with_suffix(f".{format}"))
            
            logger.info(f"開始處理: {input_file}")
            
            # 音頻預處理
            processing_status.update({"progress": 10, "message": "正在預處理音頻..."})
            processed_audio = self.audio_processor.process_audio(input_file)
            
            # 語音識別
            processing_status.update({"progress": 25, "message": "AI 正在識別語音內容..."})
            result = self.whisper_core.transcribe(
                processed_audio,
                language=language,
                task="transcribe",
                progress_callback=self._update_progress
            )
            
            if not result:
                return {"success": False, "error": "語音識別失敗"}
            
            # 格式化並保存字幕
            processing_status.update({"progress": 95, "message": "正在保存字幕文件..."})
            success = SubtitleFormatter.save_subtitle(
                result['segments'],
                output_file,
                format
            )
            
            if success:
                processing_status.update({
                    "status": "completed", 
                    "progress": 100, 
                    "message": "字幕生成完成！"
                })
                logger.info(f"字幕生成完成: {output_file}")
                return {
                    "success": True,
                    "output_file": output_file,
                    "segments_count": len(result['segments']),
                    "language": result.get('language', 'unknown'),
                    "duration": result.get('duration', 0)
                }
            else:
                return {"success": False, "error": "字幕保存失敗"}
                
        except Exception as e:
            logger.error(f"字幕生成失敗: {e}")
            processing_status.update({
                "status": "error",
                "progress": 0,
                "message": f"處理失敗: {str(e)}"
            })
            return {"success": False, "error": str(e)}
        
        finally:
            # 清理臨時文件
            self.audio_processor.cleanup_temp_files()
    
    def _update_progress(self, value: int, message: str = ""):
        """更新進度"""
        global processing_status
        processing_status.update({
            "progress": value,
            "message": message
        })

# Flask 路由
@app.route('/')
def index():
    """主頁面"""
    return send_from_directory('web_gui', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """靜態文件服務"""
    return send_from_directory('web_gui', filename)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上傳接口"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '沒有選擇文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '沒有選擇文件'})
        
        # 檢查文件類型
        allowed_extensions = {
            'mp4', 'avi', 'mov', 'mkv', 'webm',
            'mp3', 'wav', 'm4a', 'flac', 'aac', 'ogg'
        }
        
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'success': False, 'error': '不支援的文件格式'})
        
        # 保存臨時文件
        temp_dir = tempfile.gettempdir()
        filename = werkzeug.utils.secure_filename(file.filename)
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        return jsonify({
            'success': True,
            'temp_path': temp_path,
            'filename': filename,
            'size': os.path.getsize(temp_path)
        })
        
    except Exception as e:
        logger.error(f"文件上傳失敗: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/process', methods=['POST'])
def process_file():
    """處理文件接口"""
    try:
        data = request.get_json()
        
        input_file = data.get('input_file')
        language = data.get('language', 'auto')
        format = data.get('format', 'srt')
        
        if not input_file or not os.path.exists(input_file):
            return jsonify({'success': False, 'error': '輸入文件不存在'})
        
        # 語言映射
        language_map = {
            'auto': None,
            'zh': 'zh',
            'en': 'en',
            'ja': 'ja',
            'ko': 'ko'
        }
        language_code = language_map.get(language, None)
        
        # 在新線程中處理
        def process_in_background():
            global subtitle_generator
            if not subtitle_generator:
                subtitle_generator = WebSubtitleGenerator()
            
            result = subtitle_generator.generate_subtitle(
                input_file, language_code, format
            )
            
            # 處理完成後清理臨時文件
            try:
                if os.path.exists(input_file):
                    os.remove(input_file)
            except:
                pass
        
        thread = threading.Thread(target=process_in_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': '開始處理'})
        
    except Exception as e:
        logger.error(f"處理請求失敗: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/status')
def get_status():
    """獲取處理狀態"""
    global processing_status
    return jsonify(processing_status)

@app.route('/api/download/<filename>')
def download_file(filename):
    """下載生成的字幕文件"""
    try:
        # 查找文件
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        if os.path.exists(file_path):
            return send_from_directory(temp_dir, filename, as_attachment=True)
        else:
            return jsonify({'error': '文件不存在'}), 404
            
    except Exception as e:
        logger.error(f"下載失敗: {e}")
        return jsonify({'error': str(e)}), 500

def main():
    """啟動 Web 服務器"""
    print("=" * 50)
    print("智能字幕生成器 Web 版本")
    print("=" * 50)
    print("正在啟動服務器...")
    
    # 檢查 web_gui 目錄
    web_gui_path = Path(__file__).parent / 'web_gui'
    if not web_gui_path.exists():
        print("錯誤: web_gui 目錄不存在")
        return
    
    try:
        print("服務器已啟動")
        print(f"請在瀏覽器中打開: http://localhost:5000")
        print("使用 Tailwind CSS 製作的現代化界面")
        print("Notion 風格設計")
        print("支援拖放上傳")
        print("實時進度顯示")
        print("\n按 Ctrl+C 停止服務器")
        print("-" * 50)
        
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n服務器已停止")
    except Exception as e:
        print(f"服務器啟動失敗: {e}")

if __name__ == "__main__":
    main()