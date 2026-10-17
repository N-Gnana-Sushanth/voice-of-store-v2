# Voice of Store — Database Schema Documentation

## 1. Overview

The persistent database is modeled in PostgreSQL (compatible with SQLite for isolated testing) using SQLAlchemy 2.x and managed with Alembic migrations.

## 2. Entity-Relationship Overview

```
 [stores]
    |-- 1:N --> [users]
    |-- 1:N --> [feedback_records]
    |-- 1:N --> [incidents]
    |-- 1:N --> [historical_baselines]
    `-- 1:N --> [alerts]

 [incidents]
    `-- 1:N --> [feedback_records]  (traceability link preserving raw submissions)

 [users]
    |-- 1:N --> [alerts.acknowledged_by]
    `-- 1:N --> [alerts.resolved_by]

 [replay_runs] (standalone experiment records)
 [audit_events] (immutable administrative action trail)
```

## 3. Detailed Entity Definitions

### 3.1. `stores`
Stores represent physical retail outlets and hold operational exposure metrics.
- `id` (VARCHAR(36), PK): UUID.
- `store_number` (VARCHAR(50), Unique, Indexed): e.g. "STORE-101".
- `name` (VARCHAR(255), Not Null): Retail outlet name.
- `address`, `city`, `state` (VARCHAR): Location metadata.
- `size_sqft` (FLOAT, Default 10000.0): Retail floor area (secondary exposure metric).
- `avg_daily_transactions` (FLOAT, Default 1500.0): Daily transaction count (primary exposure metric).
- `is_active` (BOOLEAN, Default True): Active status.
- `created_at`, `updated_at` (TIMESTAMP WITH TIME ZONE): UTC timestamps.

### 3.2. `users`
Authenticated system users with RBAC and optional store assignment.
- `id` (VARCHAR(36), PK): UUID.
- `email` (VARCHAR(255), Unique, Indexed): User login email.
- `hashed_password` (VARCHAR(255), Not Null): Argon2id password hash.
- `full_name` (VARCHAR(255), Not Null): User name.
- `role` (VARCHAR(50), Indexed): "admin", "store_manager", or "analyst".
- `store_id` (VARCHAR(36), FK -> `stores.id`, Nullable, Indexed): Enforces store isolation for managers.
- `is_active` (BOOLEAN, Default True): Account active flag.
- `created_at`, `updated_at` (TIMESTAMP WITH TIME ZONE): UTC timestamps.

### 3.3. `feedback_records`
Permanent store of every submitted customer and employee feedback report.
- `id` (VARCHAR(36), PK): UUID.
- `store_id` (VARCHAR(36), FK -> `stores.id`, Indexed): Associated store.
- `text` (TEXT, Not Null): Original, unedited feedback narrative.
- `source` (VARCHAR(50)): "customer", "employee", "survey", "web", "inspection".
- `event_timestamp` (TIMESTAMP WITH TIME ZONE, Indexed): Normalized event time.
- `ingestion_timestamp` (TIMESTAMP WITH TIME ZONE, Indexed): Time received.
- `idempotency_key` (VARCHAR(255), Unique, Nullable, Indexed): Protects against client retry duplicates.
- `processing_status` (VARCHAR(50), Indexed): "PENDING", "PROCESSED", "FAILED".
- `error_message` (TEXT, Nullable): Diagnostic error message if downstream processing failed.
- `incident_id` (VARCHAR(36), FK -> `incidents.id`, Nullable, Indexed): Link to consolidated incident.
- `metadata_json` (JSON, Nullable): Arbitrary client context metadata.
- `created_at`, `updated_at` (TIMESTAMP WITH TIME ZONE): UTC timestamps.

### 3.4. `incidents`
Consolidated operational issues grouping one or more feedback reports.
- `id` (VARCHAR(36), PK): UUID.
- `store_id` (VARCHAR(36), FK -> `stores.id`, Indexed): Associated store.
- `category` (VARCHAR(100), Indexed): Operational category.
- `severity` (VARCHAR(50), Indexed): "LOW", "MEDIUM", "HIGH", "CRITICAL".
- `sentiment` (VARCHAR(50)): "POSITIVE", "NEUTRAL", "NEGATIVE".
- `sentiment_score` (FLOAT): Score from -1.0 to +1.0.
- `classification_confidence` (FLOAT): Calibrated ML probability.
- `safety_flag` (BOOLEAN, Indexed): Deterministic safety hazard indicator.
- `allergen_flag` (BOOLEAN, Indexed): Deterministic allergen trigger indicator.
- `policy_escalated` (BOOLEAN, Indexed): Urgent policy escalation indicator.
- `policy_escalation_reason` (TEXT, Nullable): Human-readable reason for policy escalation.
- `status` (VARCHAR(50), Indexed): "OPEN", "UNDER_INVESTIGATION", "RESOLVED", "DISMISSED".
- `first_seen_at`, `last_seen_at` (TIMESTAMP WITH TIME ZONE, Indexed): Activity window.
- `feedback_count` (INTEGER, Default 1): Number of linked feedback records.
- `model_version`, `policy_version` (VARCHAR(100)): Traceability tags.
- `evidence_summary` (TEXT, Nullable): Extracted text summary.
- `metadata_json` (JSON, Nullable): Match evidence and probability distribution.

### 3.5. `historical_baselines`
Historical rate baselines computed prior to observation windows (leak-free).
- `id` (VARCHAR(36), PK): UUID.
- `store_id` (VARCHAR(36), FK -> `stores.id`, Indexed).
- `category` (VARCHAR(100), Indexed).
- `time_window_days` (INTEGER, Default 30).
- `historical_incident_count` (INTEGER).
- `exposure_units` (FLOAT): Transaction count in baseline window.
- `normalized_rate` (FLOAT): Incidents per 1,000 transactions.
- `baseline_mean`, `baseline_std` (FLOAT): Historical distribution parameters.
- `min_sample_met` (BOOLEAN): Whether minimum sample threshold was met.
- `baseline_version` (VARCHAR(50)).
- `calculated_at` (TIMESTAMP WITH TIME ZONE).
- Unique Constraint: `(store_id, category, time_window_days, baseline_version)`.

### 3.6. `alerts`
Emerging-issue alerts triggered by unusual spikes or severe safety escalations.
- `id` (VARCHAR(36), PK): UUID.
- `store_id` (VARCHAR(36), FK -> `stores.id`, Indexed).
- `category` (VARCHAR(100), Indexed).
- `alert_type` (VARCHAR(50), Indexed): "SPIKE", "SUSTAINED_INCREASE", "PEER_DEVIATION", "URGENT_SAFETY".
- `severity` (VARCHAR(50), Indexed): "INFO", "WARNING", "HIGH", "CRITICAL".
- `status` (VARCHAR(50), Indexed): "ACTIVE", "ACKNOWLEDGED", "RESOLVED".
- `current_count` (INTEGER), `current_rate` (FLOAT), `baseline_rate` (FLOAT).
- `rate_ratio` (FLOAT), `z_score` (FLOAT, Nullable).
- `observation_window_days` (INTEGER), `exposure_volume` (FLOAT), `sample_size` (INTEGER).
- `confidence_score` (FLOAT).
- `evidence_json` (JSON): Comprehensive explainability breakdown.
- `peer_comparison_json` (JSON, Nullable).
- `first_detected_at`, `last_detected_at` (TIMESTAMP WITH TIME ZONE).
- `detection_count` (INTEGER, Default 1): Incremented on repeated scans (suppression/cooldown).
- `acknowledged_by_id`, `acknowledged_at` (FK -> `users.id`, Nullable).
- `resolved_by_id`, `resolved_at`, `resolution_notes` (FK -> `users.id`, Nullable).

### 3.7. `replay_runs`
Chronological event-time simulation records.
- `id` (VARCHAR(36), PK): UUID.
- `name` (VARCHAR(255)), `description` (TEXT, Nullable).
- `time_range_start`, `time_range_end` (TIMESTAMP WITH TIME ZONE).
- `status` (VARCHAR(50), Indexed): "PENDING", "RUNNING", "COMPLETED", "FAILED".
- `config_json`, `evaluation_metrics_json` (JSON).
- `total_records`, `processed_records`, `incidents_created`, `alerts_generated` (INTEGER).
- `start_time`, `completion_time` (TIMESTAMP WITH TIME ZONE).

### 3.8. `audit_events`
Administrative action trail.
- `id` (VARCHAR(36), PK): UUID.
- `actor_id` (VARCHAR(36), FK -> `users.id`, Nullable, Indexed).
- `actor_email` (VARCHAR(255), Nullable).
- `action` (VARCHAR(100), Indexed): e.g. "USER_LOGIN", "STORE_CREATED", "ALERT_RESOLVED".
- `resource_type` (VARCHAR(100)), `resource_id` (VARCHAR(255), Nullable, Indexed).
- `timestamp` (TIMESTAMP WITH TIME ZONE, Indexed).
- `details_json` (JSON, Nullable): Redacted metadata payload.
