# 快速打包桌面应用指南

## 🚀 三步打包

### 1. 安装打包工具
```bash
pip install pyinstaller
```

### 2. 运行打包脚本
```bash
python build_desktop.py
```

### 3. 运行打包后的应用
双击 `dist/PosterGenMaster.exe` 即可运行！

## 📋 打包前检查

确保以下文件存在：
- ✅ `app.py` - 主应用文件
- ✅ `assets/template.jpg` - 背景底图
- ✅ `assets/NotoSansSC-Regular.ttf` - 字体文件
- ✅ `assets/NotoSansSC-Bold.ttf` - 粗体字体文件
- ✅ `core/drawer.py` - 核心绘制逻辑

## ⚠️ 注意事项

1. **打包环境**：建议在 Windows 环境下打包（目标平台）
2. **文件大小**：打包后的 exe 文件约 100-300MB（包含所有依赖）
3. **首次启动**：可能需要几秒钟解压临时文件
4. **防火墙**：首次运行可能需要允许防火墙访问

## 🔧 如果遇到问题

查看详细文档：[DESKTOP_BUILD.md](DESKTOP_BUILD.md)

## 📦 分发应用

打包完成后，将 `dist/PosterGenMaster.exe` 分发给用户即可。
用户无需安装 Python 或任何依赖，双击即可运行。
