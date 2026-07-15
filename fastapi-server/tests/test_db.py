"""数据库模型测试。"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.models import Base


@pytest.mark.asyncio
async def test_all_tables_create():
    """验证所有表可以正常创建。"""
    engine = create_async_engine("sqlite+aiosqlite://", echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # 无异常即通过
    await engine.dispose()
