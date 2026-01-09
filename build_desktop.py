"""
桌面应用打包脚本
使用 PyInstaller 将 Streamlit 应用打包成 exe
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_pyinstaller():
    """检查 PyInstaller 是否已安装"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """安装 PyInstaller"""
    print("正在安装 PyInstaller...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    print("PyInstaller 安装完成")

def build_exe():
    """构建 exe 文件"""
    print("=" * 60)
    print("开始打包桌面应用...")
    print("=" * 60)
    
    # 检查 PyInstaller
    if not check_pyinstaller():
        print("PyInstaller 未安装，正在安装...")
        install_pyinstaller()
    
    # 清理之前的构建
    build_dirs = ['build', 'dist', '__pycache__']
    for dir_name in build_dirs:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name)
    
    # 清理 spec 文件
    spec_file = 'desktop_launcher.spec'
    if os.path.exists(spec_file):
        os.remove(spec_file)
    
    # 构建 PyInstaller 命令
    cmd = [
        'pyinstaller',
        '--name=PosterGenMaster',
        '--onefile',
        '--windowed',  # Windows: 不显示控制台窗口
        '--icon=NONE',  # 可以后续添加图标
        '--add-data=assets;assets',  # Windows 使用分号
        '--add-data=core;core',
        '--add-data=app.py;.',  # 包含 app.py
        '--hidden-import=streamlit',
        '--hidden-import=pandas',
        '--hidden-import=PIL',
        '--hidden-import=openpyxl',
        '--hidden-import=streamlit.web.cli',
        '--hidden-import=streamlit.runtime.scriptrunner',
        '--hidden-import=streamlit.runtime.state',
        '--collect-all=streamlit',
        '--collect-all=altair',
        'desktop_launcher.py'
    ]
    
    # macOS 使用冒号分隔
    if sys.platform == 'darwin':
        cmd = [c.replace(';', ':') if '--add-data' in c else c for c in cmd]
        # macOS 不需要 --windowed，使用 --noconsole
        cmd = [c.replace('--windowed', '--noconsole') if '--windowed' in c else c for c in cmd]
    
    # Linux
    if sys.platform == 'linux':
        cmd = [c.replace(';', ':') if '--add-data' in c else c for c in cmd]
        cmd = [c.replace('--windowed', '--noconsole') if '--windowed' in c else c for c in cmd]
    
    print("\n执行打包命令...")
    print(" ".join(cmd))
    print("\n")
    
    try:
        subprocess.check_call(cmd)
        print("\n" + "=" * 60)
        print("✅ 打包完成！")
        print("=" * 60)
        print(f"\n可执行文件位置: {os.path.abspath('dist/PosterGenMaster.exe' if sys.platform == 'win32' else 'dist/PosterGenMaster')}")
        print("\n提示:")
        print("1. 首次运行可能需要几秒钟启动时间")
        print("2. 如果遇到问题，可以查看 dist 目录下的文件")
        print("3. 可以将整个 dist 目录分发给用户")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 打包失败: {e}")
        print("\n请检查:")
        print("1. 是否已安装所有依赖: pip install -r requirements.txt")
        print("2. PyInstaller 是否正确安装")
        sys.exit(1)

if __name__ == '__main__':
    build_exe()
