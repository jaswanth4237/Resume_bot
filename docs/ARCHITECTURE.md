# ARCHITECTURE.md — ResumeMatch AI System Architecture

## Overview

ResumeMatch AI is a **hybrid AI recruitment assistance system** where:
- **LLMs** are used for document understanding and structured extraction only.
- **Application code** performs all scoring, eligibility decisions, and gap analysis.
- **Telegram** provides the user-facing interface.

---

## High-Level Data Flow

```
Resume (PDF/DOCX/TXT)          Job Description (PDF/DOCX/TXT)
        │                                   │
        ▼                                   ▼
  Document Parser                    Document Parser
  (pdf-parse / mammoth)              (pdf-parse / mammoth)
        │                                   │
        ▼                                   ▼
  Resume Extractor                   JD Extractor
  (rule-based + alias dict)          (rule-based + alias dict)
        │                                   │
        ▼                                   ▼
  Normalized Resume JSON             Normalized JD JSON
        │                                   │
        └───────────┬───────────────────────┘
                    │
                    ▼
            Skill Matching Engine
            (Exact → Alias/Partial → Missing)
                    │
                    ▼
            Experience Matcher
            (required vs. candidate years)
                    │
                    ▼
            Deterministic Scoring Engine
            (configurable weights)
                    │
                    ▼
            Eligibility Engine
            (SUITABLE / BORDERLINE / REJECT)
                    │
                    ▼
            Gap Analysis Engine
            (CRITICAL / HIGH / MEDIUM / LOW)
                    │
                    ▼
            Course Recommendation Engine
            (curated catalog, no invented URLs)
                    │
                    ▼
            MongoDB Persistence (optional)
                    │
                    ▼
            Telegram Report / REST API Response
```

---

## Component Descriptions

### `src/parsers/documentParser.js`
Handles raw file bytes → plain text extraction.
- PDF: `pdf-parse`
- DOCX: `mammoth`
- TXT: direct buffer decoding
- Throws `DocumentProcessingError` with specific error codes on failure.

### `src/ai/extractors.js`
Converts raw text into normalized JSON objects.
- `extractResume(text)` → Resume JSON (candidate info, skills, experience, education)
- `extractJobDescription(text)` → JD JSON (mandatory/preferred requirements, responsibilities)
- Uses `skill_aliases.json` for normalization.
- Rule-based with LLM integration available via `LLM_API_KEY`.

### `src/matching/skillMatcher.js`
Three-level matching:
1. **Exact match** — normalized skill names are identical.
2. **Partial/alias match** — token overlap or alias dictionary hit, subject to `strict_inequivalent` pairs.
3. **Missing** — no evidence found in resume.

### `src/matching/scoring.js`
Deterministic scoring. Weights are defined centrally:
```
Skills:         50%
Experience:     20%
Responsibilities: 15%
Education:       5%
Preferred:      10%
```
Always produces the same result for the same input.

### `src/matching/eligibility.js`
Separate from scoring. Checks:
- Missing mandatory skills → REJECT
- Experience gap against mandatory minimum → REJECT
- Education not satisfied (when mandatory) → REJECT
- Score ≥ SUITABLE_THRESHOLD → SUITABLE
- Score ≥ BORDERLINE_THRESHOLD → BORDERLINE
- Otherwise → REJECT

### `src/services/analysisService.js`
Orchestrates the full analysis pipeline for one JD + one or more resumes.

### `src/services/courseService.js`
Maps identified gaps to curated course records from `data/courses.json`.
No URLs are generated dynamically — all are in the static catalog.

### `src/services/persistenceService.js`
Wraps MongoDB persistence (gracefully degrades if MongoDB is unavailable).
In-memory Map provides fallback for the current process lifetime.

### `src/telegram/bot.js`
Stateful session handler per Telegram user ID.
Business logic is NOT in handlers — handlers call `analysisService`.

### `src/db/mongo.js`
Mongoose connection with graceful degradation.

### `src/db/redis.js`
Redis client stub — configurable via `REDIS_URL`. Provides status reporting.

---

## Technology Stack

| Concern              | Technology                    |
|----------------------|-------------------------------|
| Runtime              | Node.js 20+                   |
| Web Framework        | Express.js                    |
| Bot Framework        | grammY                        |
| PDF Parsing          | pdf-parse                     |
| DOCX Parsing         | mammoth                       |
| Database (optional)  | MongoDB via Mongoose          |
| Cache (optional)     | Redis                         |
| Container            | Docker + Docker Compose        |
| Reverse Proxy        | Nginx                         |
| Test Runner          | Node.js built-in test runner  |

---

## Deployment Topology

```
Internet
    │
    ▼
[Nginx :80]
    │
    ▼
[Express Backend :8000]
    ├── MongoDB Atlas (optional durable storage)
    └── Redis (optional session/cache)

Telegram Servers
    │
    ▼
[grammY long-poll worker]  (separate process: npm run worker)
    │
    └── calls analysisService directly (in same process)
```

For production webhook mode, Telegram sends updates to `POST /telegram/webhook` through Nginx.

---

## Security Considerations

- All secrets sourced from environment variables only.
- Files treated as untrusted binary input.
- File size limited by `MAX_FILE_SIZE_MB`.
- MIME/extension validation before parsing.
- No stack traces exposed to Telegram users.
- Resumes not logged, stored persistently only when MongoDB is configured.
- Non-root Docker user.
