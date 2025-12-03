"""
Health Check Routes
"""
from fastapi import APIRouter, status
from datetime import datetime

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Mundo Negocio Dashboard API",
        "version": "6.0.0"
    }


@router.get("/", status_code=status.HTTP_200_OK)
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Mundo Negocio Dashboard API",
        "version": "6.0.0",
        "docs": "/docs",
        "health": "/health"
    }
