from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": settings.app_version,
        "service": settings.app_name,
    }


@router.get("/version")
def version():
    return {
        "version": settings.app_version,
        "name": settings.app_name,
    }