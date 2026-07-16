"""FastAPI 应用入口。"""
import app.logging_config  # noqa: F401  初始化结构化日志
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.database import engine
from app.models import Base
from app.errors import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)

from app.api.auth import router as auth_router
from app.api.cases import router as cases_router
from app.api.consultation import router as consultation_router
from app.api.contract_review import router as contract_review_router
from app.api.evidence import router as evidence_router
from app.api.compensation import router as compensation_router
from app.api.document_gen import router as document_gen_router
from app.api.payment import router as payment_router
from app.api.admin import router as admin_router

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

    from app.legal_engine.law_store import law_store
    from app.legal_engine.case_store import case_store
    from app.agents.registry import AgentRegistry

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

app.include_router(auth_router)
app.include_router(cases_router)
app.include_router(consultation_router)
app.include_router(contract_review_router)
app.include_router(evidence_router)
app.include_router(compensation_router)
app.include_router(document_gen_router)
app.include_router(payment_router)
app.include_router(admin_router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
