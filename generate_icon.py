from PIL import Image, ImageDraw, ImageFont
import os

def create_torch_icon(output_path='icon.ico', size=256):
    """
    创建一个 PyTorch 风格的图标，保存为 .ico 文件
    """
    # 创建 RGBA 模式的图像
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # 主色调：PyTorch 红橙色 + CUDA 渐变感
    flame_colors = ['#FF3D00', '#FF8F00', '#FFD600']  # 红 -> 橙 -> 黄
    black = '#000000'

    # 绘制火焰形状（简化版）
    center_x = size // 2
    base_y = size
    top_y = size // 6

    # 分层绘制火焰
    steps = len(flame_colors)
    for i, color in enumerate(flame_colors):
        # 每层更窄
        width = (size // 2) * (1 - i / (steps * 1.5))
        x0 = center_x - width
        x1 = center_x + width
        y0 = top_y + (base_y - top_y) * (i / steps)
        y1 = top_y + (base_y - top_y) * ((i + 1) / steps)

        # 绘制椭圆层
        draw.ellipse((x0, y0, x1, y1), fill=color)

    # 绘制底部“托盘”（象征 GPU 或平台）
    tray_height = size // 8
    draw.rectangle(
        (size // 6, base_y - tray_height, size - size // 6, base_y),
        fill=black
    )

    # 可选：添加文字 "T" 或 "P"
    try:
        # 尝试使用默认字体（如果没有，使用基本文本）
        font = ImageFont.truetype("arialbd.ttf", size // 4)
    except:
        font = ImageFont.load_default()

    draw.text((center_x - size//10, top_y + size//10), "T", fill='white', font=font)

    # 保存为 .ico，支持多种尺寸
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    image.save(output_path, format='ICO', sizes=icon_sizes)

    print(f"✅ 图标已生成: {os.path.abspath(output_path)}")
    print(f"🎨 尺寸: {size}x{size} 支持多分辨率")

if __name__ == '__main__':
    create_torch_icon('icon.ico', 256)