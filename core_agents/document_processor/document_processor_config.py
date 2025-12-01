"""
Document Processor Configuration

Defines document types, parsing patterns, and metadata extraction rules
for FOMC documents (Minutes, Monetary Policy Reports, SEP).
"""

import os
from dotenv import load_dotenv
from typing import Dict, List
import re

# Load environment variables
load_dotenv()

# Document directory configuration
DOCS_BASE_DIR = os.getenv("FOMC_DOCS_DIR", "/mnt/user-data/uploads")
MINUTES_DIR = os.path.join(DOCS_BASE_DIR, "minutes")
MPR_DIR = os.path.join(DOCS_BASE_DIR, "mpr")
SEP_DIR = os.path.join(DOCS_BASE_DIR, "sep")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============================================================================
# DOCUMENT TYPES
# ============================================================================

DOCUMENT_TYPES = {
    "minutes": {
        "name": "FOMC Minutes",
        "frequency": "8 per year (after each meeting)",
        "release_lag": "3 weeks after meeting",
        "key_content": [
            "Economic conditions discussion",
            "Policy decision rationale",
            "Participant views",
            "Vote count",
            "Forward guidance language"
        ],
        "file_pattern": r"fomcminutes\d{8}\.pdf",
        "date_format": "%Y%m%d"
    },
    "mpr": {
        "name": "Monetary Policy Report",
        "frequency": "2 per year (February, July)",
        "release_lag": "~2 weeks before testimony",
        "key_content": [
            "Economic developments",
            "Monetary policy review",
            "Forward-looking analysis",
            "Box articles on special topics"
        ],
        "file_pattern": r"mpr_\d{8}\.pdf",
        "date_format": "%Y%m%d"
    },
    "sep": {
        "name": "Summary of Economic Projections",
        "frequency": "4 per year (March, June, September, December)",
        "release_lag": "Same day as meeting statement",
        "key_content": [
            "GDP growth projections",
            "Unemployment rate projections",
            "Inflation projections (PCE, Core PCE)",
            "Fed Funds rate projections",
            "Uncertainty and risk assessments"
        ],
        "file_pattern": r"fomcprojtabl\d{8}\.pdf",
        "date_format": "%Y%m%d"
    }
}

# ============================================================================
# SEP TABLE STRUCTURE
# ============================================================================
# SEP tables have a consistent structure we can parse

SEP_VARIABLES = {
    "gdp": {
        "name": "Change in real GDP",
        "patterns": [
            r"Change in real GDP",
            r"Real GDP",
            r"GDP growth"
        ],
        "unit": "percent",
        "type": "growth_rate"
    },
    "unemployment": {
        "name": "Unemployment rate",
        "patterns": [
            r"Unemployment rate",
            r"Civilian unemployment rate"
        ],
        "unit": "percent",
        "type": "rate"
    },
    "pce_inflation": {
        "name": "PCE inflation",
        "patterns": [
            r"PCE inflation",
            r"Total PCE inflation"
        ],
        "unit": "percent",
        "type": "rate"
    },
    "core_pce_inflation": {
        "name": "Core PCE inflation",
        "patterns": [
            r"Core PCE inflation",
            r"PCE inflation excluding food and energy"
        ],
        "unit": "percent",
        "type": "rate"
    },
    "fed_funds": {
        "name": "Federal funds rate",
        "patterns": [
            r"Federal funds rate",
            r"Fed funds rate"
        ],
        "unit": "percent",
        "type": "rate"
    }
}

# SEP projection years structure
# Typically: current year, +1 year, +2 year, longer run
SEP_YEAR_COLUMNS = ["current_year", "next_year", "two_years", "longer_run"]

# ============================================================================
# TEXT EXTRACTION PATTERNS
# ============================================================================

