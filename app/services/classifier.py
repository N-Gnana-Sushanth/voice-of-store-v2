"""Machine learning text classification, sentiment, and actionability pipeline."""

import os
import re
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from app.core.config import settings
from app.core.exceptions import ModelInferenceError
from app.core.logging import logger
from app.core.taxonomy import taxonomy_manager
from app.models.incident import IncidentCategory, IncidentSentiment, OwningFunction
from app.services.text_preprocessor import TextPreprocessor


# Curated seed dataset covering all retail incident categories including multilingual & code-mixed examples
SEED_TRAINING_DATA: List[Tuple[str, str]] = [
    # Customer service & Staff
    ("Long wait at customer service desk to process a return", IncidentCategory.CUSTOMER_SERVICE),
    ("Waited 20 minutes for assistance in the electronics department", IncidentCategory.CUSTOMER_SERVICE),
    ("The return policy was not explained clearly by the manager", IncidentCategory.CUSTOMER_SERVICE),
    ("Nobody answered the store phone when I called about opening hours", IncidentCategory.CUSTOMER_SERVICE),
    ("Customer support helpline was helpful but in-store desk was slow", IncidentCategory.CUSTOMER_SERVICE),
    ("Help desk rep couldn't answer questions about store warranty", IncidentCategory.CUSTOMER_SERVICE),
    ("Curbside pickup took over 30 minutes after checking in online", IncidentCategory.CUSTOMER_SERVICE),
    ("Cashier was rude, rolled eyes and ignored customer greeting", IncidentCategory.STAFF_BEHAVIOR),
    ("Staff members talking loudly to each other ignoring customers in line", IncidentCategory.STAFF_BEHAVIOR),
    ("Store associate was dismissive and refused to check the back room", IncidentCategory.STAFF_BEHAVIOR),
    ("Employee made an inappropriate comment to a shopper in aisle 3", IncidentCategory.STAFF_BEHAVIOR),
    ("Staff ne rude behavior kiya, help nahi kiya", IncidentCategory.STAFF_BEHAVIOR),
    ("Cashier romba rude ah pesinaar, mariyadhai illai", IncidentCategory.STAFF_BEHAVIOR),
    ("Staff member khup rude hote aani checkout var durlakshya kela", IncidentCategory.STAFF_BEHAVIOR),
    ("Staff member shouted at customer and walked away 😡", IncidentCategory.STAFF_BEHAVIOR),

    # Cleanliness and hygiene
    ("Restroom was dirty, no hand soap or paper towels available", IncidentCategory.CLEANLINESS_HYGIENE),
    ("Spill on aisle 4 was sticky and hadn't been mopped for hours", IncidentCategory.CLEANLINESS_HYGIENE),
    ("Shopping carts were dirty and sticky with old food residue", IncidentCategory.CLEANLINESS_HYGIENE),
    ("Dust on store shelves and sticky floors near beverage coolers", IncidentCategory.CLEANLINESS_HYGIENE),
    ("Trash cans at store entrance were overflowing with garbage", IncidentCategory.CLEANLINESS_HYGIENE),
    ("Bathroom toilet was clogged and the floor was wet and unclean", IncidentCategory.CLEANLINESS_HYGIENE),
    ("Deli meat counter glass looked smudged and unhygienic", IncidentCategory.CLEANLINESS_HYGIENE),
    ("Store mein bahut kachra hai, washroom bilkul saaf nahi hai 🤮", IncidentCategory.CLEANLINESS_HYGIENE),
    ("Restroom romba azhukku, water logging irukku", IncidentCategory.CLEANLINESS_HYGIENE),
    ("Dukaana madhye swachhata nahi, farshi kharab ahe", IncidentCategory.CLEANLINESS_HYGIENE),

    # Inventory and product availability
    ("Out of stock of whole milk and organic eggs again today", IncidentCategory.INVENTORY_AVAILABILITY),
    ("Shelf tag said on sale but the shelf was completely empty", IncidentCategory.INVENTORY_AVAILABILITY),
    ("App said item was in stock at this store but could not find any", IncidentCategory.INVENTORY_AVAILABILITY),
    ("Ran out of medium sized diapers and infant formula on shelf", IncidentCategory.INVENTORY_AVAILABILITY),
    ("Produce section had no fresh bananas or ripe avocados", IncidentCategory.INVENTORY_AVAILABILITY),
    ("Multiple items out of stock on weekly promotional flyer", IncidentCategory.INVENTORY_AVAILABILITY),
    ("Discontinued my favorite brand without any notice or alternative", IncidentCategory.INVENTORY_AVAILABILITY),
    ("Atta aur daal out of stock hai, shelf pura khali hai", IncidentCategory.INVENTORY_AVAILABILITY),
    ("Arisi and paruppu stock illai, kadaikku vandhu waste", IncidentCategory.INVENTORY_AVAILABILITY),
    ("Tandul aani tel stock madhye nahi, shelves empty ahet", IncidentCategory.INVENTORY_AVAILABILITY),

    # Product or food quality
    ("Bought strawberries yesterday and they were moldy at the bottom", IncidentCategory.PRODUCT_FOOD_QUALITY),
    ("Ground beef smelled sour and was past its expiration date", IncidentCategory.PRODUCT_FOOD_QUALITY),
    ("Rotisserie chicken was lukewarm and undercooked inside", IncidentCategory.PRODUCT_FOOD_QUALITY),
    ("Milk was sour two days before the printed sell-by date", IncidentCategory.PRODUCT_FOOD_QUALITY),
    ("Bread purchased this morning was stale and hard as a rock", IncidentCategory.PRODUCT_FOOD_QUALITY),
    ("Canned soup was dented and leaked in the grocery bag", IncidentCategory.PRODUCT_FOOD_QUALITY),
    ("Bag of salad greens was slimy and rotten inside", IncidentCategory.PRODUCT_FOOD_QUALITY),
    ("Tamatar aur sabzi kharab aur rotten nikla 🤢", IncidentCategory.PRODUCT_FOOD_QUALITY),
    ("Paal thirinjiduchu, date mudiyala aana spoiled", IncidentCategory.PRODUCT_FOOD_QUALITY),
    ("Phale aani bhajya sadi ahet, durgandhi yet ahe", IncidentCategory.PRODUCT_FOOD_QUALITY),

    # Safety
    ("Customer slipped on puddle of water near the floral freezer case", IncidentCategory.SAFETY),
    ("Broken glass on floor in aisle 7 with no warning cone placed", IncidentCategory.SAFETY),
    ("Loose electrical wire hanging from overhead display fixture", IncidentCategory.SAFETY),
    ("Pallet jack left unattended in the middle of pedestrian walkway", IncidentCategory.SAFETY),
    ("Heavy box fell from top riser shelf nearly hitting a customer", IncidentCategory.SAFETY),
    ("Emergency exit door in back was blocked with stacks of pallets", IncidentCategory.SAFETY),
    ("Ice build-up on store entrance sidewalk causing slip hazards", IncidentCategory.SAFETY),
    ("Floor pe paani tha cone ke bina, ek customer gir gaya aur chot lagi ⚠️", IncidentCategory.SAFETY),
    ("Tharayil oil irundhadhu, vazhuki vizhundhen bleeding aagudhu 🚨", IncidentCategory.SAFETY),
    ("Emergency door band ahe, wire baher padli ahe shock lagel", IncidentCategory.SAFETY),

    # Allergens
    ("Bakery cookies with peanut dust stored next to nut-free pastries", IncidentCategory.ALLERGENS),
    ("Customer suffered allergic reaction after deli sandwich had hidden walnuts", IncidentCategory.ALLERGENS),
    ("Pre-packaged salad did not list dairy allergen on the front label", IncidentCategory.ALLERGENS),
    ("Severe peanut allergy reaction, staff used same knife without cleaning", IncidentCategory.ALLERGENS),
    ("Gluten-free counter contaminated with wheat flour from bakery", IncidentCategory.ALLERGENS),
    ("Customer broke out in hives after eating food labeled allergen safe", IncidentCategory.ALLERGENS),
    ("Tree nut warning missing on artisanal dessert package", IncidentCategory.ALLERGENS),
    ("Allergen warning missing, bacche ko peanut se allergy ho gayi hospital le gaye", IncidentCategory.ALLERGENS),
    ("Nut allergy irundhadhu, label poodala, severe hives vandhuchu", IncidentCategory.ALLERGENS),

    # Billing and payments
    ("Double charged on credit card for laundry detergent at checkout", IncidentCategory.BILLING_PAYMENTS),
    ("Self-checkout scanner refused to scan barcode and overcharged", IncidentCategory.BILLING_PAYMENTS),
    ("Register charged full price instead of the displayed sale discount", IncidentCategory.BILLING_PAYMENTS),
    ("Receipt showed two items I did not purchase in my cart", IncidentCategory.BILLING_PAYMENTS),
    ("Card reader chip payment failed multiple times and froze", IncidentCategory.BILLING_PAYMENTS),
    ("Cashier gave incorrect change and refused to recount till", IncidentCategory.BILLING_PAYMENTS),
    ("Digital coupon was clipped on app but did not apply at checkout", IncidentCategory.BILLING_PAYMENTS),
    ("UPI debited twice but bill generate nahi hua, paise cut gaye 💸", IncidentCategory.BILLING_PAYMENTS),
    ("Card swiped double charge aaiduchu, refund tharala", IncidentCategory.BILLING_PAYMENTS),
    ("Bill madhye don vela paise katle, POS machine hang jhale", IncidentCategory.BILLING_PAYMENTS),

    # Equipment & Maintenance
    ("Freezer not cooling properly, all ice cream melted in aisle 4", "Equipment"),
    ("Walk-in refrigerator temperature is warm, milk cartons expanding", "Equipment"),
    ("Air conditioning unit leaking water on produce floor", "Equipment"),
    ("AC not working at all, inside store is stifling and hot", "Equipment"),
    ("Shopping cart wheels squeaking and stuck, unusable", "Equipment"),
    ("Freezer kharab ho gaya hai, sab ice cream pighal gaya", "Equipment"),
    ("Freezer vela seiyala, ice cream urugiduchu", "Equipment"),

    # Other or unknown
    ("General store feedback regarding parking lot lighting at night", IncidentCategory.OTHER_UNKNOWN),
    ("App crashes whenever I try to look at weekly savings circular", IncidentCategory.OTHER_UNKNOWN),
    ("Store background music is way too loud throughout the store", IncidentCategory.OTHER_UNKNOWN),
    ("Cart return corral in parking lot is too far from parking bays", IncidentCategory.OTHER_UNKNOWN),
    ("Not sure where to send this feedback but overall average store", IncidentCategory.OTHER_UNKNOWN),
]


