"""Deterministic Safety and Allergen Policy Engine.

Evaluates feedback strictly after ML classification to enforce business
rules, identify safety hazards, and escalate urgent allergen reports.
"""

from datetime import datetime, timezone
import re
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.models.incident import IncidentSeverity, OwningFunction
from app.services.text_preprocessor import TextPreprocessor


# Complete Written Escalation Policy Documented per Severity Level
WRITTEN_ESCALATION_POLICY = {
    "version": "1.0.0-audited",
    "last_reviewed": "2026-10-18T00:00:00Z",
    "approved_by": "Retail Safety & Compliance Council",
    "levels": {
        "CRITICAL": {
            "definition": "Imminent threat to life, serious allergic reaction, active physical injury, chemical/electrical hazard, or severe contamination.",
            "qualifying_conditions": [
                "Anaphylactic allergic reaction or EpiPen deployment",
                "Customer or employee slip-and-fall resulting in hospitalization, bleeding, or fractures",
                "Fire, smoke, gas leak, or exposed live electrical wires",
                "Pest or rodent infestation on active food contact surfaces (e.g. rats, maggots)",
                "Physical assault, weapon threat, or violent conduct in store"
            ],
            "immediate_criteria": "Triggered on a single mention (N=1), bypassing all statistical thresholds.",
            "owning_function": OwningFunction.QUALITY_COMPLIANCE,
            "sla_hours": 1,
            "human_review_required": True,
            "resolution_requirements": "Requires store manager and HQ compliance sign-off with corrective action documentation."
        },
        "HIGH": {
            "definition": "High-risk operational failure, allergen labeling omissions, perishable temperature breaches, or repeated staff misconduct.",
            "qualifying_conditions": [
                "Missing or incorrect allergen warning on pre-packaged bakery/deli foods",
                "Refrigeration or walk-in cooler breakdown causing perishable thaw/spoilage",
                "Expired baby food, dairy, or meat sold on retail shelves",
                "Unattended water or oil puddles in pedestrian walkways without hazard cones",
                "Gross staff rudeness, abusive language, or severe cashier misconduct"
            ],
            "immediate_criteria": "Triggered on single explicit keyword match or anomaly detection surge (Z > 2.0).",
            "owning_function": OwningFunction.STORE_OPS,
            "sla_hours": 4,
            "human_review_required": False,
            "resolution_requirements": "Work order dispatched or verified product quarantine logged in Action Queue."
        },
        "MEDIUM": {
            "definition": "Substandard store condition, billing discrepancy, stockout of advertised items, or checkout delays.",
            "qualifying_conditions": [
                "Card reader chip failure or double swipe billing discrepancies",
                "Restroom hygiene, sticky floors, or overflowing trash bins",
                "Out of stock promotional circular items or dairy staples",
                "Excessive checkout line wait times (>15 minutes)"
            ],
            "immediate_criteria": "Triaged by ML classification and clustered into parent incidents.",
            "owning_function": OwningFunction.STORE_OPS,
            "sla_hours": 12,
            "human_review_required": False,
            "resolution_requirements": "Logged into department queue; resolved via standard shift workflows."
        },
        "LOW": {
            "definition": "Minor convenience issues, parking lot lighting, shopping cart wheel squeaks, or general inquiries.",
            "qualifying_conditions": [
                "Wobbly shopping cart wheels",
                "Parking lot bay markings faded",
                "Music volume preferences or app layout feedback"
            ],
            "immediate_criteria": "Categorized for periodic weekly review without real-time alerting.",
            "owning_function": OwningFunction.STORE_OPS,
            "sla_hours": 24,
            "human_review_required": False,
            "resolution_requirements": "Periodic batch maintenance."
        }
    }
}


