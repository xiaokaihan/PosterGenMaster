# PosterGenMaster

🏆 **企业级批量海报生成工具**

PosterGenMaster 是一个基于 Python 和 Streamlit 的批量海报生成工具，可以读取 Excel 数据，结合背景底图，自动绘制文字，并打包下载为 ZIP 文件。

## 📋 项目总结

PosterGenMaster 是一个专为企业批量生成海报而设计的 Web 应用工具。通过简单的 Excel 数据输入，即可快速生成大量个性化的海报图片。

**核心特点：**
- 🚀 **快速批量生成**: 一次处理数百条数据，自动生成对应数量的海报
- 🎨 **灵活配置**: 支持实时调整字体大小、位置等参数，无需修改代码
- 📊 **数据驱动**: 通过 Excel 文件管理数据，易于维护和更新
- 🎯 **智能布局**: 自动处理文字居中、对齐等布局问题
- 💾 **一键下载**: 自动打包所有生成的海报为 ZIP 文件，方便分发

**适用场景：**
- 企业表彰海报批量生成
- 销售业绩展示海报制作
- 活动宣传海报批量制作
- 证书、奖状等批量生成

## ✨ 核心功能

- 📊 **Excel 数据读取**: 支持从 Excel 文件批量读取数据（城市、姓名、描述、金额、单位等）
- 🎨 **背景底图**: 支持自定义背景底图
- ✍️ **文字绘制**: 自动在底图上绘制城市+姓名（同一行）、描述、金额、单位等信息，所有文字使用粗体显示
- ⚙️ **参数微调**: 通过 Web 界面实时调整字体大小和位置
- 📦 **批量打包**: 自动将所有生成的海报打包为 ZIP 文件下载
- 🎯 **智能布局**: 城市和姓名自动居中显示在同一行，金额和单位智能对齐

## 🛠️ 技术栈

- **Python 3.10+**
- **Streamlit** - Web 界面框架
- **Pillow (PIL)** - 图像处理
- **Pandas** - 数据处理
- **openpyxl** - Excel 文件读取

## 📁 项目结构

```
PosterGenMaster/
├── app.py              # Streamlit 主入口
├── core/
│   ├── __init__.py
│   └── drawer.py       # 图片绘制核心逻辑 (PosterDrawer class)
├── utils.py            # 工具函数模块（可选）
├── assets/
│   ├── template.jpg    # 默认底图（必需）
│   ├── NotoSansSC-Regular.ttf    # 默认字体（必需）
│   ├── NotoSansSC-Bold.ttf       # 粗体字体（必需）
│   ├── demo.jpg        # 示例图片（可选）
│   └── test-data.xlsx  # 测试数据（可选）
├── requirements.txt    # 依赖包
├── run.sh              # 启动脚本（可选）
└── README.md           # 项目说明
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备资源文件

在 `assets/` 目录下放置以下文件：

- **template.jpg**: 海报背景底图（必需）
- **NotoSansSC-Regular.ttf**: 常规字体文件（必需，如不存在将使用系统默认字体）
- **NotoSansSC-Bold.ttf**: 粗体字体文件（必需，用于显示粗体文字）

### 3. 准备 Excel 数据文件

Excel 文件应包含以下列：

| 列名 | 说明 | 必需 |
|------|------|------|
| 城市 | 城市名称，与姓名显示在同一行 | ✅ |
| 姓名 | 要显示在海报上的姓名 | ✅ |
| 描述 | 描述文字 | ✅ |
| 金额 | 金额数字 | ✅ |
| 单位 | 金额单位（如：元、万元） | ✅ |
| 文件名 | 生成的文件名（不含扩展名） | ❌ |

**示例 Excel 数据：**

| 城市 | 姓名 | 描述 | 金额 | 单位 | 文件名 |
|------|------|------|------|------|--------|
| 北京 | 张三 | 销售冠军 | 100000 | 元 | zhang_san |
| 上海 | 李四 | 业绩突出 | 50000 | 元 | li_si |

### 4. 运行应用

**方式一：使用启动脚本（推荐）**
```bash
chmod +x run.sh
./run.sh
```

**方式二：直接运行 Streamlit**
```bash
streamlit run app.py
```

**方式三：使用 Python 模块方式**
```bash
python3 -m streamlit run app.py
```

应用将在浏览器中自动打开，默认地址：`http://localhost:8501`

