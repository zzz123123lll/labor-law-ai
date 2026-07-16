"""结构化日志配置。所有模块通过 get_logger 获取统一格式的 logger。"""

import logging
import sys
from pathlib import Path


def setup_logging() -> None:
    """配置应用日志——控制台（开发）+ 文件（持久化）。"""
    log_format = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # 清除已有 handler（uvicorn reload 时防重复）
    root.handlers.clear()

    # 控制台（INFO 及以上）
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    root.addHandler(console)

    # 文件（DEBUG 及以上，保留最近 30 天）
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    root.addHandler(file_handler)

    # 降低第三方库日志等级（防噪音）
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    root.info("日志系统初始化完成")


def get_logger(name: str) -> logging.Logger:
    """获取结构化 logger。"""
    return logging.getLogger(name)


# 启动时自动配置
setup_logging()
