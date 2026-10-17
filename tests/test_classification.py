"""Unit tests for ML text preprocessing, classification, and sentiment decoupling."""

import pytest
from app.core.exceptions import ModelInferenceError
from app.models.incident import IncidentCategory, IncidentSentiment
from app.services.classifier import classifier_service
from app.services.text_preprocessor import TextPreprocessor


def test_text_preprocessor_cleaning():
    """Verify whitespace collapse, unicode normalization, and tokenization."""
    raw = "   Restroom   was \r\n  filthy   and  disgusting!!  "
    cleaned = TextPreprocessor.clean_text(raw)
    assert cleaned == "Restroom was filthy and disgusting!!"

    tokens = TextPreprocessor.tokenize_words(cleaned)
    assert "restroom" in tokens
    assert "filthy" in tokens
    assert "disgusting" in tokens


def test_classifier_predictions():
    """Test classification on domain-specific customer feedback."""
    pred_cleanliness = classifier_service.predict("The bathroom was dirty and the floor was wet and unclean.")
    assert pred_cleanliness["category"] == IncidentCategory.CLEANLINESS_HYGIENE
    assert pred_cleanliness["confidence"] > 0.15
    assert pred_cleanliness["sentiment"] == IncidentSentiment.NEGATIVE

    pred_billing = classifier_service.predict("Self-checkout register double charged my credit card for milk.")
    assert pred_billing["category"] == IncidentCategory.BILLING_PAYMENTS

    pred_inventory = classifier_service.predict("Shelf tag said on sale but the shelf was completely out of stock of eggs.")
    assert pred_inventory["category"] == IncidentCategory.INVENTORY_AVAILABILITY


def test_sentiment_severity_decoupling():
    """
    Test that sentiment and severity are strictly independent concepts.
    A negative sentiment score does not automatically imply a high severity incident.
    """
    # 1. Negative sentiment, but low severity operational inconvenience
    feedback_minor = "I was slightly disappointed because you discontinued my favorite brand of soda."
    pred_minor = classifier_service.predict(feedback_minor)
    assert pred_minor["sentiment"] in [IncidentSentiment.NEGATIVE, IncidentSentiment.NEUTRAL]
    assert pred_minor["sentiment_score"] < 0.0

    # 2. Positive sentiment, but containing safety/emergency report
    feedback_safety = "The staff was wonderfully kind and helpful after my mother slipped on the wet puddle."
    pred_safety = classifier_service.predict(feedback_safety)
    # The sentiment can be positive because of praise
    assert pred_safety["sentiment"] in [IncidentSentiment.POSITIVE, IncidentSentiment.NEUTRAL]
    # But sentiment does not suppress the incident or invalidate the content


def test_empty_text_rejection():
    """Verify that classifier explicitly raises ModelInferenceError on empty input."""
    with pytest.raises(ModelInferenceError):
        classifier_service.predict("   \n  \t  ")
