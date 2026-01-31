"""
Database connection and session management.

This module sets up SQLAlchemy engine, session factory, and provides
database dependencies for FastAPI routes.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from .config import settings


# Create database engine
# Why these settings:
# - pool_pre_ping: Checks connection health before use (handles disconnects)
# - pool_recycle: Recycles connections after 1 hour (prevents timeout)
# - echo: Logs SQL statements in debug mode (useful for development)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)

# Session factory
# Why these settings:
# - autocommit=False: Requires explicit commit (safer, prevents accidental changes)
# - autoflush=False: Manual control over when changes are flushed
# - bind=engine: Associates sessions with our database engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI routes.
    How it works:
    1. Creates a new database session
    2. Yields it to the route function
    3. Automatically closes session after request (even if error occurs)
    Usage in routes:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    Why Generator:
    - The 'yield' allows FastAPI to handle cleanup
    - Session is closed in 'finally' block
    - Ensures no connection leaks
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Creates all tables defined by SQLAlchemy models.
    Only creates tables that don't exist (safe to run multiple times).
    In production, use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)