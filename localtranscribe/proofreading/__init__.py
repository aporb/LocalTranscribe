"""
Proofreading module for LocalTranscribe.

Provides automatic correction of common transcription errors.
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
    "DEFAULT_RULES"
]

# Module metadata
__version__ = "1.0.0"
__author__ = "LocalTranscribe Contributors"