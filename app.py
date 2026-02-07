"""
PosterGenMaster - 企业级批量海报生成工具
使用 Streamlit 和 Pillow 实现
"""
import streamlit as st
import pandas as pd
import zipfile
import io
import os
from PIL import Image
from core.drawer import PosterDrawer
from core.template_manager import TemplateManager


# 页面配置
st.set_page_config(
    page_title="PosterGenMaster - 批量海报生成工具",
    page_icon="🏆",
    layout="wide"
)

# 页面标题
st.title("🏆 PosterGenMaster - 自动海报生成工具")

# 初始化模板管理器
if 'template_manager' not in st.session_state:
    st.session_state.template_manager = TemplateManager()

# 初始化默认模板（如果不存在）
if 'templates_initialized' not in st.session_state:
    templates = st.session_state.template_manager.load_templates()
    if not templates:
        # 创建默认模板
        default_template = st.session_state.template_manager.initialize_default_template()
        st.session_state.templates_initialized = True
    else:
        st.session_state.templates_initialized = True

# 初始化当前模板ID
if 'current_template_id' not in st.session_state:
    default_template = st.session_state.template_manager.get_default_template()
    if default_template:
        st.session_state.current_template_id = default_template['id']
    else:
        st.session_state.current_template_id = None

# 加载当前模板
current_template = None
if st.session_state.current_template_id:
    current_template = st.session_state.template_manager.get_template(st.session_state.current_template_id)

# 初始化 PosterDrawer 实例
if 'drawer' not in st.session_state or st.session_state.get('drawer_template_id') != st.session_state.current_template_id:
    if current_template:
        # 获取模板背景图的完整路径
        template_bg_path = st.session_state.template_manager.get_template_background_path(current_template)
        if template_bg_path:
            template_config = {
                'background_path': template_bg_path,
                'config': current_template.get('config', {})
            }
            st.session_state.drawer = PosterDrawer(
                template_config=template_config,
                font_path='assets/NotoSansSC-Regular.ttf',
                bold_font_path='assets/NotoSansSC-Bold.ttf'
            )
            st.session_state.drawer_template_id = st.session_state.current_template_id
        else:
            # 降级处理：使用默认路径
            st.session_state.drawer = PosterDrawer(
                background_path='assets/template.jpg',
                font_path='assets/NotoSansSC-Regular.ttf',
                bold_font_path='assets/NotoSansSC-Bold.ttf'
            )
            st.session_state.drawer_template_id = None
    else:
        # 没有模板时使用默认路径
        st.session_state.drawer = PosterDrawer(
            background_path='assets/template.jpg',
            font_path='assets/NotoSansSC-Regular.ttf',
            bold_font_path='assets/NotoSansSC-Bold.ttf'
        )
        st.session_state.drawer_template_id = None

# 侧边栏 - 模板管理
st.sidebar.header("🖼️ 模板管理")

# 加载所有模板
templates = st.session_state.template_manager.load_templates()

# 模板选择器
if templates:
    template_options = {f"{t['name']}{' (默认)' if t.get('is_default', False) else ''}": t['id'] for t in templates}
    # 确保当前模板ID在选项列表中
    if st.session_state.current_template_id not in template_options.values():
        # 如果当前模板ID不在列表中（可能被删除了），切换到第一个模板
        if templates:
            st.session_state.current_template_id = templates[0]['id']
            st.session_state.drawer_template_id = None  # 强制重新加载drawer
    
    # 计算当前选中的索引
    try:
        current_index = list(template_options.values()).index(st.session_state.current_template_id)
    except ValueError:
        current_index = 0
        if templates:
            st.session_state.current_template_id = templates[0]['id']
    
    selected_template_name = st.sidebar.selectbox(
        "选择模板",
        options=list(template_options.keys()),
        index=current_index,
        key="template_selector",  # 添加key确保删除后能刷新
        help="选择要使用的模板"
    )
    selected_template_id = template_options[selected_template_name]
    
    # 如果切换了模板，更新当前模板，并加载该模板保存的微调参数
    if selected_template_id != st.session_state.current_template_id:
        st.session_state.current_template_id = selected_template_id
        current_template = st.session_state.template_manager.get_template(selected_template_id)
        if current_template:
            template_bg_path = st.session_state.template_manager.get_template_background_path(current_template)
            if template_bg_path:
                template_config = {
                    'background_path': template_bg_path,
                    'config': current_template.get('config', {})
                }
                st.session_state.drawer = PosterDrawer(
                    template_config=template_config,
                    font_path='assets/NotoSansSC-Regular.ttf',
                    bold_font_path='assets/NotoSansSC-Bold.ttf'
                )
                st.session_state.drawer_template_id = selected_template_id
                # 清空更新模板相关的session_state，确保显示新模板的参数
                update_keys_to_clear = [
                    'update_template_image',
                    f'up_template_text_{selected_template_id}', f'up_template_text_size_{selected_template_id}', f'up_template_text_y_{selected_template_id}',
                    f'up_size_city_{selected_template_id}', f'up_size_desc_{selected_template_id}',
                    f'up_size_amount_{selected_template_id}', f'up_size_unit_{selected_template_id}',
                    f'up_y_city_{selected_template_id}', f'up_y_desc_{selected_template_id}',
                    f'up_y_amount_{selected_template_id}', f'up_offset_{selected_template_id}'
                ]
                for key in update_keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                st.sidebar.success(f"✅ 已切换到模板: {current_template['name']}")
                st.rerun()
