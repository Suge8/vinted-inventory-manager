#!/usr/bin/env python3
"""
创建应用图标
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    """创建可爱的应用图标"""
    # 创建512x512的图标
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 背景渐变色 - 温暖的橙色到粉色
    for y in range(size):
        # 从橙色 #FF6B6B 到粉色 #4ECDC4
        r = int(255 - (255 - 78) * y / size)
        g = int(107 + (205 - 107) * y / size)
        b = int(107 + (196 - 107) * y / size)
        draw.rectangle([(0, y), (size, y+1)], fill=(r, g, b, 255))
    
    # 绘制圆角矩形背景
    corner_radius = 80
    draw.rounded_rectangle(
        [(20, 20), (size-20, size-20)], 
        radius=corner_radius, 
        fill=(255, 255, 255, 240)
    )
    
    # 绘制购物袋图标
    bag_color = (255, 107, 107, 255)  # 可爱的粉红色
    
    # 购物袋主体
    bag_width = 200
    bag_height = 240
    bag_x = (size - bag_width) // 2
    bag_y = (size - bag_height) // 2 + 20
    
    # 袋子主体
    draw.rounded_rectangle(
        [(bag_x, bag_y + 40), (bag_x + bag_width, bag_y + bag_height)],
        radius=20,
        fill=bag_color
    )
    
    # 袋子手柄
    handle_width = 60
    handle_height = 40
    handle_thickness = 15
    
    # 左手柄
    left_handle_x = bag_x + 30
    draw.rounded_rectangle(
        [(left_handle_x, bag_y), (left_handle_x + handle_width, bag_y + handle_thickness)],
        radius=8,
        fill=bag_color
    )
    draw.rounded_rectangle(
        [(left_handle_x, bag_y), (left_handle_x + handle_thickness, bag_y + handle_height)],
        radius=8,
        fill=bag_color
    )
    draw.rounded_rectangle(
        [(left_handle_x + handle_width - handle_thickness, bag_y), 
         (left_handle_x + handle_width, bag_y + handle_height)],
        radius=8,
        fill=bag_color
    )
    
    # 右手柄
    right_handle_x = bag_x + bag_width - 30 - handle_width
    draw.rounded_rectangle(
        [(right_handle_x, bag_y), (right_handle_x + handle_width, bag_y + handle_thickness)],
        radius=8,
        fill=bag_color
    )
    draw.rounded_rectangle(
        [(right_handle_x, bag_y), (right_handle_x + handle_thickness, bag_y + handle_height)],
        radius=8,
        fill=bag_color
    )
    draw.rounded_rectangle(
        [(right_handle_x + handle_width - handle_thickness, bag_y), 
         (right_handle_x + handle_width, bag_y + handle_height)],
        radius=8,
        fill=bag_color
    )
    
    # 添加可爱的装饰元素
    # 小心心
    heart_color = (255, 255, 255, 200)
    heart_size = 30
    heart_x = bag_x + bag_width // 2 - heart_size // 2
    heart_y = bag_y + 80
    
    # 简单的心形（用两个圆和一个三角形）
    draw.ellipse([(heart_x, heart_y), (heart_x + heart_size//2, heart_y + heart_size//2)], fill=heart_color)
    draw.ellipse([(heart_x + heart_size//2, heart_y), (heart_x + heart_size, heart_y + heart_size//2)], fill=heart_color)
    draw.polygon([(heart_x + heart_size//4, heart_y + heart_size//2), 
                  (heart_x + 3*heart_size//4, heart_y + heart_size//2),
                  (heart_x + heart_size//2, heart_y + heart_size)], fill=heart_color)
    
    # 添加闪光效果
    star_color = (255, 255, 255, 150)
    star_positions = [(100, 100), (400, 120), (80, 350), (420, 380)]
    
    for star_x, star_y in star_positions:
        # 简单的星星
        star_size = 20
        draw.polygon([
            (star_x, star_y - star_size),
            (star_x + star_size//3, star_y - star_size//3),
            (star_x + star_size, star_y),
            (star_x + star_size//3, star_y + star_size//3),
            (star_x, star_y + star_size),
            (star_x - star_size//3, star_y + star_size//3),
            (star_x - star_size, star_y),
            (star_x - star_size//3, star_y - star_size//3)
        ], fill=star_color)
    
    # 保存不同尺寸的图标
    sizes = [16, 32, 48, 64, 128, 256, 512]
    
    # 创建assets目录
    os.makedirs('assets', exist_ok=True)
    
    # 保存PNG格式
    img.save('assets/icon.png', 'PNG')
    print("✅ 创建了 assets/icon.png")
    
    # 创建ICO文件（Windows）
    ico_images = []
    for size in [16, 32, 48, 64, 128, 256]:
        ico_img = img.resize((size, size), Image.Resampling.LANCZOS)
        ico_images.append(ico_img)
    
    ico_images[0].save('assets/icon.ico', format='ICO', sizes=[(img.width, img.height) for img in ico_images])
    print("✅ 创建了 assets/icon.ico")
    
    # 创建ICNS文件（macOS）
    try:
        # 需要安装 pillow-icns: pip install pillow-icns
        img.save('assets/icon.icns', format='ICNS')
        print("✅ 创建了 assets/icon.icns")
    except Exception as e:
        print(f"⚠️ 无法创建ICNS文件: {e}")
        print("请安装: pip install pillow-icns")
    
    print("🎨 图标创建完成！")

if __name__ == "__main__":
    create_app_icon()
