"""
Default proofreading rules for common transcription errors.

These rules cover common speech-to-text mistakes across different domains.
Users can override or extend these with custom rules.
"""

from typing import Dict, List, Any

# Comprehensive default rules covering common transcription errors
DEFAULT_RULES: Dict[str, Any] = {
    "replacements": [
        # ============================================
        # COMMON HOMOPHONE & SOUND-ALIKE ERRORS
        # ============================================

        # Common business/tech homophones
        {"pattern": r"\brite\b(?!\s+of)", "replacement": "write", "description": "write not rite (except 'rite of passage')"},
        {"pattern": r"\bsole\s+(?:purpose|owner|proprietor)\b", "replacement": "sole", "preserve": True, "description": "Keep 'sole' in business contexts"},
        {"pattern": r"\bsole\s+(?:coach|mate|searching)\b", "replacement": "soul $1", "description": "soul coach/mate/searching"},
        {"pattern": r"\byour\s+(?:welcome|fired|hired)\b", "replacement": "you're $1", "description": "you're = you are"},
        {"pattern": r"\byou're\s+(?:computer|house|car|phone)\b", "replacement": "your $1", "description": "your = possessive"},
        {"pattern": r"\btheir\s+(?:is|are|was|were)\b", "replacement": "there $1", "description": "there is/are"},
        {"pattern": r"\bthere\s+(?:computer|house|car|phone)\b", "replacement": "their $1", "description": "their = possessive"},
        {"pattern": r"\bits\s+(?:important|possible|necessary)\b", "replacement": "it's $1", "description": "it's = it is"},
        {"pattern": r"\bit's\s+(?:purpose|function|role)\b", "replacement": "its $1", "description": "its = possessive"},

        # ============================================
        # TECHNOLOGY & SOFTWARE TERMS
        # ============================================

        # JavaScript/Web frameworks
        {"pattern": r"\b(?:reacts?|re-act)\b", "replacement": "React", "case_sensitive": False, "context": "framework"},
        {"pattern": r"\b(?:view|vu)\.?js\b", "replacement": "Vue.js", "case_sensitive": False},
        {"pattern": r"\b(?:angular|angle)\s*js\b", "replacement": "AngularJS", "case_sensitive": False},
        {"pattern": r"\bnext\s*\.?\s*(?:js|JS|gs)\b", "replacement": "Next.js", "case_sensitive": False},
        {"pattern": r"\b(?:express|ex-press)\s*\.?\s*js\b", "replacement": "Express.js", "case_sensitive": False},
        {"pattern": r"\bnode\s*\.?\s*(?:js|JS|gs)\b", "replacement": "Node.js", "case_sensitive": False},
        {"pattern": r"\b(?:typescript|type\s*script)\b", "replacement": "TypeScript", "case_sensitive": False},
        {"pattern": r"\b(?:javascript|java\s*script)\b", "replacement": "JavaScript", "case_sensitive": False},

        # Cloud platforms & services
        {"pattern": r"\b(?:AWS|a\.w\.s\.|amazon\s+web\s+services)\b", "replacement": "AWS", "case_sensitive": False},
        {"pattern": r"\b(?:gcp|g\.c\.p\.|google\s+cloud)\b", "replacement": "GCP", "case_sensitive": False},
        {"pattern": r"\b(?:azure|as\s*your|azur)\b", "replacement": "Azure", "case_sensitive": False, "context": "cloud"},
        {"pattern": r"\b(?:versel|verse\s*l|ver\s*cell)\b", "replacement": "Vercel", "case_sensitive": False},
        {"pattern": r"\b(?:net\s*lify|net\s*li\s*fy)\b", "replacement": "Netlify", "case_sensitive": False},
        {"pattern": r"\b(?:supa\s*base|soup\s*base|super\s*base)\b", "replacement": "Supabase", "case_sensitive": False},
        {"pattern": r"\b(?:fire\s*base|firebase)\b", "replacement": "Firebase", "case_sensitive": False},
        {"pattern": r"\b(?:docker|dock\s*er|dock\s*r)\b", "replacement": "Docker", "case_sensitive": False},
        {"pattern": r"\b(?:kubernetes|kube\s*er\s*net\s*ees|cooper\s*net\s*ees)\b", "replacement": "Kubernetes", "case_sensitive": False},

        # Programming languages
        {"pattern": r"\b(?:python|pie\s*thon)\b", "replacement": "Python", "case_sensitive": False},
        {"pattern": r"\b(?:java|jabba)(?!\s*script)\b", "replacement": "Java", "case_sensitive": False},
        {"pattern": r"\b(?:c\s*sharp|see\s*sharp)\b", "replacement": "C#", "case_sensitive": False},
        {"pattern": r"\b(?:c\s*plus\s*plus|see\s*plus\s*plus)\b", "replacement": "C++", "case_sensitive": False},
        {"pattern": r"\b(?:go\s*lang|goal\s*ang)\b", "replacement": "Golang", "case_sensitive": False},
        {"pattern": r"\b(?:rust|rushed)\b", "replacement": "Rust", "case_sensitive": False, "context": "programming"},
        {"pattern": r"\b(?:swift|s\s*wift)\b", "replacement": "Swift", "case_sensitive": False, "context": "programming"},
        {"pattern": r"\b(?:kotlin|coat\s*lin)\b", "replacement": "Kotlin", "case_sensitive": False},

        # Databases
        {"pattern": r"\b(?:post\s*gres|post\s*grey\s*SQL|postgres\s*SQL)\b", "replacement": "PostgreSQL", "case_sensitive": False},
        {"pattern": r"\b(?:my\s*SQL|my\s*sequel)\b", "replacement": "MySQL", "case_sensitive": False},
        {"pattern": r"\b(?:mongo\s*DB|mongo\s*d\s*b)\b", "replacement": "MongoDB", "case_sensitive": False},
        {"pattern": r"\b(?:redis|red\s*is|read\s*is)\b", "replacement": "Redis", "case_sensitive": False},
        {"pattern": r"\b(?:elastic\s*search|e\s*lastic\s*search)\b", "replacement": "Elasticsearch", "case_sensitive": False},

        # Development tools
        {"pattern": r"\b(?:git\s*hub|get\s*hub)\b", "replacement": "GitHub", "case_sensitive": False},
        {"pattern": r"\b(?:git\s*lab|get\s*lab)\b", "replacement": "GitLab", "case_sensitive": False},
        {"pattern": r"\b(?:bit\s*bucket|bid\s*bucket)\b", "replacement": "Bitbucket", "case_sensitive": False},
        {"pattern": r"\b(?:jenkins|jen\s*kins)\b", "replacement": "Jenkins", "case_sensitive": False},
        {"pattern": r"\b(?:circle\s*ci|circle\s*c\s*i)\b", "replacement": "CircleCI", "case_sensitive": False},
        {"pattern": r"\b(?:travis|trav\s*is)\s*(?:ci|c\s*i)\b", "replacement": "Travis CI", "case_sensitive": False},

        # Common tech abbreviations
        {"pattern": r"\b(?:API|a\.p\.i\.|a\s+p\s+i)\b", "replacement": "API", "case_sensitive": False},
        {"pattern": r"\b(?:REST|r\.e\.s\.t\.|rest\s+full)\b", "replacement": "REST", "case_sensitive": False},
        {"pattern": r"\b(?:GraphQL|graph\s*q\s*l|graph\s*QL)\b", "replacement": "GraphQL", "case_sensitive": False},
        {"pattern": r"\b(?:SQL|sequel|s\.q\.l\.)\b", "replacement": "SQL", "case_sensitive": False, "context": "database"},
        {"pattern": r"\b(?:HTML|h\.t\.m\.l\.|h\s+t\s+m\s+l)\b", "replacement": "HTML", "case_sensitive": False},
        {"pattern": r"\b(?:CSS|c\.s\.s\.|c\s+s\s+s)\b", "replacement": "CSS", "case_sensitive": False},
        {"pattern": r"\b(?:JSON|j\.son|jay\s*son)\b", "replacement": "JSON", "case_sensitive": False},
        {"pattern": r"\b(?:XML|x\.m\.l\.|x\s+m\s+l)\b", "replacement": "XML", "case_sensitive": False},
        {"pattern": r"\b(?:YAML|y\.a\.m\.l\.|yam\s*l)\b", "replacement": "YAML", "case_sensitive": False},

        # ============================================
        # BUSINESS & PROFESSIONAL TERMS
        # ============================================

        {"pattern": r"\b(?:CEO|c\.e\.o\.|chief\s+executive)\b", "replacement": "CEO", "case_sensitive": False},
        {"pattern": r"\b(?:CTO|c\.t\.o\.|chief\s+technology)\b", "replacement": "CTO", "case_sensitive": False},
        {"pattern": r"\b(?:CFO|c\.f\.o\.|chief\s+financial)\b", "replacement": "CFO", "case_sensitive": False},
        {"pattern": r"\b(?:COO|c\.o\.o\.|chief\s+operating)\b", "replacement": "COO", "case_sensitive": False},
        {"pattern": r"\b(?:VP|v\.p\.|vice\s+president)\b", "replacement": "VP", "case_sensitive": False},
        {"pattern": r"\b(?:ROI|r\.o\.i\.|return\s+on\s+investment)\b", "replacement": "ROI", "case_sensitive": False},
        {"pattern": r"\b(?:KPI|k\.p\.i\.|key\s+performance)\b", "replacement": "KPI", "case_sensitive": False},
        {"pattern": r"\b(?:B2B|b\s+to\s+b|business\s+to\s+business)\b", "replacement": "B2B", "case_sensitive": False},
        {"pattern": r"\b(?:B2C|b\s+to\s+c|business\s+to\s+consumer)\b", "replacement": "B2C", "case_sensitive": False},
        {"pattern": r"\b(?:SaaS|s\.a\.a\.s\.|software\s+as\s+a\s+service)\b", "replacement": "SaaS", "case_sensitive": False},

        # ============================================
        # COMMON PHRASES & EXPRESSIONS
        # ============================================

        {"pattern": r"\bfor\s+all\s+intensive\s+purposes\b", "replacement": "for all intents and purposes", "description": "Common phrase correction"},
        {"pattern": r"\bnip\s+it\s+in\s+the\s+butt\b", "replacement": "nip it in the bud", "description": "Common phrase correction"},
        {"pattern": r"\bcould\s+of\b", "replacement": "could have", "description": "could have, not could of"},
        {"pattern": r"\bwould\s+of\b", "replacement": "would have", "description": "would have, not would of"},
        {"pattern": r"\bshould\s+of\b", "replacement": "should have", "description": "should have, not should of"},
        {"pattern": r"\bmust\s+of\b", "replacement": "must have", "description": "must have, not must of"},
        {"pattern": r"\bmight\s+of\b", "replacement": "might have", "description": "might have, not might of"},

        # ============================================
        # CONTRACTIONS & GRAMMAR
        # ============================================

        {"pattern": r"\b(?:can't|cant)\b", "replacement": "can't", "case_sensitive": False},
        {"pattern": r"\b(?:won't|wont)\b", "replacement": "won't", "case_sensitive": False},
        {"pattern": r"\b(?:didn't|didnt)\b", "replacement": "didn't", "case_sensitive": False},
        {"pattern": r"\b(?:doesn't|doesnt)\b", "replacement": "doesn't", "case_sensitive": False},
        {"pattern": r"\b(?:isn't|isnt)\b", "replacement": "isn't", "case_sensitive": False},
        {"pattern": r"\b(?:aren't|arent)\b", "replacement": "aren't", "case_sensitive": False},
        {"pattern": r"\b(?:weren't|werent)\b", "replacement": "weren't", "case_sensitive": False},
        {"pattern": r"\b(?:hasn't|hasnt)\b", "replacement": "hasn't", "case_sensitive": False},
        {"pattern": r"\b(?:haven't|havent)\b", "replacement": "haven't", "case_sensitive": False},
        {"pattern": r"\b(?:wouldn't|wouldnt)\b", "replacement": "wouldn't", "case_sensitive": False},
        {"pattern": r"\b(?:shouldn't|shouldnt)\b", "replacement": "shouldn't", "case_sensitive": False},
        {"pattern": r"\b(?:couldn't|couldnt)\b", "replacement": "couldn't", "case_sensitive": False},

        # ============================================
        # NUMBERS & MEASUREMENTS
        # ============================================

        {"pattern": r"\b(\d+)\s*k\b", "replacement": r"\g<1>K", "description": "Standardize K for thousands"},
        {"pattern": r"\b(\d+)\s*m\b", "replacement": r"\g<1>M", "description": "Standardize M for millions", "context": "number"},
        {"pattern": r"\b(\d+)\s*gb\b", "replacement": r"\g<1>GB", "case_sensitive": False},
        {"pattern": r"\b(\d+)\s*mb\b", "replacement": r"\g<1>MB", "case_sensitive": False},
        {"pattern": r"\b(\d+)\s*kb\b", "replacement": r"\g<1>KB", "case_sensitive": False},
        {"pattern": r"\b(\d+)\s*tb\b", "replacement": r"\g<1>TB", "case_sensitive": False},

        # ============================================
        # COMMON FILLER WORDS (optional cleanup)
        # ============================================

        {"pattern": r"\b(?:um+|uh+|er+|ah+)\b", "replacement": "", "description": "Remove filler words", "enabled": False},
        {"pattern": r"\byou\s+know\b", "replacement": "", "description": "Remove 'you know' filler", "enabled": False},
        {"pattern": r"\bI\s+mean\b", "replacement": "", "description": "Remove 'I mean' filler", "enabled": False},
        {"pattern": r"\blike\b", "replacement": "", "description": "Remove 'like' as filler", "enabled": False, "context": "filler"},
    ],

    "repetition_cleanup": {
        "enabled": True,
        "patterns": [
            {
                "pattern": r"(\b\w+\b)(?:\s*,?\s*\1){5,}",  # Word repeated 5+ times
                "replacement": r"\1, \1, \1...",
                "description": "Reduce excessive word repetition"
            },
            {
                "pattern": r"(blah\s*,?\s*){10,}",  # "blah" repeated 10+ times
                "replacement": "blah, blah, blah...",
                "description": "Reduce excessive 'blah' repetition"
            },
            {
                "pattern": r"(etc\.?\s*,?\s*){3,}",  # "etc" repeated 3+ times
                "replacement": "etc.",
                "description": "Reduce excessive 'etc' repetition"
            },
            {
                "pattern": r"(\.\s*){4,}",  # Multiple periods
                "replacement": "...",
                "description": "Standardize ellipsis"
            }
        ]
    },

    "capitalization": {
        "enabled": True,
        "rules": [
            {
                "pattern": r"^([a-z])",  # Start of text
                "replacement": lambda m: m.group(1).upper(),
                "description": "Capitalize first letter"
            },
            {
                "pattern": r"([.!?]\s+)([a-z])",  # After sentence end
                "replacement": lambda m: m.group(1) + m.group(2).upper(),
                "description": "Capitalize after sentence"
            },
            {
                "pattern": r"\bi\b",  # Pronoun "I"
                "replacement": "I",
                "description": "Capitalize pronoun I"
            }
        ]
    },

    "metadata": {
        "version": "1.0.0",
        "description": "Comprehensive default proofreading rules for LocalTranscribe",
        "categories": ["tech", "business", "grammar", "common"],
        "last_updated": "2024-10-24"
    }
}

