from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.utils.logging import setup_logging
from app.api.routes import api_router
from app.database.redis import close_redis_connection

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting ResumeMatch AI service (env: {settings.APP_ENV})")
    yield
    logger.info("Shutting down ResumeMatch AI service...")
    await close_redis_connection()


app = FastAPI(
    title="ResumeMatch AI API",
    description="Intelligent Resume & Job Description Matching Platform API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to ResumeMatch AI API",
        "health_endpoint": "/api/v1/health",
        "docs": "/docs"
    }
