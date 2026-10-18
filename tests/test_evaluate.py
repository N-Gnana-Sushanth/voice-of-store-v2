"""Automated unit and integration tests for evaluate.py evaluation engine."""

import csv
import json
import os
import tempfile
import pytest
from evaluate import (
    calculate_classification_metrics,
    evaluate_dataset_file,
    run_incident_evaluation,
)


def test_calculate_classification_metrics_perfect():
    y_true = ["Safety", "Equipment", "Equipment", "Food Safety"]
    y_pred = ["Safety", "Equipment", "Equipment", "Food Safety"]
    metrics = calculate_classification_metrics(y_true, y_pred)

    assert metrics["accuracy"] == 1.0
    assert metrics["macro_precision"] == 1.0
    assert metrics["macro_recall"] == 1.0
    assert metrics["macro_f1"] == 1.0
    assert "Equipment" in metrics["per_class"]
    assert metrics["per_class"]["Equipment"]["support"] == 2
    assert metrics["confusion_matrix"]["Equipment"]["Equipment"] == 2


def test_calculate_classification_metrics_empty():
    metrics = calculate_classification_metrics([], [])
    assert "error" in metrics
    assert metrics["accuracy"] == 0.0


def test_run_incident_evaluation_fixtures():
    fixtures_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "fixtures", "ground_truth_test_cases.json"
    )
    assert os.path.exists(fixtures_path)

    report = run_incident_evaluation(fixtures_path)
    assert "metrics" in report
    assert "incident_evaluations" in report
    m = report["metrics"]
    assert m["total_ground_truth_incidents"] == 3
    assert m["detected_incidents"] == 3
    assert m["recall"] == 1.0
    assert m["precision"] == 1.0
    assert m["avg_peak_lead_time_days"] > 0
    assert m["median_lead_time_days"] > 0


def test_evaluate_dataset_file_csv_and_malformed():
    # Create temporary CSV with valid and malformed rows
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "category", "severity", "actionable", "timestamp"])
        writer.writerow(["Freezer #2 is broken and leaking water", "Equipment", "HIGH", "true", "2026-10-10T10:00:00Z"])
        writer.writerow(["Found rat in produce section", "Cleanliness and hygiene", "CRITICAL", "true", "2026-10-11T12:00:00Z"])
        writer.writerow(["Staff was rude to cashier", "Staff behavior", "MEDIUM", "true", "2026-10-12T14:00:00Z"])
        writer.writerow(["", "Equipment", "LOW", "true", "2026-10-13T10:00:00Z"])  # Malformed: empty text
        writer.writerow(["Some review text without label", "", "LOW", "true", "2026-10-14T10:00:00Z"])  # Malformed: empty category
        temp_csv = f.name

    try:
        report = evaluate_dataset_file(temp_csv)
        assert report["validation_summary"]["total_records"] == 5
        assert report["validation_summary"]["valid_records"] == 3
        assert report["validation_summary"]["malformed_records"] == 2
        assert report["validation_summary"]["has_timestamps"] is True
        assert "category_metrics" in report
        assert report["category_metrics"]["total_records"] == 3
        assert report["severity_metrics"].get("status") != "SKIPPED"
        assert "accuracy" in report["severity_metrics"]
        assert report["actionability_metrics"].get("status") != "SKIPPED"
        assert "accuracy" in report["actionability_metrics"]
    finally:
        if os.path.exists(temp_csv):
            os.remove(temp_csv)


def test_evaluate_dataset_file_skipped_metrics_when_labels_absent():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "category"])
        writer.writerow(["Freezer #2 temperature is warm", "Equipment"])
        writer.writerow(["Great clean store", "Cleanliness and hygiene"])
        temp_csv = f.name

    try:
        report = evaluate_dataset_file(temp_csv)
        assert report["validation_summary"]["valid_records"] == 2
        assert report["severity_metrics"]["status"] == "SKIPPED"
        assert report["actionability_metrics"]["status"] == "SKIPPED"
        assert "reason" in report["severity_metrics"]
    finally:
        if os.path.exists(temp_csv):
            os.remove(temp_csv)
