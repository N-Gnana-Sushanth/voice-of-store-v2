"""Unit tests for deterministic safety and allergen policy engine."""

from app.models.incident import IncidentSeverity
from app.services.policy_engine import policy_engine


def test_safety_escalation_critical():
    """Verify critical physical injuries and hazards trigger safety escalation."""
    text = "An elderly customer slipped and fell on water leaking from the ceiling and was bleeding."
    res = policy_engine.evaluate(text, predicted_category="Cleanliness and hygiene", predicted_confidence=0.6)
    
    assert res["safety_flag"] is True
    assert res["policy_escalated"] is True
    assert res["suggested_severity"] == IncidentSeverity.CRITICAL
    assert any("slip and fall" in r.lower() or "slipped and fell" in r.lower() or "bleeding" in r.lower() for r in res["escalation_reasons"])


def test_allergen_escalation_cross_contamination():
    """Verify allergen cross-contamination triggers allergen escalation."""
    text = "Deli staff used the same knife without cleaning, causing severe allergic reaction to walnut residue."
    res = policy_engine.evaluate(text, predicted_category="Customer service", predicted_confidence=0.5)

    assert res["allergen_flag"] is True
    assert res["policy_escalated"] is True
    assert res["suggested_severity"] in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]


def test_negation_awareness_no_false_emergency():
    """Verify negated statements do not trigger emergency escalations."""
    # Negated allergen: "no peanuts"
    text1 = "I asked the cashier if there are peanuts in this loaf and was confirmed there are no peanuts."
    res1 = policy_engine.evaluate(text1, predicted_category="Customer service", predicted_confidence=0.8)
    assert res1["allergen_flag"] is False
    assert res1["policy_escalated"] is False

    # Negated safety hazard: "nobody slipped"
    text2 = "Floor was slightly damp after mopping but caution cone was out and nobody slipped or fell."
    res2 = policy_engine.evaluate(text2, predicted_category="Cleanliness and hygiene", predicted_confidence=0.7)
    assert res2["policy_escalated"] is False


def test_hypothetical_framing():
    """Verify hypothetical statements do not trigger critical emergency escalations."""
    text = "Hypothetically if someone slipped on this aisle they could have fallen."
    res = policy_engine.evaluate(text, predicted_category="Safety", predicted_confidence=0.6)
    assert res["suggested_severity"] != IncidentSeverity.CRITICAL
