# TECH_STACK.md — ResumeMatch AI Technology Stack

## 1. Core Application Frameworks
* **Language**: Python 3.11+
* **Backend Web Framework**: FastAPI (Async/ASGI)
* **Async Server**: Uvicorn / Gunicorn
* **Bot Framework**: python-telegram-bot (v20+ async)

## 2. Document Processing & Extraction
* **PDF Processing**: `pypdf`, `pdfplumber`
* **DOCX Processing**: `python-docx`
* **Text Processing**: Built-in standard library & regex

## 3. Data Extraction & AI Integration
* **LLM Provider Integration**: OpenAI API / LangChain / Pydantic AI for structured JSON output
* **Structured Output Validation**: `pydantic` (v2)
* **Embedding Model**: OpenAI `text-embedding-3-small` / Sentence-Transformers (Semantic Matching)

## 4. Matching & Scoring Engine
* **Deterministic Scoring Engine**: Custom Python business logic
* **Normalization Engine**: Custom alias dictionary + fuzzy/semantic string matching (`rapidfuzz`, Cosine Similarity)
* **Eligibility Engine**: Deterministic rules engine (Mandatory vs. Preferred constraints)

## 5. Storage & Caching
* **Relational Database**: PostgreSQL 15+
* **ORM**: SQLAlchemy (v2.0 Async Session) + AsyncPG
* **Database Migrations**: Alembic
* **Cache & Session Management**: Redis (v7+) using `redis-py` (asyncio)

## 6. Testing & Quality Assurance
* **Test Runner**: `pytest`, `pytest-asyncio`, `pytest-cov`
* **Linting & Formatting**: `ruff`, `mypy`

## 7. Infrastructure & Deployment
* **Containerization**: Docker & Docker Compose
* **Reverse Proxy**: NGINX
* **Monitoring**: Prometheus & Grafana (health metrics, request duration, match distributions)
