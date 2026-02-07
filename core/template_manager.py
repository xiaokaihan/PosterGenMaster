"""
模板管理模块
负责模板的创建、更新、删除和持久化存储
"""
import os
import json
import shutil
import uuid
import io
from datetime import datetime
from PIL import Image


class TemplateManager:
    """模板管理器"""
    
    def __init__(self, templates_dir='templates'):
        """
        初始化模板管理器
        
        Args:
            templates_dir: 模板存储目录
        """
        self.templates_dir = templates_dir
        self.templates_json_path = os.path.join(templates_dir, 'templates.json')
        self._ensure_templates_dir()
    
    def _ensure_templates_dir(self):
        """确保模板目录存在"""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir, exist_ok=True)
    
    def load_templates(self):
        """
        加载所有模板
        
        Returns:
            list: 模板列表
        """
        if not os.path.exists(self.templates_json_path):
            return []
        
        try:
            with open(self.templates_json_path, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            return templates if isinstance(templates, list) else []
        except Exception as e:
            print(f"加载模板列表失败: {e}")
            return []
    
    def save_templates(self, templates):
        """
        保存模板列表
        
        Args:
            templates: 模板列表
        """
        self._ensure_templates_dir()
        try:
            with open(self.templates_json_path, 'w', encoding='utf-8') as f:
                json.dump(templates, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"保存模板列表失败: {str(e)}")
    
    def get_template(self, template_id):
        """
        获取指定模板
        
        Args:
            template_id: 模板ID
        
        Returns:
            dict: 模板配置，如果不存在返回None
        """
        templates = self.load_templates()
        for template in templates:
            if template['id'] == template_id:
                return template
        return None
    
    def get_default_template(self):
        """
        获取默认模板
        
        Returns:
            dict: 默认模板配置，如果不存在返回None
        """
        templates = self.load_templates()
        for template in templates:
            if template.get('is_default', False):
                return template
        # 如果没有默认模板，返回第一个模板
        return templates[0] if templates else None
    
    def create_template(self, name, config=None, uploaded_file=None, background_path=None):
        """
        创建新模板
        
        Args:
            name: 模板名称
            config: 模板配置字典
            uploaded_file: 上传的文件对象（Streamlit UploadedFile）
            background_path: 背景图片路径（如果使用已有文件）
        
        Returns:
            dict: 创建的模板配置
        """
        templates = self.load_templates()
        
        # 生成唯一ID
        template_id = str(uuid.uuid4())
        
        # 创建模板目录
        template_dir = os.path.join(self.templates_dir, template_id)
        os.makedirs(template_dir, exist_ok=True)
        
        # 处理背景图片
        if uploaded_file:
            background_path = self.save_template_image(uploaded_file, template_id)
        elif background_path and os.path.exists(background_path):
            # 如果提供了已有路径，复制到模板目录
            dest_path = os.path.join(template_dir, 'background.jpg')
            shutil.copy2(background_path, dest_path)
            background_path = os.path.join(template_id, 'background.jpg')
        else:
            background_path = None
        
        # 创建模板配置
        template = {
            'id': template_id,
            'name': name,
            'background_path': background_path,
            'config': config or {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'is_default': False
        }
        
        # 添加到列表
        templates.append(template)
        
        # 保存
        self.save_templates(templates)
        
        return template
    
    def update_template(self, template_id, name=None, config=None, uploaded_file=None):
        """
        更新模板
        
        Args:
            template_id: 模板ID
            name: 新名称（可选）
            config: 新配置（可选）
            uploaded_file: 新背景图片（可选）
        
        Returns:
            dict: 更新后的模板配置
        """
        templates = self.load_templates()
        
        template = None
        template_index = -1
        for i, t in enumerate(templates):
            if t['id'] == template_id:
                template = t
                template_index = i
                break
        
        if template is None:
            raise Exception(f"模板不存在: {template_id}")
        
        # 更新名称
        if name is not None:
            template['name'] = name
        
        # 更新配置
        if config is not None:
            template['config'] = config
        
        # 更新背景图片
        if uploaded_file:
            template['background_path'] = self.save_template_image(uploaded_file, template_id)
        
        # 更新更新时间
        template['updated_at'] = datetime.now().isoformat()
        
        # 保存
        templates[template_index] = template
        self.save_templates(templates)
        
        return template
    
    def delete_template(self, template_id):
        """
        删除模板
        
        Args:
            template_id: 模板ID
        
        Returns:
            bool: 是否删除成功
        """
        templates = self.load_templates()
        
        template = None
        template_index = -1
        for i, t in enumerate(templates):
            if t['id'] == template_id:
                template = t
                template_index = i
                break
        
        if template is None:
            raise Exception(f"模板不存在: {template_id}")
        
        # 检查是否为默认模板
        if template.get('is_default', False):
            raise Exception("不能删除默认模板")
        
        # 删除模板目录
        template_dir = os.path.join(self.templates_dir, template_id)
        if os.path.exists(template_dir):
            try:
                shutil.rmtree(template_dir)
            except Exception as e:
                raise Exception(f"删除模板目录失败: {str(e)}")
        
        # 从列表中删除
        templates.pop(template_index)
        
        # 保存更新后的模板列表
        try:
            self.save_templates(templates)
        except Exception as e:
            raise Exception(f"保存模板列表失败: {str(e)}")
        
        return True
    
    def set_default_template(self, template_id):
        """
        设置默认模板
        
        Args:
            template_id: 模板ID
        
        Returns:
            bool: 是否设置成功
        """
        templates = self.load_templates()
        
        # 取消所有模板的默认标记
        for template in templates:
            template['is_default'] = False
        
        # 设置新的默认模板
        for template in templates:
            if template['id'] == template_id:
                template['is_default'] = True
                break
        
        # 保存
        self.save_templates(templates)
        
        return True
    
    def save_template_image(self, uploaded_file, template_id):
        """
        保存模板背景图片
        
        Args:
            uploaded_file: Streamlit UploadedFile 对象
            template_id: 模板ID
        
        Returns:
            str: 保存后的相对路径
        """
        template_dir = os.path.join(self.templates_dir, template_id)
        os.makedirs(template_dir, exist_ok=True)
        
        dest_path = os.path.join(template_dir, 'background.jpg')
        
        # 读取上传的文件
        file_bytes = uploaded_file.read()
        
        # 打开图片
        img = Image.open(io.BytesIO(file_bytes))
        
        # 检测格式
        img_format = img.format
        
        # 如果是PNG，转换为JPG
        if img_format == 'PNG':
            # 转换为 RGB 模式（PNG 可能是 RGBA）
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # 使用 alpha 通道作为 mask
                img = background
            else:
                img = img.convert('RGB')
        
        # 保存文件
        img.save(dest_path, 'JPEG', quality=95)
        
        # 返回相对路径
        return os.path.join(template_id, 'background.jpg')
    
    def get_template_background_path(self, template):
        """
        获取模板背景图片的完整路径
        
        Args:
            template: 模板配置字典
        
        Returns:
            str: 背景图片的完整路径
        """
        background_path = template.get('background_path', '')
        if not background_path:
            return None
        
        # 如果是相对路径，拼接模板目录
        if not os.path.isabs(background_path):
            full_path = os.path.join(self.templates_dir, background_path)
        else:
            full_path = background_path
        
        return full_path if os.path.exists(full_path) else None
    
    def initialize_default_template(self, default_background_path='assets/template.jpg'):
        """
        初始化默认模板（如果不存在任何模板）
        
        Args:
            default_background_path: 默认背景图片路径
        
        Returns:
            dict: 创建的默认模板配置
        """
        templates = self.load_templates()
        
        # 如果已有模板，不创建
        if templates:
            return None
        
        # 默认配置（从 drawer.py 的默认配置复制）
        default_config = {
            'layers': {
                'template_text': {
                    'text': '喜签',
                    'color': '#FFEDB5',
                    'size': 100,
                    'y': 200,
                    'align': 'center',
                    'bold': True
                },
                'city_name': {
                    'color': '#FFEDB5',
                    'size': 120,
                    'y': 415,
                    'spacing': 35,
                    'align': 'center',
                    'bold': True
                },
                'desc': {
                    'color': '#FFEDB5',
                    'size': 50,
                    'y': 620,
                    'align': 'center',
                    'bold': True
                },
                'amount': {
                    'color': '#FFEDB5',
                    'size': 220,
                    'y': 750,
                    'align': 'center',
                    'bold': True
                },
                'unit': {
                    'color': '#FFEDB5',
                    'size': 80,
                    'y': 750,
                    'spacing_x': 20,
                    'spacing_y': 10,
                    'offset_y': 60,
                    'align': 'right_bottom',
                    'bold': True
                }
            }
        }
        
        # 创建默认模板
        template = self.create_template(
            name='默认模板',
            background_path=default_background_path if os.path.exists(default_background_path) else None,
            config=default_config
        )
        
        # 设置为默认模板
        self.set_default_template(template['id'])
        
        return template
