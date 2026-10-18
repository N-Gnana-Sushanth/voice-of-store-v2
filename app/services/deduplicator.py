"""Cross-channel, cross-language multi-signal incident deduplication service."""

from datetime import datetime, timedelta, timezone
import math
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session
from app.models.feedback import FeedbackRecord
from app.models.incident import Incident, IncidentStatus
from app.services.text_preprocessor import TextPreprocessor


class IncidentDeduplicator:
    """
    Groups related feedback across channels and languages into incident clusters.
    Uses hybrid character n-gram + token similarity, temporal decay, and cross-channel context.
    """

    def __init__(
        self,
        time_window_hours: int = 72,
        similarity_threshold: float = 0.40,
        uncertainty_threshold: float = 0.32,
    ):
        self.time_window_hours = time_window_hours
        self.similarity_threshold = similarity_threshold
        self.uncertainty_threshold = uncertainty_threshold

    @classmethod
    def compute_char_ngram_similarity(cls, text1: str, text2: str, n: int = 3) -> float:
        """
        Compute character n-gram Jaccard similarity for typo-tolerant cross-language matching.
        E.g. 'freezer' vs 'frezzer' or transliterated 'kachra' vs 'kachara'.
        """
        s1 = TextPreprocessor.clean_text(text1).lower()
        s2 = TextPreprocessor.clean_text(text2).lower()
        if not s1 or not s2:
            return 0.0

        ngrams1 = {s1[i:i+n] for i in range(len(s1) - n + 1)} if len(s1) >= n else {s1}
        ngrams2 = {s2[i:i+n] for i in range(len(s2) - n + 1)} if len(s2) >= n else {s2}

        intersection = len(ngrams1.intersection(ngrams2))
        union = len(ngrams1.union(ngrams2))
        return float(intersection) / float(union) if union > 0 else 0.0

    @classmethod
    def compute_hybrid_similarity(cls, text1: str, text2: str) -> float:
        """
        Hybrid metric combining word token TF cosine similarity with overlap coefficient,
        character 3-gram similarity for spelling/morphology tolerance, and entity boosting.
        """
        words1 = TextPreprocessor.tokenize_words(text1)
        words2 = TextPreprocessor.tokenize_words(text2)

        if not words1 or not words2:
            return 0.0

        # Term frequencies
        vec1: Dict[str, int] = {}
        for w in words1:
            vec1[w] = vec1.get(w, 0) + 1

        vec2: Dict[str, int] = {}
        for w in words2:
            vec2[w] = vec2.get(w, 0) + 1

        common_words = set(vec1.keys()).intersection(set(vec2.keys()))
        dot_product = sum(vec1[w] * vec2[w] for w in common_words)

        norm1 = math.sqrt(sum(v * v for v in vec1.values()))
        norm2 = math.sqrt(sum(v * v for v in vec2.values()))

        token_cos = (dot_product / (norm1 * norm2)) if (norm1 > 0 and norm2 > 0) else 0.0
        overlap_coeff = (dot_product / min(norm1 * norm1, norm2 * norm2)) if (norm1 > 0 and norm2 > 0) else 0.0
        char_sim = cls.compute_char_ngram_similarity(text1, text2, n=3)

        # Entity booster: check shared specific locations, departments, aisles, appliances
        entities1 = set(re.findall(r"\b(?:aisle|lane|register|freezer|cooler|shelf|produce|bakery|deli|dairy|checkout|entrance|parking)\s*\#?\d*\b", text1.lower()))
        entities2 = set(re.findall(r"\b(?:aisle|lane|register|freezer|cooler|shelf|produce|bakery|deli|dairy|checkout|entrance|parking)\s*\#?\d*\b", text2.lower()))
        entity_boost = 0.12 if entities1 and entities2 and entities1.intersection(entities2) else 0.0

        base_sim = max(token_cos, (0.45 * token_cos) + (0.35 * overlap_coeff) + (0.20 * char_sim))
        combined = base_sim + entity_boost
        return min(1.0, combined)

    def find_duplicate_incident(
        self,
        db: Session,
        store_id: str,
        category: str,
        text: str,
        event_timestamp: datetime,
        channel: Optional[str] = None,
    ) -> Tuple[Optional[Incident], float, Dict[str, Any]]:
        """
        Find candidate incident matching store, category, and time window.
        Returns (Incident, similarity_score, match_explanation).
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

        def to_utc(dt: Optional[datetime]) -> datetime:
            if dt is None:
                return datetime.now(timezone.utc)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)

        event_utc = to_utc(event_timestamp)

        # Filter candidates within temporal window
        candidates: List[Incident] = []
        for inc in all_candidates:
            inc_last = to_utc(inc.last_seen_at)
            diff_hours = abs((event_utc - inc_last).total_seconds()) / 3600.0
            if diff_hours <= self.time_window_hours:
                candidates.append(inc)

        if not candidates:
            return None, 0.0, {"match_type": "NO_CANDIDATE_INCIDENT", "reason": "No active incidents in time window."}

        cleaned_input = TextPreprocessor.clean_text(text)
        best_incident: Optional[Incident] = None
        best_similarity: float = 0.0
        match_details: Dict[str, Any] = {}

        for inc in candidates:
            # Check against incident summary/evidence
            sim_summary = self.compute_hybrid_similarity(cleaned_input, inc.evidence_summary or "")
            if sim_summary > best_similarity:
                best_similarity = sim_summary
                best_incident = inc
                match_details = {
                    "matched_target": "evidence_summary",
                    "incident_id": inc.id,
                    "target_text": inc.evidence_summary[:100] if inc.evidence_summary else "",
                }

            # Check linked recent feedback records
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
                    explanation = {
                        "match_type": "EXACT_DUPLICATE",
                        "similarity_score": 1.0,
                        "matched_feedback_id": fb.id,
                        "matched_channel": fb.channel,
                        "current_channel": channel,
                        "is_cross_channel": fb.channel != channel if (fb.channel and channel) else False,
                        "reason": f"Exact verbatim match with feedback {fb.id[:8]}",
                    }
                    return inc, 1.0, explanation

                sim_fb = self.compute_hybrid_similarity(cleaned_input, cleaned_fb)
                if sim_fb > best_similarity:
                    best_similarity = sim_fb
                    best_incident = inc
                    match_details = {
                        "matched_target": f"feedback_{fb.id[:8]}",
                        "matched_feedback_id": fb.id,
                        "matched_channel": fb.channel,
                        "current_channel": channel,
                        "is_cross_channel": fb.channel != channel if (fb.channel and channel) else False,
                    }

        # Determine threshold qualification
        if best_similarity >= self.similarity_threshold:
            explanation = {
                "match_type": "CROSS_CHANNEL_CLUSTER" if match_details.get("is_cross_channel") else "HIGH_SIMILARITY_CLUSTER",
                "similarity_score": round(best_similarity, 4),
                "matched_incident_id": best_incident.id if best_incident else None,
                "matched_channel": match_details.get("matched_channel"),
                "current_channel": channel,
                "is_cross_channel": match_details.get("is_cross_channel", False),
                "reason": (
                    f"Hybrid similarity ({best_similarity:.2f}) exceeds threshold ({self.similarity_threshold:.2f}). "
                    f"Corroborated across channels: {match_details.get('matched_channel', 'Unknown')} & {channel or 'Unknown'}."
                ),
            }
            return best_incident, best_similarity, explanation

        elif best_similarity >= self.uncertainty_threshold:
            explanation = {
                "match_type": "UNCERTAIN_MATCH_PENDING_REVIEW",
                "similarity_score": round(best_similarity, 4),
                "matched_incident_id": best_incident.id if best_incident else None,
                "needs_human_review": True,
                "reason": f"Similarity ({best_similarity:.2f}) falls in ambiguous band [{self.uncertainty_threshold}, {self.similarity_threshold}]. Flagged for human review.",
            }
            return None, best_similarity, explanation

        return None, best_similarity, {"match_type": "DISTINCT_ISSUE", "similarity_score": round(best_similarity, 4), "reason": "Below threshold."}


deduplicator = IncidentDeduplicator()