else:
    st.sidebar.info("暂无模板，请创建第一个模板")

# 模板操作区域
st.sidebar.subheader("模板操作")

def _build_config_from_params(drawer, size_adj, y_adj, unit_offset_y_val):
    """从微调参数（调整量）构建配置"""
    return {
        'layers': {
            'city_name': {
                'color': drawer.config['layers']['city_name']['color'],
                'size': drawer.config['layers']['city_name']['size'] + size_adj['city_name'],
                'y': drawer.config['layers']['city_name']['y'] + y_adj['city_name'],
                'spacing': drawer.config['layers']['city_name'].get('spacing', 35),
                'align': 'center',
                'bold': True
            },
            'desc': {
                'color': drawer.config['layers']['desc']['color'],
                'size': drawer.config['layers']['desc']['size'] + size_adj['desc'],
                'y': drawer.config['layers']['desc']['y'] + y_adj['desc'],
                'align': 'center',
                'bold': True
            },
            'amount': {
                'color': drawer.config['layers']['amount']['color'],
                'size': drawer.config['layers']['amount']['size'] + size_adj['amount'],
                'y': drawer.config['layers']['amount']['y'] + y_adj['amount'],
                'align': 'center',
                'bold': True
            },
            'unit': {
                'color': drawer.config['layers']['unit']['color'],
                'size': drawer.config['layers']['unit']['size'] + size_adj['unit'],
                'y': drawer.config['layers']['unit']['y'],
                'spacing_x': drawer.config['layers']['unit'].get('spacing_x', 20),
                'spacing_y': drawer.config['layers']['unit'].get('spacing_y', 10),
                'offset_y': unit_offset_y_val,
                'align': 'right_bottom',
                'bold': True
            }
        }
    }

def _build_config_from_values(base_config, template_text='', template_text_size=100, template_text_y=200, city_name_size=120, city_name_y=415, desc_size=50, desc_y=620, amount_size=220, amount_y=750, unit_size=80, unit_offset_y=60):
    """从实际数值构建配置（用于更新模板时直接保存）"""
    return {
        'layers': {
            'template_text': {
                'text': template_text,
                'color': base_config['layers'].get('template_text', {}).get('color', '#FFEDB5'),
                'size': template_text_size,
                'y': template_text_y,
                'align': 'center',
                'bold': True
            },
            'city_name': {
                'color': base_config['layers']['city_name']['color'],
                'size': city_name_size,
                'y': city_name_y,
                'spacing': base_config['layers']['city_name'].get('spacing', 35),
                'align': 'center',
                'bold': True
            },
            'desc': {
                'color': base_config['layers']['desc']['color'],
                'size': desc_size,
                'y': desc_y,
                'align': 'center',
                'bold': True
            },
            'amount': {
                'color': base_config['layers']['amount']['color'],
                'size': amount_size,
                'y': amount_y,
                'align': 'center',
                'bold': True
            },
            'unit': {
                'color': base_config['layers']['unit']['color'],
                'size': unit_size,
                'y': base_config['layers']['unit']['y'],
                'spacing_x': base_config['layers']['unit'].get('spacing_x', 20),
                'spacing_y': base_config['layers']['unit'].get('spacing_y', 10),
                'offset_y': unit_offset_y,
                'align': 'right_bottom',
                'bold': True
            }
        }
    }

