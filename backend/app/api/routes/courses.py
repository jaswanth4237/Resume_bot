import uuid
from fastapi import APIRouter, status
from app.services.course_service import CourseService

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
@router.get("/", status_code=status.HTTP_200_OK)
async def list_courses():
    if not CourseService._courses_catalog:
        CourseService.load_catalog()

    return {
        "success": True,
        "data": {
            "total_courses": len(CourseService._courses_catalog),
            "courses": CourseService._courses_catalog
        },
        "requestId": str(uuid.uuid4())
    }
