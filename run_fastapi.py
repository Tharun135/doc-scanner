#!/usr/bin/env python3
"""
FastAPI server startup script.
Alternative to: uvicorn fastapi_app.main:app --reload
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from fastapi_app.config import settings

if __name__ == "__main__":
    print(f"""
    ╔═══════════════════════════════════════════════════════╗
    ║  Doc Scanner FastAPI Server                          ║
    ║  Version: {settings.APP_VERSION}                                    ║
    ╚═══════════════════════════════════════════════════════╝
    
    🚀 Starting server on {settings.FASTAPI_HOST}:{settings.FASTAPI_PORT}
    📚 API Documentation: http://localhost:{settings.FASTAPI_PORT}/docs
    📖 ReDoc: http://localhost:{settings.FASTAPI_PORT}/redoc
    🔍 Health Check: http://localhost:{settings.FASTAPI_PORT}/health
    
    Press Ctrl+C to stop the server
    """)
    
    uvicorn.run(
        "fastapi_app.main:app",
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
