"""
Domain-specific dictionaries for enhanced proofreading.

Provides specialized terminology and correction rules for different domains
including military, technical, business, and medical contexts.
"""

from typing import Dict, List

# Military terminology (50+ terms)
MILITARY_TERMS: Dict[str, str] = {
    # Ranks - Enlisted
    r"\bkaptin\b": "Captain",
    r"\bkernal\b": "Colonel",
    r"\bsarjent\b": "Sergeant",
    r"\blootenent\b": "Lieutenant",
    r"\bmajir\b": "Major",
    r"\bgeneral\b": "General",
    r"\bpfc\b": "PFC",
    r"\bprivate first class\b": "Private First Class",
    r"\bspc\b": "SPC",
    r"\bspecialist\b": "Specialist",
    r"\bcpl\b": "CPL",
    r"\bcorporal\b": "Corporal",
    r"\bssg\b": "SSG",
    r"\bstaff sergeant\b": "Staff Sergeant",
    r"\bmsg\b": "MSG",
    r"\bmaster sergeant\b": "Master Sergeant",
    r"\bsgm\b": "SGM",
    r"\bsergeant major\b": "Sergeant Major",
    r"\bcsm\b": "CSM",
    r"\bcommand sergeant major\b": "Command Sergeant Major",

    # Equipment - Aircraft
    r"\bhumvee\b": "HMMWV",
    r"\bapache\b": "Apache",
    r"\bchinook\b": "Chinook",
    r"\bf 16\b": "F-16",
    r"\bf sixteen\b": "F-16",
    r"\bf 22\b": "F-22",
    r"\bf twenty two\b": "F-22",
    r"\bc 130\b": "C-130",
    r"\bc one thirty\b": "C-130",
    r"\bblack hawk\b": "Black Hawk",
    r"\ba 10\b": "A-10",
    r"\ba ten\b": "A-10",

    # Equipment - Weapons
    r"\bm 4\b": "M4",
    r"\bem four\b": "M4",
    r"\bm 16\b": "M16",
    r"\bem sixteen\b": "M16",
    r"\bsaw\b": "SAW",
    r"\blaw\b": "LAW",
    r"\btow\b": "TOW",
    r"\bjdam\b": "JDAM",
    r"\bmoab\b": "MOAB",
    r"\bfifty cal\b": ".50 cal",

    # Operations
    r"\brop\b": "ROP",
    r"\bcas\b": "CAS",
    r"\bclose air support\b": "Close Air Support",
    r"\bmedevac\b": "MEDEVAC",
    r"\bdustoff\b": "DUSTOFF",
    r"\bsitrep\b": "SITREP",
    r"\bsituation report\b": "Situation Report",
    r"\bopord\b": "OPORD",
    r"\boperations order\b": "Operations Order",
    r"\bfrago\b": "FRAGO",
    r"\bfragmentary order\b": "Fragmentary Order",
    r"\bwarno\b": "WARNO",
    r"\bwarning order\b": "Warning Order",
    r"\bmout\b": "MOUT",
    r"\bfob\b": "FOB",
    r"\bforward operating base\b": "Forward Operating Base",

    # Units
    r"\bplatoon\b": "platoon",
    r"\bsquad\b": "squad",
    r"\bdivision\b": "division",
    r"\bbrigade\b": "brigade",
    r"\bbattalion\b": "battalion",
    r"\bcompany\b": "company",
    r"\bregiment\b": "regiment",
}

