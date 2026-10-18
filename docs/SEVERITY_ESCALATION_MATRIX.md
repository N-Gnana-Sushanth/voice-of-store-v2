# Voice of Store — Written Severity Escalation Matrix & Policy

**Document Version:** `2.0.0-audited`
**Effective Date:** `2026-10-18`
**Governing Body:** Retail Safety, Operations & Compliance Council

---

## 1. Executive Summary & Principles

The Voice of Store operational intelligence platform operates on four strict architectural principles:

1. **Separation of Severity from Sentiment and Actionability:**
   - **Severity** reflects physical safety risk, legal compliance breach, and operational impact.
   - **Sentiment** reflects emotional tone (positive, neutral, negative). A highly negative complaint about store music is **LOW** severity, whereas a polite customer note mentioning an anaphylactic allergy is **CRITICAL** severity.
   - **Actionability** indicates whether concrete, verifiable details (aisle, counter, equipment, product name) are present to initiate investigation.

2. **Deterministic Safety Policy Override:**
   - Predefined safety and allergen triggers (anaphylaxis, slip-and-fall with injury, biological pests, food poisoning, electrical hazards) **strictly override** ordinary machine-learning classifications and volume thresholds.
   - A single report ($N=1$) triggers immediate CRITICAL escalation.

3. **Auditability and Traceability:**
   - Every escalated incident permanently logs the active policy version, matched verbatim evidence span, and chronological timestamp.

---

## 2. Severity Escalation Matrix

| Severity Level | Response SLA | Acknowledgment Window | Qualifying Conditions & Triggers | Owning Function | Required Notification | Closure Criteria |
| :--- | :---: | :---: | :--- | :--- | :--- | :--- |
| **CRITICAL** | **1 Hour** | 15 Minutes | • Anaphylactic allergic reaction or EpiPen use<br>• Slip-and-fall resulting in injury, bleeding, or hospitalization<br>• Fire, smoke, gas leak, or electrical hazard<br>• Active rodent or cockroach infestation near exposed food<br>• Credible physical violence or weapon threat | **Quality & Compliance** | Store Manager, Regional Ops Director, VP Compliance | Dual sign-off: Store Manager + HQ Compliance Officer with signed corrective action manifest. |
| **HIGH** | **4 Hours** | 60 Minutes | • Allergen warning label missing on pre-packaged foods<br>• Walk-in freezer or dairy cooler temperature failure<br>• Expired dairy, baby food, or meat on shelf<br>• Unattended spill without safety cone<br>• Gross staff verbal abuse or verified misconduct | **Store Ops** (or **HR** for misconduct) | Store Assistant Manager, Department Lead, Area Lead | Work order completion record or product quarantine manifest logged in Action Queue. |
| **MEDIUM** | **12 Hours** | 180 Minutes | • Card reader chip failure or double swipe billing issue<br>• Restroom sanitation or empty soap dispensers<br>• Promotional circular stockout or price mismatch<br>• Excessive checkout wait times (>10 min) | **Store Ops** (or **Digital** / **Merchandising**) | Shift Supervisor, Department Lead | Shift supervisor resolution confirmation note in Action Queue. |
| **LOW** | **24 Hours** | 480 Minutes | • Wobbly shopping cart wheel or squeaky basket<br>• Parking lot bay paint fading or lighting suggestions<br>• General feedback on music volume or app layout | **Store Ops** | Shift Supervisor | Closed during scheduled routine weekly maintenance sweep. |

---

## 3. Mandatory Overrides and Boundary Conditions

1. **Volume Bypass:** Mandatory CRITICAL and HIGH safety conditions do not require statistical anomaly detection or multi-report clustering.
2. **Negation & Hypothetical Protection:** The policy engine explicitly parses negation ("no pests seen", "not expired") and hypotheticals ("what if the milk spoils?") to prevent false alarms.
3. **Overdue Handling:** If a CRITICAL incident is not acknowledged within 15 minutes, automated escalation notifications are dispatched to the Regional Operations Director.