# 创建新模板
with st.sidebar.expander("➕ 创建新模板", expanded=False):
    new_template_name = st.text_input("模板名称", key="new_template_name", placeholder="请输入模板名称")
    new_template_image = st.file_uploader(
        "上传背景图片",
        type=['jpg', 'jpeg', 'png'],
        key="new_template_image",
        help="上传新的海报背景模板（建议尺寸：900x1600 或 1080x1920）"
    )
    
    st.markdown("**模板固定文字**")
    # 从当前drawer配置中获取基准值
    drawer_layers = st.session_state.drawer.config.get('layers', {})
    drawer_template_text = drawer_layers.get('template_text', {})
    create_template_text = st.text_input("模板文字内容", value=drawer_template_text.get('text', ''), key="create_template_text", placeholder="如：喜签嘉年华", help="模板固定显示的文字内容")
    col_template_text = st.columns(2)
    with col_template_text[0]:
        create_template_text_size = st.slider("模板文字字号", 40, 200, int(drawer_template_text.get('size', 100)), key="create_template_text_size", help=f"当前值: {drawer_template_text.get('size', 100)}")
    with col_template_text[1]:
        create_template_text_y = st.slider("模板文字Y", 50, 500, int(drawer_template_text.get('y', 200)), key="create_template_text_y", help=f"当前值: {drawer_template_text.get('y', 200)}")
    
    st.markdown("**参数微调（文字大小和位置）**")
    drawer_city = drawer_layers.get('city_name', {})
    drawer_desc = drawer_layers.get('desc', {})
    drawer_amount = drawer_layers.get('amount', {})
    drawer_unit = drawer_layers.get('unit', {})
    
    col1, col2 = st.columns(2)
    with col1:
        create_city_name_size = st.slider("城市+姓名字号", 60, 180, int(drawer_city.get('size', 120)), key="create_city_name_size", help=f"当前值: {drawer_city.get('size', 120)}")
        create_desc_size = st.slider("描述字号", 30, 100, int(drawer_desc.get('size', 50)), key="create_desc_size", help=f"当前值: {drawer_desc.get('size', 50)}")
        create_amount_size = st.slider("金额字号", 120, 320, int(drawer_amount.get('size', 220)), key="create_amount_size", help=f"当前值: {drawer_amount.get('size', 220)}")
        create_unit_size = st.slider("单位字号", 50, 120, int(drawer_unit.get('size', 80)), key="create_unit_size", help=f"当前值: {drawer_unit.get('size', 80)}")
    with col2:
        create_city_name_y = st.slider("城市+姓名Y", 200, 600, int(drawer_city.get('y', 415)), key="create_city_name_y", help=f"当前值: {drawer_city.get('y', 415)}")
        create_desc_y = st.slider("描述Y", 400, 800, int(drawer_desc.get('y', 620)), key="create_desc_y", help=f"当前值: {drawer_desc.get('y', 620)}")
        create_amount_y = st.slider("金额Y", 500, 900, int(drawer_amount.get('y', 750)), key="create_amount_y", help=f"当前值: {drawer_amount.get('y', 750)}")
        create_unit_offset_y = st.slider("单位Y偏移", -100, 150, int(drawer_unit.get('offset_y', 60)), key="create_unit_offset_y", help=f"当前值: {drawer_unit.get('offset_y', 60)}")
    
    if st.button("创建模板", key="create_template_btn"):
        if not new_template_name:
            st.error("请输入模板名称")
        elif not new_template_image:
            st.error("请上传背景图片")
        else:
            try:
                # 使用实际值构建配置，与更新模板保持一致
                base_config = st.session_state.drawer.config
                current_config = _build_config_from_values(
                    base_config, create_template_text, create_template_text_size, create_template_text_y,
                    create_city_name_size, create_city_name_y,
                    create_desc_size, create_desc_y, create_amount_size, create_amount_y,
                    create_unit_size, create_unit_offset_y
                )
                
                new_template = st.session_state.template_manager.create_template(
                    name=new_template_name,
                    config=current_config,
                    uploaded_file=new_template_image
                )
                st.success(f"✅ 模板 '{new_template_name}' 创建成功！")
                st.session_state.current_template_id = new_template['id']
                # 清空创建表单的所有内容
                keys_to_clear = [
                    'new_template_name', 'new_template_image',
                    'create_template_text', 'create_template_text_size', 'create_template_text_y',
                    'create_city_name_size', 'create_desc_size', 'create_amount_size', 'create_unit_size',
                    'create_city_name_y', 'create_desc_y', 'create_amount_y', 'create_unit_offset_y'
                ]
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                # 重新加载模板列表和当前模板
                current_template = st.session_state.template_manager.get_template(new_template['id'])
                if current_template:
                    template_bg_path = st.session_state.template_manager.get_template_background_path(current_template)
                    if template_bg_path:
                        template_config = {
                            'background_path': template_bg_path,
                            'config': current_template.get('config', {})
                        }
                        st.session_state.drawer = PosterDrawer(
                            template_config=template_config,
                            font_path='assets/NotoSansSC-Regular.ttf',
                            bold_font_path='assets/NotoSansSC-Bold.ttf'
                        )
                        st.session_state.drawer_template_id = new_template['id']
                st.rerun()
            except Exception as e:
                st.error(f"❌ 创建模板失败: {str(e)}")

