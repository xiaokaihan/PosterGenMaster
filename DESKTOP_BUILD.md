# 桌面应用打包指南

本指南将帮助您将 PosterGenMaster Web 应用打包成 Windows 桌面应用（.exe 文件）。

## 📦 打包方案

我们使用 **PyInstaller** 将 Streamlit 应用打包成独立的可执行文件。打包后的应用会：
1. 自动启动本地 Streamlit 服务器
2. 自动打开系统默认浏览器
3. 在浏览器中显示应用界面

## 🛠️ 环境要求

- Python 3.8 或更高版本
- Windows 10/11（本方案主要针对 Windows）
- 已安装项目依赖（`pip install -r requirements.txt`）

## 📝 打包步骤

### 方法一：使用自动打包脚本（推荐）

1. **安装打包工具**
   ```bash
   pip install pyinstaller
   ```

2. **运行打包脚本**
   ```bash
   python build_desktop.py
   ```

3. **等待打包完成**
   - 打包过程可能需要几分钟
   - 完成后会在 `dist` 目录下生成 `PosterGenMaster.exe`

4. **测试运行**
   - 双击 `dist/PosterGenMaster.exe` 运行
   - 应用会自动启动并打开浏览器

### 方法二：手动使用 PyInstaller

1. **安装 PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **执行打包命令**
   ```bash
   pyinstaller --name=PosterGenMaster --onefile --windowed --add-data="assets;assets" --add-data="core;core" --hidden-import=streamlit --hidden-import=pandas --hidden-import=PIL --hidden-import=openpyxl --collect-all=streamlit desktop_launcher.py
   ```

3. **使用 spec 文件（推荐）**
   ```bash
   pyinstaller build.spec
   ```

## 📁 打包后的文件结构

```
dist/
└── PosterGenMaster.exe  # 可执行文件（包含所有依赖）
```

**注意**：打包后的 exe 文件会比较大（通常 100-300MB），因为包含了 Python 解释器和所有依赖库。

## 🚀 分发应用

### 方式一：直接分发 exe 文件
- 将 `dist/PosterGenMaster.exe` 分发给用户
- 用户双击即可运行，无需安装 Python

### 方式二：创建安装包（可选）
可以使用以下工具创建安装程序：
- **Inno Setup**（Windows 安装程序）
- **NSIS**（Nullsoft Scriptable Install System）

## ⚙️ 高级配置

### 添加应用图标

1. 准备图标文件（`.ico` 格式，Windows）
2. 修改 `build.spec` 文件中的 `icon` 参数：
   ```python
   icon='assets/icon.ico'
   ```
3. 或在打包命令中添加：
   ```bash
   --icon=assets/icon.ico
   ```

### 减小文件大小

1. **使用 UPX 压缩**（已启用）
   - 可以进一步减小文件大小
   - 某些杀毒软件可能会误报

2. **排除不必要的模块**
   - 在 `build.spec` 的 `excludes` 中添加不需要的模块

### 调试打包问题

如果打包后运行出错，可以：

1. **使用控制台模式调试**
   - 修改 `build.spec` 中的 `console=True`
   - 重新打包，查看错误信息

2. **检查依赖**
   ```bash
   # 查看打包后的依赖
   pyinstaller --log-level=DEBUG desktop_launcher.py
   ```

3. **测试依赖**
   ```bash
   # 在打包环境中测试
   python desktop_launcher.py
   ```

## 🔧 常见问题

### Q1: 打包后的 exe 无法启动
**解决方案**：
- 检查是否所有资源文件（assets、core）都被正确打包
- 使用控制台模式查看错误信息
- 确保在 Windows 环境下打包

### Q2: 启动后浏览器无法打开
**解决方案**：
- 检查防火墙设置
- 手动访问 `http://localhost:8501`
- 检查端口 8501 是否被占用

### Q3: 文件太大
**解决方案**：
- 使用虚拟环境，只安装必要的依赖
- 排除不需要的 Streamlit 组件
- 使用 UPX 压缩（已默认启用）

### Q4: 杀毒软件误报
**解决方案**：
- 这是 PyInstaller 打包的常见问题
- 可以将 exe 文件提交给杀毒软件厂商白名单
- 或使用代码签名证书

### Q5: 首次启动很慢
**解决方案**：
- 这是正常现象，因为需要解压临时文件
- 后续启动会快一些
- 可以考虑使用 `--onedir` 模式（不打包成单个文件）

## 📋 打包检查清单

- [ ] 已安装所有依赖
- [ ] 已测试 `desktop_launcher.py` 可以正常运行
- [ ] assets 目录包含所有必需文件（template.jpg, 字体文件等）
- [ ] 已安装 PyInstaller
- [ ] 打包命令执行成功
- [ ] 测试打包后的 exe 可以正常运行
- [ ] 浏览器可以正常打开应用

## 🎯 使用建议

1. **开发环境**：继续使用 `streamlit run app.py` 进行开发
2. **生产环境**：使用打包后的 exe 分发给最终用户
3. **更新应用**：修改代码后重新打包即可

## 📚 相关资源

- [PyInstaller 官方文档](https://pyinstaller.org/)
- [Streamlit 部署文档](https://docs.streamlit.io/deploy)
- [项目 README](README.md)

## 💡 替代方案

如果 PyInstaller 方案不满足需求，可以考虑：

1. **Electron + Python 后端**
   - 使用 Electron 做前端
   - Python 作为后端服务
   - 更灵活但更复杂

2. **Tauri + Python 后端**
   - 类似 Electron，但更轻量
   - 使用 Rust + Web 技术

3. **直接使用 Streamlit Desktop**
   - 使用第三方工具如 `streamlit-desktop`

---

**提示**：首次打包建议在干净的虚拟环境中进行，以避免依赖冲突。
