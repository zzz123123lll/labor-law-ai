"""FastAPI 应用入口。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.auth import router as auth_router
from app.api.cases import router as cases_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动/关闭时执行。"""
    from pathlib import Path
    from app.legal_engine.law_store import law_store
    from app.legal_engine.case_store import case_store

    data_dir = Path(__file__).parent / "legal_engine" / "data"
    law_store.load(str(data_dir))
    case_store.load(str(data_dir))
    app.state.law_store = law_store
    app.state.case_store = case_store
    yield
    # 关闭时清理


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


@app.get("/api/health")
async def health():
    return {"status": "ok"}
