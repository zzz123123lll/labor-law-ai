"""FastAPI 依赖注入——数据库。"""
from app.database import get_db

__all__ = ["get_db"]