# Policy action patterns (for Minutes)
POLICY_ACTION_PATTERNS = {
    "rate_increase": [
        r"voted to (?:raise|increase) the target range.*?by (\d+) basis points?",
        r"increase.*?federal funds rate.*?by (\d+) basis points?",
        r"raise.*?target range.*?to ([\d.]+) to ([\d.]+) percent"
    ],
    "rate_decrease": [
        r"voted to (?:lower|decrease|reduce|cut) the target range.*?by (\d+) basis points?",
        r"decrease.*?federal funds rate.*?by (\d+) basis points?",
        r"lower.*?target range.*?to ([\d.]+) to ([\d.]+) percent"
    ],
    "rate_unchanged": [
        r"voted to (?:maintain|leave unchanged|hold) the target range",
        r"maintain the target range for the federal funds rate"
    ]
}

# Economic assessment patterns (sentiment analysis)
ECONOMIC_ASSESSMENT_PATTERNS = {
    "positive": [
        r"strong(?:er)? growth",
        r"robust expansion",
        r"labor market (?:strength|tightness)",
        r"solid (?:economic|job) growth",
        r"improving conditions"
    ],
    "negative": [
        r"slow(?:er|ing) growth",
        r"weak(?:er|ening) (?:economic|labor market)",
        r"elevated (?:inflation|unemployment)",
        r"downside risks",
        r"concerning developments"
    ],
    "uncertain": [
        r"considerable uncertainty",
        r"difficult to (?:assess|predict)",
        r"range of possible outcomes",
        r"uncertainty (?:about|regarding|surrounding)"
    ]
}

# Forward guidance patterns
FORWARD_GUIDANCE_PATTERNS = [
    r"anticipates? that (?:it will be|economic conditions will).*?(?:warrant|appropriate)",
    r"Committee (?:expects|anticipates) to (?:maintain|begin|continue)",
    r"(?:appropriate|necessary) to (?:maintain|achieve).*?inflation.*?2 percent"
]

# Hawkish/Dovish language indicators
HAWKISH_INDICATORS = [
    r"inflation (?:pressures|concerns|risks)",
    r"(?:tighten|restrict|raise|increase).*?monetary policy",
    r"combat inflation",
    r"price stability risks",
    r"overheating",
    r"wage pressures"
]

DOVISH_INDICATORS = [
    r"support(?:ing)? (?:economic|employment) growth",
    r"accommodative (?:stance|policy)",
    r"below (?:target|mandate)",
    r"downside risks? to (?:growth|employment)",
    r"maintain.*?support",
    r"substantial (?:further )?progress"
]

# ============================================================================
# MEETING DATE PATTERNS
# ============================================================================

# FOMC meetings are typically:
# - 8 per year
# - Scheduled in advance
# - January/February, March, April/May, June, July, September, October/November, December

TYPICAL_MEETING_MONTHS = [
    (1, 2),   # January or February
    (3,),     # March
    (4, 5),   # April or May
    (6,),     # June
    (7,),     # July
    (9,),     # September
    (10, 11), # October or November
    (12,)     # December
]

# Date extraction patterns
DATE_PATTERNS = [
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:–|-)\d{1,2},?\s+\d{4}",
    r"\d{1,2}(?:–|-)\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}",
    r"(?:Meeting|meeting) held on (?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:–|-)\d{1,2},?\s+\d{4}"
]

# ============================================================================
# PARTICIPANT/VOTING PATTERNS
# ============================================================================

# Extract who voted, dissents
VOTING_PATTERNS = {
    "unanimous": [
        r"Voting for.*?all members",
        r"unanimous",
        r"all (?:\d+|\w+) members voted in favor"
    ],
    "dissent": [
        r"Voting against.*?:(.*?)(?:\.|$)",
        r"(?:Mr\.|Ms\.|Mrs\.).*?(?:dissented|preferred|voted against)"
    ]
}

# Committee member patterns (for extracting participants)
MEMBER_TITLE_PATTERN = r"(?:Mr\.|Ms\.|Mrs\.|Chair(?:man|woman)?|Vice Chair(?:man|woman)?|Governor|President)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)"

