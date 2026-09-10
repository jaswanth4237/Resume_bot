import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.document_service import DocumentService, DocumentProcessingError
from app.ai.resume_extractor import ResumeExtractor

router = APIRouter()


@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_resume(file: UploadFile = File(...)):
    request_id = str(uuid.uuid4())
    try:
        content = await file.read()
        extracted_text = DocumentService.extract_text(file.filename or "resume.txt", content)
        resume_schema = await ResumeExtractor.extract(extracted_text)

        return {
            "success": True,
            "data": {
                "filename": file.filename,
                "candidate": resume_schema.candidate.model_dump(),
                "skills_count": len(resume_schema.skills),
                "skills": [s.model_dump() for s in resume_schema.skills],
                "total_experience_years": resume_schema.total_experience_years,
                "raw_text_length": len(extracted_text)
            },
            "requestId": request_id
        }
    except DocumentProcessingError as dpe:
        raise HTTPException(
            status_code=400,
            detail={"code": dpe.code, "message": dpe.message}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "INTERNAL_SERVER_ERROR", "message": str(e)}
        )
