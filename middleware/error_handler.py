"""
Error Handler Middleware
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()


async def error_handler_middleware(request: Request, call_next):
    """
    Middleware para manejo de errores
    """
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        logger.error(
            "unhandled_error",
            error=str(exc),
            path=request.url.path,
            method=request.method
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "error": str(exc) if request.app.state.settings.DEBUG else "An error occurred"
            }
        )
