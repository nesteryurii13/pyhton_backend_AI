"""
Main FastAPI application entry point.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from dotenv import load_dotenv

from app.core.logging import setup_logging, get_logger
from app.api.v1.api import api_router
from app.middleware.cors import setup_cors
from app.middleware.error_handler import (
    http_error_handler,
    validation_error_handler,
    general_error_handler
)
from app.models.schemas import SystemInfo
from app.services.gpt_service import get_gpt_service

# Load environment variables and setup logging
load_dotenv()
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    project_name = os.getenv("PROJECT_NAME", "GPT Query API")
    version = os.getenv("VERSION", "1.0.0")
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(
        "Starting up application",
        extra={"extra_fields": {
            "service": project_name,
            "version": version,
            "environment": "development" if debug else "production"
        }}
    )
    
    # Initialize services during startup
    try:
        gpt_service = await get_gpt_service()
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}", exc_info=True)
        raise
    
    yield
    
    logger.info("Shutting down application")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Get settings from environment
    project_name = os.getenv("PROJECT_NAME", "GPT Query API")
    project_description = os.getenv("PROJECT_DESCRIPTION", "A sophisticated FastAPI backend for querying GPT models")
    version = os.getenv("VERSION", "1.0.0")
    debug = os.getenv("DEBUG", "false").lower() == "true"
    api_v1_str = "/api/v1"
    
    app = FastAPI(
        title=project_name,
        description=project_description,
        version=version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",  # Serve OpenAPI spec at root level
        debug=debug,
        servers=[
            {"url": f"http://localhost:{os.getenv('SERVER_PORT', '8001')}", "description": "Development server"},
            {"url": "/", "description": "Current server"}
        ]
    )
    
    # Setup CORS
    setup_cors(app)
    
    # Add exception handlers
    app.add_exception_handler(HTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, general_error_handler)
    
    # Include API routes
    app.include_router(api_router, prefix=api_v1_str)
    
    return app


# Create the application instance
app = create_application()


@app.get(
    "/",
    response_model=SystemInfo,
    summary="System Information",
    description="Get basic system information and available endpoints"
)
async def root() -> SystemInfo:
    """
    Root endpoint providing system information.
    
    Returns:
        System information including version, documentation URLs, etc.
    """
    project_name = os.getenv("PROJECT_NAME", "GPT Query API")
    version = os.getenv("VERSION", "1.0.0")
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    return SystemInfo(
        service=project_name,
        version=version,
        environment="development" if debug else "production",
        docs_url="/docs",
        health_url="/api/v1/health"
    )


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


def custom_openapi():
    """Custom OpenAPI schema generation with proper server configuration."""
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        servers=[
            {"url": f"http://localhost:{os.getenv('SERVER_PORT', '8001')}", "description": "Development server"}
        ]
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "INFO").lower()
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level=log_level
    )