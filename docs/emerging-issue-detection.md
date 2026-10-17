# Voice of Store — Emerging Issue Detection Engine

## 1. Objective

The Emerging Issue Detection Engine is an independent, explainable statistical service designed to answer:
- Which stores are experiencing unusual increases in customer or employee complaints?
- Which operational issues are emerging compared with historical baselines?
- Which incidents represent severe safety or allergen hazards requiring immediate escalation?
- What exact mathematical evidence supports each generated alert?

## 2. Statistical Methodology

### 2.1. Exposure Normalization
Raw complaint counts are inherently biased by store foot traffic, customer count, and physical retail size. A 100-complaint volume in a flagship store with 50,000 weekly transactions represents a much lower incident density than 20 complaints in an express store with 2,000 transactions.

The platform normalizes incident frequency using customer transaction exposure:
$$\text{Normalized Rate } (R) = \left( \frac{\text{Distinct Incidents}}{\text{Total Customer Transactions}} \right) \times 1,000$$

*(If customer transaction data is temporarily unavailable for a new store, retail floor area in square feet is used as a documented fallback).*

### 2.2. Leak-Free Historical Baselines
To prevent future-data leakage, the historical baseline for store $s$ and category $c$ is computed using a 30-day baseline window strictly preceding the current observation window:
$$\text{Baseline Window} = [T - W_{\text{obs}} - W_{\text{base}}, T - W_{\text{obs}})$$

The historical baseline normalized rate is:
$$R_{\text{base}} = \left( \frac{C_{\text{base}}}{E_{\text{base}}} \right) \times 1,000$$
where $C_{\text{base}}$ is historical incident count and $E_{\text{base}}$ is historical customer transactions.

### 2.3. Rate Ratio & Poisson / Normal Z-Score
Given current observation window $W_{\text{obs}}$ (default 7 days) with exposure $E_{\text{obs}}$, the expected incident count based on historical baseline is:
$$\mu_{\text{expected}} = \left( \frac{R_{\text{base}}}{1,000} \right) \times E_{\text{obs}}$$

The Rate Ratio (RR) is:
$$\text{RR} = \frac{R_{\text{obs}}}{\max(R_{\text{base}}, 0.05)}$$

The deviation Z-score is computed using Poisson variance approximation:
$$Z = \frac{C_{\text{obs}} - \mu_{\text{expected}}}{\sqrt{\max(\mu_{\text{expected}}, 1.0)}}$$

### 2.4. Low Sample Size Guard
To prevent spurious alerts on small numbers (e.g. 1 isolated complaint on low traffic), an alert is suppressed unless:
$$C_{\text{obs}} \ge 3 \quad \text{OR} \quad \text{Incident has critical safety/allergen flag}$$

### 2.5. Peer Store Benchmarking
The engine computes the median normalized rate for the category across all other active peer stores in the same time window: $R_{\text{peer\_median}}$. This verifies whether the issue is store-specific or systemic across the entire retail network.

## 3. Alert Classification & Thresholds

| Alert Type | Severity | Qualification Conditions |
|---|---|---|
| `URGENT_SAFETY` | **CRITICAL** | Any incident with confirmed deterministic safety or allergen escalation flag (`safety_flag=True` or `allergen_flag=True`) |
| `SPIKE` | **HIGH** | Abrupt rate increase: $\text{RR} \ge 3.0$ and $Z \ge 2.5$ and $C_{\text{obs}} \ge 3$ |
| `SUSTAINED_INCREASE` | **WARNING** | Moderate increase: $\text{RR} \ge 2.0$ and $Z \ge 2.0$ and $C_{\text{obs}} \ge 3$ |
| `PEER_DEVIATION` | **WARNING / HIGH** | Store rate is $\ge 2.5\times$ higher than the network peer median rate |

## 4. Alert Deduplication, Cooldown, and Lifecycle

1. **Suppression & Cooldown**: When a scan triggers an alert for a store and category where an `ACTIVE` or `ACKNOWLEDGED` alert already exists, the engine updates the existing alert in-place (updating `current_count`, `current_rate`, `last_detected_at`, and incrementing `detection_count`). It does NOT spawn duplicate alert rows.
2. **Lifecycle States**:
   - `ACTIVE`: New or recurring alert requiring attention.
   - `ACKNOWLEDGED`: Store manager or analyst has confirmed awareness.
   - `RESOLVED`: Operational fix implemented with mandatory resolution notes.