# 更新当前模板
if current_template:
    with st.sidebar.expander("✏️ 更新当前模板", expanded=False):
        # 更新模板名称
        update_template_name = st.text_input(
            "模板名称",
            value=current_template.get('name', ''),
            key=f"update_template_name_{st.session_state.current_template_id}",
            help="修改模板名称"
        )
        
        update_template_image = st.file_uploader(
            "更新背景图片（可选）",
            type=['jpg', 'jpeg', 'png'],
            key="update_template_image",
            help="留空则只更新配置，不更新背景图"
        )
        
        st.markdown(f"**文字内容（前缀/后缀）**")
        layers = current_template.get('config', {}).get('layers', {})
        city_cfg = layers.get('city_name', {})
        desc_cfg = layers.get('desc', {})
        amount_cfg = layers.get('amount', {})
        unit_cfg = layers.get('unit', {})
        # 使用模板ID作为key后缀，确保切换模板时显示各自参数
        tid = st.session_state.current_template_id
        
        st.markdown(f"**模板固定文字**")
        template_text_cfg = layers.get('template_text', {})
        tid = st.session_state.current_template_id
        update_template_text = st.text_input("模板文字内容", value=template_text_cfg.get('text', ''), key=f"up_template_text_{tid}", placeholder="如：喜签嘉年华", help="模板固定显示的文字内容")
        col_template_text = st.columns(2)
        with col_template_text[0]:
            template_text_size_val = int(template_text_cfg.get('size', 100))
            update_template_text_size = st.slider("模板文字字号", 40, 200, template_text_size_val, key=f"up_template_text_size_{tid}", help=f"当前值: {template_text_size_val}")
        with col_template_text[1]:
            template_text_y_val = int(template_text_cfg.get('y', 200))
            update_template_text_y = st.slider("模板文字Y", 50, 500, template_text_y_val, key=f"up_template_text_y_{tid}", help=f"当前值: {template_text_y_val}")
        
        st.markdown(f"**参数微调（文字大小和位置）**")
        # 从模板配置中读取当前值
        city_size_val = int(city_cfg.get('size', 120))
        city_y_val = int(city_cfg.get('y', 415))
        desc_size_val = int(desc_cfg.get('size', 50))
        desc_y_val = int(desc_cfg.get('y', 620))
        amount_size_val = int(amount_cfg.get('size', 220))
        amount_y_val = int(amount_cfg.get('y', 750))
        unit_size_val = int(unit_cfg.get('size', 80))
        unit_offset_val = int(unit_cfg.get('offset_y', 60))
        
        col1, col2 = st.columns(2)
        with col1:
            update_city_name_size = st.slider("城市+姓名字号", 60, 180, city_size_val, key=f"up_size_city_{tid}", help=f"当前值: {city_size_val}")
            update_desc_size = st.slider("描述字号", 30, 100, desc_size_val, key=f"up_size_desc_{tid}", help=f"当前值: {desc_size_val}")
            update_amount_size = st.slider("金额字号", 120, 320, amount_size_val, key=f"up_size_amount_{tid}", help=f"当前值: {amount_size_val}")
            update_unit_size = st.slider("单位字号", 50, 120, unit_size_val, key=f"up_size_unit_{tid}", help=f"当前值: {unit_size_val}")
        with col2:
            update_city_name_y = st.slider("城市+姓名Y", 200, 600, city_y_val, key=f"up_y_city_{tid}", help=f"当前值: {city_y_val}")
            update_desc_y = st.slider("描述Y", 400, 800, desc_y_val, key=f"up_y_desc_{tid}", help=f"当前值: {desc_y_val}")
            update_amount_y = st.slider("金额Y", 500, 900, amount_y_val, key=f"up_y_amount_{tid}", help=f"当前值: {amount_y_val}")
            update_unit_offset_y = st.slider("单位Y偏移", -100, 150, unit_offset_val, key=f"up_offset_{tid}", help=f"当前值: {unit_offset_val}")
        
        if st.button("保存当前配置", key="update_template_btn"):
            try:
                base = current_template.get('config') or st.session_state.drawer.config
                if 'layers' not in base:
                    base = st.session_state.drawer.config
                current_config = _build_config_from_values(
                    base, update_template_text, update_template_text_size, update_template_text_y,
                    update_city_name_size, update_city_name_y,
                    update_desc_size, update_desc_y, update_amount_size, update_amount_y,
                    update_unit_size, update_unit_offset_y
                )
                
                update_kwargs = {'config': current_config}
                
                # 如果模板名称有变化，更新名称
                if update_template_name and update_template_name.strip() != current_template.get('name', ''):
                    update_kwargs['name'] = update_template_name.strip()
                
                if update_template_image:
                    update_kwargs['uploaded_file'] = update_template_image
                
                updated_template = st.session_state.template_manager.update_template(
                    st.session_state.current_template_id,
                    **update_kwargs
                )
                
                # 如果名称已更新，显示提示
                if 'name' in update_kwargs:
                    st.success(f"✅ 模板已更新！名称: '{updated_template['name']}'")
                else:
                    st.success(f"✅ 模板 '{updated_template['name']}' 已更新！")
                
                # 如果名称改变了，需要刷新模板选择器
                if 'name' in update_kwargs:
                    if 'template_selector' in st.session_state:
                        del st.session_state['template_selector']
                
                st.rerun()
            except Exception as e:
                st.error(f"❌ 更新模板失败: {str(e)}")
    
    # 删除模板
    templates_count = len(templates)
    if not current_template.get('is_default', False):
        if templates_count > 1:
            # 使用确认对话框
            if 'confirm_delete' not in st.session_state:
                st.session_state.confirm_delete = False
            
            if not st.session_state.confirm_delete:
                if st.sidebar.button("🗑️ 删除当前模板", key="delete_template_btn", type="secondary"):
                    st.session_state.confirm_delete = True
                    st.rerun()
            else:
                st.sidebar.warning(f"⚠️ 确认删除模板 '{current_template.get('name', '未知')}'？")
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    if st.button("✅ 确认删除", key="confirm_delete_btn", type="primary"):
                        try:
                            deleted_template_id = st.session_state.current_template_id
                            deleted_template_name = current_template.get('name', '未知')
                            
                            # 执行删除操作
                            result = st.session_state.template_manager.delete_template(deleted_template_id)
                            
                            if result:
                                st.session_state.confirm_delete = False
                                st.sidebar.success(f"✅ 模板 '{deleted_template_name}' 已删除")
                                
                                # 重新加载模板列表（确保获取最新数据）
                                templates = st.session_state.template_manager.load_templates()
                                
                                # 切换到默认模板或其他模板
                                default_template = st.session_state.template_manager.get_default_template()
                                if default_template:
                                    st.session_state.current_template_id = default_template['id']
                                    # 重新加载drawer
                                    template_bg_path = st.session_state.template_manager.get_template_background_path(default_template)
                                    if template_bg_path:
                                        template_config = {
                                            'background_path': template_bg_path,
                                            'config': default_template.get('config', {})
                                        }
                                        st.session_state.drawer = PosterDrawer(
                                            template_config=template_config,
                                            font_path='assets/NotoSansSC-Regular.ttf',
                                            bold_font_path='assets/NotoSansSC-Bold.ttf'
                                        )
                                        st.session_state.drawer_template_id = default_template['id']
                                else:
                                    # 如果没有默认模板，选择第一个模板
                                    remaining_templates = st.session_state.template_manager.load_templates()
                                    if remaining_templates:
                                        st.session_state.current_template_id = remaining_templates[0]['id']
                                        remaining_template = remaining_templates[0]
                                        template_bg_path = st.session_state.template_manager.get_template_background_path(remaining_template)
                                        if template_bg_path:
                                            template_config = {
                                                'background_path': template_bg_path,
                                                'config': remaining_template.get('config', {})
                                            }
                                            st.session_state.drawer = PosterDrawer(
                                                template_config=template_config,
                                                font_path='assets/NotoSansSC-Regular.ttf',
                                                bold_font_path='assets/NotoSansSC-Bold.ttf'
                                            )
                                            st.session_state.drawer_template_id = remaining_template['id']
                                    else:
                                        st.session_state.current_template_id = None
                                        st.session_state.drawer_template_id = None
                                # 清空模板选择器的session_state，强制刷新
                                if 'template_selector' in st.session_state:
                                    del st.session_state['template_selector']
                                st.rerun()
                            else:
                                st.session_state.confirm_delete = False
                                st.sidebar.error(f"❌ 删除模板失败：未找到模板")
                        except Exception as e:
                            st.session_state.confirm_delete = False
                            st.sidebar.error(f"❌ 删除模板失败: {str(e)}")
                            import traceback
                            st.sidebar.exception(e)
                with col2:
                    if st.button("❌ 取消", key="cancel_delete_btn"):
                        st.session_state.confirm_delete = False
                        st.rerun()
        else:
            st.sidebar.info("⚠️ 至少需要保留一个模板，无法删除")
    elif current_template.get('is_default', False) and templates_count > 1:
        st.sidebar.info("💡 提示：默认模板无法删除，请先设置其他模板为默认模板")
    
    # 设为默认模板
    if not current_template.get('is_default', False):
        if st.sidebar.button("⭐ 设为默认模板", key="set_default_template_btn"):
            try:
                st.session_state.template_manager.set_default_template(st.session_state.current_template_id)
                st.sidebar.success("✅ 已设为默认模板")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"❌ 设置失败: {str(e)}")

