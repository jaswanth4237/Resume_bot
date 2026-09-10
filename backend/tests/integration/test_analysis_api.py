import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_courses_api_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/courses")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "courses" in json_data["data"]
    assert len(json_data["data"]["courses"]) > 0


@pytest.mark.asyncio
async def test_analyze_api_endpoint(async_client: AsyncClient):
    jd_content = b"Java Developer required. Mandatory: Java, Spring Boot. 3+ years experience required."
    resume_content = b"John Doe. 4 years Java, Spring Boot, MySQL developer."

    files = {
        "jd_file": ("jd.txt", jd_content, "text/plain"),
        "resume_file": ("resume.txt", resume_content, "text/plain")
    }

    response = await async_client.post("/api/v1/analyze", files=files)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "overall_score" in json_data["data"]
    assert json_data["data"]["decision"] in ["SUITABLE", "BORDERLINE", "REJECT"]
