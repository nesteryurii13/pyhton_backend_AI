"""
CORS middleware configuration.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def setup_cors(app: FastAPI) -> None:
    """Setup CORS middleware for the application."""
    
    # Get settings from environment
    debug = os.getenv("DEBUG", "false").lower() == "true"
    cors_origins = os.getenv("BACKEND_CORS_ORIGINS", "")
    
    # Default allowed origins for development
    allowed_origins = [
        "http://localhost:3000",  # React default
        "http://localhost:8080",  # Vue default
        "http://localhost:4200",  # Angular default
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:4200",
        "http://127.0.0.1:5173",
    ]
    
    # Add configured CORS origins
    if cors_origins:
        additional_origins = [origin.strip() for origin in cors_origins.split(",")]
        allowed_origins.extend(additional_origins)
    
    # In development, allow all origins
    if debug:
        allowed_origins = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"]
    )