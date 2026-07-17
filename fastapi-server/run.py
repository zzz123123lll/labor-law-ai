"""劳动法AI 桌面应用启动器。"""
import sys
import os
import webbrowser
import threading
import time
from pathlib import Path
import uvicorn


def get_base_dir():
    """获取数据目录。开发模式用当前目录，PyInstaller 打包后用 exe 所在目录。"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent


def main():
    base_dir = get_base_dir()

    # 确保数据目录存在
    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True)

    # 设置环境变量
    os.environ.setdefault("LABOR_LAW_DATA_DIR", str(data_dir))

    # 延迟打开浏览器（等服务器启动好）
    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://localhost:5860")

    threading.Thread(target=open_browser, daemon=True).start()

    # 启动服务器
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=5860,
        log_level="info",
    )


if __name__ == "__main__":
    main()
