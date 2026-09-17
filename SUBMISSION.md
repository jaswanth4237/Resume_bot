# SUBMISSION.md — ResumeMatch AI Project Submission Details

## Project Summary
ResumeMatch AI is an intelligent, explainable recruitment assistance system and Telegram Bot that analyzes candidate resumes against Job Descriptions (JDs). It features structured document extraction using LLMs, semantic skill matching, a 100% deterministic scoring and eligibility decision engine, gap analysis, and course recommendations.

## Core Features Implemented
- **Telegram Bot Interface**: Upload JDs and Resumes, initiate analysis, receive structured reports.
- **Multi-Format Document Processing**: Extraction support for PDF, DOCX, and TXT files.
- **LLM Information Extraction**: Robust Pydantic-validated JSON extraction for Resumes and JDs.
- **Skill Normalization & Semantic Matching**: Exact, semantic (embedding-based), and alias matching.
- **Deterministic Scoring Engine**: Configurable category weights (Skills 50%, Experience 20%, Responsibilities 15%, Education 5%, Preferred 10%).
- **Eligibility Engine**: Hard-constraint checking for mandatory requirements resulting in SUITABLE, BORDERLINE, or REJECT status.
- **Gap Analysis & Course Recommendations**: Curated course mappings for identified missing or partial skill gaps.
- **Infrastructure**: Express.js backed by MongoDB, with optional Redis caching.

## Health Check Endpoint
- **URL**: `http://localhost:8000/api/v1/health`
- **Response**: Returns HTTP 200 OK with PostgreSQL, Redis, and overall app health metrics.

## Verification & Testing
- Run the Node.js test suite: `npm test`
- Start the API locally: `npm start`