# Technical/IT terminology (60+ terms)
TECHNICAL_TERMS: Dict[str, str] = {
    # Programming Languages
    r"\bpython\b": "Python",
    r"\bjavascript\b": "JavaScript",
    r"\btypescript\b": "TypeScript",
    r"\breact\b": "React",
    r"\bvue\b": "Vue",
    r"\bangular\b": "Angular",
    r"\bnode js\b": "Node.js",
    r"\bjava\b": "Java",
    r"\bc sharp\b": "C#",
    r"\bgo\b": "Go",
    r"\brust\b": "Rust",
    r"\bswift\b": "Swift",
    r"\bkotlin\b": "Kotlin",

    # Cloud Services - AWS
    r"\baws\b": "AWS",
    r"\bs three\b": "S3",
    r"\bec two\b": "EC2",
    r"\blambda\b": "Lambda",
    r"\beks\b": "EKS",
    r"\becs\b": "ECS",
    r"\becr\b": "ECR",
    r"\balb\b": "ALB",
    r"\bnlb\b": "NLB",
    r"\bvpc\b": "VPC",
    r"\bigw\b": "IGW",
    r"\bnat\b": "NAT",
    r"\brds\b": "RDS",
    r"\bdynamo db\b": "DynamoDB",
    r"\bcloud formation\b": "CloudFormation",

    # Cloud Services - Other
    r"\bgcp\b": "GCP",
    r"\bazure\b": "Azure",
    r"\bdigital ocean\b": "DigitalOcean",

    # Container & Orchestration
    r"\bkubernetes\b": "Kubernetes",
    r"\bk 8 s\b": "K8s",
    r"\bk eight s\b": "K8s",
    r"\bdocker\b": "Docker",
    r"\bhelm\b": "Helm",
    r"\bistio\b": "Istio",

    # Databases
    r"\bmongo db\b": "MongoDB",
    r"\bpostgres\b": "PostgreSQL",
    r"\bpostgresql\b": "PostgreSQL",
    r"\bmysql\b": "MySQL",
    r"\bredis\b": "Redis",
    r"\belasticsearch\b": "Elasticsearch",
    r"\bcassandra\b": "Cassandra",

    # Protocols & Standards
    r"\bhttp\b": "HTTP",
    r"\bhttps\b": "HTTPS",
    r"\bapi\b": "API",
    r"\brest\b": "REST",
    r"\brestful\b": "RESTful",
    r"\bgraphql\b": "GraphQL",
    r"\bgrpc\b": "gRPC",
    r"\bwebsocket\b": "WebSocket",
    r"\bmqtt\b": "MQTT",
    r"\bamqp\b": "AMQP",
    r"\bcoap\b": "CoAP",
    r"\bjson\b": "JSON",
    r"\bxml\b": "XML",
    r"\byaml\b": "YAML",

    # DevOps & CI/CD
    r"\bci cd\b": "CI/CD",
    r"\bci c d\b": "CI/CD",
    r"\bgitops\b": "GitOps",
    r"\biac\b": "IaC",
    r"\binfrastructure as code\b": "Infrastructure as Code",
    r"\bgit\b": "Git",
    r"\bgithub\b": "GitHub",
    r"\bgitlab\b": "GitLab",
    r"\bjenkins\b": "Jenkins",
    r"\btravis ci\b": "Travis CI",
    r"\bcircle ci\b": "CircleCI",

    # Tools & Frameworks
    r"\bterraform\b": "Terraform",
    r"\bansible\b": "Ansible",
    r"\bpuppet\b": "Puppet",
    r"\bchef\b": "Chef",
    r"\bkafka\b": "Kafka",
    r"\bnginx\b": "Nginx",

    # Architecture Patterns
    r"\bcqrs\b": "CQRS",
    r"\bevent sourcing\b": "Event Sourcing",
    r"\bddd\b": "DDD",
    r"\bdomain driven design\b": "Domain-Driven Design",
    r"\bsaga\b": "SAGA",
    r"\bmicroservices\b": "microservices",

    # Security
    r"\boauth\b": "OAuth",
    r"\boauth 2\b": "OAuth2",
    r"\bjwt\b": "JWT",
    r"\bsaml\b": "SAML",
    r"\bmfa\b": "MFA",
    r"\btwo fa\b": "2FA",
    r"\bsso\b": "SSO",
    r"\bssl\b": "SSL",
    r"\btls\b": "TLS",
}

