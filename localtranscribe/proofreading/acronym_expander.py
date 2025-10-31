"""
Acronym expansion for transcription proofreading.

Provides intelligent context-aware acronym expansion with disambiguation
using spaCy NER and context analysis.
"""

import re
from typing import Dict, Optional, List, Tuple, Any
import warnings

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    warnings.warn(
        "spaCy not installed. Advanced context-aware expansion will be disabled."
    )

try:
    from .context_matcher import ContextAwareMatcher
except ImportError:
    ContextAwareMatcher = None


# Common acronyms and their expansions (100+ definitions)
ACRONYM_DATABASE: Dict[str, List[str]] = {
    # Technical/IT
    "API": ["Application Programming Interface"],
    "AI": ["Artificial Intelligence", "Air Interdiction"],  # Context-dependent
    "ML": ["Machine Learning"],
    "DL": ["Deep Learning"],
    "NLP": ["Natural Language Processing"],
    "UI": ["User Interface"],
    "UX": ["User Experience"],
    "QA": ["Quality Assurance"],
    "R&D": ["Research and Development", "Research & Development"],
    "IT": ["Information Technology"],
    "SDK": ["Software Development Kit"],
    "CLI": ["Command Line Interface"],
    "GUI": ["Graphical User Interface"],
    "IDE": ["Integrated Development Environment"],

    # Cloud & DevOps
    "AWS": ["Amazon Web Services"],
    "GCP": ["Google Cloud Platform"],
    "CI/CD": ["Continuous Integration/Continuous Deployment"],
    "DevOps": ["Development Operations"],
    "IaC": ["Infrastructure as Code"],
    "GitOps": ["Git Operations"],
    "SaaS": ["Software as a Service"],
    "PaaS": ["Platform as a Service"],
    "IaaS": ["Infrastructure as a Service"],
    "VPC": ["Virtual Private Cloud"],
    "EKS": ["Elastic Kubernetes Service"],
    "ECS": ["Elastic Container Service"],
    "ECR": ["Elastic Container Registry"],
    "ALB": ["Application Load Balancer"],
    "NLB": ["Network Load Balancer"],
    "RDS": ["Relational Database Service"],
    "S3": ["Simple Storage Service"],
    "EC2": ["Elastic Compute Cloud"],

    # Protocols & Standards
    "HTTP": ["HyperText Transfer Protocol"],
    "HTTPS": ["HyperText Transfer Protocol Secure"],
    "REST": ["Representational State Transfer"],
    "JSON": ["JavaScript Object Notation"],
    "XML": ["Extensible Markup Language"],
    "HTML": ["HyperText Markup Language"],
    "CSS": ["Cascading Style Sheets"],
    "URL": ["Uniform Resource Locator"],
    "URI": ["Uniform Resource Identifier"],
    "IP": ["Internet Protocol", "Intellectual Property"],  # Context-dependent
    "TCP": ["Transmission Control Protocol"],
    "UDP": ["User Datagram Protocol"],
    "DNS": ["Domain Name System"],
    "VPN": ["Virtual Private Network"],
    "SSH": ["Secure Shell"],
    "SSL": ["Secure Sockets Layer"],
    "TLS": ["Transport Layer Security"],
    "gRPC": ["Google Remote Procedure Call"],
    "MQTT": ["Message Queuing Telemetry Transport"],
    "AMQP": ["Advanced Message Queuing Protocol"],

    # Databases
    "SQL": ["Structured Query Language"],
    "NoSQL": ["Not only SQL"],
    "RDBMS": ["Relational Database Management System"],
    "CRUD": ["Create, Read, Update, Delete"],
    "ACID": ["Atomicity, Consistency, Isolation, Durability"],
    "ORM": ["Object-Relational Mapping"],

    # Business & Management
    "CEO": ["Chief Executive Officer"],
    "CTO": ["Chief Technology Officer"],
    "CFO": ["Chief Financial Officer"],
    "COO": ["Chief Operating Officer"],
    "CMO": ["Chief Marketing Officer"],
    "CDO": ["Chief Data Officer"],
    "CPO": ["Chief Product Officer"],
    "VP": ["Vice President"],
    "SVP": ["Senior Vice President"],
    "EVP": ["Executive Vice President"],
    "GM": ["General Manager"],
    "HR": ["Human Resources"],
    "PR": ["Public Relations", "Pull Request"],  # Context-dependent
    "ROI": ["Return on Investment"],
    "KPI": ["Key Performance Indicator"],
    "OKR": ["Objectives and Key Results"],
    "MVP": ["Minimum Viable Product"],
    "B2B": ["Business-to-Business"],
    "B2C": ["Business-to-Consumer"],
    "NPS": ["Net Promoter Score"],
    "CSAT": ["Customer Satisfaction Score"],
    "CAC": ["Customer Acquisition Cost"],
    "LTV": ["Lifetime Value"],
    "MRR": ["Monthly Recurring Revenue"],
    "ARR": ["Annual Recurring Revenue"],
    "EBITDA": ["Earnings Before Interest, Taxes, Depreciation, and Amortization"],
    "P&L": ["Profit and Loss"],
    "CAGR": ["Compound Annual Growth Rate"],
    "IRR": ["Internal Rate of Return"],
    "NPV": ["Net Present Value"],

    # Legal
    "NDA": ["Non-Disclosure Agreement"],
    "SLA": ["Service Level Agreement"],
    "MSA": ["Master Service Agreement"],
    "SOW": ["Statement of Work"],
    "RFP": ["Request for Proposal"],
    "RFI": ["Request for Information"],
    "LOI": ["Letter of Intent"],
    "MOU": ["Memorandum of Understanding"],
    "TOS": ["Terms of Service"],
    "EULA": ["End-User License Agreement"],
    "GDPR": ["General Data Protection Regulation"],
    "CCPA": ["California Consumer Privacy Act"],
    "HIPAA": ["Health Insurance Portability and Accountability Act"],
    "SOX": ["Sarbanes-Oxley Act"],
    "DMCA": ["Digital Millennium Copyright Act"],

    # Medical
    "MRI": ["Magnetic Resonance Imaging"],
    "CT": ["Computed Tomography"],
    "ECG": ["Electrocardiogram"],
    "EKG": ["Electrocardiogram"],
    "EEG": ["Electroencephalogram"],
    "EMG": ["Electromyography"],
    "CBC": ["Complete Blood Count"],
    "BMP": ["Basic Metabolic Panel"],
    "CMP": ["Comprehensive Metabolic Panel"],
    "ICU": ["Intensive Care Unit"],
    "ED": ["Emergency Department"],
    "OR": ["Operating Room", "Operations Research"],  # Context-dependent
    "PACU": ["Post-Anesthesia Care Unit"],
    "NICU": ["Neonatal Intensive Care Unit"],
    "PICU": ["Pediatric Intensive Care Unit"],
    "COPD": ["Chronic Obstructive Pulmonary Disease"],
    "CHF": ["Congestive Heart Failure"],
    "AFib": ["Atrial Fibrillation"],
    "CKD": ["Chronic Kidney Disease"],
    "GERD": ["Gastroesophageal Reflux Disease"],
    "IBS": ["Irritable Bowel Syndrome"],

    # Academic & Research
    "PhD": ["Doctor of Philosophy"],
    "MSc": ["Master of Science"],
    "BSc": ["Bachelor of Science"],
    "MBA": ["Master of Business Administration"],
    "MD": ["Doctor of Medicine"],
    "JD": ["Juris Doctor"],
    "IRB": ["Institutional Review Board"],
    "PI": ["Principal Investigator", "Private Investigator"],  # Context-dependent
    "NIH": ["National Institutes of Health"],
    "NSF": ["National Science Foundation"],
    "DOE": ["Department of Energy"],
    "DARPA": ["Defense Advanced Research Projects Agency"],
    "DOI": ["Digital Object Identifier"],
    "ISSN": ["International Standard Serial Number"],
    "ISBN": ["International Standard Book Number"],

    # Military
    "SITREP": ["Situation Report"],
    "OPORD": ["Operations Order"],
    "FRAGO": ["Fragmentary Order"],
    "WARNO": ["Warning Order"],
    "CAS": ["Close Air Support"],
    "MEDEVAC": ["Medical Evacuation"],
    "DUSTOFF": ["Medical Evacuation"],
    "FOB": ["Forward Operating Base"],
    "MOUT": ["Military Operations in Urban Terrain"],

    # Common Abbreviations
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

    # File Formats
    "PDF": ["Portable Document Format"],
    "CSV": ["Comma-Separated Values"],
    "YAML": ["YAML Ain't Markup Language"],
    "JPEG": ["Joint Photographic Experts Group"],
    "PNG": ["Portable Network Graphics"],
    "GIF": ["Graphics Interchange Format"],
    "SVG": ["Scalable Vector Graphics"],

    # Hardware
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
    Basic acronym expansion without context awareness.

    Expands acronyms based on first match in database. For context-aware
    expansion with disambiguation, use IntelligentAcronymExpander.
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
        self.usage_frequency = {}  # Track usage frequency

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

            # Track frequency
            if acronym not in self.usage_frequency:
                self.usage_frequency[acronym] = 0
            self.usage_frequency[acronym] += len(matches)

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

    def get_usage_statistics(self) -> Dict[str, int]:
        """
        Get usage frequency statistics for acronyms.

        Returns:
            Dictionary mapping acronyms to occurrence counts
        """
        return self.usage_frequency.copy()

    def get_top_acronyms(self, n: int = 10) -> List[Tuple[str, int]]:
        """
        Get top N most frequently used acronyms.

        Args:
            n: Number of top acronyms to return

        Returns:
            List of (acronym, count) tuples sorted by frequency
        """
        return sorted(
            self.usage_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]


class IntelligentAcronymExpander(AcronymExpander):
    """
    Context-aware acronym expansion with disambiguation.

    Uses spaCy NER and context analysis to intelligently disambiguate
    acronyms with multiple meanings based on surrounding text.

    Example:
        >>> expander = IntelligentAcronymExpander()
        >>> text = "The server IP address is 192.168.1.1"
        >>> result = expander.expand_text(text)
        >>> # "The server IP (Internet Protocol) address is 192.168.1.1"
    """

    def __init__(
        self,
        nlp: Optional['spacy.Language'] = None,
        custom_acronyms: Optional[Dict[str, List[str]]] = None,
        expand_all: bool = False,
        first_occurrence_only: bool = True,
        enable_context_matching: bool = True,
        confidence_threshold: float = 0.0,
        context_window: int = 5
    ):
        """
        Initialize intelligent acronym expander.

        Args:
            nlp: spaCy language model
            custom_acronyms: Custom acronym dictionary
            expand_all: Expand all occurrences
            first_occurrence_only: Only expand first occurrence
            enable_context_matching: Use context-aware disambiguation
            confidence_threshold: Minimum confidence for disambiguation
            context_window: Number of tokens before/after for context
        """
        super().__init__(custom_acronyms, expand_all, first_occurrence_only)

        self.enable_context = enable_context_matching and SPACY_AVAILABLE

        if self.enable_context:
            if ContextAwareMatcher is None:
                warnings.warn("ContextAwareMatcher not available. Context matching disabled.")
                self.context_matcher = None
                self.enable_context = False
            else:
                self.context_matcher = ContextAwareMatcher(
                    nlp=nlp,
                    context_window=context_window,
                    confidence_threshold=confidence_threshold
                )
        else:
            self.context_matcher = None

        # Track disambiguation decisions
        self.disambiguation_history = {}

    def expand_text(self, text: str, format_style: str = "parenthetical") -> str:
        """
        Intelligently expand acronyms with context-aware disambiguation.

        Args:
            text: Input text with acronyms
            format_style: How to format expansions

        Returns:
            Text with intelligently expanded acronyms
        """
        if not self.enable_context or self.context_matcher is None:
            # Fall back to basic expansion
            return super().expand_text(text, format_style)

        result = text
        offset = 0  # Track position offset from replacements

        for acronym, expansions in self.acronym_db.items():
            # Skip if already expanded
            if self.first_occurrence_only and acronym in self.expanded_acronyms:
                continue

            # Find all occurrences
            pattern = r'\b' + re.escape(acronym) + r'\b'
            matches = list(re.finditer(pattern, text))

            if not matches:
                continue

            # Track frequency
            if acronym not in self.usage_frequency:
                self.usage_frequency[acronym] = 0
            self.usage_frequency[acronym] += len(matches)

            # Process first match (or all if expand_all)
            matches_to_process = matches if self.expand_all else [matches[0]]

            for match in matches_to_process:
                # Get expansion - use context matching if multiple meanings
                if len(expansions) > 1:
                    # Try context-aware disambiguation
                    expansion = self.context_matcher.match_with_context(
                        text,
                        acronym,
                        match.start()
                    )

                    if expansion:
                        # Track successful disambiguation
                        if acronym not in self.disambiguation_history:
                            self.disambiguation_history[acronym] = {}
                        if expansion not in self.disambiguation_history[acronym]:
                            self.disambiguation_history[acronym][expansion] = 0
                        self.disambiguation_history[acronym][expansion] += 1
                    else:
                        # Fall back to first expansion
                        expansion = expansions[0]
                else:
                    expansion = expansions[0]

                # Format expansion
                if format_style == "parenthetical":
                    replacement = f"{acronym} ({expansion})"
                elif format_style == "replacement":
                    replacement = expansion
                elif format_style == "footnote":
                    replacement = f"{acronym} [^{acronym}]"
                else:
                    replacement = f"{acronym} ({expansion})"

                # Apply replacement with offset
                start_pos = match.start() + offset
                end_pos = match.end() + offset
                result = result[:start_pos] + replacement + result[end_pos:]

                # Update offset
                offset += len(replacement) - len(acronym)

                if self.first_occurrence_only:
                    self.expanded_acronyms.add(acronym)
                    break

        return result

    def get_disambiguation_statistics(self) -> Dict[str, Dict[str, int]]:
        """
        Get statistics on disambiguation decisions.

        Returns:
            Dictionary mapping acronyms to their resolved meanings and counts
        """
        return self.disambiguation_history.copy()


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