def get_default_rules() -> Dict[str, Any]:
    """Get a copy of the default rules."""
    import copy
    return copy.deepcopy(DEFAULT_RULES)

def get_minimal_rules() -> Dict[str, Any]:
    """Get minimal set of rules for quick processing."""
    return {
        "replacements": [
            # Just the most common/critical fixes
            r for r in DEFAULT_RULES["replacements"]
            if r.get("enabled", True) and "filler" not in r.get("context", "")
        ][:20],  # Top 20 most common
        "repetition_cleanup": DEFAULT_RULES["repetition_cleanup"],
        "capitalization": {"enabled": False}  # Skip for speed
    }

def get_category_rules(categories: List[str]) -> Dict[str, Any]:
    """Get rules for specific categories only."""
    filtered_rules = []

    for rule in DEFAULT_RULES["replacements"]:
        rule_context = rule.get("context", "")
        rule_desc = rule.get("description", "").lower()

        # Check if rule matches any requested category
        for category in categories:
            cat_lower = category.lower()
            if (cat_lower in rule_context or
                cat_lower in rule_desc or
                (cat_lower == "tech" and any(term in rule_desc for term in ["api", "software", "framework", "database"]))):
                filtered_rules.append(rule)
                break

    return {
        "replacements": filtered_rules,
        "repetition_cleanup": DEFAULT_RULES["repetition_cleanup"],
        "capitalization": DEFAULT_RULES["capitalization"]
    }