# 显示当前模板预览
if current_template:
    template_bg_path = st.session_state.template_manager.get_template_background_path(current_template)
    if template_bg_path and os.path.exists(template_bg_path):
        try:
            preview_img = Image.open(template_bg_path)
            st.sidebar.subheader("模板预览")
            st.sidebar.info(f"模板: {current_template['name']}\n尺寸: {preview_img.size[0]}x{preview_img.size[1]}")
            st.sidebar.image(preview_img, caption="当前模板", use_container_width=True)
        except Exception as e:
            st.sidebar.warning(f"无法加载模板预览: {str(e)}")

st.sidebar.divider()

# 生成海报时使用当前模板的配置（参数微调在创建/更新模板时设置并保存）
if current_template:
    dynamic_config = current_template.get('config', {})
else:
    dynamic_config = st.session_state.drawer.config

# 主区域
st.header("📤 数据输入")

# 创建两个标签页：文件上传和文本输入
tab1, tab2 = st.tabs(["📁 CSV 文件上传", "✏️ 文本输入"])

# 初始化 session state
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []
if 'zip_buffer' not in st.session_state:
    st.session_state.zip_buffer = None

# 用于存储处理后的数据
df = None

# 标签页1：CSV文件上传
with tab1:
    uploaded_file = st.file_uploader(
        "请上传 CSV 文件 (.csv)",
        type=['csv'],
        help="CSV 文件应包含以下列：分公司、业务员姓名、预收规保、缴费期间"
    )
    
    if uploaded_file is not None:
        try:
            # 读取 CSV 文件（支持多种分隔符和编码）
            # Streamlit 文件对象需要特殊处理
            df = None
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig', 'latin1']
            # 优先尝试制表符（根据用户提供的列名，很可能是制表符分隔）
            separators = ['\t', ',', ';', None]  # None 表示让 pandas 自动检测
            last_error = None
            
            # 尝试不同的分隔符和编码组合
            for sep in separators:
                for encoding in encodings:
                    try:
                        uploaded_file.seek(0)  # 重置文件指针
                        
                        # 构建 read_csv 参数
                        read_params = {
                            'encoding': encoding,
                            'on_bad_lines': 'skip',
                            'engine': 'python'  # 使用 python 引擎更兼容
                        }
                        if sep is not None:
                            read_params['sep'] = sep
                        
                        df = pd.read_csv(uploaded_file, **read_params)
                        
                        # 检查是否成功读取到数据，且列数大于1（避免只有1列的情况）
                        if df is not None and len(df.columns) > 1:
                            break
                    except Exception as e:
                        last_error = str(e)
                        continue
                
                # 如果成功读取且列数大于1，跳出外层循环
                if df is not None and len(df.columns) > 1:
                    break
            
            if df is None or len(df.columns) == 0:
                error_msg = "无法读取 CSV 文件。"
                if last_error:
                    error_msg += f" 错误信息: {last_error}"
                error_msg += "\n\n请检查：\n1. 文件是否为有效的 CSV 格式\n2. 文件编码（建议使用 UTF-8 或 GBK）\n3. 文件是否包含表头行\n4. 文件分隔符（支持制表符、逗号、分号）"
                raise ValueError(error_msg)
            
            # 如果只有 1 列，可能是分隔符检测失败，尝试重新解析
            if len(df.columns) == 1:
                first_col_name = str(df.columns[0])
                # 检查第一列名是否包含多个字段（用制表符或逗号分隔）
                if '\t' in first_col_name:
                    # 重新读取，强制使用制表符分隔
                    for encoding in encodings:
                        try:
                            uploaded_file.seek(0)
                            df = pd.read_csv(uploaded_file, sep='\t', encoding=encoding, on_bad_lines='skip', engine='python')
                            if len(df.columns) > 1:
                                break
                        except:
                            continue
                elif ',' in first_col_name:
                    # 重新读取，强制使用逗号分隔
                    for encoding in encodings:
                        try:
                            uploaded_file.seek(0)
                            df = pd.read_csv(uploaded_file, sep=',', encoding=encoding, on_bad_lines='skip', engine='python')
                            if len(df.columns) > 1:
                                break
                        except:
                            continue
            
            # 显示读取到的列名（用于调试）
            st.info(f"📋 成功读取文件，共 {len(df.columns)} 列，{len(df)} 行数据。列名: {', '.join(df.columns.tolist()[:10])}{'...' if len(df.columns) > 10 else ''}")
            
            # 检查必需的列
            required_columns = ['分公司', '业务员姓名', '预收规保', '缴费期间']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ CSV 文件缺少必需的列: {', '.join(missing_columns)}")
                st.info("请确保 CSV 文件包含以下列：分公司、业务员姓名、预收规保、缴费期间")
                df = None
            else:
                # 数据转换和过滤
                # 1. 将预收规保（元）转换为万元，并过滤小于10万元的记录
                df['预收规保_万元'] = pd.to_numeric(df['预收规保'], errors='coerce') / 10000
                df = df[df['预收规保_万元'] >= 10].copy()
                
                if len(df) == 0:
                    st.warning("⚠️ 没有符合条件的记录（所有记录的预收规保都小于10万元）")
                    df = None
                else:
                    # 2. 生成描述字段
                    def generate_desc(row):
                        payment_period = pd.to_numeric(row['缴费期间'], errors='coerce')
                        if pd.isna(payment_period) or payment_period == 0:
                            return "喜签趸交保单"
                        else:
                            return f"喜签{int(payment_period)}年期保单"
                    
                    df['描述'] = df.apply(generate_desc, axis=1)
                    
                    # 3. 字段映射：转换为绘制器需要的格式
                    df['城市'] = df['分公司'].astype(str)
                    df['姓名'] = df['业务员姓名'].astype(str)
                    df['金额'] = df['预收规保_万元'].apply(lambda x: str(int(x)))
                    df['单位'] = '万'
                    
                    # 4. 按规保金额从大到小排序
                    df = df.sort_values('预收规保_万元', ascending=False).reset_index(drop=True)
        
        except Exception as e:
            st.error(f"❌ 读取 CSV 文件时出错: {str(e)}")
            st.info("请确保上传的是有效的 .csv 文件")
            df = None

