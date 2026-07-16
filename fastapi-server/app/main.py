"""FastAPI 应用入口。"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.models import Base

from app.api.auth import router as auth_router
from app.api.cases import router as cases_router
from app.api.consultation import router as consultation_router
from app.api.contract_review import router as contract_review_router
from app.api.evidence import router as evidence_router
from app.api.compensation import router as compensation_router
from app.api.document_gen import router as document_gen_router
from app.api.payment import router as payment_router
from app.api.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动/关闭时执行。"""
    # 数据库表自动创建
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 加载法律库
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

    # 关闭引擎
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
