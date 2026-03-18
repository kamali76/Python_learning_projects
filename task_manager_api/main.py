from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_tables
from routers import tasks, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(
    title="Task Manager API",
    description="A production-ready REST API with JWT auth, async endpoints, and PostgreSQL.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Task Manager API is running"}

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}