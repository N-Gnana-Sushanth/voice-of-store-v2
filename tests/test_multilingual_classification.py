"""Tests for Unicode-aware multilingual processing, Hinglish classification, and negation handling."""

import pytest
from app.services.classifier import classifier_service
from app.services.text_preprocessor import TextPreprocessor


def test_unicode_preservation_and_normalization():
    """Verify that Devanagari, Tamil, and non-Latin scripts are cleanly preserved."""
    hindi_text = "फ्रीजर खराब है और दूध फट गया है"
    tamil_text = "பால் கெட்டுப்போனது குளிர்சாதன பெட்டி வேலை செய்யவில்லை"

    cleaned_hi = TextPreprocessor.clean_text(hindi_text)
    assert "फ्रीजर" in cleaned_hi
    assert "दूध" in cleaned_hi

    cleaned_ta = TextPreprocessor.clean_text(tamil_text)
    assert "பால்" in cleaned_ta


def test_language_detection():
    """Verify script-based and token-based language identification."""
    assert TextPreprocessor.detect_language("Walk-in freezer temperature is high") == "en"
    assert TextPreprocessor.detect_language("फ्रीजर खराब है") == "hi"
    assert TextPreprocessor.detect_language("பால் கெட்டுப்போனது") == "ta"
    assert TextPreprocessor.detect_language("freezer kharab hai aur doodh leak ho raha hai") == "hinglish"


def test_multilingual_negation_awareness():
    """Verify negation detection across English, Hindi, Tamil, and Marathi."""
    # English
    assert TextPreprocessor.has_negation("The floor is not slippery") is True
    # Hindi
    assert TextPreprocessor.has_negation("फर्श पर पानी नहीं है") is True
    # Hinglish
    assert TextPreprocessor.has_negation("koi problem nahi hai floor saaf hai") is True
    # Tamil
    assert TextPreprocessor.has_negation("பிரச்சனை இல்லை") is True


def test_actionability_scoring():
    """Verify high actionability scores for specific operational complaints."""
    specific_text = "Freezer #3 in dairy aisle is leaking water onto floor creating slip hazard."
    vague_text = "I had an experience at the store today."

    score_specific = classifier_service.predict(specific_text)["actionability_score"]
    score_vague = classifier_service.predict(vague_text)["actionability_score"]

    assert score_specific > score_vague
    assert score_specific >= 0.70


def test_evidence_span_extraction():
    """Verify extraction of the most informative sentence as evidence span."""
    multi_sentence = (
        "I visited the store this morning at 9am. "
        "The milk cartons in aisle 2 were warm and completely curdled. "
        "Parking was easy outside."
    )
    pred = classifier_service.predict(multi_sentence)
    assert "milk cartons" in pred["evidence_span"] or "warm" in pred["evidence_span"]
