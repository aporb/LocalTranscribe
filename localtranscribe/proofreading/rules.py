"""
Rule loading and management for proofreading system.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum


class RuleType(Enum):
    """Types of proofreading rules."""
    REPLACEMENT = "replacement"
    REPETITION = "repetition"
    CAPITALIZATION = "capitalization"
    CUSTOM = "custom"


class RuleSource(Enum):
    """Source of proofreading rules."""
    DEFAULT = "default"
    USER_FILE = "user_file"
    INLINE = "inline"
    TEMPLATE = "template"


@dataclass
class Rule:
    """Individual proofreading rule."""
    pattern: str
    replacement: str
    description: str
    type: RuleType
    source: RuleSource
    case_sensitive: bool = True
    enabled: bool = True
    context: Optional[str] = None
    preserve: bool = False
    priority: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "pattern": self.pattern,
            "replacement": self.replacement,
            "description": self.description,
            "case_sensitive": self.case_sensitive,
            "enabled": self.enabled,
            "context": self.context,
            "preserve": self.preserve,
            "priority": self.priority
        }


class RuleManager:
    """
    Manages proofreading rules from multiple sources.

    Features:
    - Load from JSON/YAML files
    - Merge multiple rule sets
    - Validate rule syntax
    - Export rule templates
    - Rule prioritization
    """

    def __init__(self):
        """Initialize rule manager."""
        self.rules: List[Rule] = []
        self.rule_sets: Dict[str, List[Rule]] = {}

    def load_from_file(
        self,
        path: Union[str, Path],
        source_name: Optional[str] = None
    ) -> List[Rule]:
        """
        Load rules from a JSON or YAML file.

        Args:
            path: Path to rules file
            source_name: Optional name for this rule set

        Returns:
            List of loaded rules

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Rules file not found: {path}")

        # Determine file format and load
        try:
            with open(path, "r", encoding="utf-8") as f:
                if path.suffix.lower() in [".yaml", ".yml"]:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"Invalid file format in {path}: {e}")

        # Parse rules
        rules = self._parse_rule_data(data, RuleSource.USER_FILE)

        # Store in rule sets
        set_name = source_name or path.stem
        self.rule_sets[set_name] = rules

        # Add to main rules list
        self.rules.extend(rules)

        return rules

    def load_from_dict(
        self,
        data: Dict[str, Any],
        source: RuleSource = RuleSource.INLINE
    ) -> List[Rule]:
        """
        Load rules from a dictionary.

        Args:
            data: Dictionary containing rule data
            source: Source type for these rules

        Returns:
            List of loaded rules
        """
        rules = self._parse_rule_data(data, source)
        self.rules.extend(rules)
        return rules

    def _parse_rule_data(
        self,
        data: Dict[str, Any],
        source: RuleSource
    ) -> List[Rule]:
        """
        Parse rule data from dictionary format.

        Args:
            data: Rule data dictionary
            source: Source of these rules

        Returns:
            List of parsed Rule objects
        """
        rules = []

        # Parse replacement rules
        for rule_data in data.get("replacements", []):
            if not rule_data.get("enabled", True):
                continue

            rule = Rule(
                pattern=rule_data.get("pattern", ""),
                replacement=rule_data.get("replacement", ""),
                description=rule_data.get("description", "Replacement rule"),
                type=RuleType.REPLACEMENT,
                source=source,
                case_sensitive=rule_data.get("case_sensitive", True),
                enabled=rule_data.get("enabled", True),
                context=rule_data.get("context"),
                preserve=rule_data.get("preserve", False),
                priority=rule_data.get("priority", 0)
            )
            rules.append(rule)

        # Parse repetition cleanup rules
        if "repetition_cleanup" in data and data["repetition_cleanup"].get("enabled"):
            for pattern_data in data["repetition_cleanup"].get("patterns", []):
                rule = Rule(
                    pattern=pattern_data.get("pattern", ""),
                    replacement=pattern_data.get("replacement", ""),
                    description=pattern_data.get("description", "Repetition cleanup"),
                    type=RuleType.REPETITION,
                    source=source,
                    case_sensitive=False,
                    enabled=True,
                    priority=-10  # Lower priority for cleanup
                )
                rules.append(rule)

        return rules

    def validate_rules(self, rules: Optional[List[Rule]] = None) -> List[str]:
        """
        Validate rules for correctness.

        Args:
            rules: Rules to validate (defaults to self.rules)

        Returns:
            List of validation errors (empty if all valid)
        """
        import re

        rules_to_check = rules or self.rules
        errors = []

        for i, rule in enumerate(rules_to_check):
            # Check pattern validity
            try:
                re.compile(rule.pattern)
            except re.error as e:
                errors.append(f"Rule {i+1}: Invalid regex pattern '{rule.pattern}': {e}")

            # Check replacement string
            if not isinstance(rule.replacement, str):
                errors.append(f"Rule {i+1}: Replacement must be a string")

            # Check for empty pattern
            if not rule.pattern:
                errors.append(f"Rule {i+1}: Pattern cannot be empty")

        return errors

    def merge_rules(
        self,
        *rule_sets: List[Rule],
        resolve_conflicts: str = "last"
    ) -> List[Rule]:
        """
        Merge multiple rule sets.

        Args:
            *rule_sets: Rule sets to merge
            resolve_conflicts: How to handle duplicates (first, last, all)

        Returns:
            Merged list of rules
        """
        merged = []
        seen_patterns = set()

        all_rules = []
        for rule_set in rule_sets:
            all_rules.extend(rule_set)

        # Sort by priority
        all_rules.sort(key=lambda r: r.priority, reverse=True)

        for rule in all_rules:
            if resolve_conflicts == "all":
                merged.append(rule)
            elif resolve_conflicts == "first":
                if rule.pattern not in seen_patterns:
                    merged.append(rule)
                    seen_patterns.add(rule.pattern)
            else:  # last
                # Remove existing rule with same pattern
                merged = [r for r in merged if r.pattern != rule.pattern]
                merged.append(rule)

        return merged

    def export_template(
        self,
        path: Union[str, Path],
        format: str = "json",
        include_examples: bool = True
    ) -> None:
        """
        Export a rule template file.

        Args:
            path: Path to save template
            format: Output format (json or yaml)
            include_examples: Include example rules
        """
        template = {
            "metadata": {
                "name": "Custom Proofreading Rules",
                "version": "1.0.0",
                "description": "Template for custom proofreading rules"
            },
            "replacements": []
        }

        if include_examples:
            template["replacements"] = [
                {
                    "pattern": r"\byour_pattern\b",
                    "replacement": "your_replacement",
                    "description": "Example replacement rule",
                    "case_sensitive": False,
                    "enabled": True
                },
                {
                    "pattern": r"\b(\w+)\s+\1\b",
                    "replacement": r"\1",
                    "description": "Remove duplicate words",
                    "enabled": True
                }
            ]
            template["repetition_cleanup"] = {
                "enabled": True,
                "patterns": [
                    {
                        "pattern": r"(\b\w+\b)(?:\s*,?\s*\1){3,}",
                        "replacement": r"\1, \1, \1...",
                        "description": "Reduce word repetition"
                    }
                ]
            }

        path = Path(path)
        with open(path, "w", encoding="utf-8") as f:
            if format.lower() == "yaml":
                yaml.safe_dump(template, f, default_flow_style=False, sort_keys=False)
            else:
                json.dump(template, f, indent=2)

    def get_rules_by_type(self, rule_type: RuleType) -> List[Rule]:
        """Get all rules of a specific type."""
        return [r for r in self.rules if r.type == rule_type]

    def get_rules_by_context(self, context: str) -> List[Rule]:
        """Get all rules with a specific context."""
        return [r for r in self.rules if r.context == context]

    def get_enabled_rules(self) -> List[Rule]:
        """Get all enabled rules."""
        return [r for r in self.rules if r.enabled]

    def disable_rule(self, pattern: str) -> bool:
        """
        Disable a rule by pattern.

        Args:
            pattern: Pattern to match

        Returns:
            True if rule was found and disabled
        """
        for rule in self.rules:
            if rule.pattern == pattern:
                rule.enabled = False
                return True
        return False

    def enable_rule(self, pattern: str) -> bool:
        """
        Enable a rule by pattern.

        Args:
            pattern: Pattern to match

        Returns:
            True if rule was found and enabled
        """
        for rule in self.rules:
            if rule.pattern == pattern:
                rule.enabled = True
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert all rules to dictionary format."""
        return {
            "replacements": [
                r.to_dict() for r in self.rules
                if r.type == RuleType.REPLACEMENT
            ],
            "repetition_cleanup": {
                "enabled": any(r.type == RuleType.REPETITION for r in self.rules),
                "patterns": [
                    r.to_dict() for r in self.rules
                    if r.type == RuleType.REPETITION
                ]
            }
        }

    def save_rules(
        self,
        path: Union[str, Path],
        format: str = "json"
    ) -> None:
        """
        Save current rules to file.

        Args:
            path: Path to save rules
            format: Output format (json or yaml)
        """
        path = Path(path)
        data = self.to_dict()

        with open(path, "w", encoding="utf-8") as f:
            if format.lower() == "yaml":
                yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
            else:
                json.dump(data, f, indent=2)


def create_domain_rules(domain: str) -> Dict[str, Any]:
    """
    Create domain-specific rule sets.

    Args:
        domain: Domain name (tech, medical, legal, academic)

    Returns:
        Dictionary of domain-specific rules
    """
    domains = {
        "tech": {
            "replacements": [
                {"pattern": r"\bAPI\b", "replacement": "API", "case_sensitive": False},
                {"pattern": r"\bSQL\b", "replacement": "SQL", "case_sensitive": False},
                {"pattern": r"\bgit\b", "replacement": "Git", "case_sensitive": False},
            ]
        },
        "medical": {
            "replacements": [
                {"pattern": r"\bHIPAA\b", "replacement": "HIPAA", "case_sensitive": False},
                {"pattern": r"\bEKG\b", "replacement": "EKG", "case_sensitive": False},
                {"pattern": r"\bMRI\b", "replacement": "MRI", "case_sensitive": False},
            ]
        },
        "legal": {
            "replacements": [
                {"pattern": r"\bi\.e\.\b", "replacement": "i.e.", "case_sensitive": False},
                {"pattern": r"\be\.g\.\b", "replacement": "e.g.", "case_sensitive": False},
                {"pattern": r"\betc\.\b", "replacement": "etc.", "case_sensitive": False},
            ]
        },
        "academic": {
            "replacements": [
                {"pattern": r"\bPhD\b", "replacement": "PhD", "case_sensitive": False},
                {"pattern": r"\bBS\b", "replacement": "BS", "case_sensitive": False},
                {"pattern": r"\bMS\b", "replacement": "MS", "case_sensitive": False},
            ]
        }
    }

    return domains.get(domain, {"replacements": []})