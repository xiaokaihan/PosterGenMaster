"""
PosterGenMaster - 企业级批量海报生成工具
使用 Streamlit 和 Pillow 实现
"""
import streamlit as st
import pandas as pd
import zipfile
import io
from core.drawer import PosterDrawer


# 页面配置
st.set_page_config(
    page_title="PosterGenMaster - 批量海报生成工具",
    page_icon="🏆",
    layout="wide"
)

# 页面标题
st.title("🏆 PosterGenMaster - 自动海报生成工具")

# 初始化 PosterDrawer 实例
if 'drawer' not in st.session_state:
    st.session_state.drawer = PosterDrawer(
        background_path='assets/template.jpg',
        font_path='assets/NotoSansSC-Regular.ttf',
        bold_font_path='assets/NotoSansSC-Bold.ttf'
    )

# 侧边栏 - 参数微调
st.sidebar.header("⚙️ 参数微调")

# 字体大小微调滑块
st.sidebar.subheader("字体大小调整")
city_name_size_adjust = st.sidebar.slider("城市+姓名字号", -20, 20, 0, help="调整城市和姓名字体大小")
desc_size_adjust = st.sidebar.slider("描述字号", -20, 20, 0, help="调整描述字体大小")
amount_size_adjust = st.sidebar.slider("金额字号", -50, 50, 0, help="调整金额字体大小")
unit_size_adjust = st.sidebar.slider("单位字号", -20, 20, 0, help="调整单位字体大小")

# 垂直位置微调滑块
st.sidebar.subheader("垂直位置调整")
city_name_y_adjust = st.sidebar.slider("城市+姓名Y坐标", -50, 50, 0, help="调整城市和姓名垂直位置")
desc_y_adjust = st.sidebar.slider("描述Y坐标", -50, 50, 0, help="调整描述垂直位置")
amount_y_adjust = st.sidebar.slider("金额Y坐标", -50, 50, 0, help="调整金额垂直位置")
unit_offset_y = st.sidebar.slider("单位Y偏移", -100, 100, 60, help="调整单位垂直位置（正值往下，负值往上）")

# 应用微调后的配置
dynamic_config = {
    'layers': {
        'city_name': {
            'color': st.session_state.drawer.config['layers']['city_name']['color'],
            'size': st.session_state.drawer.config['layers']['city_name']['size'] + city_name_size_adjust,
            'y': st.session_state.drawer.config['layers']['city_name']['y'] + city_name_y_adjust,
            'spacing': st.session_state.drawer.config['layers']['city_name'].get('spacing', 20),
            'align': 'center',
            'bold': True
        },
        'desc': {
            'color': st.session_state.drawer.config['layers']['desc']['color'],
            'size': st.session_state.drawer.config['layers']['desc']['size'] + desc_size_adjust,
            'y': st.session_state.drawer.config['layers']['desc']['y'] + desc_y_adjust,
            'align': 'center',
            'bold': True  # 使用粗体
        },
        'amount': {
            'color': st.session_state.drawer.config['layers']['amount']['color'],
            'size': st.session_state.drawer.config['layers']['amount']['size'] + amount_size_adjust,
            'y': st.session_state.drawer.config['layers']['amount']['y'] + amount_y_adjust,
            'align': 'center',
            'bold': True
        },
        'unit': {
            'color': st.session_state.drawer.config['layers']['unit']['color'],
            'size': st.session_state.drawer.config['layers']['unit']['size'] + unit_size_adjust,
            'y': st.session_state.drawer.config['layers']['unit']['y'],
            'spacing_x': st.session_state.drawer.config['layers']['unit'].get('spacing_x', 20),
            'spacing_y': st.session_state.drawer.config['layers']['unit'].get('spacing_y', 10),
            'offset_y': unit_offset_y,  # 单位Y坐标偏移量
            'align': 'right_bottom',
            'bold': True
        }
    }
}

# 主区域
st.header("📤 文件上传")

