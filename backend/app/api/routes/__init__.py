from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.jd import router as jd_router
from app.api.routes.resume import router as resume_router
from app.api.routes.analysis import router as analysis_router
from app.api.routes.courses import router as courses_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(jd_router, prefix="/jd", tags=["Job Description"])
api_router.include_router(resume_router, prefix="/resume", tags=["Resume"])
api_router.include_router(analysis_router, tags=["Analysis"])
api_router.include_router(courses_router, prefix="/courses", tags=["Courses"])
