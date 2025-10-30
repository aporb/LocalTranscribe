"""
Acronym expansion for transcription proofreading.

Provides context-aware acronym expansion with common abbreviations.
"""

import re
from typing import Dict, Optional, List, Tuple


# Common acronyms and their expansions
ACRONYM_DATABASE: Dict[str, List[str]] = {
    "API": ["Application Programming Interface"],
    "AI": ["Artificial Intelligence"],
    "ML": ["Machine Learning"],
    "UI": ["User Interface"],
    "UX": ["User Experience"],
    "CEO": ["Chief Executive Officer"],
    "CTO": ["Chief Technology Officer"],
    "CFO": ["Chief Financial Officer"],
    "COO": ["Chief Operating Officer"],
    "VP": ["Vice President"],
    "HR": ["Human Resources"],
    "IT": ["Information Technology"],
    "PR": ["Public Relations"],
    "QA": ["Quality Assurance"],
    "R&D": ["Research and Development", "Research & Development"],
    "ROI": ["Return on Investment"],
    "KPI": ["Key Performance Indicator"],
    "OKR": ["Objectives and Key Results"],
    "SLA": ["Service Level Agreement"],
    "NDA": ["Non-Disclosure Agreement"],
    "MVP": ["Minimum Viable Product"],
    "B2B": ["Business-to-Business"],
    "B2C": ["Business-to-Consumer"],
    "SaaS": ["Software as a Service"],
    "PaaS": ["Platform as a Service"],
    "IaaS": ["Infrastructure as a Service"],
    "AWS": ["Amazon Web Services"],
    "GCP": ["Google Cloud Platform"],
    "SQL": ["Structured Query Language"],
    "NoSQL": ["Not only SQL"],
    "REST": ["Representational State Transfer"],
    "JSON": ["JavaScript Object Notation"],
    "XML": ["Extensible Markup Language"],
    "HTML": ["HyperText Markup Language"],
    "CSS": ["Cascading Style Sheets"],
    "HTTP": ["HyperText Transfer Protocol"],
    "HTTPS": ["HyperText Transfer Protocol Secure"],
    "URL": ["Uniform Resource Locator"],
    "URI": ["Uniform Resource Identifier"],
    "IP": ["Internet Protocol", "Intellectual Property"],
    "TCP": ["Transmission Control Protocol"],
    "UDP": ["User Datagram Protocol"],
    "DNS": ["Domain Name System"],
    "VPN": ["Virtual Private Network"],
    "SSH": ["Secure Shell"],
    "SSL": ["Secure Sockets Layer"],
    "TLS": ["Transport Layer Security"],
    "ASAP": ["As Soon As Possible"],
    "FYI": ["For Your Information"],
    "FAQ": ["Frequently Asked Questions"],
    "ETA": ["Estimated Time of Arrival"],
    "TBD": ["To Be Determined"],
    "TBA": ["To Be Announced"],
    "EOD": ["End of Day"],
    "COB": ["Close of Business"],
    "WIP": ["Work in Progress"],
    "RSVP": ["Répondez s'il vous plaît"],
    "PDF": ["Portable Document Format"],
    "CSV": ["Comma-Separated Values"],
    "YAML": ["YAML Ain't Markup Language"],
    "CLI": ["Command Line Interface"],
    "GUI": ["Graphical User Interface"],
    "IDE": ["Integrated Development Environment"],
    "SDK": ["Software Development Kit"],
    "CI/CD": ["Continuous Integration/Continuous Deployment"],
    "DevOps": ["Development Operations"],
    "RAM": ["Random Access Memory"],
    "ROM": ["Read-Only Memory"],
    "CPU": ["Central Processing Unit"],
    "GPU": ["Graphics Processing Unit"],
    "SSD": ["Solid State Drive"],
    "HDD": ["Hard Disk Drive"],
    "USB": ["Universal Serial Bus"],
    "HDMI": ["High-Definition Multimedia Interface"],
}


