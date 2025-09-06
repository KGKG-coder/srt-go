#!/usr/bin/env python3
"""
本地獨立GUI應用 - 字幕生成工具
無需端口或web服務，完全本地運行
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import logging
from pathlib import Path
import json

# 導入核心模組
from simplified_subtitle_core import SimplifiedSubtitleCore
from semantic_processor import SemanticSegmentProcessor

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('local_gui.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LocalSubtitleGUI:
    """本地字幕生成GUI應用"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("字幕生成工具 - 本地版")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # 核心組件
        self.subtitle_core = SimplifiedSubtitleCore()
        self.semantic_processor = SemanticSegmentProcessor()
        
        # 界面變數
        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar(value=str(Path.home() / "Desktop"))
        self.language = tk.StringVar(value="zh")
        self.format_var = tk.StringVar(value="srt")
        self.is_processing = False
        
        # 支持的格式
        self.supported_formats = [
            ("所有支持的影音檔", "*.mp4;*.mkv;*.avi;*.mov;*.wmv;*.flv;*.webm;*.m4v;*.mp3;*.wav;*.flac;*.aac;*.ogg;*.wma"),
            ("影片檔案", "*.mp4;*.mkv;*.avi;*.mov;*.wmv;*.flv;*.webm;*.m4v"),
            ("音訊檔案", "*.mp3;*.wav;*.flac;*.aac;*.ogg;*.wma"),
            ("所有檔案", "*.*")
        ]
        
        self.setup_ui()
        self.load_config()
        
        logger.info("本地GUI應用已初始化")
    
    def setup_ui(self):
        """設置用戶界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置網格權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 標題
        title_label = ttk.Label(
            main_frame, 
            text="字幕生成工具", 
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 檔案選擇區域
        file_frame = ttk.LabelFrame(main_frame, text="檔案選擇", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="輸入檔案:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(file_frame, textvariable=self.input_file, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(file_frame, text="瀏覽", command=self.browse_input_file).grid(row=0, column=2)
        
        ttk.Label(file_frame, text="輸出目錄:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Entry(file_frame, textvariable=self.output_dir, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        ttk.Button(file_frame, text="瀏覽", command=self.browse_output_dir).grid(row=1, column=2, pady=(10, 0))
        
        # 設置區域
        settings_frame = ttk.LabelFrame(main_frame, text="設置", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(settings_frame, text="語言:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        language_combo = ttk.Combobox(
            settings_frame, 
            textvariable=self.language,
            values=["zh", "en", "ja", "ko", "auto"],
            state="readonly"
        )
        language_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(settings_frame, text="格式:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        format_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.format_var,
            values=["srt", "vtt", "txt"],
            state="readonly"
        )
        format_combo.grid(row=0, column=3, sticky=tk.W)
        
        # 控制按鈕
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        self.process_btn = ttk.Button(
            button_frame, 
            text="開始生成字幕", 
            command=self.start_processing,
            style="Accent.TButton"
        )
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(
            button_frame,
            text="停止", 
            command=self.stop_processing,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT)
        
        # 進度條
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=400
        )
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 狀態標籤
        self.status_label = ttk.Label(main_frame, text="準備就緒")
        self.status_label.grid(row=5, column=0, columnspan=3, pady=(0, 10))
        
        # 日誌輸出區域
        log_frame = ttk.LabelFrame(main_frame, text="輸出日誌", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            wrap=tk.WORD,
            font=('Consolas', 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 拖拽支持
        self.setup_drag_drop()
    
    def setup_drag_drop(self):
        """設置拖拽功能"""
        # 拖拽功能將在main函數中初始化
        # 這裡只是占位函數，實際設置在應用創建後進行
        pass
    
    def init_drag_drop(self):
        """初始化拖拽功能（在創建應用後調用）"""
        if hasattr(self, 'has_dnd') and self.has_dnd:
            try:
                import tkinterdnd2
                self.root.drop_target_register(tkinterdnd2.DND_FILES)
                self.root.dnd_bind('<<Drop>>', self.on_drop)
                self.log("✓ 拖拽功能已啟用")
            except Exception as e:
                self.log(f"⚠ 拖拽功能設置失敗: {e}")
        else:
            self.log("⚠ 拖拽功能不可用，請使用瀏覽按鈕選擇檔案")
    
    def on_drop(self, event):
        """處理拖拽檔案"""
        files = self.root.tk.splitlist(event.data)
        if files:
            self.input_file.set(files[0])
            self.log(f"📁 已選擇檔案: {os.path.basename(files[0])}")
    
    def browse_input_file(self):
        """瀏覽輸入檔案"""
        filetypes = [
            ("所有支持格式", "*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm *.m4v *.mp3 *.wav *.flac *.aac *.ogg *.wma"),
            ("影片檔案", "*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm *.m4v"),
            ("音訊檔案", "*.mp3 *.wav *.flac *.aac *.ogg *.wma"),
            ("所有檔案", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="選擇影音檔案",
            filetypes=filetypes
        )
        
        if filename:
            self.input_file.set(filename)
            self.log(f"📁 已選擇檔案: {os.path.basename(filename)}")
    
    def browse_output_dir(self):
        """瀏覽輸出目錄"""
        directory = filedialog.askdirectory(
            title="選擇輸出目錄",
            initialdir=self.output_dir.get()
        )
        
        if directory:
            self.output_dir.set(directory)
            self.log(f"📂 輸出目錄: {directory}")
    
    def log(self, message):
        """添加日誌訊息"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        logger.info(message)
    
    def update_progress(self, progress, status=""):
        """更新進度"""
        self.progress_var.set(progress)
        if status:
            self.status_label.config(text=status)
        self.root.update()
    
    def start_processing(self):
        """開始處理"""
        if not self.input_file.get():
            messagebox.showerror("錯誤", "請選擇輸入檔案")
            return
        
        if not os.path.exists(self.input_file.get()):
            messagebox.showerror("錯誤", "輸入檔案不存在")
            return
        
        if not os.path.exists(self.output_dir.get()):
            messagebox.showerror("錯誤", "輸出目錄不存在")
            return
        
        # 切換UI狀態
        self.is_processing = True
        self.process_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.log_text.delete(1.0, tk.END)
        
        # 在新線程中處理
        self.processing_thread = threading.Thread(target=self.process_subtitle)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def stop_processing(self):
        """停止處理"""
        self.is_processing = False
        self.log("⏹ 正在停止處理...")
        
        # 重置UI狀態
        self.process_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="已停止")
    
    def process_subtitle(self):
        """處理字幕生成"""
        try:
            input_file = self.input_file.get()
            output_dir = self.output_dir.get()
            language = self.language.get()
            format_type = self.format_var.get()
            
            self.log(f"🎬 開始處理: {os.path.basename(input_file)}")
            self.log(f"🌍 語言: {language}")
            self.log(f"📄 格式: {format_type}")
            self.update_progress(5, "正在初始化...")
            
            # 設置進度回調
            def progress_callback(progress, message=""):
                if not self.is_processing:
                    return False
                self.update_progress(progress, message)
                self.log(f"📊 {progress:.1f}% - {message}")
                return True
            
            # 生成字幕
            self.subtitle_core.progress_callback = progress_callback
            
            result = self.subtitle_core.generate_subtitles(
                audio_path=input_file,
                output_dir=output_dir,
                language=language,
                formats=[format_type]
            )
            
            if not self.is_processing:
                return
            
            if result.get('successful', 0) > 0:
                self.update_progress(100, "處理完成!")
                self.log("✅ 字幕生成完成!")
                
                for file_result in result.get('results', []):
                    if file_result.get('success'):
                        output_file = file_result.get('output_file')
                        if output_file:
                            self.log(f"📄 輸出檔案: {output_file}")
                
                # 顯示成功訊息
                messagebox.showinfo("完成", "字幕生成完成!")
                
            else:
                self.log("❌ 字幕生成失敗")
                error_msg = result.get('errors', ['未知錯誤'])[0]
                messagebox.showerror("錯誤", f"字幕生成失敗: {error_msg}")
        
        except Exception as e:
            logger.error(f"處理失敗: {e}")
            self.log(f"❌ 處理失敗: {e}")
            messagebox.showerror("錯誤", f"處理失敗: {e}")
        
        finally:
            # 重置UI狀態
            self.is_processing = False
            self.process_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            if self.progress_var.get() < 100:
                self.status_label.config(text="準備就緒")
    
    def load_config(self):
        """載入配置"""
        try:
            config_file = "local_gui_config.json"
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.output_dir.set(config.get('output_dir', str(Path.home() / "Desktop")))
                self.language.set(config.get('language', 'zh'))
                self.format_var.set(config.get('format', 'srt'))
                
                logger.info(f"已載入配置: {config_file}")
        except Exception as e:
            logger.warning(f"載入配置失敗: {e}")
    
    def save_config(self):
        """保存配置"""
        try:
            config = {
                'output_dir': self.output_dir.get(),
                'language': self.language.get(),
                'format': self.format_var.get()
            }
            
            config_file = "local_gui_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            logger.info(f"已保存配置: {config_file}")
        except Exception as e:
            logger.warning(f"保存配置失敗: {e}")
    
    def on_closing(self):
        """關閉應用"""
        if self.is_processing:
            if messagebox.askokcancel("確認", "正在處理中，確定要關閉嗎？"):
                self.stop_processing()
                self.root.after(1000, self.root.quit)
        else:
            self.save_config()
            self.root.quit()

