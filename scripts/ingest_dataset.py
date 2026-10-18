"""Robust, observable dataset ingestion pipeline for retail feedback records.

Supports CSV, JSON, and JSONL formats with auto-encoding detection,
schema validation, duplicate prevention, and detailed audit reports.
"""

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.logging import logger
from app.models.feedback import FeedbackChannel, FeedbackSource
from app.models.store import Store
from app.schemas.feedback import FeedbackSubmitSingle
from app.services.ingestion_service import ingestion_service


def detect_encoding(file_path: str) -> str:
    """Detect file encoding from BOM or common trial encodings."""
    with open(file_path, "rb") as f:
        raw_start = f.read(4)
        if raw_start.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"
        if raw_start.startswith(b"\xff\xfe") or raw_start.startswith(b"\xfe\xff"):
            return "utf-16"

    # Try utf-8 first
    for enc in ["utf-8", "cp1252", "latin1"]:
        try:
            with open(file_path, "r", encoding=enc) as f:
                f.read(2048)
            return enc
        except UnicodeDecodeError:
            continue
    return "utf-8"


def compute_content_hash(text: str, store_id: str, ts_str: str) -> str:
    """Generate deterministic hash for idempotency and duplicate row detection."""
    payload = f"{store_id.strip()}|{text.strip()}|{ts_str.strip()}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:32]


def normalize_channel(raw_val: Optional[str]) -> str:
    if not raw_val:
        return FeedbackChannel.ONLINE_REVIEWS
    s = raw_val.strip().lower()
    if "app" in s or "play" in s or "ios" in s:
        return FeedbackChannel.APP_RATINGS
    if "staff" in s or "shift" in s or "internal" in s or "employee" in s:
        return FeedbackChannel.STAFF_NOTES
    if "call" in s or "ticket" in s or "phone" in s or "crm" in s:
        return FeedbackChannel.CALL_CENTRE
    return FeedbackChannel.ONLINE_REVIEWS


def parse_timestamp(raw_val: Optional[Any]) -> datetime:
    if not raw_val:
        return datetime.now(timezone.utc)
    if isinstance(raw_val, datetime):
        return raw_val if raw_val.tzinfo else raw_val.replace(tzinfo=timezone.utc)

    s = str(raw_val).strip()
    # Try ISO format
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        pass

    # Common date formats
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    return datetime.now(timezone.utc)


