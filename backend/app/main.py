from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.database import engine, Base
from app.models import models
from app.routers import content, distribution, conversion, insight, dashboard, config
from app.auth import router as auth_router, verify_token
from app.config import MEDIA_DIR, VIDEO_OUTPUT_DIR
# 导入 knowledge_service 以触发 ChromaDB 初始化
import app.services.knowledge_service  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="咸阳文旅AIGC智能营销平台", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WHITELIST_PATHS = {
    "/api/health",
    "/api/auth/login",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/",
}


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    path = request.url.path.rstrip("/")

    if path in WHITELIST_PATHS or path.startswith("/media/"):
        return await call_next(request)

    if path.startswith("/api/"):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "请先登录"}
            )
        try:
            token = auth_header.split(" ", 1)[1]
            verify_token(token)
        except Exception:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token无效或已过期，请重新登录"}
            )

    return await call_next(request)

app.include_router(auth_router)

app.include_router(content.router, prefix="/api/content", tags=["内容工厂"])
app.include_router(distribution.router, prefix="/api", tags=["分发网络"])
app.include_router(conversion.router, prefix="/api", tags=["流量转化"])
app.include_router(insight.router, prefix="/api/insight", tags=["客群洞察"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["仪表盘"])
app.include_router(config.router, prefix="/api/config", tags=["系统配置"])

import os
os.makedirs(MEDIA_DIR, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")


@app.get("/")
def root():
    return {"message": "咸阳文旅AIGC智能营销平台 API", "version": "1.0.0"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


