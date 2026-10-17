# Voice of Store — Backend Platform

> Intelligent feedback and emerging-issue detection platform for multi-store retail and grocery operations.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![SQLAlchemy 2.x](https://img.shields.io/badge/SQLAlchemy-2.0+-red?style=flat)](https://www.sqlalchemy.org)
[![Alembic](https://img.shields.io/badge/Alembic-Migrations-blue?style=flat)](https://alembic.sqlalchemy.org)
[![Tests](https://img.shields.io/badge/Tests-37%20Passed-brightgreen?style=flat)]()

---

## 1. Project Overview

**Voice of Store** is a specialized backend platform designed to ingest customer and employee feedback across multiple store locations, transform raw unstructured text into consolidated operational incidents, detect urgent safety and allergen concerns, normalize incident rates by customer traffic, and identify emerging operational anomalies before they escalate.

### Key Capabilities:
- **Mandatory Processing Order**:
  $$\text{Feedback Ingestion} \rightarrow \text{Preprocessing} \rightarrow \text{ML Classification} \rightarrow \text{Deduplication} \rightarrow \text{Safety Policy} \rightarrow \text{Persistence} \rightarrow \text{Analytics/Alerts}$$
- **Zero Raw Data Loss**: Consolidates near-duplicates without ever discarding source feedback records.
- **Deterministic Safety & Allergen Engine**: Detects physical hazards and allergens with context and negation awareness (e.g. distinguishing *"confirmed no peanuts"* from an active contamination emergency).
- **Exposure-Normalized Analytics**: Calculates incident density per 1,000 customer transactions, preventing distorted comparisons between large and small stores.
- **Explainable Emerging Issue Detection**: Statistical alerts powered by Poisson and Normal Z-scores, rate ratios, historical baselines, and peer store benchmarks.
- **Chronological Replay Engine**: Sequential simulation evaluated against 3 synthetic ground-truth incidents (`PLANTED-001`, `PLANTED-002`, `PLANTED-003`) with verified zero future-data leakage.
- **Role-Based Access Control (RBAC)**: Enforces access tiers (`admin`, `store_manager`, `analyst`) with store-level data isolation.

---

## 2. Technology Stack

- **Language**: Python 3.12+ (tested up to 3.14)
- **Framework**: FastAPI & Uvicorn
- **Validation**: Pydantic v2 & Pydantic-Settings
- **Database**: PostgreSQL (Production / Render), SQLite (Local Dev / Isolated Testing)
- **ORM & Migrations**: SQLAlchemy 2.x & Alembic
- **Machine Learning & NLP**: scikit-learn (TF-IDF + calibrated Logistic Regression) & NumPy
- **Authentication**: Argon2id (`argon2-cffi`) & PyJWT
- **Testing**: pytest & HTTPX
- **Deployment**: Render Web Service & Render PostgreSQL (`render.yaml` & `Dockerfile`)

---

## 3. Directory Layout

```
voice-of-store-backend/
├── app/
│   ├── api/                  # API routers, dependency injection, and RBAC
│   │   ├── deps.py           # Database session, get_current_user, require_roles, check_store_access
│   │   └── v1/               # Health, Auth, Stores, Feedback, Incidents, Analytics, Alerts, Replay
│   ├── core/                 # Config, Database engine, Argon2id security, logging, middlewares
│   ├── models/               # SQLAlchemy 2.0 ORM models (Stores, Users, Feedback, Incidents, etc.)
│   ├── schemas/              # Pydantic v2 request/response contracts
│   ├── services/             # Pipeline services (NLP, Classifier, Policy Engine, Deduplication, etc.)
│   └── main.py               # FastAPI entry point, CORS, correlation ID, structured exception handling
├── alembic/                  # Database migration scripts
├── docs/                     # Comprehensive architecture and API documentation
│   ├── architecture.md
│   ├── database-schema.md
│   ├── api-contract.md
│   ├── emerging-issue-detection.md
│   ├── replay-and-evaluation.md
│   └── deployment.md
├── tests/                    # Comprehensive pytest test suite (37 tests)
├── .env.example              # Documented configuration template
├── Dockerfile                # Production multi-stage Docker container
├── render.yaml               # Render Infrastructure-as-Code deployment blueprint
├── requirements.txt          # Production pinned dependencies
└── README.md
```

---

## 4. Local Development Setup

### 4.1. Prerequisites
- Python 3.12+
- Git

### 4.2. Virtual Environment & Dependencies
```bash
# 1. Clone repository and navigate to workspace
cd voice-of-store-backend

# 2. Create and activate virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### 4.3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Key settings:
- `DATABASE_URL`: `sqlite:///./voice_of_store.db` (or PostgreSQL: `postgresql+psycopg://user:password@localhost:5432/voice_of_store`)
- `SECRET_KEY`: Random 32+ character key.
- `INITIAL_ADMIN_EMAIL`: `admin@voiceofstore.internal`
- `INITIAL_ADMIN_PASSWORD`: Set a secure initial administrator password.

### 4.4. Run Database Migrations
```bash
alembic upgrade head
```

### 4.5. Start Local Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Open your browser to:
- **Interactive OpenAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Liveness Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Readiness Health Check**: [http://localhost:8000/ready](http://localhost:8000/ready)

---

## 5. Automated Test Suite

Run the full pytest suite:
```bash
pytest -v
```

All 37 automated tests validate:
- Health and readiness probes
- Argon2id password hashing and JWT issuance
- Single and batch feedback ingestion with idempotency protection
- ML category classification and sentiment-severity independence
- Deterministic safety and allergen policy rules with negation awareness
- Multi-signal deduplication and cross-store isolation
- Distinct incident analytics and transaction exposure normalization
- Emerging-issue detection, low-sample guards, and duplicate alert suppression
- Chronological replay evaluation against 3 planted incidents
- Mathematical proof of zero future-data leakage
- RBAC and store manager data access restrictions

---

## 6. Render Deployment

The backend is fully configured for deployment on Render.

1. **Option A (Blueprint)**: Connect your Git repo to Render and choose **New Blueprint Instance**. Render will automatically provision the PostgreSQL database and Web Service specified in `render.yaml`.
2. **Option B (Manual Web Service)**:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`

For complete deployment details, see [`docs/deployment.md`](docs/deployment.md).

---

## 7. Known Limitations & Next Improvements

- **Async Database Driver**: Currently synchronous SQLAlchemy with `psycopg` is used for rock-solid stability and easy SQLite test execution. Async SQLAlchemy with `asyncpg` can be introduced if high concurrent connection limits are required.
- **Deep Semantic Embeddings**: Classification uses calibrated TF-IDF + Logistic Regression, providing immediate millisecond inference on modest CPU instances. A fine-tuned transformer or small local embedding model (e.g. `all-MiniLM-L6-v2`) can be added for deeper synonym matching when GPU resources are available.
- **Exposure Metric Ingestion**: Store exposure currently uses configured `avg_daily_transactions`. Future extensions can introduce an hourly POS transaction ingestion feed to calculate dynamic exposure windows.
