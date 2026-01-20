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
                            return "喜签嘉年华趸交保单"
                        else:
                            return f"喜签嘉年华{int(payment_period)}年期保单"
                    
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
                        '描述': "喜签嘉年华趸交保单" if payment_period == 0 else f"喜签嘉年华{payment_period}年期保单"
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
     - 当为 0 时，显示"喜签嘉年华趸交保单"
     - 当不为 0 时，显示"喜签嘉年华x 年期保单"（x 为缴费期间数字）
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
