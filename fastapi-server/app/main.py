"""FastAPI 应用入口。"""
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.exceptions import HTTPException as StarletteHTTPException

import app.logging_config  # noqa: F401  初始化结构化日志
from app.api.admin import router as admin_router
from app.api.arbitration import router as arbitration_router
from app.api.auth import router as auth_router
from app.api.cases import router as cases_router
from app.api.compensation import router as compensation_router
from app.api.consultation import router as consultation_router
from app.api.contract_review import router as contract_review_router
from app.api.document_gen import router as document_gen_router
from app.api.evidence import router as evidence_router
from app.api.payment import router as payment_router
from app.api.settings import router as settings_router
from app.config import settings
from app.database import engine
from app.errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.models import Base

# 速率限制器（内存存储，生产环境建议换 Redis）
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["30/minute", "200/hour"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动/关闭时执行。"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from app.agents.registry import AgentRegistry
    from app.legal_engine.case_store import case_store
    from app.legal_engine.law_store import law_store

    # PyInstaller 打包后资源路径
    if getattr(sys, 'frozen', False):
        # 打包后资源在 exe 旁边
        data_dir = Path(sys.executable).parent / "legal_engine" / "data"
    else:
        data_dir = Path(__file__).parent / "legal_engine" / "data"
    law_store.load(str(data_dir))
    case_store.load(str(data_dir))
    app.state.law_store = law_store
    app.state.case_store = case_store
    app.state.agent_registry = AgentRegistry(law_store, case_store)

    yield

    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 统一错误码格式 {code, message, data}
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 托管前端静态文件（Next.js 静态导出产物）
if getattr(sys, 'frozen', False):
    frontend_dir = Path(sys.executable).parent / "frontend"
else:
    frontend_dir = Path(__file__).parent.parent.parent / "web-app" / "out"
if frontend_dir.exists():
    app.include_router(arbitration_router)
    app.include_router(auth_router)
    app.include_router(cases_router)
    app.include_router(consultation_router)
    app.include_router(contract_review_router)
    app.include_router(evidence_router)
    app.include_router(compensation_router)
    app.include_router(document_gen_router)
    app.include_router(payment_router)
    app.include_router(admin_router)
    app.include_router(settings_router)

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    # 静态文件挂载（最后注册，优先级最低）
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
else:
    # 前端目录不存在时不挂载（开发模式，前端独立启动）
    app.include_router(arbitration_router)
    app.include_router(auth_router)
    app.include_router(cases_router)
    app.include_router(consultation_router)
    app.include_router(contract_review_router)
    app.include_router(evidence_router)
    app.include_router(compensation_router)
    app.include_router(document_gen_router)
    app.include_router(payment_router)
    app.include_router(admin_router)
    app.include_router(settings_router)

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}
