"""
Mundo Negocio Dashboard API - Production Ready
FastAPI Application with Authentication, Rate Limiting, Monitoring
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator
import logging
import sys
from datetime import datetime
import structlog

from api.settings import get_settings
from api.routes import sales, auth, filters, exports, health
from middleware.auth import AuthMiddleware
from middleware.logging import LoggingMiddleware
from middleware.error_handler import error_handler_middleware
from utils.database import init_db, close_db

# Configuración
settings = get_settings()

# Logging estructurado
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Rate Limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"]
)

# FastAPI App
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Professional Sales Dashboard API",
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
    openapi_url="/api/openapi.json" if settings.debug else None,
)

# Agregar rate limiter al estado de la app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware - Orden importa
# 1. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Rate-Limit-Remaining"],
)

# 2. GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 3. Custom Logging
app.middleware("http")(LoggingMiddleware())

# 4. Custom Error Handler
app.middleware("http")(error_handler_middleware)

# 5. Authentication (para rutas protegidas)
# app.middleware("http")(AuthMiddleware())  # Se activa selectivamente por ruta

# Prometheus Metrics
if not settings.debug:
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Event Handlers
@app.on_event("startup")
async def startup_event():
    """Inicialización de la aplicación"""
    logger.info(
        "application_startup",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        debug=settings.debug
    )
    
    # Inicializar base de datos
    await init_db()
    
    logger.info("database_initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al cerrar la aplicación"""
    logger.info("application_shutdown")
    
    # Cerrar conexiones
    await close_db()
    
    logger.info("connections_closed")

# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejo de errores de validación"""
    logger.warning(
        "validation_error",
        path=request.url.path,
        errors=exc.errors(),
        body=exc.body
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Error de validación en los datos enviados",
            "details": exc.errors(),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Manejo de excepciones generales"""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "Error interno del servidor" if not settings.debug else str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Routes
@app.get("/")
@limiter.limit("30/minute")
async def root(request: Request):
    """Root endpoint con información del API"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "environment": settings.environment,
        "docs": "/api/docs" if settings.debug else "disabled",
        "health": "/health",
        "timestamp": datetime.utcnow().isoformat()
    }

# Incluir routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(sales.router, prefix="/api/sales", tags=["Sales"])
app.include_router(filters.router, prefix="/api/filters", tags=["Filters"])
app.include_router(exports.router, prefix="/api/exports", tags=["Exports"])

# Entry Point
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True,
        workers=1 if settings.debug else 4,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