# 标签页2：文本输入
with tab2:
    st.markdown("""
    **输入格式说明：**
    - 每行一条记录
    - 格式：`城市 姓名 金额 缴费期间`
    - 示例：
      - `湖北 朱玉珍 20万 趸交`
      - `广东 罗天颖 20万x6年`
      - `深圳 白利丹 100万 趸交`
    """)
    
    text_input = st.text_area(
        "请输入数据（每行一条记录）",
        height=200,
        help="每行格式：城市 姓名 金额 缴费期间（如：湖北 朱玉珍 20万 趸交 或 广东 罗天颖 20万x6年）"
    )
    
    if text_input and text_input.strip():
        try:
            # 解析文本输入
            lines = [line.strip() for line in text_input.strip().split('\n') if line.strip()]
            parsed_data = []
            
            import re
            for line in lines:
                # 解析每一行
                parts = line.split()
                if len(parts) < 3:
                    continue
                
                city = parts[0]
                name = parts[1]
                
                # 解析金额和缴费期间（可能在同一字段，如"20万x6年"）
                amount_str = parts[2]
                payment_period = 0
                
                # 检查金额字段是否包含缴费期间信息（格式：20万x6年）
                if 'x' in amount_str or 'X' in amount_str:
                    # 提取金额（去掉"万"和"x年"部分）
                    amount_match = re.search(r'(\d+(?:\.\d+)?)', amount_str)
                    if amount_match:
                        try:
                            amount = float(amount_match.group(1))
                        except:
                            continue
                    # 提取缴费期间（x后面的数字）
                    period_match = re.search(r'[xX](\d+)年', amount_str)
                    if period_match:
                        payment_period = int(period_match.group(1))
                else:
                    # 普通格式：只包含金额
                    amount_str_clean = amount_str.replace('万', '').strip()
                    try:
                        amount = float(amount_str_clean)
                    except:
                        continue
                    
                    # 如果有第四个字段，解析缴费期间
                    if len(parts) >= 4:
                        # 格式1：趸交
                        if '趸交' in parts[3]:
                            payment_period = 0
                        # 格式2：x年 或 x年期
                        elif '年' in parts[3]:
                            period_match = re.search(r'(\d+)', parts[3])
                            if period_match:
                                payment_period = int(period_match.group(1))
                
                # 检查金额是否大于等于10万
                if amount >= 10:
                    parsed_data.append({
                        '城市': city,
                        '姓名': name,
                        '金额': str(int(amount)),
                        '单位': '万',
                        '缴费期间': payment_period,
                        '描述': "喜签趸交保单" if payment_period == 0 else f"喜签{payment_period}年期保单"
                    })
            
            if parsed_data:
                df = pd.DataFrame(parsed_data)
                # 按规保金额从大到小排序（将金额字符串转换为数值后排序）
                df['金额_数值'] = pd.to_numeric(df['金额'], errors='coerce')
                df = df.sort_values('金额_数值', ascending=False).reset_index(drop=True)
                df = df.drop('金额_数值', axis=1)  # 删除临时列
                st.success(f"✅ 成功解析 {len(df)} 条数据")
            else:
                st.warning("⚠️ 未能解析出有效数据，请检查输入格式")
                df = None
                
        except Exception as e:
            st.error(f"❌ 解析文本时出错: {str(e)}")
            df = None