# Business terminology (35+ terms)
BUSINESS_TERMS: Dict[str, str] = {
    # Financial Metrics
    r"\bkpi\b": "KPI",
    r"\broi\b": "ROI",
    r"\bebitda\b": "EBITDA",
    r"\bp and l\b": "P&L",
    r"\bprofit and loss\b": "P&L",
    r"\bnps\b": "NPS",
    r"\bcsat\b": "CSAT",
    r"\bcac\b": "CAC",
    r"\bltv\b": "LTV",
    r"\bmrr\b": "MRR",
    r"\barr\b": "ARR",
    r"\bcagr\b": "CAGR",
    r"\birr\b": "IRR",
    r"\bnpv\b": "NPV",
    r"\bwacc\b": "WACC",
    r"\beps\b": "EPS",
    r"\bp e\b": "P/E",
    r"\bprice to earnings\b": "P/E",

    # Management Roles
    r"\bceo\b": "CEO",
    r"\bcfo\b": "CFO",
    r"\bcto\b": "CTO",
    r"\bcoo\b": "COO",
    r"\bcmo\b": "CMO",
    r"\bcdo\b": "CDO",
    r"\bcpo\b": "CPO",
    r"\bgm\b": "GM",
    r"\bvp\b": "VP",
    r"\bsvp\b": "SVP",
    r"\bevp\b": "EVP",

    # Methodologies & Frameworks
    r"\bagile\b": "Agile",
    r"\bscrum\b": "Scrum",
    r"\bsix sigma\b": "Six Sigma",
    r"\bokr\b": "OKR",
    r"\bswot\b": "SWOT",
    r"\bpestle\b": "PESTLE",
    r"\bbcg matrix\b": "BCG Matrix",
    r"\blean\b": "Lean",
    r"\bkanban\b": "Kanban",

    # Common phrases
    r"\baction items\b": "action items",
    r"\bsynergy\b": "synergy",
    r"\bbottom line\b": "bottom line",
    r"\bstakeholders\b": "stakeholders",
    r"\bvalue proposition\b": "value proposition",
    r"\bgo to market\b": "go-to-market",
    r"\bb to b\b": "B2B",
    r"\bb to c\b": "B2C",
    r"\bb two b\b": "B2B",
    r"\bb two c\b": "B2C",
}

# Medical terminology (45+ terms)
MEDICAL_TERMS: Dict[str, str] = {
    # Common Procedures & Tests
    r"\bmri\b": "MRI",
    r"\bct scan\b": "CT scan",
    r"\bcat scan\b": "CAT scan",
    r"\bx ray\b": "X-ray",
    r"\becg\b": "ECG",
    r"\bekg\b": "EKG",
    r"\beeg\b": "EEG",
    r"\bemg\b": "EMG",
    r"\bcbc\b": "CBC",
    r"\bcomplete blood count\b": "Complete Blood Count",
    r"\bbmp\b": "BMP",
    r"\bcmp\b": "CMP",
    r"\bua\b": "UA",
    r"\burinalysis\b": "Urinalysis",
    r"\bpet scan\b": "PET scan",

    # Medications & Drug Classes
    r"\bibuprofen\b": "ibuprofen",
    r"\bacetaminophen\b": "acetaminophen",
    r"\baspirin\b": "aspirin",
    r"\bace inhibitor\b": "ACE inhibitor",
    r"\bace inhibitors\b": "ACE inhibitors",
    r"\bnsaid\b": "NSAID",
    r"\bnsaids\b": "NSAIDs",
    r"\bssri\b": "SSRI",
    r"\bssris\b": "SSRIs",
    r"\bppi\b": "PPI",
    r"\bppis\b": "PPIs",

    # Medical Facilities & Departments
    r"\bed\b": "ED",
    r"\bemergency department\b": "Emergency Department",
    r"\bicu\b": "ICU",
    r"\bintensive care unit\b": "Intensive Care Unit",
    r"\bor\b": "OR",
    r"\boperating room\b": "Operating Room",
    r"\bpacu\b": "PACU",
    r"\bnicu\b": "NICU",
    r"\bpicu\b": "PICU",

    # Conditions & Diseases
    r"\bdiabetes\b": "diabetes",
    r"\bhypertension\b": "hypertension",
    r"\basthma\b": "asthma",
    r"\bcopd\b": "COPD",
    r"\bchronic obstructive pulmonary disease\b": "Chronic Obstructive Pulmonary Disease",
    r"\bchf\b": "CHF",
    r"\bcongestive heart failure\b": "Congestive Heart Failure",
    r"\bafib\b": "AFib",
    r"\batrial fibrillation\b": "Atrial Fibrillation",
    r"\bckd\b": "CKD",
    r"\bchronic kidney disease\b": "Chronic Kidney Disease",
    r"\bgerd\b": "GERD",
    r"\bibs\b": "IBS",
    r"\birritable bowel syndrome\b": "Irritable Bowel Syndrome",

    # Medical Professionals
    r"\bmd\b": "MD",
    r"\bdo\b": "DO",
    r"\brn\b": "RN",
    r"\blpn\b": "LPN",
    r"\bpa\b": "PA",
    r"\bnp\b": "NP",
}

