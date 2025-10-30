"""
Domain-specific dictionaries for enhanced proofreading.

Provides specialized terminology and correction rules for different domains
including military, technical, business, and medical contexts.
"""

from typing import Dict, List

# Military terminology
MILITARY_TERMS: Dict[str, str] = {
    # Ranks
    r"\bkaptin\b": "Captain",
    r"\bkernal\b": "Colonel",
    r"\bsarjent\b": "Sergeant",
    r"\blootenent\b": "Lieutenant",
    r"\bmajir\b": "Major",
    r"\bgeneral\b": "General",

    # Equipment
    r"\bhumvee\b": "HMMWV",
    r"\bapache\b": "Apache",
    r"\bchinook\b": "Chinook",
    r"\bf 16\b": "F-16",
    r"\bf sixteen\b": "F-16",

    # Operations
    r"\brop\b": "ROP",
    r"\bcas\b": "CAS",
    r"\bmedevac\b": "MEDEVAC",
    r"\bsitrep\b": "SITREP",
    r"\bopord\b": "OPORD",

    # Units
    r"\bplatoon\b": "platoon",
    r"\bsquad\b": "squad",
    r"\bdivision\b": "division",
    r"\bbrigade\b": "brigade",
}

# Technical/IT terminology
TECHNICAL_TERMS: Dict[str, str] = {
    # Programming
    r"\bpython\b": "Python",
    r"\bjavascript\b": "JavaScript",
    r"\btypescript\b": "TypeScript",
    r"\breact\b": "React",
    r"\bkubernetes\b": "Kubernetes",

    # Cloud services
    r"\baws\b": "AWS",
    r"\bgcp\b": "GCP",
    r"\bazure\b": "Azure",
    r"\bs three\b": "S3",
    r"\bec two\b": "EC2",
    r"\blambda\b": "Lambda",

    # Databases
    r"\bmongo db\b": "MongoDB",
    r"\bpostgres\b": "PostgreSQL",
    r"\bmysql\b": "MySQL",
    r"\bredis\b": "Redis",

    # Protocols/Standards
    r"\bhttp\b": "HTTP",
    r"\bhttps\b": "HTTPS",
    r"\bapi\b": "API",
    r"\brest\b": "REST",
    r"\bgraphql\b": "GraphQL",
    r"\bgrpc\b": "gRPC",

    # Tools
    r"\bdocker\b": "Docker",
    r"\bgit\b": "Git",
    r"\bjenkins\b": "Jenkins",
    r"\bterraform\b": "Terraform",
}

# Business terminology
BUSINESS_TERMS: Dict[str, str] = {
    # Financial
    r"\bkpi\b": "KPI",
    r"\broi\b": "ROI",
    r"\bebitda\b": "EBITDA",
    r"\bp and l\b": "P&L",
    r"\bprofit and loss\b": "P&L",

    # Management
    r"\bceo\b": "CEO",
    r"\bcfo\b": "CFO",
    r"\bcto\b": "CTO",
    r"\bcoo\b": "COO",
    r"\bvp\b": "VP",

    # Methodologies
    r"\bagile\b": "Agile",
    r"\bscrum\b": "Scrum",
    r"\bsix sigma\b": "Six Sigma",
    r"\bkpi\b": "KPI",
    r"\bokr\b": "OKR",

    # Common phrases
    r"\baction items\b": "action items",
    r"\bsynergy\b": "synergy",
    r"\bbottom line\b": "bottom line",
    r"\bstakeholders\b": "stakeholders",
}

# Medical terminology (basic)
MEDICAL_TERMS: Dict[str, str] = {
    # Common procedures
    r"\bmri\b": "MRI",
    r"\bct scan\b": "CT scan",
    r"\bx ray\b": "X-ray",
    r"\becg\b": "ECG",
    r"\bekg\b": "EKG",

    # Medications
    r"\bibuprofen\b": "ibuprofen",
    r"\bacetaminophen\b": "acetaminophen",
    r"\baspirin\b": "aspirin",

    # Conditions
    r"\bdiabetes\b": "diabetes",
    r"\bhypertension\b": "hypertension",
    r"\basthma\b": "asthma",
}

# Common acronyms across domains
COMMON_ACRONYMS: Dict[str, str] = {
    r"\basap\b": "ASAP",
    r"\bfyi\b": "FYI",
    r"\betc\b": "etc.",
    r"\bi e\b": "i.e.",
    r"\be g\b": "e.g.",
    r"\bvs\b": "vs.",
    r"\baq\b": "AQ",
    r"\bir\b": "IR",
    r"\bpr\b": "PR",
    r"\bhr\b": "HR",
    r"\bqa\b": "QA",
    r"\bui\b": "UI",
    r"\bux\b": "UX",
}

# Named entities that are commonly mispronounced
NAMED_ENTITIES: Dict[str, str] = {
    # Companies
    r"\bgoogle\b": "Google",
    r"\bmicrosoft\b": "Microsoft",
    r"\bamazon\b": "Amazon",
    r"\bapple\b": "Apple",
    r"\bmeta\b": "Meta",
    r"\btesla\b": "Tesla",

    # Locations (common)
    r"\bsan francisco\b": "San Francisco",
    r"\bnew york\b": "New York",
    r"\blos angeles\b": "Los Angeles",
    r"\bseattle\b": "Seattle",

    # Organizations
    r"\bnato\b": "NATO",
    r"\bun\b": "UN",
    r"\bwho\b": "WHO",
    r"\bfda\b": "FDA",
}


def get_domain_dictionary(domain: str) -> Dict[str, str]:
    """
    Get dictionary for specific domain.

    Args:
        domain: Domain name (military, technical, business, medical, common)

    Returns:
        Dictionary of regex patterns to replacements
    """
    domain_lower = domain.lower()

    if domain_lower == "military":
        return MILITARY_TERMS
    elif domain_lower in ["technical", "tech", "it"]:
        return TECHNICAL_TERMS
    elif domain_lower == "business":
        return BUSINESS_TERMS
    elif domain_lower == "medical":
        return MEDICAL_TERMS
    elif domain_lower == "common":
        return COMMON_ACRONYMS
    elif domain_lower == "entities":
        return NAMED_ENTITIES
    else:
        return {}


def get_all_domain_terms() -> Dict[str, str]:
    """
    Get combined dictionary of all domain terms.

    Returns:
        Combined dictionary of all domains
    """
    combined = {}
    combined.update(MILITARY_TERMS)
    combined.update(TECHNICAL_TERMS)
    combined.update(BUSINESS_TERMS)
    combined.update(MEDICAL_TERMS)
    combined.update(COMMON_ACRONYMS)
    combined.update(NAMED_ENTITIES)
    return combined


def get_domains_list() -> List[str]:
    """
    Get list of available domains.

    Returns:
        List of domain names
    """
    return ["military", "technical", "business", "medical", "common", "entities"]
