import os
import sys
import subprocess
import lit_muse # 导入我们自己的包

def main():
    # 动态找到你包里的 app.py 的绝对路径
    app_path = os.path.join(os.path.dirname(lit_muse.__file__), "app.py")
    
    # 相当于在终端里敲击: python -m streamlit run /path/to/app.py
    print("🎵 Lit-Muse initiating 🎵")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])

if __name__ == "__main__":
    main()