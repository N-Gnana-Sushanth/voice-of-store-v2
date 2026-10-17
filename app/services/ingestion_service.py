"""Feedback ingestion and processing pipeline orchestrator."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.exceptions import EntityNotFoundError, InvalidInputError
from app.core.logging import logger
from app.models.feedback import FeedbackRecord, FeedbackSource, ProcessingStatus
from app.models.incident import (
    Incident,
    IncidentCategory,
    IncidentSeverity,
    IncidentStatus,
)
from app.models.store import Store
from app.schemas.feedback import (
    FeedbackBatchItemResult,
    FeedbackBatchResponse,
    FeedbackSubmitBatch,
    FeedbackSubmitSingle,
)
from app.services.classifier import classifier_service
from app.services.deduplicator import deduplicator
from app.services.policy_engine import policy_engine
from app.services.text_preprocessor import TextPreprocessor


SEVERITY_RANKS = {
    IncidentSeverity.LOW: 1,
    IncidentSeverity.MEDIUM: 2,
    IncidentSeverity.HIGH: 3,
    IncidentSeverity.CRITICAL: 4,
}


class IngestionService:
    """Orchestrates ingestion, classification, deduplication, policy, and persistence."""

    @staticmethod
    def resolve_store(db: Session, store_id_or_number: str) -> Store:
        """Resolve store by UUID primary key or store_number code."""
        store = (
            db.query(Store)
            .filter(
                (Store.id == store_id_or_number) | (Store.store_number == store_id_or_number),
                Store.is_active == True,
            )
            .first()
        )
        if not store:
            raise EntityNotFoundError("Store", store_id_or_number)
        return store

    @classmethod
    def ingest_single(
        cls,
        db: Session,
        submission: FeedbackSubmitSingle,
    ) -> Tuple[FeedbackRecord, Optional[Incident], str]:
        """
        Process a single feedback submission through the mandatory pipeline:
        Ingestion -> Preprocessing -> Classification -> Deduplication -> Policy -> Persistence.
        Returns (FeedbackRecord, Incident, status_string).
        """
        # 1. Resolve and validate store
        store = cls.resolve_store(db, submission.store_id)

        # 2. Idempotency duplicate check
        if submission.idempotency_key:
            existing = (
                db.query(FeedbackRecord)
                .filter(FeedbackRecord.idempotency_key == submission.idempotency_key)
                .first()
            )
            if existing:
                incident = db.query(Incident).filter(Incident.id == existing.incident_id).first() if existing.incident_id else None
                return existing, incident, "DUPLICATE"

        # 3. Determine timestamps
        event_time = submission.event_timestamp
        if event_time is None:
            event_time = datetime.now(timezone.utc)
        elif event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)
        else:
            event_time = event_time.astimezone(timezone.utc)

        # 4. Create initial FeedbackRecord
        feedback = FeedbackRecord(
            store_id=store.id,
            text=submission.text,
            source=submission.source or FeedbackSource.CUSTOMER,
            event_timestamp=event_time,
            ingestion_timestamp=datetime.now(timezone.utc),
            idempotency_key=submission.idempotency_key,
            processing_status=ProcessingStatus.PENDING,
            metadata_json=submission.metadata,
        )
        db.add(feedback)
        db.flush()

        incident: Optional[Incident] = None

        try:
            # 5. Preprocess text
            cleaned_text = TextPreprocessor.clean_text(submission.text)
            if not cleaned_text:
                raise InvalidInputError("Feedback text contains only whitespace or invalid characters")

            # 6. ML Classification & Sentiment Analysis
            pred = classifier_service.predict(cleaned_text)
            predicted_category = pred["category"]
            confidence = pred["confidence"]
            sentiment = pred["sentiment"]
            sentiment_score = pred["sentiment_score"]
            model_ver = pred["model_version"]

            # 7. Deduplication & Incident Association
            matched_incident, sim_score = deduplicator.find_duplicate_incident(
                db=db,
                store_id=store.id,
                category=predicted_category,
                text=cleaned_text,
                event_timestamp=event_time,
            )

            # 8. Deterministic Safety & Allergen Policy Evaluation
            policy_res = policy_engine.evaluate(
                text=cleaned_text,
                predicted_category=predicted_category,
                predicted_confidence=confidence,
            )

            # 9. Persistence of Final Incident State
            if matched_incident:
                incident = matched_incident
                # Update times with timezone normalization
                inc_last = incident.last_seen_at
                if inc_last and inc_last.tzinfo is None:
                    inc_last = inc_last.replace(tzinfo=timezone.utc)
                inc_first = incident.first_seen_at
                if inc_first and inc_first.tzinfo is None:
                    inc_first = inc_first.replace(tzinfo=timezone.utc)

                if inc_last is None or event_time > inc_last:
                    incident.last_seen_at = event_time
                if inc_first is None or event_time < inc_first:
                    incident.first_seen_at = event_time

                incident.feedback_count += 1

                # NEVER suppress urgent safety or allergen escalation on deduplication
                if policy_res["safety_flag"]:
                    incident.safety_flag = True
                if policy_res["allergen_flag"]:
                    incident.allergen_flag = True
                if policy_res["policy_escalated"]:
                    incident.policy_escalated = True
                    current_reasons = incident.policy_escalation_reason or ""
                    new_reasons = "; ".join(policy_res["escalation_reasons"])
                    if new_reasons and new_reasons not in current_reasons:
                        incident.policy_escalation_reason = (
                            f"{current_reasons}; {new_reasons}".strip("; ")
                        )

                # Upgrade severity if incoming report is higher rank
                new_sev = policy_res["suggested_severity"]
                if SEVERITY_RANKS.get(new_sev, 2) > SEVERITY_RANKS.get(incident.severity, 2):
                    incident.severity = new_sev

                # Link feedback
                feedback.incident_id = incident.id
                feedback.processing_status = ProcessingStatus.PROCESSED
            else:
                # Create brand new incident
                esc_reasons = "; ".join(policy_res["escalation_reasons"]) if policy_res["escalation_reasons"] else None
                incident = Incident(
                    store_id=store.id,
                    category=predicted_category,
                    severity=policy_res["suggested_severity"],
                    sentiment=sentiment,
                    sentiment_score=sentiment_score,
                    classification_confidence=confidence,
                    safety_flag=policy_res["safety_flag"],
                    allergen_flag=policy_res["allergen_flag"],
                    policy_escalated=policy_res["policy_escalated"],
                    policy_escalation_reason=esc_reasons,
                    status=IncidentStatus.OPEN,
                    first_seen_at=event_time,
                    last_seen_at=event_time,
                    feedback_count=1,
                    model_version=model_ver,
                    policy_version=policy_res["policy_version"],
                    evidence_summary=cleaned_text[:500],
                    metadata_json={
                        "initial_evidence": policy_res["matched_evidence"],
                        "all_probabilities": pred.get("all_probabilities", {}),
                    },
                )
                db.add(incident)
                db.flush()

                feedback.incident_id = incident.id
                feedback.processing_status = ProcessingStatus.PROCESSED

            db.commit()
            return feedback, incident, "SUCCESS"

        except Exception as e:
            # Downstream ML or business error: mark feedback FAILED but PRESERVE original record
            db.rollback()
            logger.error(f"Downstream failure during feedback ingestion: {e}", exc_info=True)
            # Re-fetch or re-add the raw feedback in failed state
            try:
                failed_fb = FeedbackRecord(
                    store_id=store.id,
                    text=submission.text,
                    source=submission.source or FeedbackSource.CUSTOMER,
                    event_timestamp=event_time,
                    ingestion_timestamp=datetime.now(timezone.utc),
                    idempotency_key=submission.idempotency_key,
                    processing_status=ProcessingStatus.FAILED,
                    error_message=str(e),
                    metadata_json=submission.metadata,
                )
                db.add(failed_fb)
                db.commit()
                return failed_fb, None, "ERROR"
            except Exception as inner_e:
                db.rollback()
                logger.critical(f"Failed to record failed feedback: {inner_e}")
                raise e

    @classmethod
    def ingest_batch(
        cls,
        db: Session,
        batch: FeedbackSubmitBatch,
    ) -> FeedbackBatchResponse:
        """
        Batch ingestion with independent transactions per item.
        Ensures partial batch failures do not roll back successfully committed items.
        """
        results: List[FeedbackBatchItemResult] = []
        successful_count = 0
        duplicate_count = 0
        failed_count = 0

        for index, item in enumerate(batch.items):
            try:
                fb, inc, status = cls.ingest_single(db, item)
                if status == "SUCCESS":
                    successful_count += 1
                    results.append(FeedbackBatchItemResult(
                        index=index,
                        idempotency_key=item.idempotency_key,
                        status="SUCCESS",
                        feedback_id=fb.id,
                        incident_id=inc.id if inc else None,
                        category=inc.category if inc else None,
                        severity=inc.severity if inc else None,
                        safety_flag=inc.safety_flag if inc else False,
                        allergen_flag=inc.allergen_flag if inc else False,
                    ))
                elif status == "DUPLICATE":
                    duplicate_count += 1
                    results.append(FeedbackBatchItemResult(
                        index=index,
                        idempotency_key=item.idempotency_key,
                        status="DUPLICATE",
                        feedback_id=fb.id,
                        incident_id=inc.id if inc else None,
                    ))
                else:
                    failed_count += 1
                    results.append(FeedbackBatchItemResult(
                        index=index,
                        idempotency_key=item.idempotency_key,
                        status="ERROR",
                        feedback_id=fb.id,
                        error=fb.error_message or "Processing error",
                    ))
            except Exception as e:
                failed_count += 1
                results.append(FeedbackBatchItemResult(
                    index=index,
                    idempotency_key=item.idempotency_key,
                    status="ERROR",
                    error=str(e),
                ))

        return FeedbackBatchResponse(
            total_received=len(batch.items),
            successful_count=successful_count,
            duplicate_count=duplicate_count,
            failed_count=failed_count,
            results=results,
        )


# Singleton instance
ingestion_service = IngestionService()