### 5. 使用步骤

1. **上传 Excel 文件**: 点击上传按钮，选择你的 Excel 文件（必须包含：城市、姓名、描述、金额、单位列）
2. **预览数据**: 系统会自动显示前5行数据预览
3. **调整参数**（可选）: 使用左侧边栏的滑块微调字体大小和位置
   - 字体大小调整：城市+姓名字号、描述字号、金额字号、单位字号
   - 垂直位置调整：城市+姓名Y坐标、描述Y坐标、金额Y坐标、单位Y偏移
4. **生成海报**: 点击"开始生成"按钮，系统会显示生成进度
5. **下载结果**: 预览第一张生成的海报，点击"下载所有海报"按钮获取 ZIP 压缩包

## 📝 配置说明

### 默认配置

海报绘制器使用以下默认配置（所有文字使用粗体显示）：

- **城市+姓名**: 浅金色 (#FFEDB5)，字号 120，Y 坐标 415，城市和姓名显示在同一行，间距 35 像素
- **描述**: 浅金色 (#FFEDB5)，字号 50，Y 坐标 620
- **金额**: 浅金色 (#FFEDB5)，字号 220，Y 坐标 750
- **单位**: 浅金色 (#FFEDB5)，字号 80，位于金额右下角，水平间距 20 像素，Y 偏移 60 像素

### 自定义配置

可以通过修改 `core/drawer.py` 中的 `PosterDrawer` 类的 `config` 属性来自定义默认配置。

## 🔧 开发说明

### 核心类：PosterDrawer

`PosterDrawer` 类位于 `core/drawer.py`，负责海报绘制的核心逻辑：

```python
from core.drawer import PosterDrawer

# 创建绘制器实例
drawer = PosterDrawer(
    background_path='assets/template.jpg',
    font_path='assets/NotoSansSC-Regular.ttf',
    bold_font_path='assets/NotoSansSC-Bold.ttf'
)

# 绘制海报（data_row 需包含：城市、姓名、描述、金额、单位）
poster_image = drawer.draw(data_row, config)
```

**主要方法：**
- `draw(data_row, config=None)`: 绘制海报，返回 PIL Image 对象
- `get_font(size, bold=False)`: 获取字体对象
- `load_background()`: 加载背景底图
- `update_config(**kwargs)`: 更新配置

### 扩展功能

如需扩展功能，可以：

1. 修改 `PosterDrawer` 类添加新的绘制层
2. 在 `app.py` 中添加新的 Streamlit 组件
3. 扩展 Excel 数据列支持

## ⚠️ 注意事项

1. **底图文件**: 必须确保 `assets/template.jpg` 文件存在，否则程序会报错
2. **字体文件**: 
   - `assets/NotoSansSC-Regular.ttf` 和 `assets/NotoSansSC-Bold.ttf` 文件必需
   - 如不存在会使用系统默认字体（可能不支持中文或粗体效果）
3. **Excel 格式**: 必须使用 `.xlsx` 格式，且包含必需的列（城市、姓名、描述、金额、单位）
4. **文件大小**: 批量生成时注意内存使用，建议单次处理不超过 1000 条数据
5. **文字显示**: 所有文字默认使用粗体显示，城市和姓名会显示在同一行
6. **布局说明**: 金额和单位会智能对齐，单位显示在金额的右下角位置

## 📄 许可证

本项目采用 MIT 许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请通过 Issue 反馈。

