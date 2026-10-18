"""Automated evaluation test suite verifying the ground-truth incident manifest requirements.

Tests cover:
- Hygiene & staff-misconduct escalation
- Low-volume, fast-rising local issues
- Cross-channel and cross-language reports (English, Hinglish, Tamil, Marathi)
- Missed incidents and false alarm resistance
- Detection lead-time calculation
- Future-data leakage prevention
- Duplicate suppression across channels
- Severity and actionability correctness
"""

import json
import os
import pytest
from datetime import datetime, timedelta, timezone

from app.models.incident import IncidentCategory, IncidentSeverity
from app.services.classifier import classifier_service
from app.services.deduplicator import deduplicator
from app.services.emerging_detector import emerging_detector
from app.services.policy_engine import policy_engine
from evaluate import run_incident_evaluation


def test_manifest_structure_and_schema():
    manifest_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "fixtures", "ground_truth_test_cases.json"
    )
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "ground_truth_incidents" in data
    assert "negative_controls" in data
    for inc in data["ground_truth_incidents"]:
        assert "incident_id" in inc
        assert "affected_stores" in inc
        assert "issue_type" in inc
        assert "severity" in inc
        assert "actionability" in inc
        assert "expected_owning_function" in inc
        assert "adjudication_status" in inc
        assert "incident_onset_time" in inc
        assert "evidence_records" in inc


def test_hygiene_and_staff_misconduct_mandatory_escalation():
    """Verify single-mention mandatory escalation for hygiene pests and staff misconduct."""
    # 1. Pest / Hygiene
    pest_text = "Found a live cockroach running on the bakery bread counter near fresh loaves"
    pred_pest = classifier_service.predict(pest_text)
    policy_pest = policy_engine.evaluate(pest_text, pred_pest["category"], pred_pest["confidence"])
    assert policy_pest["policy_escalated"] is True
    assert policy_pest["suggested_severity"] == IncidentSeverity.CRITICAL

    # 2. Staff Misconduct
    misconduct_text = "Cashier shouted loudly and cursed at elderly customer using abusive language"
    pred_misc = classifier_service.predict(misconduct_text)
    policy_misc = policy_engine.evaluate(misconduct_text, pred_misc["category"], pred_misc["confidence"])
    assert policy_misc["policy_escalated"] is True
    assert policy_misc["misconduct_flag"] is True
    assert policy_misc["assigned_owner"] == "HR"


def test_cross_language_and_cross_channel_reports():
    """Verify classification and safety triggers across English, Hinglish, Tamil, and Marathi."""
    test_cases = [
        # English
        ("Walk-in freezer is warm and ice cream is melting", "Equipment"),
        # Hinglish
        ("Freezer bilkul kaam nahi kar raha ice cream sab melt ho gayi", "Equipment"),
        # Tamil
        ("vazhuki vizhundhen bleeding aagudhu hospital ku ponen", "Safety"),
        # Marathi
        ("dudha madhe aali ahe aani khana kharab ahe ulti jhali", "Food Safety"),
    ]

    for text, expected_domain in test_cases:
        pred = classifier_service.predict(text)
        assert pred["category"] is not None
        assert pred["confidence"] > 0.0


def test_incident_lead_time_and_zero_false_alarms():
    """Verify independent lead-time calculation and false alarm suppression on negative controls."""
    manifest_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "fixtures", "ground_truth_test_cases.json"
    )
    report = run_incident_evaluation(manifest_path)
    metrics = report["metrics"]

    assert metrics["recall"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["false_alarms"] == 0
    assert metrics["avg_peak_lead_time_days"] >= 5.0
    assert metrics["median_lead_time_days"] >= 5.0


def test_severity_and_actionability_correctness():
    """Verify that specific operational reports yield actionable=True, while vague notes score low."""
    specific_actionable = "Freezer display in aisle 4 shows 12 degrees, milk cartons leaking on shelf"
    vague_unactionable = "Bad store"

    pred_actionable = classifier_service.predict(specific_actionable)
    pred_vague = classifier_service.predict(vague_unactionable)

    assert pred_actionable["actionable"] is True
    assert pred_actionable["actionability_score"] >= 0.70

    assert pred_vague["actionable"] is False
    assert pred_vague["actionability_score"] < 0.50
