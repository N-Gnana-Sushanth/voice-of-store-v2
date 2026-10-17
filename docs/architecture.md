# Voice of Store — Backend Architecture Documentation

## 1. System Overview

Voice of Store is an intelligent feedback and emerging-issue detection platform built for multi-store retail and grocery operations. It collects unstructured customer feedback and employee observations, standardizes them into structured operational incidents, enforces deterministic safety and allergen escalation rules, tracks store-level trends with exposure normalization, and detects emerging operational issues before they become widespread.

## 2. Architecture Principles

The backend is engineered as a **Service-Oriented Modular Monolith**:
- **Independent Services**: NLP preprocessing, machine learning classification, policy enforcement, incident deduplication, store analytics, emerging-issue detection, and chronological replay are partitioned into dedicated service classes.
- **Strict Pipeline Sequencing**: Feedback processing enforces deterministic ordering:
  $$\text{Ingestion} \rightarrow \text{Preprocessing} \rightarrow \text{ML Classification} \rightarrow \text{Deduplication} \rightarrow \text{Safety Policy} \rightarrow \text{Persistence} \rightarrow \text{Analytics / Alerts}$$
- **Zero Raw Data Loss**: Deduplication consolidates underlying incidents while permanently preserving every raw feedback record and its traceability link.
- **Statistically Grounded Detection**: Emerging issue alerts are derived from historical baselines, transaction-normalized rates, and Poisson/Normal deviation scores, avoiding unexplainable black-box alarms.
- **Chronological Simulation Integrity**: Replay simulations prevent future-data leakage by calculating baselines strictly using observations prior to the simulated event time.

## 3. High-Level Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                  FastAPI Router                                   |
|   /health, /ready, /auth, /stores, /feedback, /incidents, /analytics, /alerts,    |
|                                     /replay                                       |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                         Cross-Cutting Middleware & Security                       |
|   Correlation ID, Request Size Guard, Sliding-Window Rate Limiter, Argon2id, JWT   |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                          Feedback Processing Pipeline                             |
|                                                                                   |
|  1. Text Preprocessor       --> Unicode NFKC cleaning, sentence splitting         |
|  2. Feedback Classifier     --> Scikit-Learn TF-IDF + Logistic Regression         |
|  3. Incident Deduplicator   --> Lexical cosine similarity within 72h window       |
|  4. Safety Policy Engine    --> Deterministic hazard & allergen context checking  |
|  5. Transaction Persistence --> Raw feedback + Incident linking                   |
+-----------------------------------------------------------------------------------+
       |                                                    |
       v                                                    v
+-----------------------------+             +---------------------------------------+
|  Analytics Service          |             | Emerging Issue Detector               |
|  - Distinct incident counts |             | - Leak-free historical baselines      |
|  - Exposure normalization   |             | - Rate ratio & Poisson Z-score        |
|  - Peer store comparisons   |             | - Network peer store benchmarking     |
+-----------------------------+             | - Cooldown & duplicate suppression    |
                                            +---------------------------------------+
                                                            |
                                                            v
                                            +---------------------------------------+
                                            | Chronological Replay Engine           |
                                            | - Deterministic tie-breaking          |
                                            | - 3 Synthetic planted incidents eval  |
                                            | - Lead time & recall measurement      |
                                            +---------------------------------------+
```

## 4. Role-Based Access Control (RBAC) & Data Isolation

The backend enforces three distinct roles:
1. **Admin (`admin`)**:
   - Manage retail stores and global configuration.
   - Provision users and assign roles.
   - Access global analytics, replay runs, and audit logs.
2. **Store Manager (`store_manager`)**:
   - Restricted strictly to their assigned `store_id`.
   - Access feedback, incidents, and active alerts for their store only.
   - Acknowledge and resolve alerts for their store.
   - Cannot view or manipulate data belonging to other stores.
3. **Analyst (`analyst`)**:
   - View cross-store analytics and store comparisons.
   - Trigger emerging issue scans across the network.
   - Launch chronological replay simulations and inspect evaluation metrics.

## 5. Security & Operational Reliability

- **Argon2id Password Hashing**: State-of-the-art memory-hard hashing resistant to GPU cracking.
- **Stateless JWT Authentication**: Tokens carry user ID, role, and store ID claims with short expiration.
- **Request Correlation ID**: Injected via `X-Correlation-ID` header and tracked in logs across async threads.
- **Audit Logging**: Sensitive operations (login, store creation, status change, alert resolution) are logged to `audit_events` with scrubbed credentials.
- **Graceful Error Handling**: Unhandled exceptions return structured JSON error payloads without leaking database connection strings or internal tracebacks.