# 统一的数据预览和生成逻辑
if df is not None and len(df) > 0:
    # 数据预览
    st.subheader("📊 数据预览（全部待生成海报）")
    # 显示转换后的关键字段（全部数据）
    preview_df = df[['城市', '姓名', '描述', '金额', '单位']]
    st.dataframe(preview_df, use_container_width=True)
    
    st.info(f"✅ 共读取 {len(df)} 条有效数据")
    
    # 生成按钮
    if st.button("🚀 开始生成", type="primary", use_container_width=True):
        # 清空之前的结果
        st.session_state.generated_images = []
        
        # 创建进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 生成所有海报
        # 使用 enumerate 获取从 0 开始的连续索引，避免使用 DataFrame 的原始索引
        for current_idx, (original_idx, row) in enumerate(df.iterrows()):
            try:
                # 使用 PosterDrawer 绘制海报
                poster_image = st.session_state.drawer.draw(row, dynamic_config)
                
                # 保存到 session state
                img_buffer = io.BytesIO()
                poster_image.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                # 生成文件名：城市-姓名-金额万-缴费期间年期-保单（或趸交）
                # 清理文件名中的特殊字符（Windows 和 Unix 系统不支持的字符）
                def clean_filename(text):
                    if pd.isna(text):
                        return ""
                    # 替换不支持的字符为下划线
                    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\n', '\r', '\t']
                    text = str(text).strip()
                    for char in invalid_chars:
                        text = text.replace(char, '_')
                    return text
                
                city = clean_filename(row.get('城市', ''))
                name = clean_filename(row.get('姓名', ''))
                amount = clean_filename(row.get('金额', ''))
                
                # 处理缴费期间：如果为0显示"趸交"，否则显示"{缴费期间}年期"
                payment_period_raw = row.get('缴费期间', 0)
                try:
                    payment_period_num = pd.to_numeric(payment_period_raw, errors='coerce')
                    if pd.isna(payment_period_num) or payment_period_num == 0:
                        payment_period_str = "趸交"
                    else:
                        payment_period_str = f"{int(payment_period_num)}年期"
                except:
                    payment_period_str = "趸交"
                
                # 组合文件名：城市-姓名-金额万-缴费期间-保单
                filename = f"{city}-{name}-{amount}万-{payment_period_str}-保单.png"
                
                st.session_state.generated_images.append({
                    'image': poster_image,
                    'buffer': img_buffer,
                    'filename': filename
                })
                
                # 更新进度（使用连续索引计算，确保值在 0.0 到 1.0 之间）
                progress = (current_idx + 1) / len(df)
                # 确保进度值不超过 1.0
                progress = min(progress, 1.0)
                progress_bar.progress(progress)
                status_text.text(f"正在生成第 {current_idx + 1}/{len(df)} 张海报...")
                
            except FileNotFoundError as e:
                st.error(f"❌ {str(e)}")
                break
            except Exception as e:
                st.warning(f"⚠️ 第 {current_idx + 1} 行数据生成失败: {str(e)}")
                continue
        
        # 完成提示
        if st.session_state.generated_images:
            progress_bar.progress(1.0)
            status_text.text(f"✅ 成功生成 {len(st.session_state.generated_images)} 张海报！")
            
            # 创建 ZIP 压缩包
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for item in st.session_state.generated_images:
                    zip_file.writestr(
                        item['filename'],
                        item['buffer'].getvalue()
                    )
            zip_buffer.seek(0)
            st.session_state.zip_buffer = zip_buffer
            
            st.success("🎉 所有海报生成完成！")
            
            # 显示生成结果
            if st.session_state.generated_images:
                st.divider()
                st.header("📸 生成结果")
                
                # 预览第一张图片
                st.subheader("预览（第1张海报）")
                preview_image = st.session_state.generated_images[0]['image']
                st.image(preview_image, use_container_width=True, caption="预览图")
                
                # 下载按钮
                st.subheader("📥 下载")
                if st.session_state.zip_buffer:
                    st.download_button(
                        label="⬇️ 下载所有海报 (.zip)",
                        data=st.session_state.zip_buffer.getvalue(),
                        file_name="posters.zip",
                        mime="application/zip",
                        type="primary",
                        use_container_width=True
                    )
                
                # 显示所有生成的文件名
                st.subheader("📋 生成的文件列表")
                file_list = [item['filename'] for item in st.session_state.generated_images]
                st.write(f"共 {len(file_list)} 个文件：")
                for filename in file_list:
                    st.write(f"- {filename}")
    
