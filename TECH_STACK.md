# TECH_STACK.md — ResumeMatch AI Technology Stack

## 1. Core Application Frameworks
* **Language**: Node.js 20+
* **Backend Web Framework**: Express.js
* **HTTP Server**: Node.js
* **Bot Framework**: grammY

## 2. Document Processing & Extraction
* **PDF Processing**: `pdf-parse`
* **DOCX Processing**: `mammoth`
* **Text Processing**: Node.js built-ins & regex

## 3. Data Extraction & AI Integration
* **LLM Provider Integration**: Configurable LLM API integration
* **Structured Output Validation**: JavaScript object validation
* **Embedding Model**: Configurable semantic matching integration

## 4. Matching & Scoring Engine
* **Deterministic Scoring Engine**: Custom JavaScript business logic
* **Normalization Engine**: Custom alias dictionary + fuzzy/semantic string matching
* **Eligibility Engine**: Deterministic rules engine (Mandatory vs. Preferred constraints)

## 5. Storage & Caching
* **Document Database**: MongoDB via Mongoose
* **Database Models**: Mongoose schemas
* **Cache & Session Management**: Optional Redis-compatible service

## 6. Testing & Quality Assurance
* **Test Runner**: Node.js built-in test runner

## 7. Infrastructure & Deployment
* **Monitoring**: Prometheus & Grafana (health metrics, request duration, match distributions)
