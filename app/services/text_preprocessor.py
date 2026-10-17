"""Text preprocessing, normalization, and linguistic tokenization utilities."""

import re
import unicodedata
from typing import List, Tuple


class TextPreprocessor:
    """Cleans and normalizes raw feedback text while preserving semantic context."""

    # Regex for stripping excess whitespace
    WHITESPACE_RE = re.compile(r"\s+")
    
    # Common negation words in customer feedback
    NEGATION_WORDS = {
        "no", "not", "never", "neither", "nor", "none", "nobody", "nowhere",
        "nothing", "hardly", "scarcely", "barely", "wasn't", "weren't", "didn't",
        "hasn't", "haven't", "hadn't", "won't", "wouldn't", "shouldn't", "can't",
        "cannot", "couldn't", "without"
    }

    # Hypothetical or speculative markers
    HYPOTHETICAL_MARKERS = {
        "if", "hypothetically", "suppose", "assuming", "what if", "could have",
        "would have", "might have"
    }

    @classmethod
    def clean_text(cls, text: str) -> str:
        """Normalize Unicode, collapse extra spaces, and trim."""
        if not text:
            return ""
        # Normalize NFKC Unicode (collapses compatibility characters)
        normalized = unicodedata.normalize("NFKC", text)
        # Replace carriage returns and newlines with spaces
        normalized = normalized.replace("\r", " ").replace("\n", " ")
        # Collapse multiple spaces
        normalized = cls.WHITESPACE_RE.sub(" ", normalized).strip()
        return normalized

    @classmethod
    def split_sentences(cls, text: str) -> List[str]:
        """Split text into sentences using common punctuation delimiters."""
        if not text:
            return []
        cleaned = cls.clean_text(text)
        # Split on '.', '!', '?', or ';' followed by space or end of string
        sentences = re.split(r"(?<=[.!?;\n])\s+", cleaned)
        return [s.strip() for s in sentences if s.strip()]

    @classmethod
    def tokenize_words(cls, text: str) -> List[str]:
        """Extract lowercase alphabetic word tokens."""
        if not text:
            return []
        return re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())

    @classmethod
    def is_negated(cls, sentence: str, target_phrase: str, window_words: int = 4) -> bool:
        """
        Check if a target phrase in a sentence is preceded by a negation word
        within a sliding window of words.
        """
        sent_lower = sentence.lower()
        target_lower = target_phrase.lower()
        
        if target_lower not in sent_lower:
            return False

        # Tokenize sentence words
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
        return False

    @classmethod
    def is_hypothetical(cls, sentence: str) -> bool:
        """Check if sentence contains hypothetical framing."""
        sent_lower = sentence.lower()
        for marker in cls.HYPOTHETICAL_MARKERS:
            if re.search(r"\b" + re.escape(marker) + r"\b", sent_lower):
                return True
        return False
