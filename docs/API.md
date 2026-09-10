# API.md — REST API Specification

All endpoints are versioned under `/api/v1`.

## Endpoints

### 1. Health Check
`GET /api/v1/health`
- **Response**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "services": {
      "database": "connected",
      "redis": "connected"
    }
  },
  "requestId": "uuid"
}
```

### 2. Upload Job Description
`POST /api/v1/jd/upload`

### 3. Upload Candidate Resume
`POST /api/v1/resume/upload`

### 4. Analyze Match
`POST /api/v1/analyze`

### 5. Get Analysis Result
`GET /api/v1/analysis/{analysis_id}`

### 6. Get Analysis Report
`GET /api/v1/analysis/{analysis_id}/report`

### 7. List Available Courses
`GET /api/v1/courses`
