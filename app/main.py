import logging
import time
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.exceptions import CustomException
from app.core.logging import setup_logging

# Set up logging configuration
logger = logging.getLogger(__name__)

# Application startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for FastAPI application lifespan.
    Used to setup and teardown resources.
    """
    # Setup - runs before application starts accepting requests
    setup_logging()
    app.state.start_time = time.time()
    logger.info("Application startup complete")
    
    yield
    
    # Cleanup - runs when application is shutting down
    logger.info("Application shutdown complete")

def create_app() -> FastAPI:
    """
    Application factory pattern for creating the FastAPI app with all configurations.
    """
    # Initialize FastAPI application
    app = FastAPI(
        title="SentimentFlow API",
        description="A microservices-based sentiment analysis API built with FastAPI",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, limit this to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add request processing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next: Callable):
        """
        Middleware to add processing time to response headers and log request details.
        """
        start_time = time.time()
        logger.debug(f"Request started: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # Add custom header with processing time
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            logger.debug(f"Request completed: {request.method} {request.url.path} - {response.status_code} ({process_time:.4f}s)")
            return response
        except Exception as e:
            logger.exception(f"Request failed: {request.method} {request.url.path}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
    
    # Exception handler for custom exceptions
    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        """
        Global exception handler for handling custom exceptions.
        """
        logger.error(f"CustomException: {exc.detail} - {request.method} {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    # Include API routers
    app.include_router(api_router, prefix="/api/v1")
    
    # Add health endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Health check endpoint to verify API is running and provide basic system info.
        """
        uptime = time.time() - app.state.start_time
        return {
            "status": "healthy",
            "version": app.version,
            "uptime_seconds": uptime,
            "server_time": time.time()
        }
    
    return app

# Create the FastAPI application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
