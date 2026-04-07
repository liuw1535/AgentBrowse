"""FastAPI服务器"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from lengchain.api.routes import router
from lengchain.api.middleware import APIKeyMiddleware, LoggingMiddleware
from lengchain.config import settings
from lengchain.utils.logger import setup_logger, get_logger
import uvicorn

# 设置日志
setup_logger(level=settings.log_level)
logger = get_logger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="LangChain Browser Automation API",
    description="基于LangChain和LCEL构建的浏览器自动化AI助手",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加自定义中间件
app.add_middleware(LoggingMiddleware)
if settings.api_key:
    app.add_middleware(APIKeyMiddleware)
    logger.info("API密钥验证已启用")

# 注册路由
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("=" * 50)
    logger.info("浏览器自动化助手 API 启动中...")
    logger.info(f"监听地址: {settings.api_host}:{settings.api_port}")
    logger.info(f"文档地址: http://{settings.api_host}:{settings.api_port}/docs")
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("API 服务关闭")


def run_server():
    """运行服务器"""
    uvicorn.run(
        "lengchain.api.server:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    run_server()