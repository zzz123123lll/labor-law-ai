"""FastAPI 依赖注入——数据库。"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
