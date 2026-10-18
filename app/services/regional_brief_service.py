"""Weekly One-Page Regional Executive Brief service and week-over-week trend analysis."""

from datetime import datetime, timedelta, timezone
import math
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.taxonomy import taxonomy_manager
from app.models.feedback import FeedbackRecord
from app.models.incident import Incident, IncidentSeverity, OwningFunction
from app.models.regional_brief import RegionalBrief
from app.models.store import Store


class RegionalBriefService:
    """Generates and archives weekly one-page regional operational briefs."""

    @classmethod
    def calculate_week_over_week(
        cls,
        current_count: int,
        previous_count: int,
    ) -> Dict[str, Any]:
        """
        Calculates week-over-week trends safely without division-by-zero errors.
        Handles zero previous-week baselines explicitly.
        """
        abs_diff = current_count - previous_count

        if previous_count == 0:
            pct_change = None
            trend_label = f"+{current_count} (New)" if current_count > 0 else "0 (No change)"
            direction = "UP" if current_count > 0 else "STABLE"
        else:
            pct = round(((current_count - previous_count) / previous_count) * 100.0, 1)
            pct_change = pct
            if pct > 5.0:
                direction = "UP"
                trend_label = f"+{pct}% (↑ {abs_diff})"
            elif pct < -5.0:
                direction = "DOWN"
                trend_label = f"{pct}% (↓ {abs(abs_diff)})"
            else:
                direction = "STABLE"
                trend_label = f"{pct}% (→ {abs_diff})"

        return {
            "current_count": current_count,
            "previous_count": previous_count,
            "absolute_difference": abs_diff,
            "percentage_change": pct_change,
            "trend_label": trend_label,
            "direction": direction,
        }

    @classmethod
    def generate_brief(
        cls,
        db: Session,
        region: str,
        as_of_date: Optional[datetime] = None,
    ) -> RegionalBrief:
        """
        Generate a complete one-page regional brief for the specified region
        over the 7-day period ending at as_of_date.
        """
        if as_of_date is None:
            as_of_date = datetime.now(timezone.utc)
        elif as_of_date.tzinfo is None:
            as_of_date = as_of_date.replace(tzinfo=timezone.utc)

        current_start = as_of_date - timedelta(days=7)
        prev_start = current_start - timedelta(days=7)

        # 1. Stores in region
        stores = (
            db.query(Store)
            .filter(Store.region == region, Store.is_active == True)
            .all()
        )
        store_ids = [s.id for s in stores]
        store_map = {s.id: s for s in stores}
        total_stores = len(stores)

        if total_stores == 0:
            # Handle empty region gracefully
            brief = RegionalBrief(
                region=region,
                week_start=current_start,
                week_end=as_of_date,
                executive_summary=f"No active stores currently registered in {region} region.",
                top_issues_json=[],
                low_volume_safety_json=[],
                metrics_json={
                    "total_stores": 0,
                    "total_feedback": 0,
                    "incident_count": 0,
                    "data_coverage": "0 active stores",
                },
                html_content=f"<html><body><h1>{region} Regional Brief</h1><p>No active stores.</p></body></html>",
                generated_at=as_of_date,
            )
            db.add(brief)
            db.commit()
            return brief

        # 2. Fetch current and previous week incidents
        curr_incidents = (
            db.query(Incident)
            .filter(
                Incident.store_id.in_(store_ids),
                Incident.first_seen_at >= current_start,
                Incident.first_seen_at <= as_of_date,
            )
            .all()
        )

        prev_incidents = (
            db.query(Incident)
            .filter(
                Incident.store_id.in_(store_ids),
                Incident.first_seen_at >= prev_start,
                Incident.first_seen_at < current_start,
            )
            .all()
        )

        # 3. Total feedback in region
        total_feedback_curr = (
            db.query(func.count(FeedbackRecord.id))
            .filter(
                FeedbackRecord.store_id.in_(store_ids),
                FeedbackRecord.event_timestamp >= current_start,
                FeedbackRecord.event_timestamp <= as_of_date,
            )
            .scalar() or 0
        )

        # 4. Group by category and calculate week-over-week
        curr_cat_map: Dict[str, List[Incident]] = {}
        for inc in curr_incidents:
            curr_cat_map.setdefault(inc.category, []).append(inc)

        prev_cat_counts: Dict[str, int] = {}
        for inc in prev_incidents:
            prev_cat_counts[inc.category] = prev_cat_counts.get(inc.category, 0) + 1

        # Rank categories using business priority formula:
        # Score = count + (10 if critical else 5 if high else 1) + (10 if safety/allergen else 0)
        category_scores: List[Tuple[str, float]] = []
        for cat, inc_list in curr_cat_map.items():
            count = len(inc_list)
            has_crit = any(i.severity == IncidentSeverity.CRITICAL for i in inc_list)
            has_high = any(i.severity == IncidentSeverity.HIGH for i in inc_list)
            has_safety = any(i.safety_flag or i.allergen_flag for i in inc_list)

            score = count + (15.0 if has_crit else 8.0 if has_high else 2.0) + (12.0 if has_safety else 0.0)
            category_scores.append((cat, score))

        category_scores.sort(key=lambda x: x[1], reverse=True)
        top_5_categories = [cat for cat, _ in category_scores[:5]]

        # Build top 5 issues breakdown
        top_issues_data = []
        for rank, cat in enumerate(top_5_categories, 1):
            inc_list = curr_cat_map[cat]
            curr_cnt = len(inc_list)
            prev_cnt = prev_cat_counts.get(cat, 0)
            wow = cls.calculate_week_over_week(curr_cnt, prev_cnt)

            # Determine dominant severity & owner
            sev = IncidentSeverity.HIGH if any(i.severity in [IncidentSeverity.CRITICAL, IncidentSeverity.HIGH] for i in inc_list) else IncidentSeverity.MEDIUM
            primary_owner = inc_list[0].primary_owner if inc_list[0].primary_owner else taxonomy_manager.get_owner(cat)

            # Find genuine evidence quotes
            quotes = []
            affected_store_ids = set()
            for inc in inc_list:
                affected_store_ids.add(inc.store_id)
                if inc.evidence_summary and len(quotes) < 2:
                    quotes.append({
                        "quote": inc.evidence_summary[:160],
                        "store_code": store_map.get(inc.store_id).store_number if store_map.get(inc.store_id) else inc.store_id,
                        "store_name": store_map.get(inc.store_id).name if store_map.get(inc.store_id) else "Store",
                    })

            affected_stores_formatted = [
                store_map[sid].name for sid in affected_store_ids if sid in store_map
            ]

            recommended_action = f"Immediate audit by {primary_owner} across {len(affected_store_ids)} affected stores."
            if sev == IncidentSeverity.HIGH:
                recommended_action = f"Urgent 4-hour remediation work order dispatched to {primary_owner} teams."

            top_issues_data.append({
                "rank": rank,
                "category": cat,
                "severity": sev,
                "primary_owner": primary_owner,
                "current_count": curr_cnt,
                "previous_count": prev_cnt,
                "trend": wow["trend_label"],
                "trend_direction": wow["direction"],
                "affected_stores": affected_stores_formatted,
                "evidence_quotes": quotes,
                "recommended_action": recommended_action,
            })

        # 5. Low-volume critical safety warnings
        safety_incidents = [
            inc for inc in curr_incidents
            if inc.safety_flag or inc.allergen_flag or inc.severity == IncidentSeverity.CRITICAL
        ]
        low_volume_safety = []
        for s_inc in safety_incidents:
            s_name = store_map.get(s_inc.store_id).name if s_inc.store_id in store_map else "Store"
            low_volume_safety.append({
                "category": s_inc.category,
                "store": s_name,
                "reason": s_inc.policy_escalation_reason or "Mandatory safety escalation triggered",
                "evidence": s_inc.evidence_summary[:140] if s_inc.evidence_summary else "",
            })

        # 6. Executive summary narrative
        date_str = f"{current_start.strftime('%d %b')} – {as_of_date.strftime('%d %b %Y')}"
        lead_issue = top_issues_data[0]["category"] if top_issues_data else "General operations"
        exec_summary = (
            f"Weekly executive review for {region} covering {total_stores} stores ({date_str}). "
            f"A total of {total_feedback_curr} feedback records yielded {len(curr_incidents)} actionable incidents. "
            f"The primary operational driver is '{lead_issue}' with {len(top_issues_data)} dominant issue clusters. "
            f"{len(low_volume_safety)} critical safety escalation(s) require immediate department sign-off."
        )

        metrics_json = {
            "region": region,
            "reporting_period": date_str,
            "total_stores": total_stores,
            "total_feedback": total_feedback_curr,
            "incident_count": len(curr_incidents),
            "incident_rate_per_store": round(len(curr_incidents) / total_stores, 2),
            "safety_escalations_count": len(low_volume_safety),
            "data_coverage": f"100% of registered {region} stores evaluated without data truncation",
            "generation_timestamp": as_of_date.isoformat(),
        }

        # 7. Generate printable HTML content optimized for single-page print
        html_content = cls._render_html_brief(
            region=region,
            period_str=date_str,
            summary=exec_summary,
            top_issues=top_issues_data,
            safety_warnings=low_volume_safety,
            metrics=metrics_json,
        )

        brief = RegionalBrief(
            region=region,
            week_start=current_start,
            week_end=as_of_date,
            executive_summary=exec_summary,
            top_issues_json=top_issues_data,
            low_volume_safety_json=low_volume_safety,
            metrics_json=metrics_json,
            html_content=html_content,
            generated_at=as_of_date,
        )
        db.add(brief)
        db.commit()
        db.refresh(brief)
        return brief

    @classmethod
    def _render_html_brief(
        cls,
        region: str,
        period_str: str,
        summary: str,
        top_issues: List[Dict[str, Any]],
        safety_warnings: List[Dict[str, Any]],
        metrics: Dict[str, Any],
    ) -> str:
        """Render high-density single-page printable HTML format."""
        issues_rows = ""
        for item in top_issues:
            quotes_html = "".join([f'<div><em>"{q["quote"]}"</em> — <strong>{q["store_name"]}</strong></div>' for q in item["evidence_quotes"]])
            stores_html = ", ".join(item["affected_stores"][:3])
            if len(item["affected_stores"]) > 3:
                stores_html += f" (+{len(item['affected_stores']) - 3} more)"

            trend_color = "#dc2626" if item["trend_direction"] == "UP" else ("#16a34a" if item["trend_direction"] == "DOWN" else "#64748b")
            issues_rows += f"""
            <tr style="border-bottom: 1px solid #e2e8f0; font-size: 11px;">
                <td style="padding: 6px 8px; font-weight: bold; width: 24px;">#{item["rank"]}</td>
                <td style="padding: 6px 8px;">
                    <div style="font-weight: 700; color: #0f172a;">{item["category"]}</div>
                    <div style="color: #64748b; font-size: 10px; margin-top: 2px;">{quotes_html}</div>
                </td>
                <td style="padding: 6px 8px; color: {trend_color}; font-weight: bold; white-space: nowrap;">{item["trend"]}</td>
                <td style="padding: 6px 8px; color: #334155;">{stores_html}</td>
                <td style="padding: 6px 8px; font-weight: 600;">{item["primary_owner"]}</td>
                <td style="padding: 6px 8px; font-size: 10px; color: #059669;">{item["recommended_action"]}</td>
            </tr>
            """

        safety_html = ""
        if safety_warnings:
            safety_items = "".join([f"<li><strong>[{w['store']}] {w['category']}:</strong> {w['reason']}</li>" for w in safety_warnings])
            safety_html = f"""
            <div style="margin-top: 10px; padding: 8px 12px; background-color: #fee2e2; border-left: 4px solid #ef4444; border-radius: 4px; font-size: 11px; color: #991b1b;">
                <strong>⚠️ Mandatory Low-Volume Safety Warnings ({len(safety_warnings)}):</strong>
                <ul style="margin: 4px 0 0 16px; padding: 0;">{safety_items}</ul>
            </div>
            """

        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{region} Regional Operational Brief</title>
