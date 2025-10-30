"""
Proofreading module for LocalTranscribe.

Provides automatic correction of common transcription errors with
domain-specific dictionaries, acronym expansion, and NER support.
"""

from .proofreader import (
    Proofreader,
    ProofreadingLevel,
    ProofreadingResult,
    ProofreadingChange
)
from .rules import (
    RuleManager,
    Rule,
    RuleType,
    RuleSource,
    create_domain_rules
)
from .defaults import (
    get_default_rules,
    get_minimal_rules,
    get_category_rules,
    DEFAULT_RULES
)
from .domain_dictionaries import (
    get_domain_dictionary,
    get_all_domain_terms,
    get_domains_list
)
from .acronym_expander import (
    AcronymExpander,
    create_acronym_glossary
)

__all__ = [
    # Main classes
    "Proofreader",
    "ProofreadingLevel",
    "ProofreadingResult",
    "ProofreadingChange",

    # Rule management
    "RuleManager",
    "Rule",
    "RuleType",
    "RuleSource",
    "create_domain_rules",

    # Default rules
    "get_default_rules",
    "get_minimal_rules",
    "get_category_rules",
    "DEFAULT_RULES",

    # Domain dictionaries (Phase 2)
    "get_domain_dictionary",
    "get_all_domain_terms",
    "get_domains_list",

    # Acronym expansion (Phase 2)
    "AcronymExpander",
    "create_acronym_glossary",
]

# Module metadata
__version__ = "1.0.0"
__author__ = "LocalTranscribe Contributors"