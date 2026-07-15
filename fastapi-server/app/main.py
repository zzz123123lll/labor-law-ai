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
    # 启动时加载法律库到内存
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
