# Voice of Store — REST API Contract Documentation

## 1. Conventions

- **Base URL**: `http://localhost:8000` (or your Render URL: `https://<service-name>.onrender.com`)
- **API Version Prefix**: `/api/v1`
- **Interactive Documentation**:
  - Swagger UI: `/docs`
  - ReDoc: `/redoc`
  - OpenAPI JSON: `/openapi.json`
- **Authentication**: Bearer JWT passed in header: `Authorization: Bearer <token>`
- **Correlation Tracking**: Client or server-generated UUID in `X-Correlation-ID` header.
- **Structured Error Format**:
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human-readable explanation of error.",
      "details": {}
    }
  }
  ```

---

## 2. API Endpoints Reference

### 2.1. Health & Probes
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | Public | Liveness probe returning server status and version |
| `GET` | `/ready` | Public | Readiness probe checking database and ML classifier status |
| `GET` | `/api/v1/health` | Public | Versioned liveness probe |
| `GET` | `/api/v1/ready` | Public | Versioned readiness probe |

### 2.2. Authentication (`/api/v1/auth`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/login` | Public (Rate-limited) | Login with email and password; returns JWT |
| `GET` | `/api/v1/auth/me` | Authenticated | Retrieve current user profile and role |
| `POST` | `/api/v1/auth/users` | Admin Only | Create system user (`admin`, `store_manager`, `analyst`) |

#### Sample Login Request:
```json
POST /api/v1/auth/login
{
  "email": "admin@voiceofstore.internal",
  "password": "your_secure_password"
}
```
#### Sample Login Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "expires_in_seconds": 86400,
  "user": {
    "id": "b3e0c0d8-...",
    "email": "admin@voiceofstore.internal",
    "full_name": "System Administrator",
    "role": "admin",
    "store_id": null,
    "is_active": true,
    "created_at": "2026-10-17T18:00:00Z"
  }
}
```

---

### 2.3. Stores (`/api/v1/stores`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/stores` | Admin Only | Create new retail store with exposure baseline |
| `GET` | `/api/v1/stores` | Authenticated | List stores (paginated; filtered for store managers) |
| `GET` | `/api/v1/stores/{store_id}` | Authenticated | Get store details (enforces store isolation) |
| `PATCH` | `/api/v1/stores/{store_id}` | Admin Only | Update store floor area or transaction metrics |

#### Sample Store Create Request:
```json
POST /api/v1/stores
{
  "store_number": "STORE-101",
  "name": "Downtown Grocery Supercenter",
  "address": "100 Michigan Ave",
  "city": "Chicago",
  "state": "IL",
  "size_sqft": 30000.0,
  "avg_daily_transactions": 3500.0
}
```

---

### 2.4. Feedback (`/api/v1/feedback`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/feedback` | Public / Ingestion Key | Ingest single feedback record with idempotency protection |
| `POST` | `/api/v1/feedback/batch` | Public / Ingestion Key | Ingest batch of up to 500 records with isolated savepoints |
| `GET` | `/api/v1/feedback` | Authenticated | List raw feedback records with filters and pagination |
| `GET` | `/api/v1/feedback/{feedback_id}` | Authenticated | Get single raw feedback record details |

#### Sample Feedback Submission:
```json
POST /api/v1/feedback
{
  "store_id": "STORE-101",
  "text": "Card reader in lane 3 froze during checkout and charged my card twice.",
  "source": "customer",
  "event_timestamp": "2026-10-17T14:30:00Z",
  "idempotency_key": "pos-terminal-retry-10192",
  "metadata": {"terminal_id": "POS-3"}
}
```

---

### 2.5. Incidents (`/api/v1/incidents`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/incidents` | Authenticated | List consolidated incidents (filter by store, category, severity, safety) |
| `GET` | `/api/v1/incidents/{incident_id}` | Authenticated | Retrieve incident with all linked raw feedback records |
| `GET` | `/api/v1/incidents/{incident_id}/feedback` | Authenticated | Retrieve source feedback records linked to incident |
| `PATCH` | `/api/v1/incidents/{incident_id}/status` | Admin / Store Manager | Update incident status (`OPEN`, `UNDER_INVESTIGATION`, `RESOLVED`, `DISMISSED`) |

---

### 2.6. Analytics (`/api/v1/analytics`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/analytics/summary` | Authenticated | Store or consolidated metrics, breakdowns, and normalized rate per 1,000 transactions |
| `GET` | `/api/v1/analytics/comparisons` | Authenticated | Normalized side-by-side store comparisons avoiding raw volume distortion |

#### Query Parameters for `/api/v1/analytics/summary`:
- `store_id` (optional): Filter to a specific store.
- `time_window_days` (default 30): Observation window in days.

---

### 2.7. Emerging Issues (`/api/v1/alerts`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/alerts` | Authenticated | List active and historical alerts |
| `GET` | `/api/v1/alerts/{alert_id}` | Authenticated | Get alert with full statistical evidence breakdown |
| `POST` | `/api/v1/alerts/scan` | Admin / Analyst | Trigger network emerging issue detection scan |
| `POST` | `/api/v1/alerts/{alert_id}/acknowledge` | Admin / Store Manager | Acknowledge active alert |
| `POST` | `/api/v1/alerts/{alert_id}/resolve` | Admin / Store Manager | Resolve alert with mandatory documented action notes |

---

### 2.8. Replay & Evaluation (`/api/v1/replay`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/replay` | Admin / Analyst | Launch deterministic chronological event-time replay simulation |
| `GET` | `/api/v1/replay` | Admin / Analyst | List historical replay experiments |
| `GET` | `/api/v1/replay/{replay_id}` | Admin / Analyst | Retrieve evaluation metrics, detection lead times, and planted incident results |
