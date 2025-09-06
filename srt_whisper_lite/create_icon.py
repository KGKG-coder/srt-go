#!/usr/bin/env python3
"""
創建程式圖標（藍色閃電圖案）
"""
import os
from PIL import Image, ImageDraw

def create_lightning_icon():
    """創建藍色閃電圖標"""
    # 創建多個尺寸的圖標
    sizes = [16, 32, 48, 64, 128, 256]
    icons = []
    
    for size in sizes:
        # 創建圖像
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 計算圖標參數
        padding = int(size * 0.15)
        line_width = max(int(size * 0.08), 2)
        
        # 藍色 (#0066FF)
        blue_color = (0, 102, 255, 255)
        
        # 閃電路徑點（相對坐標）
        lightning_path = [
            (0.65, 0.1),   # 頂部
            (0.35, 0.45),  # 左中
            (0.5, 0.45),   # 中間左
            (0.35, 0.9),   # 底部
            (0.65, 0.55),  # 右中
            (0.5, 0.55),   # 中間右
            (0.65, 0.1)    # 回到頂部
        ]
        
        # 轉換為實際坐標
        points = []
        for x, y in lightning_path:
            px = padding + int((size - 2 * padding) * x)
            py = padding + int((size - 2 * padding) * y)
            points.append((px, py))
        
        # 繪製填充的閃電
        draw.polygon(points[:-1], fill=blue_color)
        
        # 添加圓角背景（可選）
        if size >= 48:
            # 創建新圖像用於圓角背景
            bg = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            bg_draw = ImageDraw.Draw(bg)
            
            # 繪製圓角矩形背景
            radius = int(size * 0.2)
            bg_draw.rounded_rectangle(
                [(0, 0), (size-1, size-1)],
                radius=radius,
                fill=blue_color
            )
            
            # 在背景上繪製白色閃電
            fg = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            fg_draw = ImageDraw.Draw(fg)
            
            # 繪製白色閃電
            white_color = (255, 255, 255, 255)
            fg_draw.polygon(points[:-1], fill=white_color)
            
            # 合併圖層
            img = Image.alpha_composite(bg, fg)
        
        icons.append(img)
    
    # 保存為 ICO（嘗試不同的方法）
    output_path = "icon.ico"
    try:
        # 方法1：使用最大尺寸保存為ICO
        icons[-1].save(output_path, format='ICO')
        print(f"圖標已創建: {output_path}")
    except Exception as e:
        print(f"ICO 格式保存失敗: {e}")
        # 使用 PNG 替代
        output_path = "icon_fallback.png"
        icons[-1].save(output_path, format='PNG')
        print(f"使用 PNG 替代: {output_path}")
    
    # 同時保存 PNG 版本供 Electron 使用
    png_path = "icon.png"
    icons[-1].save(png_path, format='PNG')
    print(f"PNG 圖標已創建: {png_path}")
    
    # 複製到 Electron 應用目錄
    electron_icon_path = os.path.join("electron-react-app", "icon.png")
    if os.path.exists("electron-react-app"):
        icons[-1].save(electron_icon_path, format='PNG')
        print(f"圖標已複製到 Electron 目錄: {electron_icon_path}")
    
    # 創建 macOS 圖標（可選）
    icns_path = "icon.icns"
    try:
        # macOS 圖標需要特定尺寸
        mac_sizes = [16, 32, 64, 128, 256, 512]
        mac_icons = []
        
        for size in mac_sizes:
            if size <= 256:
                # 使用已有的圖標
                idx = sizes.index(size) if size in sizes else -1
                mac_icons.append(icons[idx])
            else:
                # 創建更大的圖標
                img = create_single_icon(size, blue_color)
                mac_icons.append(img)
        
        # 注意：實際的 .icns 創建需要 macOS 工具
        print(f"準備創建 macOS 圖標: {icns_path}")
    except Exception as e:
        print(f"macOS 圖標創建失敗: {e}")
    
    return output_path

def create_single_icon(size, color):
    """創建單個尺寸的圖標"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 繪製圓角背景
    radius = int(size * 0.2)
    draw.rounded_rectangle(
        [(0, 0), (size-1, size-1)],
        radius=radius,
        fill=color
    )
    
    # 計算閃電參數
    padding = int(size * 0.15)
    
    # 閃電路徑
    lightning_path = [
        (0.65, 0.1),
        (0.35, 0.45),
        (0.5, 0.45),
        (0.35, 0.9),
        (0.65, 0.55),
        (0.5, 0.55)
    ]
    
    points = []
    for x, y in lightning_path:
        px = padding + int((size - 2 * padding) * x)
        py = padding + int((size - 2 * padding) * y)
        points.append((px, py))
    
    # 繪製白色閃電
    draw.polygon(points, fill=(255, 255, 255, 255))
    
    return img

if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw
        create_lightning_icon()
    except ImportError:
        print("請安裝 Pillow 庫: pip install Pillow")
    except Exception as e:
        print(f"創建圖標時發生錯誤: {e}")