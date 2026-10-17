"""Multi-signal incident deduplication service."""

from datetime import datetime, timedelta, timezone
import math
from typing import List, Optional, Set, Tuple
from sqlalchemy.orm import Session
from app.models.feedback import FeedbackRecord
from app.models.incident import Incident, IncidentStatus
from app.services.text_preprocessor import TextPreprocessor


class IncidentDeduplicator:
    """Detects exact and near-duplicate feedback to consolidate incidents."""

    def __init__(
        self,
        time_window_hours: int = 72,
        similarity_threshold: float = 0.40,
    ):
        self.time_window_hours = time_window_hours
        self.similarity_threshold = similarity_threshold

    @classmethod
    def compute_jaccard_similarity(cls, tokens1: Set[str], tokens2: Set[str]) -> float:
        """Calculate Jaccard similarity between two token sets."""
        if not tokens1 or not tokens2:
            return 0.0
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        return float(intersection) / float(union) if union > 0 else 0.0

    @classmethod
    def compute_cosine_similarity(cls, text1: str, text2: str) -> float:
        """
        Compute lightweight term-frequency cosine similarity between two texts.
        Avoids external heavy dependencies while giving precise lexical overlap.
        """
        words1 = TextPreprocessor.tokenize_words(text1)
        words2 = TextPreprocessor.tokenize_words(text2)

        if not words1 or not words2:
            return 0.0

        # Term frequencies
        vec1: dict[str, int] = {}
        for w in words1:
            vec1[w] = vec1.get(w, 0) + 1

        vec2: dict[str, int] = {}
        for w in words2:
            vec2[w] = vec2.get(w, 0) + 1

        common_words = set(vec1.keys()).intersection(set(vec2.keys()))
        dot_product = sum(vec1[w] * vec2[w] for w in common_words)

        norm1 = math.sqrt(sum(v * v for v in vec1.values()))
        norm2 = math.sqrt(sum(v * v for v in vec2.values()))

        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def find_duplicate_incident(
        self,
        db: Session,
        store_id: str,
        category: str,
        text: str,
        event_timestamp: datetime,
    ) -> Tuple[Optional[Incident], float]:
        """
        Find an existing open incident at the same store in the same category within
        the temporal window that matches the incoming text above the similarity threshold.
        """
        # 1. Query candidate active incidents for store & category
        all_candidates: List[Incident] = (
            db.query(Incident)
            .filter(
                Incident.store_id == store_id,
                Incident.category == category,
                Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.UNDER_INVESTIGATION]),
            )
            .order_by(Incident.last_seen_at.desc())
            .all()
        )

        def to_utc(dt: Optional[datetime]) -> Optional[datetime]:
            if dt is None:
                return None
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)

        event_utc = to_utc(event_timestamp) or datetime.now(timezone.utc)

        # Filter candidates within time window
        candidates: List[Incident] = []
        for inc in all_candidates:
            inc_last = to_utc(inc.last_seen_at)
            if inc_last:
                diff_hours = abs((event_utc - inc_last).total_seconds()) / 3600.0
                if diff_hours <= self.time_window_hours:
                    candidates.append(inc)

        if not candidates:
            return None, 0.0

        cleaned_input = TextPreprocessor.clean_text(text)
        best_incident: Optional[Incident] = None
        best_similarity: float = 0.0

        for inc in candidates:
            # Check against incident summary/evidence
            sim_summary = self.compute_cosine_similarity(cleaned_input, inc.evidence_summary or "")
            if sim_summary > best_similarity:
                best_similarity = sim_summary
                best_incident = inc

            # Check linked recent feedback records for exact or near duplicate
            recent_feedbacks: List[FeedbackRecord] = (
                db.query(FeedbackRecord)
                .filter(FeedbackRecord.incident_id == inc.id)
                .order_by(FeedbackRecord.event_timestamp.desc())
                .limit(5)
                .all()
            )

            for fb in recent_feedbacks:
                cleaned_fb = TextPreprocessor.clean_text(fb.text)
                # Exact string match check
                if cleaned_input.lower() == cleaned_fb.lower():
                    return inc, 1.0

                sim_fb = self.compute_cosine_similarity(cleaned_input, cleaned_fb)
                if sim_fb > best_similarity:
                    best_similarity = sim_fb
                    best_incident = inc

        if best_similarity >= self.similarity_threshold:
            return best_incident, best_similarity

        return None, best_similarity


# Singleton instance
deduplicator = IncidentDeduplicator()
