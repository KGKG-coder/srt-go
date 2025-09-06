#!/usr/bin/env python3
"""
LOGO管理工具 - 讓用戶輕鬆替換自定義LOGO
"""

import os
import sys
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

class LogoManager:
    """LOGO管理器"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SRT GO - LOGO管理器")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # 支援的圖片格式
        self.supported_formats = [
            ('.png', 'PNG files'),
            ('.jpg', 'JPEG files'),
            ('.jpeg', 'JPEG files'),
            ('.gif', 'GIF files'),
            ('.bmp', 'BMP files')
        ]
        
        self.create_widgets()
        
    def create_widgets(self):
        """創建界面組件"""
        # 標題
        title_label = tk.Label(
            self.root,
            text="SRT GO LOGO 管理器",
            font=("Arial", 16, "bold"),
            pady=20
        )
        title_label.pack()
        
        # 當前LOGO顯示區域
        current_frame = tk.LabelFrame(self.root, text="當前LOGO", padx=10, pady=10)
        current_frame.pack(fill='x', padx=20, pady=10)
        
        self.current_logo_label = tk.Label(current_frame, text="沒有LOGO", bg='lightgray', width=20, height=10)
        self.current_logo_label.pack(pady=10)
        
        self.logo_info_label = tk.Label(current_frame, text="", font=("Arial", 9))
        self.logo_info_label.pack()
        
        # 載入當前LOGO
        self.load_current_logo()
        
        # 操作按鈕區域
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        # 選擇新LOGO按鈕
        select_button = tk.Button(
            button_frame,
            text="選擇新LOGO",
            command=self.select_new_logo,
            bg='#0078D4',
            fg='white',
            font=("Arial", 12),
            padx=20,
            pady=5
        )
        select_button.pack(side='left', padx=10)
        
        # 移除LOGO按鈕
        remove_button = tk.Button(
            button_frame,
            text="移除LOGO",
            command=self.remove_logo,
            bg='#DA1E37',
            fg='white',
            font=("Arial", 12),
            padx=20,
            pady=5
        )
        remove_button.pack(side='left', padx=10)
        
        # 重新載入按鈕
        reload_button = tk.Button(
            button_frame,
            text="重新載入",
            command=self.load_current_logo,
            bg='#107C10',
            fg='white',
            font=("Arial", 12),
            padx=20,
            pady=5
        )
        reload_button.pack(side='left', padx=10)
        
        # 說明文字
        info_text = """
使用說明：
1. 點擊「選擇新LOGO」來選擇您的圖片文件
2. 支援格式：PNG、JPG、JPEG、GIF、BMP
3. 建議使用正方形比例的圖片，程式會自動調整大小
4. 替換LOGO後需要重新啟動SRT GO才會生效
5. 如果要使用文字標題，可以點擊「移除LOGO」

