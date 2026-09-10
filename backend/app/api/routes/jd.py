import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.document_service import DocumentService, DocumentProcessingError
from app.ai.jd_extractor import JDExtractor

router = APIRouter()


@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_job_description(file: UploadFile = File(...)):
    request_id = str(uuid.uuid4())
    try:
        content = await file.read()
        extracted_text = DocumentService.extract_text(file.filename or "jd.txt", content)
        jd_schema = await JDExtractor.extract(extracted_text)

        return {
            "success": True,
            "data": {
                "filename": file.filename,
                "job_title": jd_schema.job_title,
                "mandatory_requirements": jd_schema.mandatory_requirements.model_dump(),
                "preferred_requirements": jd_schema.preferred_requirements.model_dump(),
                "responsibilities": jd_schema.responsibilities,
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
