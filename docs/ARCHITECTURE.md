# ARCHITECTURE.md — System Architecture & Component Design

## 1. Architectural Overview
ResumeMatch AI uses a decoupled hybrid AI pipeline. The system enforces strict separation between **Document Intelligence** (unstructured data parsing via LLM) and **Decision Logic** (deterministic scoring and eligibility engines in application code).

## 2. Core Service Modules
- **Document Service**: Parses PDF, DOCX, and TXT files into clean text.
- **AI Extraction Service**: Calls LLM to extract schema-valid structured JSON for Resumes and JDs.
- **Skill Normalizer**: Maps skill variations (e.g. "Postgres" -> "PostgreSQL") using alias rules.
- **Matching Engine**: Performs exact, semantic (embeddings), and gap analysis on candidate skills vs. JD skills.
- **Deterministic Scoring Engine**: Computes transparent category scores and overall match percentage.
- **Eligibility Engine**: Evaluates mandatory requirements (e.g., min experience, mandatory skills) to issue SUITABLE, BORDERLINE, or REJECT decisions.
- **Course Recommendation Engine**: Recommends verified courses for identified missing/partial skills.
- **Telegram Bot Service**: User interface for file uploads and structured report formatting.

## 3. Data & Storage Layer
- **PostgreSQL**: Stores users, analysis sessions, JDs, resumes, match results, gaps, and course catalogs.
- **Redis**: Handles temporary session state, rate limiting, and task queueing.