class FeedbackClassifier:
    """Production ML classification service using scikit-learn TF-IDF & Logistic Regression."""

    def __init__(self, model_version: str = settings.MODEL_VERSION):
        self.model_version = model_version
        self.model_dir = settings.MODEL_DIR
        self.model_path = os.path.join(self.model_dir, f"classifier_{self.model_version}.joblib")
        self.pipeline: Optional[Pipeline] = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Load trained model or train and save seed baseline."""
        try:
            if os.path.exists(self.model_path):
                logger.info(f"Loading cached ML model from {self.model_path}")
                self.pipeline = joblib.load(self.model_path)
            else:
                logger.info(f"Training baseline ML classifier {self.model_version}")
                os.makedirs(self.model_dir, exist_ok=True)
                texts = [item[0] for item in SEED_TRAINING_DATA]
                labels = [item[1] for item in SEED_TRAINING_DATA]

                pipeline = Pipeline([
                    ("tfidf", TfidfVectorizer(
                        ngram_range=(1, 2),
                        max_features=10000,
                        sublinear_tf=True,
                        preprocessor=TextPreprocessor.clean_text,
                    )),
                    ("clf", LogisticRegression(
                        max_iter=1000,
                        class_weight="balanced",
                        random_state=42,
                        C=2.0,
                    )),
                ])
                pipeline.fit(texts, labels)
                joblib.dump(pipeline, self.model_path)
                self.pipeline = pipeline
                logger.info(f"Model successfully saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to initialize ML classifier: {e}", exc_info=True)
            self.pipeline = None

    def is_ready(self) -> bool:
        """Check if classifier pipeline is loaded and ready."""
        return self.pipeline is not None

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predict normalized category, confidence score, sentiment, actionability,
        multilingual detection, and evidence span.
        """
        if not text or not text.strip():
            raise ModelInferenceError("Cannot classify empty or blank text")

        if not self.pipeline:
            raise ModelInferenceError("ML classifier model is not initialized or failed to load")

        cleaned = TextPreprocessor.clean_text(text)
        detected_lang = TextPreprocessor.detect_language(cleaned)
        emojis = TextPreprocessor.extract_emojis(cleaned)

        try:
            # Predict category probabilities
            probs = self.pipeline.predict_proba([cleaned])[0]
            classes = self.pipeline.classes_
            top_idx = int(np.argmax(probs))
            predicted_category = str(classes[top_idx])
            confidence = float(probs[top_idx])

            # Class probability distribution map
            all_probs = {str(c): round(float(p), 4) for c, p in zip(classes, probs)}

            # Multi-label detection: identify secondary categories with significant probability
            secondary_categories = [
                str(c) for c, p in zip(classes, probs)
                if p >= 0.20 and str(c) != predicted_category
            ]

            # Uncertainty & human review determination
            needs_human_review = confidence < 0.35 or predicted_category == IncidentCategory.OTHER_UNKNOWN

            # Extract evidence span (highest relevance sentence)
            evidence_span = self._extract_evidence_span(cleaned, predicted_category)

            # Compute actionability score (0.0 to 1.0)
            actionability_score = self._compute_actionability(cleaned)

            # Perform independent sentiment scoring
            sentiment, sentiment_score = self.analyze_sentiment(cleaned, emojis)

            # Look up owning function and category metadata from taxonomy
            tax_cat = taxonomy_manager.get(predicted_category)
            primary_owner = tax_cat.primary_owner if tax_cat else "Store Ops"
            predicted_issue_type = tax_cat.slug if tax_cat else "unknown"
            default_sev = tax_cat.default_severity if tax_cat else "MEDIUM"
            severity_conf = 0.85 if confidence >= 0.50 else 0.65

            # Actionability classification & confidence
            is_actionable = actionability_score >= 0.50
            actionability_conf = round(min(0.99, max(0.50, actionability_score if is_actionable else (1.0 - actionability_score))), 4)

            return {
                "category": predicted_category,
                "confidence": round(confidence, 4),
                "predicted_issue_type": predicted_issue_type,
                "predicted_severity": default_sev,
                "actionable": is_actionable,
                "actionability_confidence": actionability_conf,
                "classification_confidence": round(confidence, 4),
                "severity_confidence": round(severity_conf, 4),
                "secondary_categories": secondary_categories,
                "needs_human_review": needs_human_review,
                "primary_owner": primary_owner,
                "evidence_span": evidence_span,
                "actionability_score": round(actionability_score, 4),
                "language": detected_lang,
                "emojis_found": emojis,
                "all_probabilities": all_probs,
                "sentiment": sentiment,
                "sentiment_score": round(sentiment_score, 4),
                "model_version": self.model_version,
            }
        except Exception as e:
            logger.error(f"Inference error during text classification: {e}", exc_info=True)
            raise ModelInferenceError(f"Model inference failed: {str(e)}")

    def _extract_evidence_span(self, text: str, category: str) -> str:
        """Find the sentence providing the strongest supporting evidence for the prediction."""
        sentences = TextPreprocessor.split_sentences(text)
        if not sentences:
            return text[:120]
        if len(sentences) == 1:
            return sentences[0]

        # Score sentences against category name tokens and taxonomy keywords
        cat_words = set(TextPreprocessor.tokenize_words(category))
        tax_cat = taxonomy_manager.get(category)
        if tax_cat and tax_cat.keywords:
            for kw in tax_cat.keywords:
                cat_words.update(TextPreprocessor.tokenize_words(kw))

        best_sentence = sentences[0]
        best_score = -1.0

        for sent in sentences:
            sent_words = set(TextPreprocessor.tokenize_words(sent))
            overlap = len(sent_words.intersection(cat_words))
            # Also boost if sentence contains problem/action words
            action_boost = 1.0 if any(w in sent.lower() for w in ["spoiled", "curdled", "broken", "leak", "dirty", "unlabeled", "slip", "expired", "warm", "rotten", "defect", "smell", "bad"]) else 0.0
            total_score = overlap + action_boost
            if total_score > best_score:
                best_score = total_score
                best_sentence = sent

        return best_sentence

    def _compute_actionability(self, text: str) -> float:
        """
        Calculates actionability score (0.0 to 1.0) based on specificity:
        - Department/product references
        - Concrete event descriptions
        - Low score for generic vague complaints like 'store is bad'
        """
        words = TextPreprocessor.tokenize_words(text)
        if len(words) < 3:
            return 0.30  # Very short text has low actionability

        actionable_tokens = {
            "freezer", "aisle", "counter", "register", "pos", "milk", "bread",
            "chicken", "receipt", "charge", "refund", "card", "floor", "shelf",
            "door", "exit", "cart", "restroom", "toilet", "cashier", "manager",
            "slip", "fell", "puddle", "leak", "mold", "expired", "roach", "rat"
        }

        matches = sum(1 for w in words if w in actionable_tokens)
        base = 0.50
        bonus = min(0.45, matches * 0.15)
        length_bonus = 0.05 if len(words) >= 10 else 0.0
        return min(0.99, base + bonus + length_bonus)

    @classmethod
    def analyze_sentiment(cls, text: str, emojis: Optional[List[str]] = None) -> Tuple[str, float]:
        """
        Extract sentiment score (-1.0 to 1.0) and categorical sentiment.
        Sentiment is strictly separated from severity.
        """
        words = TextPreprocessor.tokenize_words(text)
        if not words and not emojis:
            return IncidentSentiment.NEUTRAL, 0.0

        positive_lexicon = {
            "great", "good", "excellent", "clean", "friendly", "helpful", "prompt",
            "fast", "courteous", "polite", "loved", "fresh", "satisfaction", "easy",
            "wonderful", "pleasant", "best", "recommend", "thank", "thanks", "saaf", "achha"
        }
        negative_lexicon = {
            "bad", "terrible", "awful", "horrible", "dirty", "filthy", "rude", "slow",
            "broken", "expired", "rotten", "spoiled", "sour", "worst", "unhelpful",
            "smelly", "moldy", "overcharged", "disappointed", "poor", "pain", "hurt",
            "fail", "failed", "refused", "annoyed", "upset", "angry", "never",
            "kharab", "ganda", "kachra", "bekar", "azhukku"
        }

        pos_count = sum(1 for w in words if w in positive_lexicon)
        neg_count = sum(1 for w in words if w in negative_lexicon)

        # Factor in emojis
        if emojis:
            for emoji in emojis:
                if emoji in ["🤮", "🤢", "😡", "😠", "👎", "⚠️", "🚨", "💀", "❌", "💸"]:
                    neg_count += 2
                elif emoji in ["👍", "❤️", "😊", "💯", "✨"]:
                    pos_count += 2

        total_matched = pos_count + neg_count

        if total_matched == 0:
            score = -0.1  # Slight negative bias for incident feedback by default
        else:
            score = (pos_count - neg_count) / total_matched

        score = max(-1.0, min(1.0, score))

        if score > 0.15:
            sentiment = IncidentSentiment.POSITIVE
        elif score < -0.15:
            sentiment = IncidentSentiment.NEGATIVE
        else:
            sentiment = IncidentSentiment.NEUTRAL

        return sentiment, score


# Singleton instance
classifier_service = FeedbackClassifier()
