"""
Main entry point for the FastAPI application.
This file serves as the application entry point and imports from the app package.
"""
import os
from dotenv import load_dotenv
from app.main import app

# Load environment variables
load_dotenv()

# This allows running the app with `uvicorn main:app`
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "INFO").lower()
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level=log_level
    )