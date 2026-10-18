"""Text preprocessing, normalization, and multilingual linguistic tokenization utilities."""

import re
import unicodedata
from typing import Dict, List, Optional, Set, Tuple


class TextPreprocessor:
    """Cleans and normalizes raw feedback text while preserving semantic and multilingual context."""

    WHITESPACE_RE = re.compile(r"\s+")

    # Comprehensive multilingual negation words (English, Hinglish, Hindi, Tamil, Marathi)
    NEGATION_WORDS: Set[str] = {
        # English
        "no", "not", "never", "neither", "nor", "none", "nobody", "nowhere",
        "nothing", "hardly", "scarcely", "barely", "wasn't", "weren't", "didn't",
        "hasn't", "haven't", "hadn't", "won't", "wouldn't", "shouldn't", "can't",
        "cannot", "couldn't", "without", "dont", "doesnt", "isnt", "arent",
        # Hindi / Hinglish
        "nahi", "nahin", "na", "mat", "bina", "kabhi nahi", "bilkul nahi",
        "नहीं", "ना", "मत", "बिना", "कभी नहीं",
        # Tamil (Transliterated & Script)
        "illai", "aagavillai", "kidayathu", "vendaam", "இல்லை", "கிடையாது",
        # Marathi
        "nahi", "nahit", "nako", "नाही", "नाहीत", "नको"
    }

    # Hypothetical or speculative markers
    HYPOTHETICAL_MARKERS: Set[str] = {
        "if", "hypothetically", "suppose", "assuming", "what if", "could have",
        "would have", "might have", "agar", "kaash", "ஒருவேளை", "जर"
    }

    # High-signal emojis for sentiment and safety
    MEANINGFUL_EMOJIS: Dict[str, str] = {
        "🤮": "vomiting_disgust",
        "🤢": "nausea_sick",
        "😡": "angry_outraged",
        "😠": "annoyed_angry",
        "👎": "thumbs_down_negative",
        "⚠️": "warning_hazard",
        "🚨": "emergency_alert",
        "🐀": "rat_pest",
        "🪳": "cockroach_pest",
        "💀": "severe_danger",
        "🩹": "injury_hurt",
        "❌": "failure_cross",
        "💸": "expensive_overcharged",
        "👍": "thumbs_up_positive",
        "❤️": "love_positive",
        "😊": "happy_positive",
        "💯": "perfect_positive",
    }

    # Common retail phonetic spelling variations and typos in English/Hinglish
    SPELLING_CORRECTIONS: Dict[str, str] = {
        "freezr": "freezer",
        "frezzer": "freezer",
        "refrigrator": "refrigerator",
        "expir": "expired",
        "expierd": "expired",
        "expiery": "expiry",
        "allrgy": "allergy",
        "alergic": "allergic",
        "peenut": "peanut",
        "billeing": "billing",
        "reciept": "receipt",
        "kachra": "garbage",
        "azhukku": "dirty",
        "kichad": "mud",
        "saaf": "clean",
        "kharab": "bad",
        "ganda": "dirty",
    }

    @classmethod
    def clean_text(cls, text: str) -> str:
        """
        Normalize Unicode (NFKC), preserve meaningful emojis and non-Latin scripts
        (Devanagari, Tamil, etc.), collapse whitespace, and trim.
        """
        if not text:
            return ""
        # Normalize NFKC Unicode (collapses compatibility characters while preserving scripts)
        normalized = unicodedata.normalize("NFKC", text)

        # Replace carriage returns and newlines with spaces
        normalized = normalized.replace("\r", " ").replace("\n", " ")

        # Collapse multiple spaces
        normalized = cls.WHITESPACE_RE.sub(" ", normalized).strip()
        return normalized

    @classmethod
    def split_sentences(cls, text: str) -> List[str]:
        """Split text into sentences using common punctuation and newline delimiters."""
        if not text:
            return []
        cleaned = cls.clean_text(text)
        # Split on '.', '!', '?', ';', '|', or Hindi purna viram '।'
        sentences = re.split(r"(?<=[.!?;\n।|])\s+", cleaned)
        return [s.strip() for s in sentences if s.strip()]

    @classmethod
    def tokenize_words(cls, text: str) -> List[str]:
        """
        Unicode-aware tokenization: extracts words across English, Devanagari,
        Tamil, and alphanumeric characters.
        """
        if not text:
            return []
        cleaned = cls.clean_text(text).lower()
        # Match alphanumeric word characters including Devanagari (\u0900-\u097F) and Tamil (\u0B80-\u0BFF) combining signs/matras
        tokens = re.findall(r"[\w\u0900-\u097F\u0B80-\u0BFF]+", cleaned, re.UNICODE)
        # Apply phonetic spelling corrections
        return [cls.SPELLING_CORRECTIONS.get(t, t) for t in tokens if len(t) > 1 or re.match(r"[0-9\u0900-\u097F\u0B80-\u0BFF]", t)]

    @classmethod
    def detect_language(cls, text: str) -> str:
        """
        Detect language or code-mix based on Unicode script distribution.
        Returns: 'en', 'hi', 'ta', 'mr', 'hinglish', or 'mixed'.
        """
        if not text:
            return "en"

        has_devanagari = bool(re.search(r"[\u0900-\u097F]", text))
        has_tamil = bool(re.search(r"[\u0B80-\u0BFF]", text))
        has_latin = bool(re.search(r"[a-zA-Z]", text))

        if has_tamil and has_latin:
            return "tanglish"
        if has_tamil:
            return "ta"
        if has_devanagari and has_latin:
            return "hinglish"
        if has_devanagari:
            # Check Marathi distinctive characters or default to hi
            if any(w in text for w in ["आहे", "नाही", "झाले", "केले", "खूप"]):
                return "mr"
            return "hi"

        # Check for Latin-script Hinglish markers
        lower = text.lower()
        hinglish_markers = ["nahi", "kharab", "karo", "bohot", "bahut", "dukaan", "bhai", "paisa", "paani", "kaam", "hai"]
        if any(re.search(r"\b" + m + r"\b", lower) for m in hinglish_markers):
            return "hinglish"

        return "en"

    @classmethod
    def extract_emojis(cls, text: str) -> List[str]:
        """Extract meaningful sentiment and safety emojis from feedback."""
        return [e for e in cls.MEANINGFUL_EMOJIS if e in text]

    @classmethod
    def is_negated(cls, sentence: str, target_phrase: str, window_words: int = 4) -> bool:
        """
        Check if a target phrase in a sentence is preceded by a negation word
        within a sliding window of words (supports English, Hindi, Hinglish, Tamil).
        """
        sent_lower = sentence.lower()
        target_lower = target_phrase.lower()

        if target_lower not in sent_lower:
            return False

        # Tokenize sentence words using Unicode-aware tokenizer
        words = cls.tokenize_words(sent_lower)
        target_words = cls.tokenize_words(target_lower)

        if not target_words:
            return False

        # Find position of target in word list
        target_start_word = target_words[0]
        for i, word in enumerate(words):
            if word == target_start_word:
                # Check preceding words within window
                start_window = max(0, i - window_words)
                preceding = set(words[start_window:i])
                if preceding.intersection(cls.NEGATION_WORDS):
                    return True
                # Also check immediate succeeding word for post-positioned negation in Hindi/Tamil (e.g., 'freezer kaam nahi kar raha')
                end_window = min(len(words), i + len(target_words) + 2)
                succeeding = set(words[i + len(target_words):end_window])
                if succeeding.intersection(cls.NEGATION_WORDS):
                    return True
        return False

    @classmethod
    def is_hypothetical(cls, sentence: str) -> bool:
        """Check if sentence contains hypothetical framing."""
        sent_lower = sentence.lower()
        for marker in cls.HYPOTHETICAL_MARKERS:
            if re.search(r"\b" + re.escape(marker) + r"\b", sent_lower):
                return True
        return False

    @classmethod
    def has_negation(cls, text: str) -> bool:
        """Check if text contains any recognized multilingual negation token."""
        if not text:
            return False
        tokens = set(cls.tokenize_words(text.lower()))
        return bool(tokens.intersection(cls.NEGATION_WORDS))
