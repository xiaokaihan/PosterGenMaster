# 部署指南

本文档介绍如何将 PosterGenMaster 项目部署到各种平台。

## 📋 目录

- [EdgeOne Pages 部署](#edgeone-pages-部署)
- [Streamlit Cloud 部署（推荐）](#streamlit-cloud-部署推荐)
- [Docker 部署](#docker-部署)
- [其他部署方案](#其他部署方案)

---

## EdgeOne Pages 部署

⚠️ **重要提示**: EdgeOne Pages 主要用于静态网站部署，而 Streamlit 应用需要 Python 运行时环境。因此，EdgeOne Pages **不能直接运行 Streamlit 应用**。

### 方案一：使用 EdgeOne Pages + 静态化（不推荐）

如果您必须使用 EdgeOne Pages，可以考虑将应用改造为静态网站，但这会失去交互功能。

### 方案二：EdgeOne + 其他云服务（推荐）

1. **将 Streamlit 应用部署到支持 Python 的平台**（见下方其他方案）
2. **使用 EdgeOne CDN 加速**访问该应用

### EdgeOne Pages 部署步骤（如果改造为静态网站）

1. **准备项目文件**
   ```bash
   # 确保项目文件完整
   ls -la
   ```

2. **创建 ZIP 压缩包**
   ```bash
   # 排除不需要的文件
   zip -r postergenmaster.zip . -x "*.git*" -x "__pycache__/*" -x "*.pyc" -x ".DS_Store"
   ```

3. **登录 EdgeOne 控制台**
   - 访问 [EdgeOne 控制台](https://console.cloud.tencent.com/edgeone)
   - 导航至 **Pages 服务**

4. **创建项目**
   - 点击"创建项目"
   - 选择"直接上传"方式
   - 填写项目名称：`PosterGenMaster`
   - 选择加速区域

5. **上传项目**
   - 将 ZIP 压缩包拖拽到上传区域
   - 点击"开始部署"

6. **配置环境**
   - 设置环境变量（如需要）
   - 选择 Node.js 版本（如果使用 Node.js 构建）

7. **预览和发布**
   - 部署成功后获取预览链接
   - 确认无误后发布到生产环境

---

## Streamlit Cloud 部署（推荐）

Streamlit Cloud 是 Streamlit 官方提供的免费部署平台，最适合部署 Streamlit 应用。

### 部署步骤

1. **准备 GitHub 仓库**
   - 确保代码已推送到 GitHub（已完成 ✅）
   - 仓库地址：`https://github.com/xiaokaihan/PosterGenMaster.git`

2. **登录 Streamlit Cloud**
   - 访问 [Streamlit Cloud](https://streamlit.io/cloud)
   - 使用 GitHub 账号登录

3. **创建新应用**
   - 点击 "New app"
   - 选择 GitHub 仓库：`xiaokaihan/PosterGenMaster`
   - 选择分支：`main`
   - 主文件路径：`app.py`

4. **配置应用**
   - **Python version**: 3.10 或更高
   - **Advanced settings**（可选）:
     - Secrets: 如需环境变量，可在此配置

5. **部署**
   - 点击 "Deploy"
   - 等待构建完成（通常 2-5 分钟）
   - 获取应用 URL：`https://your-app-name.streamlit.app`

6. **后续更新**
   - 代码推送到 GitHub 后，Streamlit Cloud 会自动重新部署

### 优势
- ✅ 完全免费
- ✅ 自动部署（GitHub 推送即部署）
- ✅ 官方支持，稳定可靠
- ✅ 支持自定义域名

---

## Docker 部署

使用 Docker 可以将应用容器化，部署到任何支持 Docker 的平台。

### 1. 创建 Dockerfile

创建 `Dockerfile` 文件：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8501

# 健康检查
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# 启动命令
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 2. 创建 .dockerignore

创建 `.dockerignore` 文件：

```
__pycache__
*.pyc
.git
.gitignore
.DS_Store
*.md
.env
venv/
```

### 3. 构建 Docker 镜像

```bash
docker build -t postergenmaster:latest .
```

### 4. 运行容器

```bash
docker run -p 8501:8501 postergenmaster:latest
```

### 5. 部署到云平台

可以将 Docker 镜像部署到：
- **Railway**: 支持 Docker，免费额度充足
- **Render**: 支持 Docker，免费套餐可用
- **Fly.io**: 支持 Docker，全球边缘部署
- **腾讯云容器服务**: 国内访问速度快

---

## 其他部署方案

### Railway 部署

1. **访问 [Railway](https://railway.app)**
2. **使用 GitHub 登录**
3. **创建新项目** → 选择 GitHub 仓库
4. **配置部署**:
   - Railway 会自动检测 Python 项目
   - 设置启动命令：`streamlit run app.py --server.port=$PORT`
5. **部署完成**，获取公网 URL

### Render 部署

1. **访问 [Render](https://render.com)**
2. **创建 Web Service**
3. **连接 GitHub 仓库**
4. **配置**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
5. **部署**

### 腾讯云轻量应用服务器

1. **购买轻量应用服务器**（Linux 系统）
2. **SSH 连接到服务器**
3. **安装 Python 和依赖**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   git clone https://github.com/xiaokaihan/PosterGenMaster.git
   cd PosterGenMaster
   pip3 install -r requirements.txt
   ```
4. **使用 screen 或 systemd 运行**:
   ```bash
   # 使用 screen
   screen -S streamlit
   streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   
   # 或使用 systemd（创建服务文件）
   sudo nano /etc/systemd/system/postergenmaster.service
   ```
5. **配置防火墙**，开放 8501 端口
6. **（可选）使用 EdgeOne CDN 加速**访问服务器

---

## 推荐方案对比

| 方案 | 难度 | 成本 | 适用场景 |
|------|------|------|----------|
| **Streamlit Cloud** | ⭐ 简单 | 免费 | 快速部署，个人/小团队项目 |
| **Railway** | ⭐⭐ 中等 | 免费/付费 | 需要更多控制权 |
| **Docker + 云平台** | ⭐⭐⭐ 较难 | 免费/付费 | 企业级部署，需要定制化 |
| **轻量服务器** | ⭐⭐⭐ 较难 | 付费 | 国内访问，需要完全控制 |

---

## 注意事项

1. **资源文件**: 确保 `assets/` 目录下的文件（字体、模板图片）已包含在部署包中
2. **文件大小**: EdgeOne Pages 单个文件限制 25MB，注意字体文件大小
3. **环境变量**: 如需配置敏感信息，使用环境变量而非硬编码
4. **端口配置**: 部署到云平台时，注意使用平台提供的 PORT 环境变量
5. **域名绑定**: 大多数平台支持自定义域名，可绑定到 EdgeOne CDN

---

## 获取帮助

- Streamlit 文档: https://docs.streamlit.io/
- EdgeOne 文档: https://cloud.tencent.com/document/product/1552
- 项目 Issues: https://github.com/xiaokaihan/PosterGenMaster/issues

