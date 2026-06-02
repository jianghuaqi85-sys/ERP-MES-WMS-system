import time
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import settings

# Configure Loguru
logger.add("logs/app.log", rotation="500 MB", retention="10 days", level="INFO")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS configuration - 生产环境通过 CORS_ORIGINS 环境变量配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for request timing and logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}ms"
    )
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # 生产环境隐藏内部异常详情，仅记录日志
    logger.error(f"Global exception: {traceback.format_exc()}")
    detail = str(exc) if not settings.IS_PRODUCTION else "请联系管理员"
    return JSONResponse(
        status_code=500,
        content={"code": 50000, "message": "Internal Server Error", "details": detail},
    )

from app.apps.erp.router import router as erp_router
from app.apps.wms.router import router as wms_router
from app.apps.mes.router import router as mes_router
from app.apps.auth.router import router as auth_router
from app.apps.traceability.router import router as trace_router
from app.apps.system.router import router as system_router

app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(erp_router, prefix=f"{settings.API_V1_STR}/erp", tags=["ERP"])
app.include_router(wms_router, prefix=f"{settings.API_V1_STR}/wms", tags=["WMS"])
app.include_router(mes_router, prefix=f"{settings.API_V1_STR}/mes", tags=["MES"])
app.include_router(trace_router, prefix=f"{settings.API_V1_STR}/traceability", tags=["Traceability"])
app.include_router(system_router, prefix=f"{settings.API_V1_STR}/system", tags=["System"])

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
