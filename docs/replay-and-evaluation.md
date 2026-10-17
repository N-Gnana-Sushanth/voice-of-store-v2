# Voice of Store — Chronological Replay and Evaluation Engine

## 1. Objective

The Chronological Replay Engine is designed to evaluate emerging-issue detection algorithms historically without risk of retrospective data leakage. It reproduces real-world conditions by advancing simulated time sequentially, ensuring that at any simulated timestamp $t$, the system only possesses knowledge of feedback records generated at or before $t$.

## 2. Leakage Prevention Architecture

- **Event-Time Ordering**: Records are sorted strictly by `(event_timestamp, record_id)` with the unique ID acting as a deterministic tie-breaker.
- **Strict Baseline Partitioning**: When evaluating emerging issues as of simulated timestamp $t$, baselines are calculated exclusively on events occurring before $t - W_{\text{obs}}$.
- **Mathematical Proof**: Automated tests in `tests/test_replay_engine.py::test_no_future_data_leakage_proof` confirm that injecting subsequent high-volume future incidents does not change baselines or alerts calculated at earlier time points.

## 3. The 3 Synthetic Planted Ground-Truth Incidents

To establish measurable evaluation benchmarks, the replay system includes three synthetic planted failure scenarios with known onset times:

### 3.1. Planted Incident 1 (`PLANTED-001`): Deli Cross-Contamination Outbreak
- **Target Store**: `STORE-101`
- **Category**: `Allergens`
- **Onset Offset**: Day 10 (10:00 UTC)
- **Failure Mode**: Cross-contamination where deli counter staff sliced turkey using unwashed knives with walnut and peanut butter residue, triggering allergic reactions, throat swelling, and hives.
- **Detection Benchmark**: Detected promptly via deterministic allergen policy escalation (`URGENT_SAFETY` alert).

### 3.2. Planted Incident 2 (`PLANTED-002`): POS Terminal Payment Freeze Spike
- **Target Store**: `STORE-102`
- **Category**: `Billing and payments`
- **Onset Offset**: Day 14 (10:00 UTC)
- **Failure Mode**: Network bug causing card readers to freeze during chip swipes and bill customer accounts twice.
- **Detection Benchmark**: Detected as a volume rate surge (`SPIKE` alert) with statistical Z-score $\ge 2.5$.

### 3.3. Planted Incident 3 (`PLANTED-003`): HVAC Ceiling Water Leak Hazard
- **Target Store**: `STORE-103`
- **Category**: `Safety`
- **Onset Offset**: Day 18 (10:00 UTC)
- **Failure Mode**: Unrepaired HVAC ceiling leak creating a large slippery puddle without warning signs, resulting in customer slip-and-fall injuries.
- **Detection Benchmark**: Detected via physical hazard safety escalation (`URGENT_SAFETY` / `SPIKE` alert).

## 4. Evaluation Metrics

For each replay experiment, the engine measures:
- **Detection Lead Time**:
  $$\text{Lead Time (Hours)} = \text{Detection Timestamp} - \text{Incident Onset Timestamp}$$
- **Planted Recall**:
  $$\text{Recall} = \frac{\text{Planted Incidents Detected}}{\text{Total Planted Incidents (3)}}$$
- **Alert Precision**:
  $$\text{Precision} = \frac{\text{True Planted Alerts}}{\text{Total Alerts Triggered}}$$
- **False Positive Count**: Number of unexplainable alerts generated on normal background variation.