# Legal terminology (30+ terms) - NEW DOMAIN
LEGAL_TERMS: Dict[str, str] = {
    # Legal Documents & Agreements
    r"\bnda\b": "NDA",
    r"\bnon disclosure agreement\b": "Non-Disclosure Agreement",
    r"\bsla\b": "SLA",
    r"\bservice level agreement\b": "Service Level Agreement",
    r"\bmsa\b": "MSA",
    r"\bmaster service agreement\b": "Master Service Agreement",
    r"\bsow\b": "SOW",
    r"\bstatement of work\b": "Statement of Work",
    r"\brfp\b": "RFP",
    r"\brequest for proposal\b": "Request for Proposal",
    r"\brfi\b": "RFI",
    r"\brequest for information\b": "Request for Information",
    r"\bloi\b": "LOI",
    r"\bletter of intent\b": "Letter of Intent",
    r"\bmou\b": "MOU",
    r"\bmemorandum of understanding\b": "Memorandum of Understanding",
    r"\btos\b": "TOS",
    r"\bterms of service\b": "Terms of Service",
    r"\beula\b": "EULA",

    # Business Entities
    r"\bllc\b": "LLC",
    r"\blimited liability company\b": "Limited Liability Company",
    r"\bllp\b": "LLP",
    r"\binc\b": "Inc.",
    r"\bincorporated\b": "Incorporated",
    r"\bcorp\b": "Corp.",
    r"\bcorporation\b": "Corporation",
    r"\bltd\b": "Ltd.",

    # Compliance & Regulations
    r"\bgdpr\b": "GDPR",
    r"\bccpa\b": "CCPA",
    r"\bhipaa\b": "HIPAA",
    r"\bsox\b": "SOX",
    r"\bsarbanes oxley\b": "Sarbanes-Oxley",
    r"\bpci dss\b": "PCI DSS",
    r"\bferpa\b": "FERPA",

    # Legal Processes
    r"\bip\b": "IP",
    r"\bintellectual property\b": "Intellectual Property",
    r"\bdmca\b": "DMCA",
}

# Academic terminology (20+ terms) - NEW DOMAIN
ACADEMIC_TERMS: Dict[str, str] = {
    # Academic Degrees
    r"\bphd\b": "PhD",
    r"\bph d\b": "Ph.D.",
    r"\bmsc\b": "MSc",
    r"\bm sc\b": "M.Sc.",
    r"\bbsc\b": "BSc",
    r"\bb sc\b": "B.Sc.",
    r"\bmba\b": "MBA",
    r"\bm b a\b": "M.B.A.",
    r"\bjd\b": "JD",
    r"\bmd\b": "MD",
    r"\bm d\b": "M.D.",
    r"\bedd\b": "EdD",
    r"\bma\b": "MA",
    r"\bba\b": "BA",

    # Research & Organizations
    r"\birb\b": "IRB",
    r"\binstitutional review board\b": "Institutional Review Board",
    r"\bpi\b": "PI",
    r"\bprincipal investigator\b": "Principal Investigator",
    r"\bco pi\b": "Co-PI",
    r"\bnih\b": "NIH",
    r"\bnsf\b": "NSF",
    r"\bdoe\b": "DOE",
    r"\bdarpa\b": "DARPA",

    # Publishing & Research
    r"\bdoi\b": "DOI",
    r"\bissn\b": "ISSN",
    r"\bisbn\b": "ISBN",
    r"\bpeer review\b": "peer review",
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
        domain: Domain name (military, technical, business, medical, legal, academic, common, entities)

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
    elif domain_lower == "legal":
        return LEGAL_TERMS
    elif domain_lower == "academic":
        return ACADEMIC_TERMS
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
        Combined dictionary of all domains (260+ terms)
    """
    combined = {}
    combined.update(MILITARY_TERMS)
    combined.update(TECHNICAL_TERMS)
    combined.update(BUSINESS_TERMS)
    combined.update(MEDICAL_TERMS)
    combined.update(LEGAL_TERMS)
    combined.update(ACADEMIC_TERMS)
    combined.update(COMMON_ACRONYMS)
    combined.update(NAMED_ENTITIES)
    return combined


def get_domains_list() -> List[str]:
    """
    Get list of available domains.

    Returns:
        List of domain names (8 domains)
    """
    return ["military", "technical", "business", "medical", "legal", "academic", "common", "entities"]