技術提示：
- LOGO會被調整為64x64像素
- 透明背景的PNG格式效果最佳
- 檔案會被保存為「user_logo.png」
        """
        
        info_label = tk.Label(
            self.root,
            text=info_text,
            justify='left',
            font=("Arial", 9),
            bg='#F5F5F5'
        )
        info_label.pack(fill='both', expand=True, padx=20, pady=10)
        
    def load_current_logo(self):
        """載入並顯示當前LOGO"""
        try:
            if not HAS_PIL:
                self.current_logo_label.configure(text="PIL未安裝\n無法顯示圖片")
                self.logo_info_label.configure(text="請安裝Pillow庫：pip install Pillow")
                return
            
            # 查找現有的LOGO文件
            logo_files = [
                "user_logo.png", "user_logo.jpg", "user_logo.jpeg",
                "custom_logo.png", "custom_logo.jpg", "custom_logo.jpeg",
                "logo.png", "logo.jpg", "logo.jpeg", "logo.gif", "logo.bmp"
            ]
            
            logo_path = None
            for filename in logo_files:
                path = Path(filename)
                if path.exists():
                    logo_path = path
                    break
            
            if logo_path:
                # 載入圖片
                image = Image.open(logo_path)
                # 調整大小以適合顯示（保持比例）
                display_image = image.copy()
                display_image.thumbnail((80, 80), Image.Resampling.LANCZOS)
                
                # 創建tkinter圖片對象
                tk_image = ImageTk.PhotoImage(display_image)
                
                # 更新顯示
                self.current_logo_label.configure(image=tk_image, text="")
                self.current_logo_label.image = tk_image  # 保持引用
                
                # 顯示圖片信息
                file_size = logo_path.stat().st_size
                info_text = f"文件：{logo_path.name}\n大小：{image.size}\n文件大小：{file_size} bytes"
                self.logo_info_label.configure(text=info_text)
                
            else:
                self.current_logo_label.configure(image="", text="沒有找到\nLOGO文件")
                self.logo_info_label.configure(text="沒有LOGO文件")
                
        except Exception as e:
            self.current_logo_label.configure(image="", text=f"載入失敗\n{str(e)}")
            self.logo_info_label.configure(text="")
    
    def select_new_logo(self):
        """選擇新的LOGO文件"""
        try:
            # 創建文件類型過濾器
            filetypes = [('Image files', '*.png *.jpg *.jpeg *.gif *.bmp')]
            filetypes.extend(self.supported_formats)
            filetypes.append(('All files', '*.*'))
            
            # 打開文件選擇對話框
            file_path = filedialog.askopenfilename(
                title="選擇LOGO圖片",
                filetypes=filetypes
            )
            
            if file_path:
                self.install_logo(file_path)
                
        except Exception as e:
            messagebox.showerror("錯誤", f"選擇文件失敗：{str(e)}")
    
    def install_logo(self, source_path):
        """安裝新的LOGO"""
        try:
            source_path = Path(source_path)
            
            if not source_path.exists():
                messagebox.showerror("錯誤", "選擇的文件不存在")
                return
            
            # 檢查文件格式
            if not HAS_PIL:
                messagebox.showerror("錯誤", "PIL未安裝，無法處理圖片\\n請執行：pip install Pillow")
                return
            
            # 測試圖片是否有效
            try:
                image = Image.open(source_path)
                image.verify()  # 驗證圖片
            except Exception as e:
                messagebox.showerror("錯誤", f"無效的圖片文件：{str(e)}")
                return
            
            # 重新打開圖片（verify後需要重新打開）
            image = Image.open(source_path)
            
            # 調整大小
            image.thumbnail((64, 64), Image.Resampling.LANCZOS)
            
            # 保存為user_logo.png
            target_path = Path("user_logo.png")
            image.save(target_path, "PNG")
            
            messagebox.showinfo(
                "成功", 
                f"LOGO已成功安裝！\\n\\n原文件：{source_path.name}\\n保存為：{target_path.name}\\n\\n請重新啟動SRT GO以查看新LOGO。"
            )
            
            # 重新載入顯示
            self.load_current_logo()
            
        except Exception as e:
            messagebox.showerror("錯誤", f"安裝LOGO失敗：{str(e)}")
    
    def remove_logo(self):
        """移除當前LOGO"""
        try:
            # 查找用戶LOGO文件
            user_logos = ["user_logo.png", "user_logo.jpg", "user_logo.jpeg", "custom_logo.png"]
            
            removed_files = []
            for filename in user_logos:
                path = Path(filename)
                if path.exists():
                    path.unlink()
                    removed_files.append(filename)
            
            if removed_files:
                messagebox.showinfo(
                    "成功",
                    f"已移除LOGO文件：{', '.join(removed_files)}\\n\\n重新啟動SRT GO後將只顯示文字標題。"
                )
                self.load_current_logo()
            else:
                messagebox.showinfo("提示", "沒有找到用戶自定義的LOGO文件")
                
        except Exception as e:
            messagebox.showerror("錯誤", f"移除LOGO失敗：{str(e)}")
    
    def run(self):
        """運行LOGO管理器"""
        self.root.mainloop()

def main():
    """主函數"""
    if not HAS_PIL:
        print("Warning: PIL (Pillow) not installed. Image processing will be limited.")
        print("To install: pip install Pillow")
    
    app = LogoManager()
    app.run()

if __name__ == "__main__":
    main()