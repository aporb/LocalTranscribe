"""
Main proofreader class for applying transcription corrections.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum

from .defaults import get_default_rules, get_minimal_rules, get_category_rules


class ProofreadingLevel(Enum):
    """Proofreading thoroughness levels."""
    MINIMAL = "minimal"      # Quick, essential fixes only
    STANDARD = "standard"    # Default comprehensive rules
    THOROUGH = "thorough"    # All rules including experimental
    CUSTOM = "custom"        # User-provided rules only


@dataclass
class ProofreadingChange:
    """Record of a single proofreading change."""
    original: str
    replacement: str
    position: int
    rule_description: str
    line_number: Optional[int] = None


@dataclass
class ProofreadingResult:
    """Result of proofreading operation."""
    original_text: str
    corrected_text: str
    changes: List[ProofreadingChange] = field(default_factory=list)
    rules_applied: int = 0
    total_changes: int = 0
    processing_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None

    @property
    def has_changes(self) -> bool:
        """Check if any changes were made."""
        return self.total_changes > 0

    def get_summary(self) -> str:
        """Get a human-readable summary of changes."""
        if not self.has_changes:
            return "No changes needed."

        summary = f"Made {self.total_changes} correction"
        if self.total_changes != 1:
            summary += "s"

        # Group changes by rule
        change_types = {}
        for change in self.changes:
            desc = change.rule_description
            if desc not in change_types:
                change_types[desc] = 0
            change_types[desc] += 1

        # Add breakdown
        if change_types:
            summary += ":\n"
            for desc, count in sorted(change_types.items(), key=lambda x: x[1], reverse=True):
                summary += f"  • {desc}: {count}\n"

        return summary.strip()


class Proofreader:
    """
    Applies proofreading rules to transcription text.

    Features:
    - Multiple rule sources (default, custom, category-specific)
    - Change tracking and logging
    - Configurable proofreading levels
    - Support for complex regex patterns
    - Preserve original formatting options
    """

    def __init__(
        self,
        rules: Optional[Dict[str, Any]] = None,
        level: ProofreadingLevel = ProofreadingLevel.STANDARD,
        track_changes: bool = True,
        preserve_timestamps: bool = True,
        verbose: bool = False,
        # Phase 2 enhancements
        enable_domain_dictionaries: bool = False,
        domains: Optional[List[str]] = None,
        enable_acronym_expansion: bool = False,
        acronym_format: str = "parenthetical"
    ):
        """
        Initialize proofreader.

        Args:
            rules: Custom rules dictionary (overrides defaults if provided)
            level: Proofreading thoroughness level
            track_changes: Whether to track individual changes
            preserve_timestamps: Preserve timestamp formatting in transcripts
            verbose: Enable verbose logging
            enable_domain_dictionaries: Enable domain-specific term corrections (Phase 2)
            domains: List of domains to enable (e.g., ["technical", "business"])
            enable_acronym_expansion: Enable acronym expansion (Phase 2)
            acronym_format: Format for acronym expansion (parenthetical, replacement)
        """
        self.level = level
        self.track_changes = track_changes
        self.preserve_timestamps = preserve_timestamps
        self.verbose = verbose

        # Phase 2 enhancements
        self.enable_domain_dictionaries = enable_domain_dictionaries
        self.domains = domains or ["common"]
        self.enable_acronym_expansion = enable_acronym_expansion
        self.acronym_format = acronym_format

        # Load appropriate rules based on level
        if rules:
            self.rules = rules
            self.level = ProofreadingLevel.CUSTOM
        else:
            self.rules = self._load_rules_for_level(level)

        # Compile regex patterns for efficiency
        self._compile_patterns()

        # Initialize domain dictionaries if enabled
        self.domain_patterns = {}
        if self.enable_domain_dictionaries:
            self._load_domain_dictionaries()

        # Initialize acronym expander if enabled
        self.acronym_expander = None
        if self.enable_acronym_expansion:
            from .acronym_expander import AcronymExpander
            self.acronym_expander = AcronymExpander(
                first_occurrence_only=True
            )

    def _load_rules_for_level(self, level: ProofreadingLevel) -> Dict[str, Any]:
        """Load rules based on proofreading level."""
        if level == ProofreadingLevel.MINIMAL:
            return get_minimal_rules()
        elif level == ProofreadingLevel.STANDARD:
            return get_default_rules()
        elif level == ProofreadingLevel.THOROUGH:
            # Include all rules, even disabled ones
            rules = get_default_rules()
            for rule in rules.get("replacements", []):
                rule["enabled"] = True
            return rules
        else:
            return get_default_rules()

    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns for better performance."""
        self.compiled_rules = []

        for rule in self.rules.get("replacements", []):
            if not rule.get("enabled", True):
                continue

            pattern = rule.get("pattern", "")
            if not pattern:
                continue

            try:
                flags = 0
                if not rule.get("case_sensitive", True):
                    flags |= re.IGNORECASE

                compiled = re.compile(pattern, flags)
                self.compiled_rules.append({
                    "pattern": compiled,
                    "replacement": rule.get("replacement", ""),
                    "description": rule.get("description", "Pattern replacement"),
                    "preserve": rule.get("preserve", False)
                })
            except re.error as e:
                if self.verbose:
                    print(f"Warning: Invalid regex pattern '{pattern}': {e}")

    def _load_domain_dictionaries(self) -> None:
        """Load and compile domain-specific dictionaries."""
        from .domain_dictionaries import get_domain_dictionary

        self.domain_patterns = {}

        for domain in self.domains:
            domain_dict = get_domain_dictionary(domain)
            compiled_patterns = []

            for pattern, replacement in domain_dict.items():
                try:
                    compiled = re.compile(pattern, re.IGNORECASE)
                    compiled_patterns.append({
                        "pattern": compiled,
                        "replacement": replacement,
                        "description": f"Domain correction: {domain}"
                    })
                except re.error as e:
                    if self.verbose:
                        print(f"Warning: Invalid domain pattern '{pattern}': {e}")

            self.domain_patterns[domain] = compiled_patterns

            if self.verbose:
                print(f"Loaded {len(compiled_patterns)} patterns for domain: {domain}")

    def load_rules_from_file(self, path: Path) -> None:
        """
        Load proofreading rules from a JSON or YAML file.

        Args:
            path: Path to rules file

        Raises:
            FileNotFoundError: If rules file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        if not path.exists():
            raise FileNotFoundError(f"Rules file not found: {path}")

        with open(path, "r") as f:
            if path.suffix.lower() in [".yaml", ".yml"]:
                import yaml
                self.rules = yaml.safe_load(f)
            else:
                self.rules = json.load(f)

        self._compile_patterns()
        self.level = ProofreadingLevel.CUSTOM

    def proofread(
        self,
        text: str,
        apply_repetition_cleanup: bool = True,
        apply_capitalization: bool = True,
        custom_rules: Optional[List[Dict[str, str]]] = None
    ) -> ProofreadingResult:
        """
        Apply proofreading rules to text.

        Args:
            text: Text to proofread
            apply_repetition_cleanup: Apply repetition cleanup rules
            apply_capitalization: Apply capitalization rules
            custom_rules: Additional one-time rules to apply

        Returns:
            ProofreadingResult with corrected text and change details
        """
        import time
        start_time = time.time()

        result = ProofreadingResult(
            original_text=text,
            corrected_text=text,
            changes=[],
            rules_applied=0
        )

        try:
            corrected = text
            changes = []

            # Phase 2: Apply domain-specific dictionaries first
            if self.enable_domain_dictionaries and self.domain_patterns:
                if self.verbose:
                    print("Applying domain-specific corrections...")

                for domain, patterns in self.domain_patterns.items():
                    for rule in patterns:
                        pattern = rule["pattern"]
                        replacement = rule["replacement"]
                        description = rule["description"]

                        # Track changes if enabled
                        if self.track_changes:
                            matches = list(pattern.finditer(corrected))
                            for match in reversed(matches):
                                original_text = match.group(0)
                                new_text = pattern.sub(replacement, original_text)

                                if original_text != new_text:
                                    changes.append(ProofreadingChange(
                                        original=original_text,
                                        replacement=new_text,
                                        position=match.start(),
                                        rule_description=description
                                    ))

                        # Apply the replacement
                        new_corrected = pattern.sub(replacement, corrected)
                        if new_corrected != corrected:
                            result.rules_applied += 1
                            corrected = new_corrected

            # Apply main replacement rules
            if self.verbose:
                print("Applying replacement rules...")

            # Apply compiled rules
            for rule in self.compiled_rules:
                if rule.get("preserve"):
                    continue

                pattern = rule["pattern"]
                replacement = rule["replacement"]
                description = rule["description"]

                # Track changes if enabled
                if self.track_changes:
                    matches = list(pattern.finditer(corrected))
                    for match in reversed(matches):  # Process in reverse to maintain positions
                        original_text = match.group(0)
                        new_text = pattern.sub(replacement, original_text)

                        if original_text != new_text:
                            changes.append(ProofreadingChange(
                                original=original_text,
                                replacement=new_text,
                                position=match.start(),
                                rule_description=description
                            ))

                # Apply the replacement
                new_corrected = pattern.sub(replacement, corrected)
                if new_corrected != corrected:
                    result.rules_applied += 1
                    corrected = new_corrected

            # Apply repetition cleanup
            if apply_repetition_cleanup and self.rules.get("repetition_cleanup", {}).get("enabled"):
                if self.verbose:
                    print("Cleaning up repetitions...")

                for pattern_rule in self.rules["repetition_cleanup"].get("patterns", []):
                    pattern = re.compile(pattern_rule["pattern"], re.IGNORECASE)
                    replacement = pattern_rule["replacement"]

                    new_corrected = pattern.sub(replacement, corrected)
                    if new_corrected != corrected:
                        result.rules_applied += 1
                        corrected = new_corrected

                        if self.track_changes:
                            changes.append(ProofreadingChange(
                                original="[repetition]",
                                replacement="[cleaned]",
                                position=-1,
                                rule_description=pattern_rule.get("description", "Repetition cleanup")
                            ))

            # Apply capitalization fixes
            if apply_capitalization and self.rules.get("capitalization", {}).get("enabled"):
                if self.verbose:
                    print("Fixing capitalization...")

                for cap_rule in self.rules["capitalization"].get("rules", []):
                    pattern = re.compile(cap_rule["pattern"])
                    replacement = cap_rule.get("replacement")

                    if callable(replacement):
                        # Lambda replacement
                        new_corrected = pattern.sub(replacement, corrected)
                    else:
                        new_corrected = pattern.sub(replacement, corrected)

                    if new_corrected != corrected:
                        result.rules_applied += 1
                        corrected = new_corrected

            # Apply custom one-time rules if provided
            if custom_rules:
                for custom in custom_rules:
                    pattern = re.compile(custom.get("pattern", ""), re.IGNORECASE)
                    replacement = custom.get("replacement", "")
                    corrected = pattern.sub(replacement, corrected)

            # Phase 2: Apply acronym expansion (last step)
            if self.enable_acronym_expansion and self.acronym_expander:
                if self.verbose:
                    print("Expanding acronyms...")

                expanded = self.acronym_expander.expand_text(
                    corrected,
                    format_style=self.acronym_format
                )

                if expanded != corrected:
                    result.rules_applied += 1
                    if self.track_changes:
                        changes.append(ProofreadingChange(
                            original="[acronyms]",
                            replacement="[expanded]",
                            position=-1,
                            rule_description="Acronym expansion"
                        ))
                    corrected = expanded

            # Update result
            result.corrected_text = corrected
            result.changes = changes
            result.total_changes = len(changes)
            result.processing_time = time.time() - start_time
            result.success = True

            if self.verbose:
                print(f"Proofreading complete: {result.total_changes} changes in {result.processing_time:.2f}s")

        except Exception as e:
            result.success = False
            result.error_message = str(e)
            result.processing_time = time.time() - start_time

        return result

    def proofread_file(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        create_backup: bool = True
    ) -> ProofreadingResult:
        """
        Proofread a file and save the results.

        Args:
            input_path: Path to input file
            output_path: Path to output file (defaults to input_path with _proofread suffix)
            create_backup: Create backup of original file

        Returns:
            ProofreadingResult
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Read input file
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Proofread the text
        result = self.proofread(text)

        if result.success and result.has_changes:
            # Determine output path
            if output_path is None:
                output_path = input_path.with_stem(input_path.stem + "_proofread")

            # Create backup if requested
            if create_backup and output_path == input_path:
                backup_path = input_path.with_suffix(".backup" + input_path.suffix)
                input_path.rename(backup_path)
                if self.verbose:
                    print(f"Created backup: {backup_path}")

            # Save corrected text
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result.corrected_text)

            if self.verbose:
                print(f"Saved proofread text to: {output_path}")

        return result

    def generate_change_report(self, result: ProofreadingResult) -> str:
        """
        Generate a detailed change report.

        Args:
            result: ProofreadingResult to report on

        Returns:
            Formatted change report
        """
        if not result.has_changes:
            return "No changes were made during proofreading."

        report = []
        report.append(f"# Proofreading Report")
        report.append(f"\n**Total Changes:** {result.total_changes}")
        report.append(f"**Rules Applied:** {result.rules_applied}")
        report.append(f"**Processing Time:** {result.processing_time:.2f}s")

        if self.track_changes and result.changes:
            report.append("\n## Changes Made\n")

            # Group by description
            grouped = {}
            for change in result.changes:
                desc = change.rule_description
                if desc not in grouped:
                    grouped[desc] = []
                grouped[desc].append(change)

            for desc, changes in grouped.items():
                report.append(f"\n### {desc} ({len(changes)} changes)")
                for i, change in enumerate(changes[:5], 1):  # Show first 5
                    if change.position >= 0:
                        report.append(f"{i}. '{change.original}' → '{change.replacement}'")

                if len(changes) > 5:
                    report.append(f"   ... and {len(changes) - 5} more")

        return "\n".join(report)

    @classmethod
    def from_level(cls, level: str, **kwargs) -> "Proofreader":
        """
        Create a Proofreader from a string level name.

        Args:
            level: Level name (minimal, standard, thorough)
            **kwargs: Additional arguments for Proofreader

        Returns:
            Configured Proofreader instance
        """
        try:
            level_enum = ProofreadingLevel(level.lower())
        except ValueError:
            level_enum = ProofreadingLevel.STANDARD

        return cls(level=level_enum, **kwargs)