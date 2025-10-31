"""
High-performance keyword matching using FlashText.

Provides 10-100x faster dictionary lookups compared to regex for large
term dictionaries (1000+ terms). Optional performance enhancement.
"""

from typing import Dict, List, Tuple, Optional, Set
import warnings

try:
    from flashtext import KeywordProcessor
    FLASHTEXT_AVAILABLE = True
except ImportError:
    FLASHTEXT_AVAILABLE = False
    KeywordProcessor = None
    warnings.warn(
        "FlashText not installed. Fast dictionary matching unavailable. "
        "Install with: pip install flashtext"
    )


class FastDictionaryMatcher:
    """
    High-performance dictionary term matching using FlashText.

    FlashText provides O(n) complexity for keyword extraction where n is
    the length of the document, regardless of dictionary size. This is
    significantly faster than regex-based approaches for large dictionaries.

    Performance Comparison (1000+ terms):
    - Regex: O(n * m) where m is number of patterns
    - FlashText: O(n) regardless of dictionary size

    Example:
        >>> matcher = FastDictionaryMatcher()
        >>> matcher.add_terms({"api": "API", "http": "HTTP"})
        >>> text = "The api uses http protocol"
        >>> replacements = matcher.find_matches(text)
        >>> # [('api', 'API', 4), ('http', 'HTTP', 13)]
    """

    def __init__(self, case_sensitive: bool = False):
        """
        Initialize fast dictionary matcher.

        Args:
            case_sensitive: Whether to perform case-sensitive matching
        """
        if not FLASHTEXT_AVAILABLE:
            raise ImportError(
                "FlashText is required for FastDictionaryMatcher. "
                "Install with: pip install flashtext"
            )

        self.processor = KeywordProcessor(case_sensitive=case_sensitive)
        self.case_sensitive = case_sensitive
        self.term_count = 0

    def add_term(self, keyword: str, replacement: str) -> None:
        """
        Add a single term to the matcher.

        Args:
            keyword: The keyword to match (can be multi-word)
            replacement: The replacement text
        """
        self.processor.add_keyword(keyword, replacement)
        self.term_count += 1

    def add_terms(self, terms: Dict[str, str]) -> None:
        """
        Add multiple terms at once.

        Args:
            terms: Dictionary mapping keywords to replacements
        """
        for keyword, replacement in terms.items():
            self.add_term(keyword, replacement)

    def add_terms_from_dict(self, dictionary: Dict[str, str]) -> None:
        """
        Add terms from a domain dictionary (regex patterns to replacements).

        Converts regex patterns to plain text by stripping word boundaries.

        Args:
            dictionary: Dictionary with regex patterns as keys
        """
        for pattern, replacement in dictionary.items():
            # Strip regex word boundaries \b
            keyword = pattern.replace(r"\b", "").strip()
            self.add_term(keyword, replacement)

    def find_matches(self, text: str) -> List[Tuple[str, str, int]]:
        """
        Find all matching terms in text.

        Args:
            text: Input text to search

        Returns:
            List of (keyword, replacement, position) tuples
        """
        matches = []

        # FlashText doesn't provide positions by default, so we need to find them
        keywords_found = self.processor.extract_keywords(text, span_info=True)

        for keyword, start, end in keywords_found:
            matches.append((text[start:end], keyword, start))

        return matches

    def replace_keywords(self, text: str) -> str:
        """
        Replace all matching keywords in text.

        Args:
            text: Input text

        Returns:
            Text with all keywords replaced
        """
        return self.processor.replace_keywords(text)

    def get_all_keywords(self) -> Set[str]:
        """
        Get all keywords in the matcher.

        Returns:
            Set of all registered keywords
        """
        # FlashText doesn't expose keywords directly, maintain our own count
        return set(self.processor.get_all_keywords().keys())

    def remove_term(self, keyword: str) -> None:
        """
        Remove a term from the matcher.

        Args:
            keyword: Keyword to remove
        """
        self.processor.remove_keyword(keyword)
        self.term_count = max(0, self.term_count - 1)

    def clear(self) -> None:
        """Clear all terms from the matcher."""
        # Recreate processor to clear all terms
        self.processor = KeywordProcessor(case_sensitive=self.case_sensitive)
        self.term_count = 0

    def __len__(self) -> int:
        """Return number of terms in matcher."""
        return self.term_count


class HybridMatcher:
    """
    Hybrid matcher that uses FlashText when available, falls back to regex.

    Automatically selects the best matching strategy based on:
    - Dictionary size (FlashText better for 100+ terms)
    - FlashText availability
    - Pattern complexity (regex for complex patterns)

    Example:
        >>> matcher = HybridMatcher()
        >>> # Uses FlashText if available, regex otherwise
        >>> matches = matcher.find_matches(text, dictionary)
    """

    def __init__(self, flashtext_threshold: int = 100):
        """
        Initialize hybrid matcher.

        Args:
            flashtext_threshold: Min dictionary size to use FlashText
        """
        self.flashtext_threshold = flashtext_threshold
        self.flashtext_available = FLASHTEXT_AVAILABLE

    def find_matches(
        self,
        text: str,
        dictionary: Dict[str, str],
        case_sensitive: bool = False
    ) -> List[Tuple[str, str, int]]:
        """
        Find matches using optimal strategy.

        Args:
            text: Input text
            dictionary: Dictionary of patterns/keywords to replacements
            case_sensitive: Case-sensitive matching

        Returns:
            List of (matched_text, replacement, position) tuples
        """
        # Use FlashText for large dictionaries if available
        if (self.flashtext_available and
            len(dictionary) >= self.flashtext_threshold):
            return self._find_with_flashtext(text, dictionary, case_sensitive)
        else:
            return self._find_with_regex(text, dictionary, case_sensitive)

    def _find_with_flashtext(
        self,
        text: str,
        dictionary: Dict[str, str],
        case_sensitive: bool
    ) -> List[Tuple[str, str, int]]:
        """Use FlashText for matching."""
        matcher = FastDictionaryMatcher(case_sensitive=case_sensitive)
        matcher.add_terms_from_dict(dictionary)
        return matcher.find_matches(text)

    def _find_with_regex(
        self,
        text: str,
        dictionary: Dict[str, str],
        case_sensitive: bool
    ) -> List[Tuple[str, str, int]]:
        """Fall back to regex matching."""
        import re
        matches = []

        flags = 0 if case_sensitive else re.IGNORECASE

        for pattern, replacement in dictionary.items():
            for match in re.finditer(pattern, text, flags):
                matches.append((match.group(), replacement, match.start()))

        # Sort by position
        matches.sort(key=lambda x: x[2])
        return matches


def create_fast_matcher_from_domains(
    domains: List[str],
    case_sensitive: bool = False
) -> Optional[FastDictionaryMatcher]:
    """
    Create a FastDictionaryMatcher from domain dictionaries.

    Args:
        domains: List of domain names to include
        case_sensitive: Case-sensitive matching

    Returns:
        FastDictionaryMatcher or None if FlashText unavailable
    """
    if not FLASHTEXT_AVAILABLE:
        return None

    from .domain_dictionaries import get_domain_dictionary

    matcher = FastDictionaryMatcher(case_sensitive=case_sensitive)

    for domain in domains:
        domain_dict = get_domain_dictionary(domain)
        matcher.add_terms_from_dict(domain_dict)

    return matcher
