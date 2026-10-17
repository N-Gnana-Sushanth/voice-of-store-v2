"""Deterministic Safety and Allergen Policy Engine.

Evaluates feedback strictly after ML classification to enforce business
rules, identify safety hazards, and escalate urgent allergen reports.
"""

from datetime import datetime, timezone
import re
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.models.incident import IncidentSeverity
from app.services.text_preprocessor import TextPreprocessor


class SafetyPolicyEngine:
    """Enforces deterministic safety and allergen escalation rules."""

    POLICY_VERSION = settings.POLICY_VERSION

    # High-severity allergen terms
    ALLERGEN_SEVERE_TERMS = [
        "anaphylaxis", "anaphylactic", "epipen", "epi-pen", "throat closing",
        "swollen throat", "swollen tongue", "hives", "allergic reaction",
        "cross-contamination", "cross contamination", "same slicer", "same knife"
    ]

    ALLERGEN_INGREDIENTS = [
        "peanut", "peanuts", "tree nut", "tree nuts", "walnut", "walnuts",
        "almond", "almonds", "cashew", "cashews", "shellfish", "shrimp",
        "crab", "dairy", "milk allergy", "gluten", "celiac", "sesame"
    ]

    # Critical physical hazards
    CRITICAL_SAFETY_TERMS = [
        "slipped and fell", "slip and fall", "slipped on", "tripped on", "tripped over",
        "fell down", "bleeding", "ambulance", "paramedic", "paramedics", "hospital",
        "broken bone", "concussion", "electrical shock", "fire", "smoke", "gas leak",
        "chemical spill", "assault", "physical fight", "weapon", "robbery", "armed",
        "food poisoning", "hospitalized from food", "rat", "cockroach", "roach", "maggot",
        "glass in food", "metal in food", "dead mouse", "mouse droppings"
    ]

    # Moderate physical hazards
    MODERATE_SAFETY_TERMS = [
        "broken glass", "wet floor without cone", "water leaking from ceiling",
        "exposed wire", "blocked fire exit", "pallet falling", "slippery puddle",
        "sharp edge", "unstable display"
    ]

    @classmethod
    def evaluate(
        cls,
        text: str,
        predicted_category: str,
        predicted_confidence: float,
    ) -> Dict[str, Any]:
        """
        Evaluate deterministic safety and allergen policies on preprocessed text.
        Preserves matched evidence and strictly accounts for negation and hypothetical framing.
        """
        sentences = TextPreprocessor.split_sentences(text)
        
        safety_flag = False
        allergen_flag = False
        escalated = False
        reasons: List[str] = []
        matched_evidence: List[Dict[str, Any]] = []

        suggested_severity = IncidentSeverity.MEDIUM

        # 1. Allergen evaluation
        for sentence in sentences:
            sent_lower = sentence.lower()
            if TextPreprocessor.is_hypothetical(sentence):
                continue

            # Check severe allergen terms
            for term in cls.ALLERGEN_SEVERE_TERMS:
                if re.search(r"\b" + re.escape(term) + r"\b", sent_lower):
                    if not TextPreprocessor.is_negated(sentence, term):
                        allergen_flag = True
                        escalated = True
                        reasons.append(f"Severe allergen trigger detected: '{term}'")
                        matched_evidence.append({
                            "type": "ALLERGEN_SEVERE",
                            "term": term,
                            "sentence": sentence,
                        })
                        suggested_severity = IncidentSeverity.CRITICAL

            # Check ingredient + reaction / contamination
            for ingredient in cls.ALLERGEN_INGREDIENTS:
                if re.search(r"\b" + re.escape(ingredient) + r"\b", sent_lower):
                    if not TextPreprocessor.is_negated(sentence, ingredient):
                        # Verify whether there is an adverse issue context or allergy mention
                        if any(k in sent_lower for k in ["allergy", "allergic", "sick", "reaction", "hospital", "labeled", "wrong"]):
                            allergen_flag = True
                            escalated = True
                            reasons.append(f"Allergen risk trigger detected for ingredient: '{ingredient}'")
                            matched_evidence.append({
                                "type": "ALLERGEN_INGREDIENT",
                                "term": ingredient,
                                "sentence": sentence,
                            })
                            if suggested_severity != IncidentSeverity.CRITICAL:
                                suggested_severity = IncidentSeverity.HIGH

        # 2. Safety evaluation
        for sentence in sentences:
            sent_lower = sentence.lower()
            is_hypo = TextPreprocessor.is_hypothetical(sentence)

            # Check Critical safety terms
            for term in cls.CRITICAL_SAFETY_TERMS:
                if re.search(r"\b" + re.escape(term) + r"\b", sent_lower):
                    if not TextPreprocessor.is_negated(sentence, term):
                        if not is_hypo:
                            safety_flag = True
                            escalated = True
                            reasons.append(f"Critical safety hazard detected: '{term}'")
                            matched_evidence.append({
                                "type": "SAFETY_CRITICAL",
                                "term": term,
                                "sentence": sentence,
                            })
                            suggested_severity = IncidentSeverity.CRITICAL

            # Check Moderate safety terms
            for term in cls.MODERATE_SAFETY_TERMS:
                if re.search(r"\b" + re.escape(term) + r"\b", sent_lower):
                    if not TextPreprocessor.is_negated(sentence, term):
                        safety_flag = True
                        if not is_hypo:
                            escalated = True
                            reasons.append(f"Physical safety hazard detected: '{term}'")
                            matched_evidence.append({
                                "type": "SAFETY_MODERATE",
                                "term": term,
                                "sentence": sentence,
                            })
                            if suggested_severity not in (IncidentSeverity.CRITICAL, IncidentSeverity.HIGH):
                                suggested_severity = IncidentSeverity.HIGH

        # Fallback if category was predicted as Safety or Allergens with high confidence
        # but no explicit policy keywords matched
        if not safety_flag and predicted_category == "Safety" and predicted_confidence > 0.70:
            suggested_severity = IncidentSeverity.HIGH
            reasons.append("ML model classified as Safety with high confidence.")

        if not allergen_flag and predicted_category == "Allergens" and predicted_confidence > 0.70:
            suggested_severity = IncidentSeverity.HIGH
            reasons.append("ML model classified as Allergens with high confidence.")

        return {
            "safety_flag": safety_flag,
            "allergen_flag": allergen_flag,
            "policy_escalated": escalated,
            "suggested_severity": suggested_severity,
            "escalation_reasons": reasons,
            "matched_evidence": matched_evidence,
            "policy_version": cls.POLICY_VERSION,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }


# Singleton instance
policy_engine = SafetyPolicyEngine()