# 文件上传器
uploaded_file = st.file_uploader(
    "请上传 Excel 文件 (.xlsx)",
    type=['xlsx'],
    help="Excel 文件应包含以下列：城市、姓名、描述、金额、单位、文件名（可选）"
)

# 初始化 session state
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []
if 'zip_buffer' not in st.session_state:
    st.session_state.zip_buffer = None

if uploaded_file is not None:
    try:
        # 读取 Excel 文件
        df = pd.read_excel(uploaded_file)
        
        # 检查必需的列
        required_columns = ['城市', '姓名', '描述', '金额', '单位']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"❌ Excel 文件缺少必需的列: {', '.join(missing_columns)}")
            st.info("请确保 Excel 文件包含以下列：城市、姓名、描述、金额、单位、文件名（可选）")
        else:
            # 数据预览
            st.subheader("📊 数据预览（前5行）")
            st.dataframe(df.head(5), use_container_width=True)
            
            st.info(f"✅ 共读取 {len(df)} 条数据")
            
            # 生成按钮
            if st.button("🚀 开始生成", type="primary", use_container_width=True):
                # 清空之前的结果
                st.session_state.generated_images = []
                
                # 创建进度条
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 生成所有海报
                for idx, row in df.iterrows():
                    try:
                        # 使用 PosterDrawer 绘制海报
                        poster_image = st.session_state.drawer.draw(row, dynamic_config)
                        
                        # 保存到 session state
                        img_buffer = io.BytesIO()
                        poster_image.save(img_buffer, format='PNG')
                        img_buffer.seek(0)
                        
                        # 获取文件名（如果有文件名列则使用，否则使用序号）
                        if '文件名' in df.columns and pd.notna(row.get('文件名')):
                            filename = str(row['文件名']).strip()
                            # 确保文件名有扩展名
                            if not filename.endswith('.png'):
                                filename += '.png'
                        else:
                            filename = f"poster_{idx + 1:04d}.png"
                        
                        st.session_state.generated_images.append({
                            'image': poster_image,
                            'buffer': img_buffer,
                            'filename': filename
                        })
                        
                        # 更新进度
                        progress = (idx + 1) / len(df)
                        progress_bar.progress(progress)
                        status_text.text(f"正在生成第 {idx + 1}/{len(df)} 张海报...")
                        
                    except FileNotFoundError as e:
                        st.error(f"❌ {str(e)}")
                        break
                    except Exception as e:
                        st.warning(f"⚠️ 第 {idx + 1} 行数据生成失败: {str(e)}")
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
    
    except Exception as e:
        st.error(f"❌ 读取 Excel 文件时出错: {str(e)}")
        st.info("请确保上传的是有效的 .xlsx 文件")

else:
    st.info("👆 请先上传 Excel 文件开始使用")

# 页脚说明
st.divider()
st.markdown("""
### 📝 使用说明

1. **准备文件**：
   - 确保在 `assets/` 目录下放置 `template.jpg` 底图文件
   - 确保在 `assets/` 目录下放置 `NotoSansSC-Regular.ttf` 和 `NotoSansSC-Bold.ttf` 字体文件
   - 准备包含以下列的 Excel 文件：`城市`、`姓名`、`描述`、`金额`、`单位`、`文件名`（可选）

2. **上传数据**：
   - 点击上传按钮，选择你的 Excel 文件
   - 系统会自动预览前5行数据

3. **调整参数**（可选）：
   - 使用左侧边栏的滑块微调字体大小和位置

4. **生成海报**：
   - 点击"开始生成"按钮
   - 等待生成完成
   - 城市和姓名会显示在同一行（粗体），金额和单位也会使用粗体显示

5. **下载结果**：
   - 预览第一张生成的海报
   - 点击"下载所有海报"按钮获取 ZIP 压缩包

### 🛠️ 技术栈
- **Python 3.10+**
- **Streamlit** - Web 界面框架
- **Pillow (PIL)** - 图像处理
- **Pandas** - 数据处理
- **openpyxl** - Excel 文件读取
""")