class AcronymExpander:
    """
    Acronym expansion with context awareness.

    Expands acronyms based on context and frequency, with support for
    custom acronym definitions.
    """

    def __init__(
        self,
        custom_acronyms: Optional[Dict[str, List[str]]] = None,
        expand_all: bool = False,
        first_occurrence_only: bool = True
    ):
        """
        Initialize acronym expander.

        Args:
            custom_acronyms: Custom acronym dictionary to merge with defaults
            expand_all: Expand all occurrences or only first
            first_occurrence_only: Only expand first occurrence of each acronym
        """
        self.acronym_db = ACRONYM_DATABASE.copy()
        if custom_acronyms:
            self.acronym_db.update(custom_acronyms)

        self.expand_all = expand_all
        self.first_occurrence_only = first_occurrence_only
        self.expanded_acronyms = set()  # Track what we've already expanded

    def expand_text(self, text: str, format_style: str = "parenthetical") -> str:
        """
        Expand acronyms in text.

        Args:
            text: Input text with acronyms
            format_style: How to format expansions:
                - "parenthetical": API (Application Programming Interface)
                - "replacement": Application Programming Interface
                - "footnote": API [1]

        Returns:
            Text with expanded acronyms
        """
        result = text

        for acronym, expansions in self.acronym_db.items():
            # Skip if we've already expanded this acronym and only doing first occurrence
            if self.first_occurrence_only and acronym in self.expanded_acronyms:
                continue

            # Find all occurrences of the acronym
            pattern = r'\b' + re.escape(acronym) + r'\b'
            matches = list(re.finditer(pattern, result))

            if not matches:
                continue

            # Get the primary expansion (first in list)
            expansion = expansions[0]

            # Expand based on format style
            if format_style == "parenthetical":
                replacement = f"{acronym} ({expansion})"
            elif format_style == "replacement":
                replacement = expansion
            elif format_style == "footnote":
                replacement = f"{acronym} [^{acronym}]"
            else:
                replacement = f"{acronym} ({expansion})"

            # Replace first occurrence or all
            if self.first_occurrence_only or not self.expand_all:
                # Replace only first occurrence
                match = matches[0]
                result = result[:match.start()] + replacement + result[match.end():]
                self.expanded_acronyms.add(acronym)
            else:
                # Replace all occurrences
                result = re.sub(pattern, replacement, result)

        return result

    def identify_acronyms(self, text: str) -> List[Tuple[str, str, int]]:
        """
        Identify all acronyms in text without expanding.

        Args:
            text: Input text

        Returns:
            List of tuples (acronym, expansion, position)
        """
        found_acronyms = []

        for acronym, expansions in self.acronym_db.items():
            pattern = r'\b' + re.escape(acronym) + r'\b'
            for match in re.finditer(pattern, text):
                found_acronyms.append((
                    acronym,
                    expansions[0],
                    match.start()
                ))

        # Sort by position
        found_acronyms.sort(key=lambda x: x[2])

        return found_acronyms

    def get_expansion(self, acronym: str) -> Optional[str]:
        """
        Get expansion for a specific acronym.

        Args:
            acronym: Acronym to expand

        Returns:
            Expansion string or None if not found
        """
        expansions = self.acronym_db.get(acronym.upper())
        return expansions[0] if expansions else None

    def add_acronym(self, acronym: str, expansion: str, alternatives: Optional[List[str]] = None):
        """
        Add custom acronym definition.

        Args:
            acronym: Acronym string
            expansion: Primary expansion
            alternatives: Alternative expansions
        """
        expansions = [expansion]
        if alternatives:
            expansions.extend(alternatives)

        self.acronym_db[acronym.upper()] = expansions

    def reset_expanded(self):
        """Reset tracking of expanded acronyms."""
        self.expanded_acronyms.clear()


def create_acronym_glossary(text: str) -> str:
    """
    Create acronym glossary from text.

    Args:
        text: Input text

    Returns:
        Formatted glossary string
    """
    expander = AcronymExpander()
    acronyms = expander.identify_acronyms(text)

    if not acronyms:
        return ""

    # Remove duplicates while preserving order
    seen = set()
    unique_acronyms = []
    for acr, exp, _ in acronyms:
        if acr not in seen:
            unique_acronyms.append((acr, exp))
            seen.add(acr)

    glossary_lines = ["## Acronym Glossary\n"]
    for acr, exp in sorted(unique_acronyms):
        glossary_lines.append(f"- **{acr}**: {exp}")

    return "\n".join(glossary_lines)
