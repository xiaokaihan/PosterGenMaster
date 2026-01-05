"""
PosterGen - 海报绘制工具函数模块
处理图片绘制相关的核心逻辑
"""
from PIL import Image, ImageDraw, ImageFont
import os


# 配置字典 - 方便后续微调坐标和颜色
CONFIG = {
    'font_path': 'font.ttf',  # 字体文件路径
    'background_path': 'background.jpg',  # 底图路径
    'layers': {
        'name': {
            'color': '#FFEDB5',  # 浅金色
            'size': 80,
            'y': 550,
            'align': 'center'
        },
        'desc': {
            'color': '#FFFFFF',  # 纯白色
            'size': 50,
            'y': 680,
            'align': 'center'
        },
        'amount': {
            'color': '#FFDFA0',  # 亮金色
            'size': 220,
            'y': 850,
            'align': 'center'
        },
        'unit': {
            'color': '#FFFFFF',  # 纯白色
            'size': 80,
            'y': 850,  # 与金额底部对齐，实际会动态调整
            'spacing': 20,  # 金额和单位之间的间距
            'align': 'left'  # 紧跟在金额后面
        }
    }
}


def get_font(font_path, size):
    """
    获取字体对象，如果字体文件不存在则使用默认字体
    
    Args:
        font_path: 字体文件路径
        size: 字体大小
    
    Returns:
        ImageFont 对象
    """
    try:
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        else:
            # 使用默认字体
            return ImageFont.load_default()
    except Exception as e:
        print(f"警告: 无法加载字体 {font_path}: {e}，使用默认字体")
        return ImageFont.load_default()


def get_text_bbox(draw, text, font):
    """
    获取文字的边界框（用于计算文字宽度和高度）
    
    Args:
        draw: ImageDraw 对象
        text: 文字内容
        font: 字体对象
    
    Returns:
        (left, top, right, bottom) 元组
    """
    return draw.textbbox((0, 0), text, font=font)


def draw_poster(base_image, data_row, config=None):
    """
    在底图上绘制文字，生成海报
    
    Args:
        base_image: Pillow Image 对象（底图）
        data_row: 字典，包含 '姓名', '描述', '金额', '单位' 等字段
        config: 配置字典，如果为 None 则使用默认 CONFIG
    
    Returns:
        绘制好的 Image 对象
    """
    if config is None:
        config = CONFIG
    
    # 创建底图的副本，避免修改原图
    img = base_image.copy()
    draw = ImageDraw.Draw(img)
    
    # 获取画布尺寸
    canvas_width = img.width
    canvas_height = img.height
    center_x = canvas_width // 2
    
    layers_config = config['layers']
    
    # 1. 绘制姓名（居中）
    name = str(data_row.get('姓名', ''))
    name_config = layers_config['name']
    name_font = get_font(config['font_path'], name_config['size'])
    name_bbox = get_text_bbox(draw, name, name_font)
    name_width = name_bbox[2] - name_bbox[0]
    name_x = center_x - name_width // 2
    draw.text(
        (name_x, name_config['y']),
        name,
        fill=name_config['color'],
        font=name_font
    )
    
    # 2. 绘制描述（居中）
    desc = str(data_row.get('描述', ''))
    desc_config = layers_config['desc']
    desc_font = get_font(config['font_path'], desc_config['size'])
    desc_bbox = get_text_bbox(draw, desc, desc_font)
    desc_width = desc_bbox[2] - desc_bbox[0]
    desc_x = center_x - desc_width // 2
    draw.text(
        (desc_x, desc_config['y']),
        desc,
        fill=desc_config['color'],
        font=desc_font
    )
    
    # 3. 绘制金额（居中）
    amount = str(data_row.get('金额', ''))
    amount_config = layers_config['amount']
    amount_font = get_font(config['font_path'], amount_config['size'])
    amount_bbox = get_text_bbox(draw, amount, amount_font)
    amount_width = amount_bbox[2] - amount_bbox[0]
    amount_height = amount_bbox[3] - amount_bbox[1]
    amount_x = center_x - amount_width // 2
    amount_y = amount_config['y'] - amount_height // 2  # 调整Y坐标，使文字垂直居中
    draw.text(
        (amount_x, amount_y),
        amount,
        fill=amount_config['color'],
        font=amount_font
    )
    
    # 4. 绘制单位（紧跟在金额右侧）
    unit = str(data_row.get('单位', ''))
    unit_config = layers_config['unit']
    unit_font = get_font(config['font_path'], unit_config['size'])
    unit_bbox = get_text_bbox(draw, unit, unit_font)
    unit_height = unit_bbox[3] - unit_bbox[1]
    
    # 计算单位的X坐标：画布中心 + 金额宽度的一半 + 间距
    unit_x = center_x + amount_width // 2 + unit_config.get('spacing', 20)
    
    # 计算单位的Y坐标：与金额底部对齐
    # amount_y 是金额的顶部，amount_height 是金额的高度
    # 单位需要与金额底部对齐，所以 unit_y = amount_y + amount_height - unit_height
    unit_y = amount_y + amount_height - unit_height
    
    draw.text(
        (unit_x, unit_y),
        unit,
        fill=unit_config['color'],
        font=unit_font
    )
    
    return img

