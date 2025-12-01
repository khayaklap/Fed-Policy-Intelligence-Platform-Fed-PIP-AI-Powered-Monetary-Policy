"""
Policy Analyzer Configuration

Defines thresholds and parameters for analyzing Fed policy stance evolution,
regime changes, and sentiment trends over time.
"""

import os
from dotenv import load_dotenv
from typing import Dict, List

# Load environment variables
load_dotenv()

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============================================================================
# POLICY STANCE CLASSIFICATION
# ============================================================================

# Sentiment score ranges for stance classification
# Scores come from hawkish_count - dovish_count
STANCE_THRESHOLDS = {
    "highly_dovish": -15,       # Score < -15
    "dovish": -8,               # Score < -8
    "neutral": 8,               # -8 <= Score <= 8
    "hawkish": 15,              # Score <= 15
    "highly_hawkish": 15        # Score > 15
}

# Rate of change thresholds (for detecting shifts)
STANCE_SHIFT_THRESHOLD = 10  # Change of 10+ in score = significant shift

# ============================================================================
# REGIME CLASSIFICATION
# ============================================================================

# Fed policy regimes based on actions and sentiment
POLICY_REGIMES = {
    "accommodative": {
        "description": "Easing policy, supporting growth",
        "indicators": [
            "rate cuts",
            "dovish sentiment",
            "forward guidance emphasizes support",
            "concerned about downside risks"
        ]
    },
    "tightening": {
        "description": "Raising rates to combat inflation",
        "indicators": [
            "rate increases",
            "hawkish sentiment",
            "inflation concerns",
            "forward guidance signals more hikes"
        ]
    },
    "neutral": {
        "description": "Stable policy, data dependent",
        "indicators": [
            "rates unchanged",
            "neutral sentiment",
            "balanced assessment",
            "patient approach"
        ]
    },
    "pivot_to_tightening": {
        "description": "Transitioning from ease to tightening",
        "indicators": [
            "sentiment shift to hawkish",
            "preparing for rate hikes",
            "inflation concerns rising"
        ]
    },
    "pivot_to_easing": {
        "description": "Transitioning from tightening to ease",
        "indicators": [
            "sentiment shift to dovish",
            "preparing for rate cuts",
            "growth concerns rising"
        ]
    }
}

# ============================================================================
# REGIME CHANGE DETECTION
# ============================================================================

# Minimum meetings for establishing a regime
MIN_REGIME_LENGTH = 2  # At least 2 consecutive meetings

# Thresholds for detecting regime change
REGIME_CHANGE_INDICATORS = {
    "sentiment_reversal": {
        "threshold": 0.7,  # 70% of meetings show opposite sentiment
        "min_meetings": 3
    },
    "policy_action_change": {
        "types": ["unchanged_to_increase", "increase_to_unchanged", "increase_to_decrease"]
    },
    "forward_guidance_shift": {
        "keywords": {
            "tightening": ["raise", "increase", "tighten", "restrictive"],
            "easing": ["lower", "reduce", "ease", "accommodative", "support"],
            "neutral": ["maintain", "patient", "appropriate", "data-dependent"]
        }
    }
}

# Change point detection parameters (for statistical methods)
CHANGEPOINT_CONFIG = {
    "penalty": 5.0,  # Higher = fewer change points detected
    "min_size": 3,   # Minimum segment size
    "method": "pelt" # Algorithm: PELT (Pruned Exact Linear Time)
}

# ============================================================================
# HISTORICAL COMPARISON PERIODS
# ============================================================================

# Notable Fed policy episodes for comparison
HISTORICAL_EPISODES = {
    "volcker_disinflation": {
        "period": ("1979-08-01", "1987-08-01"),
        "description": "Volcker's aggressive tightening to break inflation",
        "regime": "tightening",
        "peak_rate": 20.0,
        "characteristics": ["very hawkish", "inflation priority", "recession accepted"]
    },
    "greenspan_gradualism": {
        "period": ("1987-08-01", "2006-01-31"),
        "description": "Greenspan era - gradual adjustments",
        "regime": "neutral",
        "characteristics": ["data-dependent", "gradual moves", "asymmetric easing"]
    },
    "gfc_response": {
        "period": ("2007-09-01", "2009-12-31"),
        "description": "Great Financial Crisis - aggressive easing",
        "regime": "accommodative",
        "characteristics": ["zero rates", "QE", "highly dovish"]
    },
    "taper_tantrum": {
        "period": ("2013-05-01", "2013-12-31"),
        "description": "Market reaction to QE taper discussion",
        "regime": "pivot_to_tightening",
        "characteristics": ["communication challenge", "market volatility"]
    },
    "2015_2019_normalization": {
        "period": ("2015-12-01", "2019-10-31"),
        "description": "Post-GFC normalization - gradual hikes then pivot",
        "regime": "tightening",
        "characteristics": ["gradual hikes", "balance sheet reduction", "pivot to cuts"]
    },
    "covid_response": {
        "period": ("2020-03-01", "2021-11-30"),
        "description": "COVID-19 - emergency easing and support",
        "regime": "accommodative",
        "characteristics": ["emergency cuts", "unlimited QE", "forward guidance"]
    },
    "2022_inflation_fight": {
        "period": ("2022-03-01", "2023-07-31"),
        "description": "Fastest tightening since 1980s",
        "regime": "tightening",
        "characteristics": ["75bp hikes", "very hawkish", "fighting inflation"]
    },
    "2024_higher_for_longer": {
        "period": ("2023-08-01", "2024-12-31"),
        "description": "Maintaining restrictive stance",
        "regime": "neutral",
        "characteristics": ["rates stable", "patient approach", "data-dependent"]
    }
}

