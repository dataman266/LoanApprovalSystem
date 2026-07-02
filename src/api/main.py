"""FastAPI application initialization and setup"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging

from src.logger import get_logger
from src.database import init_db

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title="Loan Approval System",
        description="Multi-Agent Agentic AI system for loan application evaluation",
        version="0.1.0",
    )

    # Initialize database
    init_db()

    # Add routes
    from src.api.routes import router

    app.include_router(router)

    # Health check
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    @app.exception_handler(Exception)
    async def exception_handler(request, exc):
        logger.error("Unhandled exception", error=str(exc))
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    logger.info("FastAPI application created successfully")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
