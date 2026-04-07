"""API中间件"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from lengchain.config import settings
from lengchain.utils.logger import get_logger
import time

logger = get_logger(__name__)


class APIKeyMiddleware(BaseHTTPMiddleware):
    """API密钥验证中间件"""
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 如果未设置API密钥，跳过验证
        if not settings.api_key:
            return await call_next(request)
        
        # 健康检查端点不需要验证
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # 验证API密钥
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Missing Authorization header"}
            )
        
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid Authorization header format"}
            )
        
        token = auth_header.replace("Bearer ", "")
        if token != settings.api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid API key"}
            )
        
        return await call_next(request)


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        start_time = time.time()
        
        # 记录请求
        logger.info(f"请求: {request.method} {request.url.path}")
        
        # 处理请求
        response = await call_next(request)
        
        # 记录响应
        process_time = time.time() - start_time
        logger.info(
            f"响应: {request.method} {request.url.path} "
            f"状态码={response.status_code} 耗时={process_time:.2f}s"
        )
        
        # 添加处理时间header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response