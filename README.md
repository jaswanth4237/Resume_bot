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
- Node.js 20+
- A MongoDB deployment (optional for local deterministic API use; required for durable analyses/users)
- Redis is optional

### 1. Environment Setup
From the repository root, enter the backend directory and copy `.env.example` to `.env`:
```bash
cd backend
cp .env.example .env
```
Set `MONGODB_URI` when a MongoDB cluster is available. Add `TELEGRAM_BOT_TOKEN` to run the bot worker.

### 2. Start Application
```bash
npm install
npm start
```

For development, use `npm run dev`. Run the Telegram worker separately with `npm run worker`.

### 3. Verify Health Endpoint
```bash
curl http://localhost:8000/api/v1/health
```

## ☁️ Optional Render Deployment

Render is not required for local use or testing. Deploy to Render when the API or Telegram bot must run continuously online.

This repository includes a [`render.yaml`](render.yaml) Blueprint that creates:
- A Web Service for the Node.js API
- A Background Worker for Telegram polling
- A Redis service

For a manual Render Web Service, set Root Directory to `backend` and use:
- Build command: `npm ci`
- Start command: `npm start`

For the separate Background Worker, use the same build command and `npm run worker` as the start command. Set `MONGODB_URI`, `TELEGRAM_BOT_TOKEN`, and optionally `REDIS_URL` and `LLM_API_KEY`. Render may require a paid instance for the Background Worker; choose a plan available to your account.

---

## 🧪 Running Tests
```bash
cd backend
npm test
```

The Node.js API preserves the versioned routes under `/api/v1`: health, JD upload, resume upload, analysis, analysis reports, and courses.

---

## 📚 Documentation
- [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [API.md](docs/API.md)
- [SCORING.md](docs/SCORING.md)
- [EVALUATION.md](docs/EVALUATION.md)
- [TECH_STACK.md](TECH_STACK.md)
