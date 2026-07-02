#!/usr/bin/env python3
"""Run FastAPI server"""

import sys
sys.path.insert(0, '/home/ubuntu/Desktop/Assignment')

import uvicorn
from src.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info",
    )