elif df is None:
    st.info("👆 请上传 CSV 文件或输入文本数据开始使用")

# 页脚说明
st.divider()
st.markdown("""
### 📝 使用说明

1. **准备文件**：
   - 确保在 `assets/` 目录下放置 `template.jpg` 底图文件
   - 确保在 `assets/` 目录下放置 `NotoSansSC-Regular.ttf` 和 `NotoSansSC-Bold.ttf` 字体文件
   - 准备包含以下列的 CSV 文件：`分公司`、`业务员姓名`、`预收规保`、`缴费期间`

2. **上传数据**：
   - 点击上传按钮，选择你的 CSV 文件
   - 系统会自动预览全部待生成海报的数据
   - 系统会自动过滤预收规保小于10万元的记录

3. **数据转换规则**：
   - `分公司` → 作为城市显示
   - `业务员姓名` → 作为姓名显示
   - `预收规保`（元）→ 转换为万元，小于10万元的记录会被过滤
   - `缴费期间` → 生成描述：
     - 当为 0 时，显示"喜签趸交保单"
     - 当不为 0 时，显示"喜签x 年期保单"（x 为缴费期间数字）
   - 金额只取整数部分，单位固定为"万"

4. **调整参数**（可选）：
   - 使用左侧边栏的滑块微调字体大小和位置

5. **生成海报**：
   - 点击"开始生成"按钮
   - 等待生成完成
   - 城市和姓名会显示在同一行（粗体），金额和单位也会使用粗体显示

6. **下载结果**：
   - 预览第一张生成的海报
   - 点击"下载所有海报"按钮获取 ZIP 压缩包
""")