# ============================================================================
# TABLE EXTRACTION SETTINGS
# ============================================================================

# pdfplumber table extraction settings
TABLE_SETTINGS = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "snap_tolerance": 3,
    "join_tolerance": 3,
    "edge_min_length": 3,
    "min_words_vertical": 3,
    "min_words_horizontal": 1,
}

# ============================================================================
# OUTPUT STRUCTURE
# ============================================================================

# Standard output schema for parsed documents
DOCUMENT_SCHEMA = {
    "metadata": {
        "document_type": "str",
        "meeting_date": "datetime",
        "release_date": "datetime",
        "file_path": "str",
        "source": "str"
    },
    "policy_decision": {
        "action": "str",  # increase, decrease, unchanged
        "target_range": "tuple",  # (lower, upper)
        "change_amount": "float",  # basis points
        "vote_split": "str",  # "unanimous" or "X-Y"
        "dissenters": "list"
    },
    "economic_projections": {
        "gdp": "dict",  # {year: value}
        "unemployment": "dict",
        "pce_inflation": "dict",
        "core_pce_inflation": "dict",
        "fed_funds": "dict"
    },
    "text_analysis": {
        "sentiment": "str",  # hawkish, dovish, neutral
        "key_phrases": "list",
        "forward_guidance": "str",
        "economic_assessment": "dict"
    },
    "participants": {
        "voting_members": "list",
        "non_voting_members": "list"
    }
}

# ============================================================================
# ERROR HANDLING
# ============================================================================

# Common parsing errors and how to handle them
ERROR_HANDLING = {
    "missing_table": "warn_and_continue",
    "malformed_date": "use_filename_date",
    "incomplete_projections": "return_partial",
    "ocr_errors": "flag_for_review"
}

# Validation thresholds
VALIDATION_THRESHOLDS = {
    "min_text_length": 1000,  # Minimum characters for valid document
    "max_gdp_projection": 10.0,  # Unrealistic if higher (%)
    "min_gdp_projection": -10.0,  # Unrealistic if lower (%)
    "max_inflation": 15.0,  # Unrealistic if higher (%)
    "max_unemployment": 25.0,  # Unrealistic if higher (%)
    "max_fed_funds": 20.0  # Unrealistic if higher (%)
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_config() -> List[str]:
    """Validate document processor configuration and return list of issues."""
    issues = []
    
    # Check if document directories exist
    import os
    if not os.path.exists(DOCS_BASE_DIR):
        issues.append(f"Base documents directory does not exist: {DOCS_BASE_DIR}")
    
    if not os.path.exists(MINUTES_DIR):
        issues.append(f"Minutes directory does not exist: {MINUTES_DIR}")
    
    if not os.path.exists(MPR_DIR):
        issues.append(f"MPR directory does not exist: {MPR_DIR}")
    
    if not os.path.exists(SEP_DIR):
        issues.append(f"SEP directory does not exist: {SEP_DIR}")
    
    # Check validation thresholds
    if VALIDATION_THRESHOLDS["min_text_length"] <= 0:
        issues.append("Minimum text length must be positive")
    
    return issues


def get_config_info() -> Dict[str, any]:
    """Get current configuration information."""
    import os
    return {
        "docs_base_dir": DOCS_BASE_DIR,
        "dirs_exist": {
            "base": os.path.exists(DOCS_BASE_DIR),
            "minutes": os.path.exists(MINUTES_DIR),
            "mpr": os.path.exists(MPR_DIR),
            "sep": os.path.exists(SEP_DIR)
        },
        "log_level": LOG_LEVEL,
        "document_types_count": len(DOCUMENT_TYPES)
    }


def is_fully_configured() -> bool:
    """Check if document processor is fully configured."""
    issues = validate_config()
    critical_issues = [issue for issue in issues if "does not exist" in issue]
    return len(critical_issues) == 0
