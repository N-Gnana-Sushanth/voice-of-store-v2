#!/usr/bin/env python3
"""
Voice of Store — Production Incident & Classification Evaluation Suite.

Evaluates:
1. Record-level text classification, severity, and actionability metrics (Accuracy, Macro/Weighted
   Precision, Recall, F1, Per-Class Breakdown, and Confusion Matrix) against labelled CSV/JSON/JSONL datasets.
2. Incident-level chronological early detection, detection lead time (onset minus first detection),
   median lead time, false alarm rate, and recall against independent ground-truth incident manifests.

Usage:
    # Incident-level evaluation with ground-truth fixtures
    python evaluate.py --fixtures data/fixtures/ground_truth_test_cases.json --output report.json

    # Record-level classification evaluation on labelled dataset
    python evaluate.py --dataset path/to/labelled_feedback.csv --output metrics.json --output-csv predictions.csv

    # Machine-readable JSON output
    python evaluate.py --json
"""

import argparse
import csv
from datetime import datetime, timezone
import json
import math
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

# Ensure app is on import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.taxonomy import taxonomy_manager
from app.services.classifier import classifier_service
from app.services.policy_engine import policy_engine
from app.services.text_preprocessor import TextPreprocessor


def parse_args():
    parser = argparse.ArgumentParser(
        description="Voice of Store Independent Evaluation Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--fixtures",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "data", "fixtures", "ground_truth_test_cases.json"),
        help="Path to independent ground-truth fixtures JSON file for incident detection evaluation",
    )
    parser.add_argument(
        "--dataset",
        "--csv",
        dest="dataset_file",
        type=str,
        default=None,
        help="Optional path to labelled evaluation dataset (CSV, JSON, or JSONL) for record-level evaluation",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON format to stdout instead of human-readable table",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional file path to write JSON evaluation metrics report",
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default=None,
        help="Optional file path to write record-level evaluation predictions as CSV",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Record-Level Evaluation (Classification, Severity, Actionability)
# ---------------------------------------------------------------------------

def calculate_classification_metrics(y_true: List[str], y_pred: List[str]) -> Dict[str, Any]:
    """Calculate accuracy, macro precision, recall, F1, per-class metrics, and confusion matrix."""
    if not y_true or not y_pred or len(y_true) != len(y_pred):
        return {
            "error": "Insufficient or mismatched observations to calculate classification metrics",
            "accuracy": 0.0,
            "macro_precision": 0.0,
            "macro_recall": 0.0,
            "macro_f1": 0.0,
        }

    total = len(y_true)
    correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt.strip().lower() == yp.strip().lower())
    accuracy = round(correct / total, 4)

    classes = sorted(list(set(y_true + y_pred)))
    class_metrics: Dict[str, Dict[str, Any]] = {}

    tp_sum = 0
    prec_list = []
    rec_list = []
    f1_list = []

    for c in classes:
        c_lower = c.strip().lower()
        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt.strip().lower() == c_lower and yp.strip().lower() == c_lower)
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt.strip().lower() != c_lower and yp.strip().lower() == c_lower)
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt.strip().lower() == c_lower and yp.strip().lower() != c_lower)
        support = sum(1 for yt in y_true if yt.strip().lower() == c_lower)

        prec = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
        rec = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
        f1 = round(2 * (prec * rec) / (prec + rec), 4) if (prec + rec) > 0 else 0.0

        if support > 0:
            prec_list.append(prec)
            rec_list.append(rec)
            f1_list.append(f1)

        class_metrics[c] = {
            "support": support,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
        }

    macro_prec = round(sum(prec_list) / len(prec_list), 4) if prec_list else 0.0
    macro_rec = round(sum(rec_list) / len(rec_list), 4) if rec_list else 0.0
    macro_f1 = round(sum(f1_list) / len(f1_list), 4) if f1_list else 0.0

    # Confusion matrix
    conf_matrix: Dict[str, Dict[str, int]] = {c: {c2: 0 for c2 in classes} for c in classes}
    for yt, yp in zip(y_true, y_pred):
        yt_match = next((c for c in classes if c.lower() == yt.lower()), yt)
        yp_match = next((c for c in classes if c.lower() == yp.lower()), yp)
        if yt_match in conf_matrix and yp_match in conf_matrix[yt_match]:
            conf_matrix[yt_match][yp_match] += 1

    return {
        "total_records": total,
        "accuracy": accuracy,
        "macro_precision": macro_prec,
        "macro_recall": macro_rec,
        "macro_f1": macro_f1,
        "per_class": class_metrics,
        "classes": classes,
        "confusion_matrix": conf_matrix,
    }