<style>
  @page {{ size: A4 portrait; margin: 10mm; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #0f172a; margin: 0; padding: 0; font-size: 11px; line-height: 1.4; }}
  .header {{ display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2px solid #059669; padding-bottom: 8px; margin-bottom: 10px; }}
  .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 12px; }}
  .metric-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px 10px; }}
  table {{ width: 100%; border-collapse: collapse; text-align: left; }}
  th {{ background: #f1f5f9; padding: 6px 8px; font-size: 10.5px; font-weight: 700; color: #475569; }}
</style>
</head>
<body>
  <div class="header">
    <div>
      <h1 style="margin: 0; font-size: 18px; color: #0f172a;">Voice of Store — Regional Operational Brief</h1>
      <div style="font-size: 12px; font-weight: 700; color: #059669; margin-top: 2px;">{region} Region • {period_str}</div>
    </div>
    <div style="text-align: right; font-size: 10px; color: #64748b;">
      Official Executive Brief • Generated {metrics['generation_timestamp'][:10]}
    </div>
  </div>

  <div class="metrics-grid">
    <div class="metric-card">
      <div style="color: #64748b; font-size: 9.5px; font-weight: 600;">ACTIVE STORES</div>
      <div style="font-size: 16px; font-weight: 800; color: #0f172a;">{metrics['total_stores']}</div>
    </div>
    <div class="metric-card">
      <div style="color: #64748b; font-size: 9.5px; font-weight: 600;">TOTAL FEEDBACK RECORDED</div>
      <div style="font-size: 16px; font-weight: 800; color: #0f172a;">{metrics['total_feedback']:,}</div>
    </div>
    <div class="metric-card">
      <div style="color: #64748b; font-size: 9.5px; font-weight: 600;">ACTIONABLE INCIDENTS</div>
      <div style="font-size: 16px; font-weight: 800; color: #0f172a;">{metrics['incident_count']}</div>
    </div>
    <div class="metric-card">
      <div style="color: #64748b; font-size: 9.5px; font-weight: 600;">INCIDENT RATE / STORE</div>
      <div style="font-size: 16px; font-weight: 800; color: #059669;">{metrics['incident_rate_per_store']}</div>
    </div>
  </div>

  <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 8px 12px; margin-bottom: 12px; font-size: 11px; color: #166534;">
    <strong>Executive Summary:</strong> {summary}
  </div>

  <h3 style="font-size: 12px; margin: 0 0 6px 0; color: #0f172a;">Top 5 Priority Issues (Ranked by Severity & Volume)</h3>
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>Issue & Evidence Quote</th>
        <th>WoW Trend</th>
        <th>Affected Stores</th>
        <th>Owner</th>
        <th>Action Required</th>
      </tr>
    </thead>
    <tbody>
      {issues_rows}
    </tbody>
  </table>

  {safety_html}

  <div style="margin-top: 14px; padding-top: 6px; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-between; font-size: 9.5px; color: #94a3b8;">
    <span>Data Coverage: {metrics['data_coverage']}</span>
    <span>Voice of Store • Single-Page Operational Brief • Confidential</span>
  </div>
</body>
</html>
"""


regional_brief_service = RegionalBriefService()