def read_records(file_path: str, encoding: str) -> Generator[Dict[str, Any], None, None]:
    """Generator yielding parsed raw dictionary rows from CSV, JSON, or JSONL."""
    ext = Path(file_path).suffix.lower()

    if ext == ".jsonl":
        with open(file_path, "r", encoding=encoding) as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Malformed JSONL at line {line_no}: {e}")
    elif ext == ".json":
        with open(file_path, "r", encoding=encoding) as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    yield item
            elif isinstance(data, dict):
                yield data
    else:  # Assume CSV
        with open(file_path, "r", encoding=encoding, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield dict(row)


def map_row_to_submission(row: Dict[str, Any], known_stores: Dict[str, str]) -> Tuple[Optional[FeedbackSubmitSingle], Optional[str]]:
    """Map flexible column headers to FeedbackSubmitSingle schema."""
    # Find text
    text = (
        row.get("text")
        or row.get("feedback")
        or row.get("review")
        or row.get("comment")
        or row.get("description")
        or row.get("narrative")
    )
    if not text or len(str(text).strip()) < 3:
        return None, "Missing or insufficient feedback text"

    # Find store identifier
    store_val = (
        row.get("store_id")
        or row.get("store_number")
        or row.get("store")
        or row.get("store_code")
        or row.get("Store")
    )
    if not store_val:
        return None, "Missing store identifier"

    clean_store = str(store_val).strip()
    resolved_store_id = known_stores.get(clean_store) or known_stores.get(clean_store.upper())
    if not resolved_store_id:
        # Check if clean_store is already a valid store UUID
        if clean_store in known_stores.values():
            resolved_store_id = clean_store
        else:
            return None, f"Store '{clean_store}' not found in active store directory"

    # Timestamp
    raw_ts = (
        row.get("event_timestamp")
        or row.get("timestamp")
        or row.get("date")
        or row.get("created_at")
        or row.get("review_date")
    )
    event_time = parse_timestamp(raw_ts)

    # Rating
    raw_rating = row.get("rating") or row.get("stars") or row.get("score")
    rating_val = None
    if raw_rating is not None and str(raw_rating).strip():
        try:
            r = float(raw_rating)
            if 1.0 <= r <= 5.0:
                rating_val = r
        except ValueError:
            pass

    # Channel & Source
    raw_channel = row.get("channel") or row.get("source_channel") or row.get("type")
    channel_val = normalize_channel(raw_channel)

    raw_source = row.get("source")
    if not raw_source:
        raw_source = FeedbackSource.EMPLOYEE if channel_val == FeedbackChannel.STAFF_NOTES else FeedbackSource.CUSTOMER

    idempotency_key = (
        row.get("idempotency_key")
        or row.get("id")
        or compute_content_hash(text, resolved_store_id, event_time.isoformat())
    )

    lang = row.get("language")

    submission = FeedbackSubmitSingle(
        store_id=resolved_store_id,
        text=str(text).strip(),
        source=raw_source,
        channel=channel_val,
        rating=rating_val,
        language=lang,
        event_timestamp=event_time,
        idempotency_key=str(idempotency_key),
        metadata={"import_source": "ingest_dataset_cli", "raw_row": {k: v for k, v in row.items() if k not in ("text", "feedback")}},
    )
    return submission, None


def ingest_dataset_file(
    file_path: str,
    dry_run: bool = False,
    batch_size: int = 100,
    output_report: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute ingestion pipeline on given file."""
    start_time = time.time()
    enc = detect_encoding(file_path)
    logger.info(f"Starting ingestion: file='{file_path}', encoding='{enc}', dry_run={dry_run}")

    db: Session = SessionLocal()
    try:
        # Load active store lookup map
        stores = db.query(Store).filter(Store.is_active == True).all()
        known_stores: Dict[str, str] = {}
        for s in stores:
            known_stores[s.id] = s.id
            if s.store_number:
                known_stores[s.store_number] = s.id
                known_stores[s.store_number.upper()] = s.id
            if s.name:
                known_stores[s.name.lower()] = s.id

        total_records = 0
        valid_records = 0
        invalid_records = 0
        duplicate_records = 0
        successful_records = 0
        failed_records = 0
        errors: List[Dict[str, Any]] = []

        for row in read_records(file_path, enc):
            total_records += 1
            submission, err = map_row_to_submission(row, known_stores)
            if err:
                invalid_records += 1
                if len(errors) < 50:
                    errors.append({"record_index": total_records, "error": err, "sample": str(row)[:100]})
                continue

            valid_records += 1

            if not dry_run:
                try:
                    fb, inc, status = ingestion_service.ingest_single(db, submission)
                    if status == "SUCCESS":
                        successful_records += 1
                    elif status == "DUPLICATE":
                        duplicate_records += 1
                    else:
                        failed_records += 1
                        if len(errors) < 50:
                            errors.append({"record_index": total_records, "error": fb.error_message or "Ingestion failed"})
                except Exception as e:
                    failed_records += 1
                    if len(errors) < 50:
                        errors.append({"record_index": total_records, "error": str(e)})

        duration = round(time.time() - start_time, 2)
        report = {
            "file": file_path,
            "encoding": enc,
            "dry_run": dry_run,
            "total_records": total_records,
            "valid_records": valid_records,
            "invalid_records": invalid_records,
            "successful_records": successful_records if not dry_run else 0,
            "duplicate_records": duplicate_records if not dry_run else 0,
            "failed_records": failed_records if not dry_run else 0,
            "duration_seconds": duration,
            "sample_errors": errors[:20],
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

        if output_report:
            with open(output_report, "w", encoding="utf-8") as rf:
                json.dump(report, rf, indent=2)
            logger.info(f"Audit report written to {output_report}")

        return report
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Voice of Store Dataset Ingestion CLI")
    parser.add_argument("--file", required=True, help="Path to CSV, JSON, or JSONL dataset file")
    parser.add_argument("--dry-run", action="store_true", help="Validate and parse without persisting to database")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch processing chunk size")
    parser.add_argument("--output-report", default=None, help="Path to write JSON audit report")

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' does not exist.", file=sys.stderr)
        sys.exit(1)

    report = ingest_dataset_file(
        file_path=args.file,
        dry_run=args.dry_run,
        batch_size=args.batch_size,
        output_report=args.output_report,
    )

    print("\n--- Ingestion Audit Report ---")
    print(f"File:            {report['file']}")
    print(f"Encoding:        {report['encoding']}")
    print(f"Dry Run:         {report['dry_run']}")
    print(f"Total Rows:      {report['total_records']}")
    print(f"Valid Rows:      {report['valid_records']}")
    print(f"Invalid Rows:    {report['invalid_records']}")
    if not report['dry_run']:
        print(f"Committed:       {report['successful_records']}")
        print(f"Duplicates:      {report['duplicate_records']}")
        print(f"Failed:          {report['failed_records']}")
    print(f"Duration:        {report['duration_seconds']}s")
    if report["sample_errors"]:
        print(f"\nSample errors ({len(report['sample_errors'])}):")
        for err in report["sample_errors"][:5]:
            print(f"  - Row {err.get('record_index')}: {err.get('error')}")


if __name__ == "__main__":
    main()
