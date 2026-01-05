"""
PosterGenMaster - 海报绘制核心逻辑
PosterDrawer 类：负责在底图上绘制文字，生成海报
"""
from PIL import Image, ImageDraw, ImageFont
import os


class PosterDrawer:
    """海报绘制器类，负责在底图上绘制文字生成海报"""
    
    def __init__(self, background_path='assets/template.jpg', font_path='assets/font.ttf', bold_font_path='assets/NotoSansSC-Bold.ttf'):
        """
        初始化海报绘制器
        
        Args:
            background_path: 背景底图路径，默认为 'assets/template.jpg'
            font_path: 字体文件路径，默认为 'assets/font.ttf'
            bold_font_path: 粗体字体文件路径，默认为 'assets/NotoSansSC-Bold.ttf'
        """
        self.background_path = background_path
        self.font_path = font_path
        self.bold_font_path = bold_font_path
        
        # 默认配置字典 - 方便后续微调坐标和颜色
        # 整体往上移动，Y坐标都减少了
        self.config = {
            'layers': {
                'city_name': {  # 城市+姓名（同一行）
                    'color': '#FFEDB5',  # 浅金色
                    'size': 120,  # 字号+20
                    'y': 415,  # Y坐标-15（往上移动）
                    'spacing': 35,  # 城市和姓名之间的间距（增大）
                    'align': 'center',
                    'bold': True  # 使用粗体
                },
                'desc': {
                    'color': '#FFEDB5',  # 浅金色（统一颜色）
                    'size': 50,
                    'y': 620,  # Y坐标+20（往下移动）
                    'align': 'center',
                    'bold': True  # 使用粗体
                },
                'amount': {
                    'color': '#FFEDB5',  # 浅金色（统一颜色）
                    'size': 220,
                    'y': 750,  # 往上移动
                    'align': 'center',
                    'bold': True  # 使用粗体
                },
                'unit': {
                    'color': '#FFEDB5',  # 浅金色（统一颜色）
                    'size': 80,
                    'y': 750,  # 与金额底部对齐，实际会动态调整
                    'spacing_x': 20,  # 金额和单位之间的水平间距
                    'spacing_y': 10,  # 金额和单位之间的垂直间距（单位在右下角）
                    'offset_y': 60,  # 单位Y坐标的偏移量（正值往下移动，负值往上移动）
                    'align': 'right_bottom',  # 单位在金额右下角
                    'bold': True  # 使用粗体
                }
            }
        }
    
    def get_font(self, size, bold=False):
        """
        获取字体对象，如果字体文件不存在则使用默认字体
        
        Args:
            size: 字体大小
            bold: 是否使用粗体字体，默认为 False
        
        Returns:
            ImageFont 对象
        """
        font_file = self.bold_font_path if bold else self.font_path
        try:
            if os.path.exists(font_file):
                return ImageFont.truetype(font_file, size)
            else:
                # 使用默认字体
                return ImageFont.load_default()
        except Exception as e:
            print(f"警告: 无法加载字体 {font_file}: {e}，使用默认字体")
            return ImageFont.load_default()
    
    def get_text_bbox(self, draw, text, font):
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
    
    def load_background(self):
        """
        加载背景底图
        
        Returns:
            PIL Image 对象
        
        Raises:
            FileNotFoundError: 如果底图文件不存在
        """
        if not os.path.exists(self.background_path):
            raise FileNotFoundError(
                f"底图文件不存在: {self.background_path}\n"
                f"请确保在 assets/ 目录下放置 template.jpg 文件"
            )
        return Image.open(self.background_path)
    
    def draw(self, data_row, config=None):
        """
        在底图上绘制文字，生成海报
        
        Args:
            data_row: 字典或 pandas Series，包含 '城市', '姓名', '描述', '金额', '单位' 等字段
            config: 配置字典，如果为 None 则使用默认配置
        
        Returns:
            绘制好的 Image 对象
        """
        # 加载底图
        base_image = self.load_background()
        
        # 使用传入的配置或默认配置
        if config is None:
            config = self.config
        
        # 创建底图的副本，避免修改原图
        img = base_image.copy()
        draw = ImageDraw.Draw(img)
        
        # 获取画布尺寸
        canvas_width = img.width
        canvas_height = img.height
        center_x = canvas_width // 2
        
        layers_config = config.get('layers', self.config['layers'])
        
        # 1. 绘制城市+姓名（同一行，居中，粗体）
        city = str(data_row.get('城市', ''))
        name = str(data_row.get('姓名', ''))
        city_name_config = layers_config['city_name']
        city_name_font = self.get_font(city_name_config['size'], bold=city_name_config.get('bold', False))
        
        # 计算城市和姓名的总宽度
        city_bbox = self.get_text_bbox(draw, city, city_name_font)
        name_bbox = self.get_text_bbox(draw, name, city_name_font)
        city_width = city_bbox[2] - city_bbox[0]
        name_width = name_bbox[2] - name_bbox[0]
        spacing = city_name_config.get('spacing', 20)
        total_width = city_width + spacing + name_width
        
        # 计算起始X坐标（居中）
        start_x = center_x - total_width // 2
        
        # 绘制城市
        city_x = start_x
        draw.text(
            (city_x, city_name_config['y']),
            city,
            fill=city_name_config['color'],
            font=city_name_font
        )
        
        # 绘制姓名
        name_x = start_x + city_width + spacing
        draw.text(
            (name_x, city_name_config['y']),
            name,
            fill=city_name_config['color'],
            font=city_name_font
        )
        
        # 2. 绘制描述（居中）
        desc = str(data_row.get('描述', ''))
        desc_config = layers_config['desc']
        desc_font = self.get_font(desc_config['size'], bold=desc_config.get('bold', False))
        desc_bbox = self.get_text_bbox(draw, desc, desc_font)
        desc_width = desc_bbox[2] - desc_bbox[0]
        desc_x = center_x - desc_width // 2
        draw.text(
            (desc_x, desc_config['y']),
            desc,
            fill=desc_config['color'],
            font=desc_font
        )
        
        # 3. 先计算金额和单位的尺寸（用于整体居中）
        amount = str(data_row.get('金额', ''))
        amount_config = layers_config['amount']
        amount_font = self.get_font(amount_config['size'], bold=amount_config.get('bold', False))
        amount_bbox = self.get_text_bbox(draw, amount, amount_font)
        amount_width = amount_bbox[2] - amount_bbox[0]
        amount_height = amount_bbox[3] - amount_bbox[1]
        
        unit = str(data_row.get('单位', ''))
        unit_config = layers_config['unit']
        unit_font = self.get_font(unit_config['size'], bold=unit_config.get('bold', False))
        unit_bbox = self.get_text_bbox(draw, unit, unit_font)
        unit_width = unit_bbox[2] - unit_bbox[0]
        unit_height = unit_bbox[3] - unit_bbox[1]
        
        # 计算金额+单位的整体宽度（金额宽度 + 间距 + 单位宽度）
        spacing_x = unit_config.get('spacing_x', 20)
        total_width = amount_width + spacing_x + unit_width
        
        # 让金额+单位作为整体居中
        # 金额的X坐标 = 中心 - 整体宽度的一半
        amount_x = center_x - total_width // 2
        amount_y = amount_config['y'] - amount_height // 2  # 调整Y坐标，使文字垂直居中
        
        # 计算金额的底部Y坐标
        amount_bottom = amount_y + amount_height
        
        # 绘制金额
        draw.text(
            (amount_x, amount_y),
            amount,
            fill=amount_config['color'],
            font=amount_font
        )
        
        # 4. 绘制单位（在金额右下角，粗体）
        # 单位的X坐标：金额右边缘 + 水平间距
        unit_x = amount_x + amount_width + spacing_x
        
        # 计算单位的Y坐标：让单位的底部与金额的底部对齐，然后加上偏移量
        # 单位应该在金额的右下角，底部对齐
        # unit_y + unit_height = amount_bottom + offset_y
        # 所以：unit_y = amount_bottom - unit_height + offset_y
        offset_y = unit_config.get('offset_y', 0)  # 获取Y坐标偏移量（正值往下，负值往上）
        unit_y = amount_bottom - unit_height + offset_y
        
        draw.text(
            (unit_x, unit_y),
            unit,
            fill=unit_config['color'],
            font=unit_font
        )
        
        return img
    
    def update_config(self, **kwargs):
        """
        更新配置
        
        Args:
            **kwargs: 配置项，例如 layers={'name': {'size': 100}}
        """
        if 'layers' in kwargs:
            # 深度合并 layers 配置
            for layer_name, layer_config in kwargs['layers'].items():
                if layer_name in self.config['layers']:
                    self.config['layers'][layer_name].update(layer_config)
                else:
                    self.config['layers'][layer_name] = layer_config
        else:
            self.config.update(kwargs)

