"""
Logging Middleware
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import structlog

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging de requests
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Log request y response
        """
        start_time = time.time()
        
        # Log request
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=f"{duration:.3f}s"
        )
        
        return response
