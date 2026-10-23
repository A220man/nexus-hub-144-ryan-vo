"""Exception classes and error handlers."""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base application exception."""
    
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AppException):
    """Resource not found."""
    
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            f"{resource} not found: {identifier}",
            status_code=404,
            details={"resource": resource, "identifier": identifier},
        )


class ValidationError(AppException):
    """Validation error."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=422, details=details)


class ConflictError(AppException):
    """Resource conflict."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=409, details=details)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning(f"AppException: {exc.message}", extra=exc.details)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "details": exc.details},
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )
    
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        logger.warning(f"ValidationError: {exc}")
        return JSONResponse(
            status_code=422,
            content={"error": "Validation failed", "details": exc.errors()},
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
        )