def main():
    """主函數"""
    try:
        # 嘗試創建支持拖拽的根窗口
        try:
            import tkinterdnd2
            root = tkinterdnd2.TkinterDnD.Tk()
            has_dnd = True
        except ImportError:
            # 如果沒有拖拽支持，使用普通tkinter
            root = tk.Tk()
            has_dnd = False
        
        # 設置窗口圖標
        try:
            if os.path.exists('icon.ico'):
                root.iconbitmap('icon.ico')
            elif os.path.exists('icon.png'):
                # 如果有PNG圖標，也可以使用
                pass
        except:
            pass
        
        # 創建應用
        app = LocalSubtitleGUI(root)
        app.has_dnd = has_dnd
        
        # 初始化拖拽功能
        app.init_drag_drop()
        
        # 設置關閉事件
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # 居中窗口
        try:
            root.eval('tk::PlaceWindow . center')
        except:
            # 手動居中
            root.update_idletasks()
            width = root.winfo_width()
            height = root.winfo_height()
            x = (root.winfo_screenwidth() // 2) - (width // 2)
            y = (root.winfo_screenheight() // 2) - (height // 2)
            root.geometry(f'+{x}+{y}')
        
        logger.info("本地GUI應用已啟動")
        
        # 啟動主循環
        root.mainloop()
        
    except Exception as e:
        logger.error(f"應用啟動失敗: {e}")
        try:
            messagebox.showerror("錯誤", f"應用啟動失敗: {e}")
        except:
            print(f"錯誤: 應用啟動失敗: {e}")

if __name__ == "__main__":
    main()