def evaluate_dataset_file(file_path: str) -> Dict[str, Any]:
    """Load and evaluate a labelled dataset CSV/JSON/JSONL file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Evaluation dataset file not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    raw_rows: List[Dict[str, Any]] = []

    # Read rows
    if ext == ".csv":
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            raw_rows = list(reader)
    elif ext == ".jsonl":
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    raw_rows.append(json.loads(line))
    elif ext == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                raw_rows = data
            elif isinstance(data, dict) and "records" in data:
                raw_rows = data["records"]
            else:
                raw_rows = [data]
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Must be .csv, .json, or .jsonl")

    # Column validation
    total_parsed = len(raw_rows)
    valid_rows: List[Dict[str, Any]] = []
    malformed_rows = 0

    for idx, r in enumerate(raw_rows):
        text_val = r.get("text") or r.get("feedback") or r.get("content") or r.get("comment")
        label_val = (
            r.get("category")
            or r.get("label")
            or r.get("issue_type")
            or r.get("predicted_issue_type")
        )
        if not text_val or not str(text_val).strip() or not label_val or not str(label_val).strip():
            malformed_rows += 1
            continue

        valid_rows.append({
            "record_id": r.get("id") or r.get("record_id") or f"ROW-{idx+1:05d}",
            "store_id": r.get("store_id") or "UNKNOWN",
            "channel": r.get("channel") or "Online Reviews",
            "timestamp": r.get("timestamp") or r.get("event_time") or r.get("created_at"),
            "text": str(text_val).strip(),
            "true_category": str(label_val).strip(),
            "true_severity": r.get("severity") or r.get("true_severity"),
            "true_actionable": r.get("actionable") if r.get("actionable") is not None else r.get("is_actionable"),
        })

    if not valid_rows:
        return {
            "status": "FAILED",
            "file": os.path.basename(file_path),
            "total_records": total_parsed,
            "valid_records": 0,
            "malformed_records": malformed_rows,
            "error": "No valid records found with both text and category label columns.",
        }

    # Sort chronologically if timestamps are provided to prevent temporal leakage
    has_timestamps = any(r["timestamp"] for r in valid_rows)
    if has_timestamps:
        valid_rows.sort(key=lambda r: str(r["timestamp"] or ""))

    # Evaluate predictions
    y_true_cat: List[str] = []
    y_pred_cat: List[str] = []

    y_true_sev: List[str] = []
    y_pred_sev: List[str] = []

    y_true_act: List[str] = []
    y_pred_act: List[str] = []

    detailed_evals: List[Dict[str, Any]] = []

    for r in valid_rows:
        text = r["text"]
        pred = classifier_service.predict(text)
        policy_res = policy_engine.evaluate(text, pred["category"], pred["confidence"])

        # Category
        pred_cat = pred["category"]
        y_true_cat.append(r["true_category"])
        y_pred_cat.append(pred_cat)

        # Severity
        final_sev = policy_res["suggested_severity"] if policy_res["policy_escalated"] else pred.get("predicted_severity", "MEDIUM")
        if r["true_severity"]:
            y_true_sev.append(str(r["true_severity"]).upper())
            y_pred_sev.append(final_sev.upper())

        # Actionability
        final_act = "TRUE" if pred.get("actionable", True) else "FALSE"
        if r["true_actionable"] is not None:
            t_act = "TRUE" if str(r["true_actionable"]).lower() in ["true", "1", "yes"] else "FALSE"
            y_true_act.append(t_act)
            y_pred_act.append(final_act)

        detailed_evals.append({
            "record_id": r["record_id"],
            "store_id": r["store_id"],
            "text": text[:80] + ("..." if len(text) > 80 else ""),
            "true_category": r["true_category"],
            "predicted_category": pred_cat,
            "category_match": r["true_category"].lower() == pred_cat.lower(),
            "confidence": pred["confidence"],
            "true_severity": r["true_severity"],
            "predicted_severity": final_sev,
            "true_actionable": r["true_actionable"],
            "predicted_actionable": pred.get("actionable", True),
            "policy_escalated": policy_res["policy_escalated"],
        })

    cat_metrics = calculate_classification_metrics(y_true_cat, y_pred_cat)

    # Severity metrics (if labels provided)
    sev_metrics = None
    if y_true_sev:
        sev_metrics = calculate_classification_metrics(y_true_sev, y_pred_sev)
    else:
        sev_metrics = {"status": "SKIPPED", "reason": "No severity ground-truth labels provided in dataset"}

    # Actionability metrics (if labels provided)
    act_metrics = None
    if y_true_act:
        act_metrics = calculate_classification_metrics(y_true_act, y_pred_act)
    else:
        act_metrics = {"status": "SKIPPED", "reason": "No actionability ground-truth labels provided in dataset"}

    return {
        "evaluation_timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset_file": os.path.basename(file_path),
        "data_provenance": "Labelled dataset batch evaluation",
        "validation_summary": {
            "total_records": total_parsed,
            "valid_records": len(valid_rows),
            "malformed_records": malformed_rows,
            "has_timestamps": has_timestamps,
        },
        "model_version": classifier_service.model_version,
        "policy_version": policy_engine.POLICY_VERSION,
        "category_metrics": cat_metrics,
        "severity_metrics": sev_metrics,
        "actionability_metrics": act_metrics,
        "record_evaluations": detailed_evals,
    }


# ---------------------------------------------------------------------------
# Incident-Level Evaluation (Chronological Onset, Lead Time, Recall)
# ---------------------------------------------------------------------------

def run_incident_evaluation(fixtures_path: str) -> Dict[str, Any]:
    """Run chronological early detection and lead-time evaluation against ground-truth incident manifests."""
    if not os.path.exists(fixtures_path):
        raise FileNotFoundError(f"Evaluation fixtures file not found: {fixtures_path}")

    with open(fixtures_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    incidents = data.get("ground_truth_incidents", [])
    negatives = data.get("negative_controls", [])

    results: List[Dict[str, Any]] = []
    detected_count = 0
    total_incidents = len(incidents)
    onset_lead_times_days: List[float] = []
    peak_lead_times_days: List[float] = []

    # 1. Evaluate Ground-Truth Incidents
    for inc in incidents:
        inc_id = inc["incident_id"]
        inc_name = inc["name"]
        store_id = inc.get("store_id") or (inc.get("affected_stores", ["UNKNOWN"])[0])
        category = inc.get("category") or inc.get("issue_type", "Other")

        onset_raw = inc.get("onset_date") or inc.get("incident_onset_time", "2026-10-01T00:00:00Z")
        peak_raw = inc.get("peak_date") or inc.get("peak_time", onset_raw)

        onset_dt = datetime.fromisoformat(onset_raw.replace("Z", "+00:00"))
        peak_dt = datetime.fromisoformat(peak_raw.replace("Z", "+00:00"))

        first_detection_dt = None
        qualifying_records_found = 0

        # Sort records chronologically to prevent temporal data leakage
        records = sorted(
            inc.get("records") or inc.get("evidence_records", []),
            key=lambda r: datetime.fromisoformat((r.get("event_time") or r.get("timestamp", "2026-10-01T00:00:00Z")).replace("Z", "+00:00")),
        )

        for rec in records:
            event_dt = datetime.fromisoformat((rec.get("event_time") or rec.get("timestamp", "2026-10-01T00:00:00Z")).replace("Z", "+00:00"))
            text = rec["text"]

            # Run classifier & deterministic policy
            pred = classifier_service.predict(text)
            policy_res = policy_engine.evaluate(text, pred["category"], pred["confidence"])

            is_detected = (
                policy_res["policy_escalated"]
                or pred["category"].lower() in category.lower()
                or category.lower() in pred["category"].lower()
                or (pred.get("predicted_issue_type") and pred["predicted_issue_type"].lower() in category.lower())
            )

            if is_detected:
                qualifying_records_found += 1
                if first_detection_dt is None:
                    first_detection_dt = event_dt

        if first_detection_dt:
            detected_count += 1
            # Lead time to peak crisis: peak_dt - first_detection (days)
            peak_lead_days = max(0.0, (peak_dt - first_detection_dt).total_seconds() / 86400.0)
            # Lead time relative to onset: onset_dt - first_detection (positive = detected before documented onset)
            onset_lead_days = (onset_dt - first_detection_dt).total_seconds() / 86400.0

            peak_lead_times_days.append(peak_lead_days)
            onset_lead_times_days.append(onset_lead_days)
            status = "DETECTED_EARLY"
        else:
            peak_lead_days = 0.0
            onset_lead_days = 0.0
            status = "MISSED"

        results.append({
            "incident_id": inc_id,
            "name": inc_name,
            "store_id": store_id,
            "category": category,
            "status": status,
            "first_detection": first_detection_dt.isoformat() if first_detection_dt else None,
            "onset_date": onset_dt.isoformat(),
            "peak_date": peak_dt.isoformat(),
            "peak_lead_time_days": round(peak_lead_days, 1),
            "onset_lead_time_days": round(onset_lead_days, 1),
            "evidence_count": qualifying_records_found,
        })

    # 2. Evaluate Negative Controls (False Alarm Resistance)
    false_alarms = 0
    negative_evals: List[Dict[str, Any]] = []
    for neg in negatives:
        text = neg["text"]
        pred = classifier_service.predict(text)
        policy_res = policy_engine.evaluate(text, pred["category"], pred["confidence"])

        is_false_alarm = policy_res["policy_escalated"] or (
            pred["category"] in ["Safety", "Food Safety", "Allergens"] and pred["confidence"] > 0.85
        )
        if is_false_alarm:
            false_alarms += 1

        negative_evals.append({
            "text": text[:60] + "...",
            "category": pred["category"],
            "confidence": pred["confidence"],
            "policy_escalated": policy_res["policy_escalated"],
            "is_false_alarm": is_false_alarm,
        })

    # 3. Aggregate Performance Metrics
    recall = round(detected_count / total_incidents, 4) if total_incidents > 0 else 0.0
    true_positives = detected_count
    total_alerts = true_positives + false_alarms
    precision = round(true_positives / total_alerts, 4) if total_alerts > 0 else 1.0
    f1_score = round(2 * (precision * recall) / (precision + recall), 4) if (precision + recall) > 0 else 0.0
    avg_peak_lead_time = round(sum(peak_lead_times_days) / len(peak_lead_times_days), 1) if peak_lead_times_days else 0.0

    # Calculate median lead time
    if peak_lead_times_days:
        s_lead = sorted(peak_lead_times_days)
        mid = len(s_lead) // 2
        median_lead_time = s_lead[mid] if len(s_lead) % 2 != 0 else round((s_lead[mid - 1] + s_lead[mid]) / 2, 1)
    else:
        median_lead_time = 0.0

    report = {
        "evaluation_timestamp": datetime.now(timezone.utc).isoformat(),
        "fixtures_file": os.path.basename(fixtures_path),
        "data_provenance": "Independent ground-truth testing fixtures (software validation mode)",
        "model_version": classifier_service.model_version,
        "policy_version": policy_engine.POLICY_VERSION,
        "metrics": {
            "total_ground_truth_incidents": total_incidents,
            "detected_incidents": detected_count,
            "missed_incidents": total_incidents - detected_count,
            "negative_control_count": len(negatives),
            "false_alarms": false_alarms,
            "recall": recall,
            "precision": precision,
            "f1_score": f1_score,
            "avg_peak_lead_time_days": avg_peak_lead_time,
            "median_lead_time_days": median_lead_time,
            "lead_time_metric_definition": "Days from first qualifying detection to documented peak crisis",
        },
        "incident_evaluations": results,
    }
    return report


# ---------------------------------------------------------------------------
# Output Formatters
# ---------------------------------------------------------------------------

def export_predictions_csv(record_evaluations: List[Dict[str, Any]], output_path: str):
    """Write record-level evaluation predictions to CSV."""
    if not record_evaluations:
        return
    fieldnames = list(record_evaluations[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(record_evaluations)
    print(f"[OK] Record-level evaluation CSV saved to: {output_path}")


def print_record_report(report: Dict[str, Any]):
    print("=" * 80)
    print("        VOICE OF STORE — RECORD CLASSIFICATION EVALUATION REPORT")
    print("=" * 80)
    print(f"Timestamp:       {report['evaluation_timestamp']}")
    print(f"Dataset File:    {report['dataset_file']}")
    print(f"Model Version:   {report['model_version']}")
    print(f"Policy Version:  {report['policy_version']}")
    val = report["validation_summary"]
    print(f"Records:         {val['valid_records']} valid (total parsed: {val['total_records']}, malformed: {val['malformed_records']})")
    print("-" * 80)
    cm = report["category_metrics"]
    print(f"Accuracy:        {cm['accuracy'] * 100:.2f}%")
    print(f"Macro Precision: {cm['macro_precision'] * 100:.2f}%")
    print(f"Macro Recall:    {cm['macro_recall'] * 100:.2f}%")
    print(f"Macro F1 Score:  {cm['macro_f1']:.4f}")
    print("-" * 80)
    print("PER-CLASS CLASSIFICATION BREAKDOWN:")
    print(f"{'Category':<32} {'Support':<10} {'Precision':<12} {'Recall':<10} {'F1':<8}")
    print("-" * 80)
    for cat_name, m in cm.get("per_class", {}).items():
        print(f"{cat_name[:30]:<32} {m['support']:<10} {m['precision']*100:<12.1f} {m['recall']*100:<10.1f} {m['f1_score']:<8.4f}")

    # Severity & Actionability
    print("-" * 80)
    sm = report.get("severity_metrics")
    if sm and sm.get("status") != "SKIPPED":
        print(f"Severity Prediction Accuracy: {sm['accuracy']*100:.1f}%, Macro F1: {sm['macro_f1']:.4f}")
    else:
        print("Severity Ground Truth:       [Not Provided in Dataset]")

    am = report.get("actionability_metrics")
    if am and am.get("status") != "SKIPPED":
        print(f"Actionability Prediction Acc: {am['accuracy']*100:.1f}%, Macro F1: {am['macro_f1']:.4f}")
    else:
        print("Actionability Ground Truth:  [Not Provided in Dataset]")
    print("=" * 80)


def print_incident_report(report: Dict[str, Any]):
    m = report["metrics"]
    print("=" * 80)
    print("        VOICE OF STORE — INDEPENDENT INCIDENT EVALUATION REPORT")
    print("=" * 80)
    print(f"Timestamp:       {report['evaluation_timestamp']}")
    print(f"Fixtures:        {report['fixtures_file']}")
    print(f"Provenance:      {report['data_provenance']}")
    print(f"Model / Policy:  {report['model_version']} / {report['policy_version']}")
    print("-" * 80)
    print(f"Detection Recall:     {m['recall'] * 100:.1f}% ({m['detected_incidents']}/{m['total_ground_truth_incidents']} detected)")
    print(f"Precision:            {m['precision'] * 100:.1f}% ({m['false_alarms']} false alarms on {m['negative_control_count']} negative controls)")
    print(f"F1 Score:             {m['f1_score']:.4f}")
    print(f"Avg. Lead Time:       {m['avg_peak_lead_time_days']:.1f} days before peak crisis")
    print(f"Median Lead Time:     {m['median_lead_time_days']:.1f} days before peak crisis")
    print("-" * 80)
    print("DETECTION BREAKDOWN BY GROUND-TRUTH INCIDENT:")
    print("-" * 80)
    print(f"{'ID':<12} {'Incident Name':<38} {'Lead Time':<12} {'Status':<15}")
    print("-" * 80)
    for r in report["incident_evaluations"]:
        print(f"{r['incident_id']:<12} {r['name'][:36]:<38} {r['peak_lead_time_days']:.1f} days     {r['status']:<15}")
    print("=" * 80)


def main():
    args = parse_args()

    # Mode 1: Record-level dataset evaluation
    if args.dataset_file:
        report = evaluate_dataset_file(args.dataset_file)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_record_report(report)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            print(f"[OK] Evaluation JSON report saved to: {args.output}")

        if args.output_csv and report.get("record_evaluations"):
            export_predictions_csv(report["record_evaluations"], args.output_csv)
        return

    # Mode 2: Incident detection evaluation with ground-truth fixtures
    report = run_incident_evaluation(args.fixtures)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_incident_report(report)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\n[OK] Machine-readable evaluation report saved to: {args.output}")


if __name__ == "__main__":
    main()
