# 部署指南

本文档介绍如何将 PosterGenMaster 项目部署到各种平台。

## 📋 目录

- [中国大陆用户推荐方案](#中国大陆用户推荐方案)
- [EdgeOne Pages 部署](#edgeone-pages-部署)
- [Streamlit Cloud 部署](#streamlit-cloud-部署)
- [Docker 部署](#docker-部署)
- [其他部署方案](#其他部署方案)

---

## ⚠️ 重要提示：中国大陆用户

**Streamlit Cloud 在中国大陆访问受限**：
- Streamlit Cloud 依赖 AWS 和 Google Cloud，在中国大陆访问可能不稳定或无法访问
- 注册时国家列表中不包含中国
- 建议中国大陆用户使用以下方案：

### 推荐方案（按优先级）

1. **腾讯云轻量应用服务器 + EdgeOne CDN**（最推荐）
   - 国内访问速度快
   - 可使用 EdgeOne CDN 加速
   - 成本低（轻量服务器约 24-50 元/月）

2. **阿里云 ECS + CDN**
   - 稳定可靠
   - 国内访问速度快

3. **华为云 ECS**
   - 国内访问稳定

4. **Railway / Render**（需要科学上网）
   - 免费额度充足
   - 但访问需要代理

---

## 中国大陆用户推荐方案

### 方案一：腾讯云轻量应用服务器 + EdgeOne CDN（最推荐）

这是最适合中国大陆用户的部署方案，访问速度快且稳定。

#### 1. 购买腾讯云轻量应用服务器

1. **访问 [腾讯云轻量应用服务器](https://cloud.tencent.com/product/lighthouse)**
2. **选择配置**：
   - 地域：选择离用户最近的地域（如：北京、上海、广州）
   - 镜像：Ubuntu 22.04 LTS 或 CentOS 7.9
   - 套餐：2核2G 或更高（约 24-50 元/月）
3. **购买并获取服务器 IP 和 root 密码**

#### 2. 连接服务器并安装环境

```bash
# SSH 连接到服务器
ssh root@你的服务器IP

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 3.10+
sudo apt install python3 python3-pip python3-venv -y

# 安装 Git
sudo apt install git -y

# 安装系统依赖（Pillow 需要）
sudo apt install libgl1-mesa-glx libglib2.0-0 -y
```

#### 3. 部署应用

```bash
# 克隆项目
cd /opt
git clone https://github.com/xiaokaihan/PosterGenMaster.git
cd PosterGenMaster

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 测试运行（确保 assets 目录下有必需文件）
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

#### 4. 配置 systemd 服务（开机自启）

创建服务文件：

```bash
sudo nano /etc/systemd/system/postergenmaster.service
```

添加以下内容：

```ini
[Unit]
Description=PosterGenMaster Streamlit App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/PosterGenMaster
Environment="PATH=/opt/PosterGenMaster/venv/bin"
ExecStart=/opt/PosterGenMaster/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start postergenmaster

# 设置开机自启
sudo systemctl enable postergenmaster

# 查看状态
sudo systemctl status postergenmaster
```

#### 5. 配置防火墙

```bash
# 开放 8501 端口
sudo ufw allow 8501/tcp
# 或使用腾讯云控制台的防火墙规则
```

#### 6. 配置 EdgeOne CDN 加速（可选但推荐）

1. **登录 [EdgeOne 控制台](https://console.cloud.tencent.com/edgeone)**
2. **添加站点**：
   - 站点类型：选择"自有源站"
   - 源站地址：填写你的服务器 IP 或域名
   - 端口：8501
3. **配置加速域名**：
   - 添加你的域名（需要先备案）
   - 或使用 EdgeOne 提供的测试域名
4. **配置完成**，通过 CDN 域名访问应用

#### 7. 使用 Nginx 反向代理（推荐，更专业）

安装 Nginx：

```bash
sudo apt install nginx -y
```

配置 Nginx：

```bash
sudo nano /etc/nginx/sites-available/postergenmaster
```

添加配置：

```nginx
server {
    listen 80;
    server_name 你的域名或IP;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/postergenmaster /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

现在可以通过 `http://你的域名或IP` 访问应用。

### 方案二：阿里云 ECS 部署

步骤与腾讯云类似：

1. **购买阿里云 ECS**
2. **配置安全组**，开放 8501 端口
3. **按照上述步骤部署应用**
4. **（可选）配置阿里云 CDN 加速**

### 方案三：使用 Docker 部署到国内云平台

如果使用 Docker，可以：

1. **构建镜像**：
   ```bash
   docker build -t postergenmaster:latest .
   ```

2. **运行容器**：
   ```bash
   docker run -d -p 8501:8501 --name postergenmaster postergenmaster:latest
   ```

3. **部署到**：
   - 腾讯云容器服务 TKE
   - 阿里云容器服务 ACK
   - 华为云 CCE

---

## 成本对比（中国大陆）

| 方案 | 月成本 | 访问速度 | 稳定性 |
|------|--------|----------|--------|
| **腾讯云轻量服务器** | 24-50 元 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **阿里云 ECS** | 50-100 元 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **华为云 ECS** | 50-100 元 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Streamlit Cloud** | 免费 | ❌ 无法访问 | ❌ 无法访问 |
| **Railway** | 免费/付费 | ⭐⭐ 需代理 | ⭐⭐⭐ |

---

## 后续维护

### 更新应用

```bash
cd /opt/PosterGenMaster
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart postergenmaster
```

### 查看日志

```bash
# 查看服务日志
sudo journalctl -u postergenmaster -f

# 查看 Streamlit 日志
tail -f /opt/PosterGenMaster/.streamlit/logs/*.log
```

### 备份

定期备份 `assets/` 目录和配置文件：

```bash
tar -czf backup-$(date +%Y%m%d).tar.gz assets/ app.py core/ requirements.txt
```

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

## Streamlit Cloud 部署

⚠️ **注意**：Streamlit Cloud 在中国大陆访问受限，建议中国大陆用户使用 [腾讯云轻量服务器方案](#方案一腾讯云轻量应用服务器--edgeone-cdn最推荐)。

Streamlit Cloud 是 Streamlit 官方提供的免费部署平台，适合海外用户或能访问的用户。

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

### 海外用户

| 方案 | 难度 | 成本 | 适用场景 |
|------|------|------|----------|
| **Streamlit Cloud** | ⭐ 简单 | 免费 | 快速部署，个人/小团队项目 |
| **Railway** | ⭐⭐ 中等 | 免费/付费 | 需要更多控制权 |
| **Docker + 云平台** | ⭐⭐⭐ 较难 | 免费/付费 | 企业级部署，需要定制化 |

### 中国大陆用户

| 方案 | 难度 | 成本 | 适用场景 |
|------|------|------|----------|
| **腾讯云轻量服务器** | ⭐⭐⭐ 较难 | 24-50 元/月 | 国内访问，稳定快速（最推荐） |
| **阿里云 ECS** | ⭐⭐⭐ 较难 | 50-100 元/月 | 企业级，稳定可靠 |
| **华为云 ECS** | ⭐⭐⭐ 较难 | 50-100 元/月 | 企业级，稳定可靠 |
| **Docker + 国内云平台** | ⭐⭐⭐⭐ 较难 | 按需付费 | 容器化部署，适合大规模应用 |

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

