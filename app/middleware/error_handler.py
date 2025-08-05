"""
Global error handling middleware.
"""
import uuid
from typing import Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.models.schemas import ErrorResponse, ErrorDetail
from app.core.logging import get_logger

logger = get_logger(__name__)


async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    request_id = str(uuid.uuid4())
    
    logger.error(
        "HTTP error occurred",
        extra={"extra_fields": {
            "request_id": request_id,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "url": str(request.url),
            "method": request.method
        }}
    )
    
    error_response = ErrorResponse(
        error=exc.detail,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode='json')
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors."""
    request_id = str(uuid.uuid4())
    
    details = []
    for error in exc.errors():
        details.append(ErrorDetail(
            type=error["type"],
            message=error["msg"],
            field=".".join(str(x) for x in error["loc"][1:]) if len(error["loc"]) > 1 else None
        ))
    
    logger.error(
        "Validation error occurred",
        extra={"extra_fields": {
            "request_id": request_id,
            "errors": [detail.dict() for detail in details],
            "url": str(request.url),
            "method": request.method
        }}
    )
    
    error_response = ErrorResponse(
        error="Validation error",
        details=details,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=422,
        content=error_response.model_dump(mode='json')
    )


async def general_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    request_id = str(uuid.uuid4())
    
    logger.error(
        "Unhandled exception occurred",
        extra={"extra_fields": {
            "request_id": request_id,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "url": str(request.url),
            "method": request.method
        }},
        exc_info=True
    )
    
    error_response = ErrorResponse(
        error="Internal server error",
        details=[ErrorDetail(
            type="internal_error",
            message="An unexpected error occurred"
        )],
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump(mode='json')
    )