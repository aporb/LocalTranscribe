"""
Fuzzy string matching for typo tolerance and near-miss corrections.

Uses RapidFuzz for fast fuzzy string matching to handle misspellings,
typos, and variations in domain-specific terminology.
"""

from typing import Dict, List, Tuple, Optional
import warnings

try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    warnings.warn(
        "RapidFuzz not installed. Fuzzy matching for typos unavailable. "
        "Install with: pip install rapidfuzz"
    )


class FuzzyTermMatcher:
    """
    Fuzzy matcher for handling typos and near-miss term corrections.

    Uses RapidFuzz for fast fuzzy string matching with configurable
    similarity thresholds. Useful for correcting OCR errors, transcription
    mistakes, and common misspellings.

    Similarity Scoring:
    - 100: Exact match
    - 90-99: Very similar (likely typo)
    - 80-89: Similar (possible match)
    - <80: Different terms

    Example:
        >>> matcher = FuzzyTermMatcher(threshold=85)
        >>> matcher.add_terms({"API": "API", "HTTP": "HTTP"})
        >>> matches = matcher.find_fuzzy_matches("The APi uses HTP")
        >>> # [('APi', 'API', 95), ('HTP', 'HTTP', 75)]
    """

    def __init__(
        self,
        threshold: int = 85,
        max_results: int = 3,
        scorer: str = "WRatio"
    ):
        """
        Initialize fuzzy term matcher.

        Args:
            threshold: Minimum similarity score (0-100) for matches
            max_results: Maximum number of fuzzy matches to return per term
            scorer: Scoring algorithm:
                - "WRatio": Weighted ratio (best for mixed case/length)
                - "QRatio": Quick ratio (faster, less accurate)
                - "Ratio": Basic ratio
                - "TokenSort": Token sort ratio
        """
        if not RAPIDFUZZ_AVAILABLE:
            raise ImportError(
                "RapidFuzz is required for FuzzyTermMatcher. "
                "Install with: pip install rapidfuzz"
            )

        self.threshold = threshold
        self.max_results = max_results
        self.terms = {}  # term -> canonical form

        # Select scorer function
        if scorer == "WRatio":
            self.scorer = fuzz.WRatio
        elif scorer == "QRatio":
            self.scorer = fuzz.QRatio
        elif scorer == "Ratio":
            self.scorer = fuzz.ratio
        elif scorer == "TokenSort":
            self.scorer = fuzz.token_sort_ratio
        else:
            self.scorer = fuzz.WRatio

    def add_term(self, term: str, canonical: Optional[str] = None) -> None:
        """
        Add a term to the matcher.

        Args:
            term: The term to match against
            canonical: Canonical form (defaults to term itself)
        """
        self.terms[term.lower()] = canonical or term

    def add_terms(self, terms: Dict[str, str]) -> None:
        """
        Add multiple terms at once.

        Args:
            terms: Dictionary mapping terms to canonical forms
        """
        for term, canonical in terms.items():
            self.add_term(term, canonical)

    def add_terms_from_dict(self, dictionary: Dict[str, str]) -> None:
        """
        Add terms from a domain dictionary.

        Strips regex patterns and uses replacement as canonical form.

        Args:
            dictionary: Dictionary with patterns as keys, replacements as values
        """
        for pattern, replacement in dictionary.items():
            # Strip regex word boundaries
            term = pattern.replace(r"\b", "").strip()
            self.add_term(term, replacement)

    def find_best_match(
        self,
        query: str,
        min_score: Optional[int] = None
    ) -> Optional[Tuple[str, str, float]]:
        """
        Find best fuzzy match for a query term.

        Args:
            query: Term to match
            min_score: Minimum similarity score (uses threshold if None)

        Returns:
            Tuple of (matched_term, canonical_form, score) or None
        """
        if not self.terms:
            return None

        min_score = min_score or self.threshold

        # Use process.extractOne for best match
        result = process.extractOne(
            query.lower(),
            self.terms.keys(),
            scorer=self.scorer,
            score_cutoff=min_score
        )

        if result:
            matched_term, score, _ = result
            canonical = self.terms[matched_term]
            return (matched_term, canonical, score)

        return None

    def find_fuzzy_matches(
        self,
        query: str,
        limit: Optional[int] = None
    ) -> List[Tuple[str, str, float]]:
        """
        Find multiple fuzzy matches for a query.

        Args:
            query: Term to match
            limit: Maximum number of results (uses max_results if None)

        Returns:
            List of (matched_term, canonical_form, score) tuples
        """
        if not self.terms:
            return []

        limit = limit or self.max_results

        # Use process.extract for multiple matches
        results = process.extract(
            query.lower(),
            self.terms.keys(),
            scorer=self.scorer,
            score_cutoff=self.threshold,
            limit=limit
        )

        return [
            (matched_term, self.terms[matched_term], score)
            for matched_term, score, _ in results
        ]

    def correct_text(
        self,
        text: str,
        word_by_word: bool = True,
        min_word_length: int = 3
    ) -> Tuple[str, List[Tuple[str, str, float]]]:
        """
        Correct typos in text using fuzzy matching.

        Args:
            text: Input text with potential typos
            word_by_word: Process word by word vs. full phrases
            min_word_length: Minimum word length to attempt correction

        Returns:
            Tuple of (corrected_text, list of corrections made)
        """
        if not word_by_word:
            # Try to match full text
            match = self.find_best_match(text)
            if match:
                _, canonical, score = match
                return canonical, [(text, canonical, score)]
            return text, []

        # Word-by-word correction
        import re
        words = re.findall(r'\b\w+\b', text)
        corrections = []
        result = text

        for word in words:
            if len(word) < min_word_length:
                continue

            match = self.find_best_match(word)
            if match and match[1] != word:
                matched_term, canonical, score = match
                # Replace in result text (preserve case in context)
                pattern = r'\b' + re.escape(word) + r'\b'
                result = re.sub(pattern, canonical, result, count=1)
                corrections.append((word, canonical, score))

        return result, corrections

    def get_similarity_score(self, term1: str, term2: str) -> float:
        """
        Get similarity score between two terms.

        Args:
            term1: First term
            term2: Second term

        Returns:
            Similarity score (0-100)
        """
        return self.scorer(term1.lower(), term2.lower())

    def remove_term(self, term: str) -> None:
        """
        Remove a term from the matcher.

        Args:
            term: Term to remove
        """
        self.terms.pop(term.lower(), None)

    def clear(self) -> None:
        """Clear all terms from the matcher."""
        self.terms.clear()

    def __len__(self) -> int:
        """Return number of terms in matcher."""
        return len(self.terms)


