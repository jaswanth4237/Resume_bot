# API.md — ResumeMatch AI REST API Reference

Base URL: `http://localhost:8000/api/v1`

All responses follow a consistent envelope format.

---

## Response Envelope

### Success
```json
{
  "success": true,
  "data": {},
  "requestId": "uuid-v4"
}
```

### Error
```json
{
  "success": false,
  "detail": {
    "code": "ERROR_CODE",
    "message": "Human-readable description"
  }
}
```

---

## Error Codes

| Code                        | HTTP Status | Description                          |
|-----------------------------|-------------|--------------------------------------|
| `INVALID_FILE`              | 400         | No file provided or unreadable       |
| `UNSUPPORTED_FORMAT`        | 400         | File extension not pdf/docx/txt      |
| `PARSE_ERROR`               | 400         | File could not be parsed             |
| `INVALID_RESUME`            | 400         | Resume/JD file missing from request  |
| `ANALYSIS_NOT_FOUND`        | 404         | Analysis ID does not exist           |
| `INTERNAL_SERVER_ERROR`     | 500         | Unhandled server error               |

---

## Endpoints

---

### `GET /api/v1/health`

Returns service health status.

**Response (200)**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "services": {
      "database": "connected",
      "redis": "disabled"
    }
  },
  "requestId": "uuid"
}
```

`status` values: `healthy` | `degraded`
`database` values: `connected` | `disconnected` | `disabled`
`redis` values: `connected` | `configured` | `disabled`

---

### `POST /api/v1/jd/upload`

Upload and parse a Job Description. Returns structured extraction.

**Request** — `multipart/form-data`

| Field  | Type | Required | Description          |
|--------|------|----------|----------------------|
| `file` | File | ✅        | PDF, DOCX, or TXT    |

**Response (200)**
```json
{
  "success": true,
  "data": {
    "filename": "backend_jd.pdf",
    "job_title": "Java Backend Developer",
    "mandatory_requirements": {
      "skills": ["Java", "Spring Boot", "Microservices"],
      "minimum_experience_years": 3
    },
    "preferred_requirements": {
      "skills": ["Docker", "AWS", "Kubernetes"]
    },
    "responsibilities": ["Develop backend services", "Build REST APIs"],
    "raw_text_length": 1247
  },
  "requestId": "uuid"
}
```

---

### `POST /api/v1/resume/upload`

Upload and parse a candidate Resume. Returns structured extraction.

**Request** — `multipart/form-data`

| Field  | Type | Required | Description          |
|--------|------|----------|----------------------|
| `file` | File | ✅        | PDF, DOCX, or TXT    |

**Response (200)**
```json
{
  "success": true,
  "data": {
    "filename": "john_doe_resume.pdf",
    "candidate": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890"
    },
    "skills_count": 8,
    "skills": [
      { "name": "Java", "level": "intermediate", "years": 0, "evidence": "Found in document as Java" }
    ],
    "total_experience_years": 3,
    "raw_text_length": 2103
  },
  "requestId": "uuid"
}
```

---

### `POST /api/v1/analyze`

Run the full matching + scoring pipeline for one JD and one or more resumes.

**Request** — `multipart/form-data`

| Field           | Type    | Required | Description                              |
|-----------------|---------|----------|------------------------------------------|
| `jd_file`       | File    | ✅        | Job Description (PDF/DOCX/TXT)           |
| `resume_file`   | File    | ✅        | Single resume (can combine with below)   |
| `resume_files`  | File[]  | ❌        | Additional resumes for batch ranking     |

**Single resume response (200)**
```json
{
  "success": true,
  "data": {
    "analysis_id": "uuid",
    "candidate": { "name": "John Doe", "email": "john@example.com" },
    "job_title": "Java Backend Developer",
    "overall_score": 78,
    "decision": "BORDERLINE",
    "decision_reasons": ["Candidate satisfies mandatory requirements and meets borderline score threshold."],
    "category_scores": {
      "skills": 82,
      "experience": 67,
      "responsibilities": 100,
      "education": 100,
      "preferred": 50
    },
    "matched_requirements": ["Java", "Spring Boot"],
    "partial_requirements": ["Microservices", "AWS"],
    "missing_requirements": ["Docker"],
    "mandatory_failures": [],
    "experience_gap": { "required_years": 3, "candidate_years": 2.4, "gap_years": 0.6 },
    "gaps": [
      { "skill": "Docker", "gap_type": "MISSING_SKILL", "priority": "CRITICAL", "description": "Missing mandatory skill: Docker" }
    ],
    "explanation": "Candidate has 1 critical requirement gaps.",
    "course_recommendations": [
      { "skill": "Docker", "title": "Docker Fundamentals", "platform": "Docker Docs", "level": "Beginner", "url": "https://docs.docker.com/get-started/", "duration": "6 hours", "gap_skill": "Docker" }
    ]
  },
  "requestId": "uuid"
}
```

**Multiple resumes response (200)**
```json
{
  "success": true,
  "data": {
    "job_title": "Java Backend Developer",
    "total_candidates": 3,
    "rankings": [
      { "rank": 1, "candidate_name": "Alice", "score": 91, "decision": "SUITABLE", "analysis_id": "uuid1" },
      { "rank": 2, "candidate_name": "Bob", "score": 74, "decision": "BORDERLINE", "analysis_id": "uuid2" },
      { "rank": 3, "candidate_name": "Carol", "score": 45, "decision": "REJECT", "analysis_id": "uuid3" }
    ],
    "detailed_results": [...]
  },
  "requestId": "uuid"
}
```

---

### `GET /api/v1/analysis/:analysisId`

Retrieve a previously computed analysis result.

**Response (200)** — Same as the single-resume `POST /api/v1/analyze` response data object.

**Response (404)**
```json
{ "success": false, "detail": { "code": "ANALYSIS_NOT_FOUND", "message": "Analysis ID 'xyz' not found." } }
```

---

### `GET /api/v1/analysis/:analysisId/report`

Get a human-readable plain-text report for an analysis.

**Response (200)**
```json
{
  "success": true,
  "data": {
    "analysis_id": "uuid",
    "report": "RESUME MATCH REPORT\n\nCandidate: John Doe\nPosition: Java Backend Developer\n..."
  },
  "requestId": "uuid"
}
```

---

### `GET /api/v1/courses`

Return the full course catalog.

**Response (200)**
```json
{
  "success": true,
  "data": {
    "total_courses": 8,
    "courses": [
      { "skill": "Docker", "title": "Docker Fundamentals", "platform": "Docker Docs", "level": "Beginner", "url": "https://docs.docker.com/get-started/", "duration": "6 hours" }
    ]
  },
  "requestId": "uuid"
}
```