# ============================================================================
# SENTIMENT TREND ANALYSIS
# ============================================================================

# Moving average windows for smoothing sentiment
SENTIMENT_MA_WINDOWS = {
    "short_term": 3,   # 3 meetings (~9 months)
    "medium_term": 6,  # 6 meetings (~18 months)
    "long_term": 12    # 12 meetings (~3 years)
}

# Trend classification
TREND_THRESHOLDS = {
    "strong_hawkish_trend": 0.5,    # Slope > 0.5 per meeting
    "moderate_hawkish_trend": 0.2,
    "stable": 0.2,                   # |Slope| < 0.2
    "moderate_dovish_trend": -0.2,
    "strong_dovish_trend": -0.5      # Slope < -0.5
}

# ============================================================================
# FORWARD GUIDANCE ANALYSIS
# ============================================================================

# Key phrases indicating guidance stance
GUIDANCE_PHRASES = {
    "hawkish": [
        "additional firming",
        "ongoing increases",
        "further tightening",
        "above neutral",
        "restrictive stance",
        "determined to bring inflation down"
    ],
    "dovish": [
        "patient approach",
        "pause",
        "maintain support",
        "accommodative",
        "monitoring developments",
        "support economic recovery"
    ],
    "data_dependent": [
        "data-dependent",
        "appropriate as the data indicate",
        "assess incoming information",
        "depends on the evolution",
        "monitoring conditions"
    ]
}

# ============================================================================
# MEETING FREQUENCY & TIMING
# ============================================================================

# FOMC meeting schedule
MEETINGS_PER_YEAR = 8
TYPICAL_MEETING_INTERVAL_DAYS = 45  # ~6 weeks

# Period definitions in number of meetings
PERIOD_DEFINITIONS = {
    "recent": 3,        # Last 3 meetings
    "short_term": 6,    # Last 6 meetings (~1.5 years)
    "medium_term": 12,  # Last 12 meetings (~3 years)
    "long_term": 24     # Last 24 meetings (~6 years)
}

# ============================================================================
# STANCE CONSISTENCY METRICS
# ============================================================================

# Measures how consistent the Fed's stance is
CONSISTENCY_THRESHOLDS = {
    "very_consistent": 0.9,   # 90%+ meetings same stance
    "consistent": 0.75,       # 75%+ meetings same stance
    "mixed": 0.5,            # 50-75% same stance
    "inconsistent": 0.5      # <50% same stance
}

# ============================================================================
# TURNING POINT DETECTION
# ============================================================================

# Parameters for identifying policy turning points
TURNING_POINT_CONFIG = {
    "min_meetings_before": 3,  # Need 3+ meetings before to establish trend
    "min_meetings_after": 2,   # Need 2+ meetings after to confirm turn
    "sentiment_reversal": 15,  # Score change of 15+ = turning point
    "action_reversal": True    # Policy action reverses direction
}

# ============================================================================
# VISUALIZATION SETTINGS
# ============================================================================

# For generating charts in reports
VIZ_CONFIG = {
    "figure_size": (12, 6),
    "dpi": 100,
    "style": "seaborn-v0_8-darkgrid",
    "colors": {
        "hawkish": "#d62728",      # Red
        "neutral": "#7f7f7f",      # Gray
        "dovish": "#2ca02c",       # Green
        "regime_change": "#ff7f0e" # Orange
    }
}

# ============================================================================
# OUTPUT SCHEMA
# ============================================================================

# Standard output structure for policy analysis
POLICY_ANALYSIS_SCHEMA = {
    "current_stance": {
        "classification": "str",  # hawkish, dovish, neutral
        "confidence": "float",    # 0-1
        "score": "int",          # Sentiment score
        "description": "str"
    },
    "trend": {
        "direction": "str",      # hawkish_trend, dovish_trend, stable
        "strength": "str",       # strong, moderate, weak
        "duration": "int"        # Number of meetings
    },
    "regime": {
        "current": "str",        # accommodative, tightening, neutral
        "duration": "int",       # Meetings in current regime
        "last_change": "date",   # When regime changed
        "stability": "str"       # stable, transitioning
    },
    "historical_context": {
        "similar_episodes": "list",
        "percentile": "float",  # Where current stance ranks historically
        "comparison": "str"
    }
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_config() -> List[str]:
    """Validate policy analyzer configuration and return list of issues."""
    issues = []
    
    # Check sentiment thresholds
    sentiment_thresholds = STANCE_CLASSIFICATION["sentiment_thresholds"]
    if sentiment_thresholds["hawkish"] <= sentiment_thresholds["neutral"]:
        issues.append("Hawkish sentiment threshold must be higher than neutral")
    
    if sentiment_thresholds["dovish"] >= sentiment_thresholds["neutral"]:
        issues.append("Dovish sentiment threshold must be lower than neutral")
    
    # Check regime thresholds
    regime_thresholds = REGIME_CHANGE_DETECTION["thresholds"]
    if regime_thresholds["significance"] <= 0 or regime_thresholds["significance"] >= 1:
        issues.append("Significance threshold must be between 0 and 1")
    
    return issues


def get_config_info() -> Dict[str, any]:
    """Get current configuration information."""
    return {
        "sentiment_keywords_count": len(SENTIMENT_KEYWORDS),
        "stance_indicators_count": len(STANCE_CLASSIFICATION["indicators"]),
        "regime_types": list(REGIME_CHANGE_DETECTION["regime_types"].keys()),
        "log_level": LOG_LEVEL
    }


def is_fully_configured() -> bool:
    """Check if policy analyzer is fully configured."""
    issues = validate_config()
    return len(issues) == 0
