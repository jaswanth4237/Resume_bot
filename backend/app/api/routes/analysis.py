import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.matching_service import MatchingService
from app.services.document_service import DocumentProcessingError

router = APIRouter()

# In-memory store for quick session retrieval
ANALYSIS_STORE = {}


@router.post("/analyze", status_code=status.HTTP_200_OK)
async def analyze_match(
    jd_file: UploadFile = File(...),
    resume_file: UploadFile = File(None),
    resume_files: List[UploadFile] = File(None)
):
    request_id = str(uuid.uuid4())
    resumes_to_process = []

    if resume_files:
        resumes_to_process.extend(resume_files)
    if resume_file and resume_file not in resumes_to_process:
        resumes_to_process.append(resume_file)

    if not resumes_to_process:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_RESUME", "message": "At least one resume file must be provided."}
        )

    try:
        jd_bytes = await jd_file.read()
        results = []

        for r_file in resumes_to_process:
            r_bytes = await r_file.read()
            match_result = await MatchingService.analyze_candidate_against_jd(
                resume_filename=r_file.filename or "resume.pdf",
                resume_bytes=r_bytes,
                jd_filename=jd_file.filename or "jd.pdf",
                jd_bytes=jd_bytes
            )
            ANALYSIS_STORE[match_result["analysis_id"]] = match_result
            results.append(match_result)

        # Sort multiple candidates by score descending
        results.sort(key=lambda x: x["overall_score"], reverse=True)

        if len(results) == 1:
            return {
                "success": True,
                "data": results[0],
                "requestId": request_id
            }

        return {
            "success": True,
            "data": {
                "job_title": results[0]["job_title"],
                "total_candidates": len(results),
                "rankings": [
                    {
                        "rank": idx + 1,
                        "candidate_name": r["candidate"]["name"],
                        "score": r["overall_score"],
                        "decision": r["decision"],
                        "analysis_id": r["analysis_id"]
                    }
                    for idx, r in enumerate(results)
                ],
                "detailed_results": results
            },
            "requestId": request_id
        }
    except DocumentProcessingError as dpe:
        raise HTTPException(status_code=400, detail={"code": dpe.code, "message": dpe.message})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"code": "ANALYSIS_FAILED", "message": str(e)})


@router.get("/analysis/{analysis_id}", status_code=status.HTTP_200_OK)
async def get_analysis_result(analysis_id: str):
    request_id = str(uuid.uuid4())
    if analysis_id not in ANALYSIS_STORE:
        raise HTTPException(
            status_code=404,
            detail={"code": "ANALYSIS_NOT_FOUND", "message": f"Analysis ID '{analysis_id}' not found."}
        )

    return {
        "success": True,
        "data": ANALYSIS_STORE[analysis_id],
        "requestId": request_id
    }


@router.get("/analysis/{analysis_id}/report", status_code=status.HTTP_200_OK)
async def get_analysis_report(analysis_id: str):
    if analysis_id not in ANALYSIS_STORE:
        raise HTTPException(
            status_code=404,
            detail={"code": "ANALYSIS_NOT_FOUND", "message": f"Analysis ID '{analysis_id}' not found."}
        )

    data = ANALYSIS_STORE[analysis_id]
    decision_emoji = "🟢" if data["decision"] == "SUITABLE" else "🟡" if data["decision"] == "BORDERLINE" else "🔴"

    matched_list = "\n".join([f"✓ {m}" for m in data.get("matched_requirements", [])]) or "None"
    partial_list = "\n".join([f"⚠ {p}" for p in data.get("partial_requirements", [])]) or "None"
    missing_list = "\n".join([f"✗ {m}" for m in data.get("missing_requirements", [])]) or "None"

    courses = data.get("course_recommendations", [])
    courses_formatted = "\n".join([f"{idx+1}. {c['title']} ({c['platform']}) - {c['url']}" for idx, c in enumerate(courses)]) or "No courses needed"

    report_text = f"""
━━━━━━━━━━━━━━━━━━━━
🤖 RESUME MATCH REPORT
━━━━━━━━━━━━━━━━━━━━

👤 Candidate:
{data['candidate']['name']}

💼 Position:
{data['job_title']}

🎯 Match Score:
{data['overall_score']}%

{decision_emoji} Decision:
{data['decision']}

━━━━━━━━━━━━━━━━━━━━
📊 SCORE BREAKDOWN
━━━━━━━━━━━━━━━━━━━━

Skills: {data['category_scores']['skills']}%
Experience: {data['category_scores']['experience']}%
Responsibilities: {data['category_scores']['responsibilities']}%
Education: {data['category_scores']['education']}%

━━━━━━━━━━━━━━━━━━━━
✅ MATCHED
━━━━━━━━━━━━━━━━━━━━

{matched_list}

━━━━━━━━━━━━━━━━━━━━
⚠️ PARTIAL
━━━━━━━━━━━━━━━━━━━━

{partial_list}

━━━━━━━━━━━━━━━━━━━━
❌ MISSING
━━━━━━━━━━━━━━━━━━━━

{missing_list}

━━━━━━━━━━━━━━━━━━━━
📚 LEARNING RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━

{courses_formatted}

━━━━━━━━━━━━━━━━━━━━

Why?

{data['explanation']}
"""
    return {
        "success": True,
        "data": {
            "analysis_id": analysis_id,
            "report": report_text.strip()
        },
        "requestId": str(uuid.uuid4())
    }
