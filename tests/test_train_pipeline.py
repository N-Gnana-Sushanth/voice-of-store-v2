"""Automated tests for scripts/train_classifier.py ML training pipeline."""

import csv
import json
import os
import tempfile
import pytest

from scripts.train_classifier import (
    prepare_dataset_pipeline,
    split_dataset,
    train_and_evaluate_pipeline,
)


def test_prepare_dataset_pipeline_seed_mode():
    records, quality_report = prepare_dataset_pipeline(None)
    assert len(records) > 0
    assert quality_report["dataset_status"] == "MISSING_REAL_DATASET"
    assert quality_report["valid_records"] == len(records)
    assert "class_distribution" in quality_report
    assert "language_distribution" in quality_report


def test_split_dataset_chronological_and_deterministic():
    # Synthetic records with timestamps
    records = [
        {"record_id": f"R-{i}", "text": f"text {i}", "label": "Equipment", "timestamp": f"2026-10-{i+1:02d}T10:00:00Z"}
        for i in range(20)
    ]
    train, val, test = split_dataset(records)
    assert len(train) == 14  # 70%
    assert len(val) == 3     # 15%
    assert len(test) == 3    # 15%

    # Verify chronological sequence (no future data leakage)
    assert train[-1]["timestamp"] <= val[0]["timestamp"]
    assert val[-1]["timestamp"] <= test[0]["timestamp"]


def test_train_and_evaluate_pipeline_execution():
    with tempfile.TemporaryDirectory() as temp_dir:
        meta = train_and_evaluate_pipeline(
            dataset_path=None,  # Uses seed fixtures
            model_version="v_test_eval",
            output_dir=temp_dir,
            seed=42,
        )

        assert meta["model_version"] == "v_test_eval"
        assert "dataset_metadata" in meta
        assert "model_comparison" in meta
        assert "test_metrics" in meta
        assert meta["test_metrics"]["test_accuracy"] >= 0.0

        # Verify artifacts were generated
        model_file = os.path.join(temp_dir, "classifier_v_test_eval.joblib")
        label_file = os.path.join(temp_dir, "label_mapping_v_test_eval.json")
        meta_file = os.path.join(temp_dir, "training_metadata_v_test_eval.json")

        assert os.path.exists(model_file)
        assert os.path.exists(label_file)
        assert os.path.exists(meta_file)


def test_train_pipeline_with_custom_csv():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f_csv:
        writer = csv.writer(f_csv)
        writer.writerow(["text", "category", "store_id", "timestamp"])
        for i in range(15):
            writer.writerow([f"Customer says freezer {i} is completely broken", "Equipment", "STR-1", f"2026-10-{i+1:02d}T10:00:00Z"])
            writer.writerow([f"Staff rudeness incident at register {i}", "Staff behavior", "STR-2", f"2026-10-{i+1:02d}T11:00:00Z"])
        temp_csv = f_csv.name

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            meta = train_and_evaluate_pipeline(
                dataset_path=temp_csv,
                model_version="v_custom_test",
                output_dir=temp_dir,
                seed=42,
            )
            assert meta["dataset_metadata"]["dataset_status"] == "FOUND"
            assert meta["dataset_metadata"]["valid_records"] == 30
            assert meta["test_metrics"]["test_accuracy"] > 0.80
        finally:
            if os.path.exists(temp_csv):
                os.remove(temp_csv)
