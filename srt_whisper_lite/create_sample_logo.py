#!/usr/bin/env python3
"""
創建一個示例LOGO - 如果用戶沒有提供圖片的話
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("PIL not available, cannot create sample logo")

def create_sample_logo():
    """創建一個簡單的SRT GO LOGO"""
    if not HAS_PIL:
        return False
    
    try:
        # 創建64x64的圖片
        size = (64, 64)
        image = Image.new('RGBA', size, (0, 0, 0, 0))  # 透明背景
        draw = ImageDraw.Draw(image)
        
        # 繪製圓形背景
        circle_color = (0, 120, 215, 255)  # 藍色
        draw.ellipse([4, 4, 60, 60], fill=circle_color)
        
        # 繪製文字 "SRT"
        try:
            # 嘗試使用較好的字體
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", 14)
            except:
                # 使用預設字體
                font = ImageFont.load_default()
        
        # 繪製白色文字
        text = "SRT"
        # 計算文字位置以居中
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (64 - text_width) // 2
        y = (64 - text_height) // 2 - 8
        
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        
        # 繪製 "GO" 文字
        text2 = "GO"
        bbox2 = draw.textbbox((0, 0), text2, font=font)
        text2_width = bbox2[2] - bbox2[0]
        x2 = (64 - text2_width) // 2
        y2 = y + text_height - 4
        
        draw.text((x2, y2), text2, fill=(255, 255, 255, 255), font=font)
        
        # 保存圖片
        image.save("logo.png", "PNG")
        print("Sample logo created successfully: logo.png")
        return True
        
    except Exception as e:
        print(f"Failed to create sample logo: {e}")
        return False

if __name__ == "__main__":
    create_sample_logo()