def create_fuzzy_matcher_from_domains(
    domains: List[str],
    threshold: int = 85
) -> Optional[FuzzyTermMatcher]:
    """
    Create a FuzzyTermMatcher from domain dictionaries.

    Args:
        domains: List of domain names to include
        threshold: Minimum similarity score for matches

    Returns:
        FuzzyTermMatcher or None if RapidFuzz unavailable
    """
    if not RAPIDFUZZ_AVAILABLE:
        return None

    from .domain_dictionaries import get_domain_dictionary

    matcher = FuzzyTermMatcher(threshold=threshold)

    for domain in domains:
        domain_dict = get_domain_dictionary(domain)
        matcher.add_terms_from_dict(domain_dict)

    return matcher


def suggest_corrections(
    text: str,
    dictionary: Dict[str, str],
    threshold: int = 85,
    max_suggestions: int = 3
) -> Dict[str, List[Tuple[str, float]]]:
    """
    Suggest corrections for potentially misspelled terms.

    Args:
        text: Input text
        dictionary: Dictionary of correct terms
        threshold: Minimum similarity score
        max_suggestions: Maximum suggestions per term

    Returns:
        Dictionary mapping found terms to list of (suggestion, score) tuples
    """
    if not RAPIDFUZZ_AVAILABLE:
        return {}

    matcher = FuzzyTermMatcher(threshold=threshold, max_results=max_suggestions)
    matcher.add_terms_from_dict(dictionary)

    import re
    words = re.findall(r'\b\w+\b', text)
    suggestions = {}

    for word in set(words):  # Unique words only
        matches = matcher.find_fuzzy_matches(word)
        if matches and matches[0][0] != word.lower():
            # Only suggest if not exact match
            suggestions[word] = [
                (canonical, score)
                for _, canonical, score in matches
            ]

    return suggestions
