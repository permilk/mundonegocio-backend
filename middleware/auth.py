"""
Authentication Middleware
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware para autenticación
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Procesar request
        """
        # Por ahora, solo pass-through
        # La autenticación real se maneja en los endpoints
        response = await call_next(request)
        return response