class SafetyPolicyEngine:
    """Enforces deterministic safety, allergen, and physical hazard escalation rules."""

    POLICY_VERSION = settings.POLICY_VERSION

    # High-severity allergen terms (English + Hinglish/Tamil/Marathi variations)
    ALLERGEN_SEVERE_TERMS = [
        "anaphylaxis", "anaphylactic", "epipen", "epi-pen", "throat closing",
        "swollen throat", "swollen tongue", "hives", "allergic reaction",
        "cross-contamination", "cross contamination", "same slicer", "same knife",
        "bacche ko allergy", "severe hives", "hospital le gaye", " सांस लेने में तकलीफ"
    ]

    ALLERGEN_INGREDIENTS = [
        "peanut", "peanuts", "tree nut", "tree nuts", "walnut", "walnuts",
        "almond", "almonds", "cashew", "cashews", "shellfish", "shrimp",
        "crab", "dairy", "milk allergy", "gluten", "celiac", "sesame",
        "mungfali", "badam", "kaju"
    ]

    # Critical physical hazards & medical emergencies (Multilingual)
    CRITICAL_SAFETY_TERMS = [
        # English
        "slipped and fell", "slip and fall", "slipped on", "tripped on", "tripped over",
        "fell down", "bleeding", "ambulance", "paramedic", "paramedics", "hospital",
        "broken bone", "concussion", "electrical shock", "fire", "smoke", "gas leak",
        "chemical spill", "assault", "physical fight", "weapon", "robbery", "armed",
        "food poisoning", "hospitalized from food", "rat", "cockroach", "roach", "maggot",
        "glass in food", "metal in food", "dead mouse", "mouse droppings", "vomited", "vomiting",
        # Hinglish / Hindi
        "gir gaya", "gir gayi", "chot lagi", "khoon nikal raha", "current laga", "aag lag gayi",
        "dhuan nikal raha", "hospital le gaye", "khana kharab tha ulti hui", "food poisoning ho gaya",
        "chuha", "keeda",
        # Tamil
        "vazhuki vizhundhen", "bleeding aagudhu", "hospital ku ponen", "thee pidithadhu",
        "shock adichudhu", "food poisoning aaiduchu", "periya eli", "karapaan poochi", "azhukku",
        # Marathi
        "padle", "rakt yet ahe", "davakhanyat gele", "aag lagli", "shock basla",
        "jevan kharab hote ulti jhali", "undir", "jhurla"
    ]

    # Moderate physical hazards
    MODERATE_SAFETY_TERMS = [
        "broken glass", "wet floor without cone", "water leaking from ceiling",
        "exposed wire", "blocked fire exit", "pallet falling", "slippery puddle",
        "sharp edge", "unstable display", "ceiling dripping", "slick floor",
        "kichad", "paani phail gaya"
    ]

    # Gross staff misconduct
    STAFF_MISCONDUCT_TERMS = [
        "assault", "hit customer", "groped", "stole money", "threatened violence",
        "drunk staff", "intoxicated employee", "cursed at customer", "shouted loudly",
        "gaali diya", "badtameezi"
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
        misconduct_flag = False
        escalated = False
        reasons: List[str] = []
        matched_evidence: List[Dict[str, Any]] = []

        suggested_severity = IncidentSeverity.MEDIUM
        assigned_owner = OwningFunction.STORE_OPS

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
                        assigned_owner = OwningFunction.QUALITY_COMPLIANCE

            # Check ingredient + adverse reaction / contamination
            for ingredient in cls.ALLERGEN_INGREDIENTS:
                if re.search(r"\b" + re.escape(ingredient) + r"\b", sent_lower):
                    if not TextPreprocessor.is_negated(sentence, ingredient):
                        if any(k in sent_lower for k in ["allergy", "allergic", "sick", "reaction", "hospital", "labeled", "wrong", "hives", "ill"]):
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
                            assigned_owner = OwningFunction.QUALITY_COMPLIANCE

        # 2. Critical Safety evaluation
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
                            if any(k in term for k in ["rat", "mouse", "cockroach", "roach", "maggot", "food poisoning", "vomit"]):
                                assigned_owner = OwningFunction.QUALITY_COMPLIANCE
                            else:
                                assigned_owner = OwningFunction.STORE_OPS

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

            # Check Staff Misconduct terms
            for term in cls.STAFF_MISCONDUCT_TERMS:
                if re.search(r"\b" + re.escape(term) + r"\b", sent_lower):
                    if not TextPreprocessor.is_negated(sentence, term):
                        if not is_hypo:
                            misconduct_flag = True
                            escalated = True
                            reasons.append(f"Staff misconduct trigger detected: '{term}'")
                            matched_evidence.append({
                                "type": "STAFF_MISCONDUCT",
                                "term": term,
                                "sentence": sentence,
                            })
                            suggested_severity = IncidentSeverity.HIGH
                            assigned_owner = OwningFunction.HR

        # Fallback if category was predicted as Safety or Allergens with high confidence
        if not safety_flag and predicted_category == "Safety" and predicted_confidence > 0.70:
            suggested_severity = IncidentSeverity.HIGH
            reasons.append("ML model classified as Safety with high confidence.")

        if not allergen_flag and predicted_category == "Allergens" and predicted_confidence > 0.70:
            suggested_severity = IncidentSeverity.HIGH
            assigned_owner = OwningFunction.QUALITY_COMPLIANCE
            reasons.append("ML model classified as Allergens with high confidence.")

        return {
            "safety_flag": safety_flag,
            "allergen_flag": allergen_flag,
            "misconduct_flag": misconduct_flag,
            "policy_escalated": escalated,
            "suggested_severity": suggested_severity,
            "assigned_owner": assigned_owner,
            "escalation_reasons": reasons,
            "matched_evidence": matched_evidence,
            "policy_version": cls.POLICY_VERSION,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }

    @classmethod
    def get_written_policy(cls) -> Dict[str, Any]:
        """Return the complete written escalation policy."""
        return WRITTEN_ESCALATION_POLICY


# Singleton instance
policy_engine = SafetyPolicyEngine()
