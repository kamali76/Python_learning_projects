"""
FastAPI Application Entry Point.

This is the main file that:
1. Creates the FastAPI application
2. Configures middleware (CORS)
3. Includes routers
4. Initializes database
5. Defines root endpoints
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db
from .routes import users


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    A secure authentication service with JWT tokens.

    ## Features

    * **User Registration**: Create new accounts with email validation
    * **Login**: Get JWT access tokens
    * **Protected Routes**: Secure endpoints with token authentication
    * **Password Security**: Bcrypt hashing for passwords

    ## Authentication

    1. Register a new account at `/auth/register`
    2. Login at `/auth/login` to get an access token
    3. Use the token in the `Authorization` header: `Bearer <token>`
    4. Access protected routes like `/auth/me`
    """,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)


# CORS Middleware
# Why CORS:
# - Allows frontend apps (React, Vue, etc.) to call this API
# - Browser enforces same-origin policy by default
# - CORS headers tell browser to allow cross-origin requests
#
# Security Note:
# - In production, set specific origins (not "*")
# - Example: ["https://myapp.com", "https://admin.myapp.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Allowed domains
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Event handlers
@app.on_event("startup")
async def startup_event():
    """
    Run when application starts.

    Initializes database tables.

    Note: In production, use Alembic migrations instead of init_db()
    """
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Debug mode: {settings.DEBUG}")
    init_db()
    print("Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run when application shuts down.

    Cleanup tasks go here (close connections, etc.)
    """
    print(f"Shutting down {settings.APP_NAME}")


# Include routers
app.include_router(users.router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information.

    Returns basic API info and available endpoints.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "register": "/auth/register",
            "login": "/auth/login",
            "me": "/auth/me"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.

    Used by:
    - Load balancers (AWS ALB, etc.)
    - Monitoring systems (Prometheus, Datadog)
    - Container orchestration (Kubernetes, ECS)

    Returns:
        200: Application is running
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Run with: uvicorn app.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )