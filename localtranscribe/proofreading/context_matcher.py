"""
Context-aware term matching using spaCy NER.

Provides intelligent disambiguation of terms based on surrounding context,
entity recognition, and keyword analysis.
"""

from typing import Dict, List, Optional, Tuple, Any
import re
import warnings

try:
    import spacy
    from spacy.tokens import Doc, Span
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    warnings.warn(
        "spaCy not installed. Context-aware matching will be disabled. "
        "Install with: pip install spacy && python -m spacy download en_core_web_sm"
    )


class ContextAwareMatcher:
    """
    Intelligent context-aware term matching using spaCy NER.
    Disambiguates terms based on surrounding context.

    This matcher analyzes the context around ambiguous terms to determine
    the most appropriate expansion based on:
    - Named Entity Recognition (NER) - entity types in context
    - Keyword matching - domain-specific keywords nearby
    - Confidence scoring - weighted scoring for best match

    Example:
        >>> matcher = ContextAwareMatcher(nlp)
        >>> text = "The server IP address is 192.168.1.1"
        >>> expansion = matcher.match_with_context(text, "IP", 11)
        >>> print(expansion)  # "Internet Protocol"
    """

    def __init__(
        self,
        nlp: Optional['spacy.Language'] = None,
        context_window: int = 5,
        confidence_threshold: float = 0.0
    ):
        """
        Initialize the context-aware matcher.

        Args:
            nlp: spaCy language model. If None, will attempt to load default model.
            context_window: Number of tokens before/after to consider (default: 5)
            confidence_threshold: Minimum confidence score for disambiguation (default: 0.0)
        """
        if not SPACY_AVAILABLE:
            self.nlp = None
            self.enabled = False
            return

        if nlp is None:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                warnings.warn(
                    "spaCy model 'en_core_web_sm' not found. "
                    "Install with: python -m spacy download en_core_web_sm"
                )
                self.nlp = None
                self.enabled = False
                return
        else:
            self.nlp = nlp

        self.context_window = context_window
        self.confidence_threshold = confidence_threshold
        self.enabled = True
        self.context_rules = self._build_context_rules()

    def _build_context_rules(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Define context rules for disambiguation.

        Returns:
            Dictionary mapping acronyms to possible expansions with scoring rules
        """
        return {
            # IP - Internet Protocol vs Intellectual Property
            "IP": {
                "Internet Protocol": {
                    "entities": ["ORG", "PRODUCT", "GPE"],  # tech context
                    "keywords": [
                        "network", "address", "tcp", "http", "port", "server",
                        "router", "subnet", "dns", "gateway", "firewall",
                        "packet", "protocol", "ipv4", "ipv6"
                    ],
                    "weight": {
                        "entity": 3,
                        "keyword": 2
                    }
                },
                "Intellectual Property": {
                    "entities": ["LAW", "ORG", "PERSON"],  # legal/business context
                    "keywords": [
                        "patent", "trademark", "copyright", "license", "licensing",
                        "infringement", "royalty", "portfolio", "protection",
                        "rights", "legal", "ownership"
                    ],
                    "weight": {
                        "entity": 3,
                        "keyword": 2
                    }
                }
            },

            # PR - Public Relations vs Pull Request
            "PR": {
                "Public Relations": {
                    "entities": ["ORG", "PERSON", "GPE"],
                    "keywords": [
                        "media", "press", "announcement", "release", "statement",
                        "spokesperson", "campaign", "publicity", "marketing",
                        "communications", "journalist"
                    ],
                    "weight": {
                        "entity": 3,
                        "keyword": 2
                    }
                },
                "Pull Request": {
                    "entities": ["PRODUCT", "ORG"],
                    "keywords": [
                        "github", "gitlab", "code", "merge", "review", "commit",
                        "branch", "repository", "diff", "approval", "changes",
                        "developer", "programming"
                    ],
                    "weight": {
                        "entity": 3,
                        "keyword": 2
                    }
                }
            },

            # AI - Artificial Intelligence vs Air Interdiction (military)
            "AI": {
                "Artificial Intelligence": {
                    "entities": ["PRODUCT", "ORG"],
                    "keywords": [
                        "machine learning", "neural", "model", "algorithm",
                        "training", "data", "prediction", "automation",
                        "chatbot", "llm", "deep learning"
                    ],
                    "weight": {
                        "entity": 2,
                        "keyword": 3
                    }
                },
                "Air Interdiction": {
                    "entities": ["GPE", "ORG"],
                    "keywords": [
                        "military", "aircraft", "mission", "strike", "target",
                        "combat", "forces", "enemy", "operations"
                    ],
                    "weight": {
                        "entity": 2,
                        "keyword": 3
                    }
                }
            },

            # OR - Operating Room vs Operations Research
            "OR": {
                "Operating Room": {
                    "entities": ["FAC", "ORG"],
                    "keywords": [
                        "surgery", "surgical", "patient", "hospital", "doctor",
                        "nurse", "procedure", "anesthesia", "medical"
                    ],
                    "weight": {
                        "entity": 3,
                        "keyword": 2
                    }
                },
                "Operations Research": {
                    "entities": ["ORG"],
                    "keywords": [
                        "optimization", "mathematical", "model", "analysis",
                        "logistics", "simulation", "decision", "algorithm"
                    ],
                    "weight": {
                        "entity": 2,
                        "keyword": 3
                    }
                }
            },

            # PI - Principal Investigator vs Private Investigator
            "PI": {
                "Principal Investigator": {
                    "entities": ["PERSON", "ORG"],
                    "keywords": [
                        "research", "study", "grant", "university", "lab",
                        "academic", "scientist", "professor", "experiment",
                        "nih", "nsf", "funding"
                    ],
                    "weight": {
                        "entity": 3,
                        "keyword": 2
                    }
                },
                "Private Investigator": {
                    "entities": ["PERSON"],
                    "keywords": [
                        "detective", "investigation", "surveillance", "case",
                        "evidence", "client", "hired", "background check"
                    ],
                    "weight": {
                        "entity": 2,
                        "keyword": 3
                    }
                }
            },
        }

    def match_with_context(
        self,
        text: str,
        acronym: str,
        position: int
    ) -> Optional[str]:
        """
        Match acronym considering surrounding context.

        Args:
            text: Full text
            acronym: Acronym to disambiguate
            position: Character position of acronym

        Returns:
            Best matching expansion or None if no good match
        """
        if not self.enabled or self.nlp is None:
            return None

        # Check if acronym has disambiguation rules
        if acronym.upper() not in self.context_rules:
            return None

        # Process text with spaCy
        doc = self.nlp(text)

        # Find the token containing the acronym
        token_span = self._find_token_span(doc, position, acronym)
        if not token_span:
            return None

        # Extract context window
        context_start = max(0, token_span.start - self.context_window)
        context_end = min(len(doc), token_span.end + self.context_window)
        context = doc[context_start:context_end]

        # Score each possible expansion
        expansions = self.context_rules[acronym.upper()]
        scores = self._score_expansions(context, expansions)

        # Return highest scoring expansion if above threshold
        if scores:
            best_expansion, best_score = max(scores.items(), key=lambda x: x[1])
            if best_score > self.confidence_threshold:
                return best_expansion

        return None

    def _score_expansions(
        self,
        context: Span,
        expansions: Dict[str, Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Score each possible expansion based on context.

        Args:
            context: spaCy Span containing context tokens
            expansions: Dictionary of possible expansions with rules

        Returns:
            Dictionary mapping expansions to scores
        """
        scores = {}

        # Extract context features
        context_entities = [ent.label_ for ent in context.ents]
        context_text = context.text.lower()

        for expansion, rules in expansions.items():
            score = 0.0

            # Score based on entity types
            entity_weight = rules.get("weight", {}).get("entity", 1)
            for entity_type in rules.get("entities", []):
                if entity_type in context_entities:
                    score += entity_weight

            # Score based on keywords
            keyword_weight = rules.get("weight", {}).get("keyword", 1)
            for keyword in rules.get("keywords", []):
                if keyword.lower() in context_text:
                    score += keyword_weight

            scores[expansion] = score

        return scores

    def _find_token_span(
        self,
        doc: Doc,
        char_pos: int,
        text: str
    ) -> Optional[Span]:
        """
        Find span containing the character position.

        Args:
            doc: spaCy Doc
            char_pos: Character position in original text
            text: The text to find

        Returns:
            Span containing the position or None
        """
        for token in doc:
            if token.idx <= char_pos < token.idx + len(token.text):
                return doc[token.i:token.i+1]
        return None

    def add_disambiguation_rule(
        self,
        acronym: str,
        expansion: str,
        entities: List[str],
        keywords: List[str],
        entity_weight: int = 3,
        keyword_weight: int = 2
    ) -> None:
        """
        Add a custom disambiguation rule.

        Args:
            acronym: The acronym to disambiguate
            expansion: The expansion text
            entities: List of spaCy entity types for this context
            keywords: List of keywords indicating this context
            entity_weight: Weight for entity matches (default: 3)
            keyword_weight: Weight for keyword matches (default: 2)
        """
        if acronym not in self.context_rules:
            self.context_rules[acronym] = {}

        self.context_rules[acronym][expansion] = {
            "entities": entities,
            "keywords": keywords,
            "weight": {
                "entity": entity_weight,
                "keyword": keyword_weight
            }
        }

    def get_all_ambiguous_acronyms(self) -> List[str]:
        """
        Get list of all acronyms with disambiguation rules.

        Returns:
            List of acronyms that can be disambiguated
        """
        return list(self.context_rules.keys())
