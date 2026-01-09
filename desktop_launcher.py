"""
桌面应用启动器
用于将 Streamlit 应用打包成桌面应用
"""
import subprocess
import sys
import os
import time
import threading
import webbrowser
from pathlib import Path

# 获取应用根目录
if getattr(sys, 'frozen', False):
    # 如果是打包后的 exe，使用 PyInstaller 临时目录
    # PyInstaller 会创建一个临时文件夹，资源文件在那里
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录（资源文件在这里）
        BASE_DIR = Path(sys._MEIPASS)
    else:
        BASE_DIR = Path(sys.executable).parent
else:
    # 如果是开发模式，使用脚本所在目录
    BASE_DIR = Path(__file__).parent

# 设置工作目录（确保资源文件可以访问）
os.chdir(BASE_DIR)

# Streamlit 应用文件路径
# 在打包后，app.py 会在临时目录的根目录
APP_FILE = BASE_DIR / 'app.py'

# 如果找不到 app.py，尝试其他位置
if not APP_FILE.exists():
    # 尝试在 exe 所在目录查找
    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).parent
        alt_app_file = exe_dir / 'app.py'
        if alt_app_file.exists():
            APP_FILE = alt_app_file
            BASE_DIR = exe_dir
            os.chdir(BASE_DIR)

def start_streamlit():
    """启动 Streamlit 服务器"""
    try:
        # 构建 streamlit run 命令
        cmd = [
            sys.executable,
            '-m', 'streamlit', 'run',
            str(APP_FILE),
            '--server.headless', 'true',
            '--server.port', '8501',
            '--server.address', 'localhost',
            '--browser.gatherUsageStats', 'false'
        ]
        
        # 启动 Streamlit（不显示控制台窗口）
        if sys.platform == 'win32':
            # Windows: 隐藏控制台窗口
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                cwd=str(BASE_DIR)
            )
        else:
            # macOS/Linux
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(BASE_DIR)
            )
        
        return process
    except Exception as e:
        print(f"启动 Streamlit 失败: {e}")
        return None

def wait_for_server(max_wait=30):
    """等待服务器启动"""
    import urllib.request
    import urllib.error
    
    url = 'http://localhost:8501'
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except (urllib.error.URLError, OSError):
            time.sleep(0.5)
    
    return False

def open_browser():
    """打开浏览器"""
    url = 'http://localhost:8501'
    # 等待服务器启动
    if wait_for_server():
        webbrowser.open(url)
        print(f"应用已启动，请在浏览器中访问: {url}")
    else:
        print("警告: 服务器启动超时，请手动访问 http://localhost:8501")

def main():
    """主函数"""
    print("正在启动 PosterGenMaster...")
    
    # 检查 app.py 是否存在
    if not APP_FILE.exists():
        print(f"错误: 找不到应用文件 {APP_FILE}")
        input("按回车键退出...")
        sys.exit(1)
    
    # 启动 Streamlit 服务器
    process = start_streamlit()
    if process is None:
        print("无法启动应用")
        input("按回车键退出...")
        sys.exit(1)
    
    try:
        # 等待服务器启动并打开浏览器
        open_browser()
        
        # 保持进程运行
        print("\n应用正在运行中...")
        print("关闭此窗口将停止应用")
        print("=" * 50)
        
        # 等待进程结束
        process.wait()
    except KeyboardInterrupt:
        print("\n正在关闭应用...")
    finally:
        # 终止 Streamlit 进程
        if process:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        print("应用已关闭")

if __name__ == '__main__':
    main()
