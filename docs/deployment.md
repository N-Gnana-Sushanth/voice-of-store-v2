# Voice of Store — Render Deployment & Production Guide

## 1. Prerequisites

- A [Render](https://render.com/) account.
- Git repository containing this backend codebase.
- Render PostgreSQL database (or external managed PostgreSQL).

## 2. Infrastructure as Code: `render.yaml`

The repository includes a complete `render.yaml` blueprint defining the Web Service and PostgreSQL database.

### Deploying via Render Blueprint:
1. Push this repository to GitHub or GitLab.
2. In the Render Dashboard, navigate to **Blueprints** -> **New Blueprint Instance**.
3. Select your repository. Render will automatically parse `render.yaml` and configure:
   - Web Service: `voice-of-store-backend` (Python 3.12+ runtime)
   - Database: `voice-of-store-db` (PostgreSQL)
4. Click **Apply**.

---

## 3. Manual Deployment Setup on Render

If creating the services manually through the Render UI:

### Step 3.1: Create PostgreSQL Database
1. Go to **Dashboard** -> **New +** -> **PostgreSQL**.
2. Name: `voice-of-store-db`
3. Database: `voice_of_store`
4. User: `store_admin`
5. Plan: `Free` or higher.
6. Click **Create Database** and copy the **Internal Database URL**.

### Step 3.2: Create Web Service
1. Go to **Dashboard** -> **New +** -> **Web Service**.
2. Connect your Git repository.
3. Configure settings:
   - **Name**: `voice-of-store-backend`
   - **Environment**: `Python`
   - **Region**: Same region as your PostgreSQL instance (e.g. Oregon).
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`

### Step 3.3: Configure Environment Variables
In the Web Service **Environment** tab, configure:

| Key | Example Value | Description |
|---|---|---|
| `ENVIRONMENT` | `production` | Deployment environment |
| `DEBUG` | `false` | Disable debug mode |
| `DATABASE_URL` | `postgresql+psycopg://user:pass@host/voice_of_store` | Render PostgreSQL Internal Connection String |
| `SECRET_KEY` | *(Generate 32+ character random secret)* | JWT signing secret |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token expiration in minutes |
| `CORS_ORIGINS` | `https://your-frontend.onrender.com,http://localhost:3000` | Allowed frontend origins |
| `MAX_REQUEST_BODY_BYTES` | `2097152` | 2MB payload guard |
| `RATE_LIMIT_PER_MINUTE` | `120` | Rate limiting for sensitive routes |
| `INITIAL_ADMIN_EMAIL` | `admin@voiceofstore.internal` | Bootstrap admin email |
| `INITIAL_ADMIN_PASSWORD` | `YourSecureAdminPassword123!` | Bootstrap admin password |

---

## 4. Database Migrations

Database migrations run automatically during the Render build phase via:
```bash
alembic upgrade head
```
If you need to run migrations manually from a Render shell:
```bash
alembic upgrade head
```

---

## 5. Verification Probes

Once deployed, verify health and readiness:
```bash
# 1. Liveness Probe
curl -i https://<your-service>.onrender.com/health

# 2. Readiness Probe (checks DB & ML model)
curl -i https://<your-service>.onrender.com/ready

# 3. Interactive OpenAPI documentation
https://<your-service>.onrender.com/docs
```
