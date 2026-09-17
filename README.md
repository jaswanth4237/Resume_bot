# ResumeMatch AI — Intelligent Resume & Job Description Matching Telegram Bot

## 🚀 Overview
**ResumeMatch AI** is a production-ready AI-powered recruitment assistance platform. It analyzes candidate resumes against Job Descriptions (JDs), calculates an explainable compatibility score, determines candidate suitability, identifies skill/experience gaps, and recommends targeted learning resources.

### Key Highlights
- **100% Deterministic Decisions**: LLMs perform structured extraction; application code handles scoring & eligibility.
- **Telegram Bot Interface**: Instant candidate screening through Telegram file uploads.
- **Multi-Format Parsing**: Supports PDF, DOCX, and TXT files.
- **Skill Normalization & Semantic Matching**: Exact, alias, and vector embedding matching.
- **Gap & Course Recommendations**: Maps skill gaps to curated courses without fake links.

---

## 🛠️ Architecture & Core Principles
```
Resume Document ──► Parser ──► LLM Extractor ──► Resume JSON ──┐
                                                               ├──► Matching Engine ──► Deterministic Scoring Engine ──► Eligibility Engine ──► Gap Analysis & Courses ──► Telegram Report
Job Description ──► Parser ──► LLM Extractor ──► JD JSON     ──┘
```

---

## 🚦 Quick Start

### Prerequisites
- Python 3.11+ (for local development)
- PostgreSQL 15+
- Redis 7+

### 1. Environment Setup
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your credentials (`TELEGRAM_BOT_TOKEN`, `LLM_API_KEY`).

### 2. Start Application
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Verify Health Endpoint
```bash
curl http://localhost:8000/api/v1/health
```

## ☁️ Optional Render Deployment

Render is not required for local use or testing. Deploy to Render when the API or Telegram bot must run continuously online.

This repository includes a [`render.yaml`](render.yaml) Blueprint that creates:
- A Web Service for the FastAPI API
- A Background Worker for Telegram polling
- A PostgreSQL database
- A Redis service

To deploy, create a Blueprint in the Render dashboard from this repository, then enter the prompted `TELEGRAM_BOT_TOKEN` and `LLM_API_KEY` values. The worker must remain a separate service because Telegram polling and the API server are separate long-running processes. Render may require a paid instance for the Background Worker; choose a plan available to your account.

---

## 🧪 Running Tests
```bash
cd backend
pytest
```

---

## 📚 Documentation
- [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [API.md](docs/API.md)
- [SCORING.md](docs/SCORING.md)
- [EVALUATION.md](docs/EVALUATION.md)
- [TECH_STACK.md](TECH_STACK.md)
