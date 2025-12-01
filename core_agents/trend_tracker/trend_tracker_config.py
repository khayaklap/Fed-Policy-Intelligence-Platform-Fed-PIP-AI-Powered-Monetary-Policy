"""
Trend Tracker Configuration

Defines parameters for long-term Fed policy trend analysis, cycle detection,
reaction function analysis, and predictive indicators.
"""

import os
from dotenv import load_dotenv
from typing import Dict, List

# Load environment variables
load_dotenv()

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============================================================================
# TIME HORIZONS
# ============================================================================

# Analysis periods (in number of meetings)
TIME_HORIZONS = {
    "short_term": 6,        # 1.5 years - Policy Analyzer territory
    "medium_term": 12,      # 3 years - Trend Tracker starts here
    "long_term": 24,        # 6 years - Full cycle
    "very_long_term": 40,   # 10 years - Multi-cycle
    "historical": 80        # 20 years - Full dataset
}

# Minimum data requirements
MIN_DATA_REQUIREMENTS = {
    "cycle_detection": 24,      # Need 6+ years for full cycle
    "trend_analysis": 12,       # Need 3+ years for trends
    "reaction_function": 20,    # Need 5+ years for robust estimates
    "forecast_bias": 16         # Need 4+ years for bias patterns
}

# ============================================================================
# POLICY CYCLE DEFINITIONS
# ============================================================================

# Fed policy cycles typically consist of phases
POLICY_CYCLE_PHASES = {
    "expansion_early": {
        "description": "Early recovery, accommodative policy",
        "typical_duration": "1-2 years",
        "characteristics": ["low rates", "dovish", "QE possible"]
    },
    "expansion_mid": {
        "description": "Growth established, policy normalizing",
        "typical_duration": "2-3 years", 
        "characteristics": ["gradual hikes", "neutral shift", "data dependent"]
    },
    "expansion_late": {
        "description": "Economy hot, inflation risk rising",
        "typical_duration": "1-2 years",
        "characteristics": ["continued hikes", "hawkish", "restrictive"]
    },
    "slowdown": {
        "description": "Growth slowing, inflation moderating",
        "typical_duration": "1-2 years",
        "characteristics": ["pause", "neutral to dovish shift", "patient"]
    },
    "recession": {
        "description": "Contraction, aggressive easing",
        "typical_duration": "6 months - 2 years",
        "characteristics": ["rate cuts", "very dovish", "emergency measures"]
    }
}

# Historical Fed cycles (with recession dates from NBER)
HISTORICAL_CYCLES = {
    "dot_com_cycle": {
        "period": ("1999-06-30", "2003-06-25"),
        "description": "Dot-com bubble to recovery",
        "phases": {
            "tightening": ("1999-06-30", "2000-05-16"),  # 175bp hikes
            "recession": ("2001-01-03", "2001-11-30"),   # 475bp cuts
            "recovery": ("2001-12-11", "2003-06-25")     # Accommodative
        },
        "characteristics": ["gradual hikes", "aggressive cuts", "slow recovery"]
    },
    "housing_boom_gfc": {
        "period": ("2004-06-30", "2015-12-16"),
        "description": "Housing boom to GFC recovery",
        "phases": {
            "tightening": ("2004-06-30", "2006-06-29"),  # 425bp hikes
            "pause": ("2006-08-08", "2007-09-18"),
            "crisis": ("2007-09-18", "2008-12-16"),      # 500bp cuts
            "zero_bound": ("2008-12-16", "2015-12-16")   # ZLB + QE
        },
        "characteristics": ["measured pace", "financial crisis", "unconventional policy"]
    },
    "post_gfc_normalization": {
        "period": ("2015-12-16", "2019-10-30"),
        "description": "Post-GFC normalization attempt",
        "phases": {
            "liftoff": ("2015-12-16", "2016-12-14"),     # 25bp + 25bp
            "tightening": ("2017-03-15", "2018-12-19"),  # 200bp hikes
            "pivot": ("2019-01-30", "2019-10-30")        # 75bp cuts
        },
        "characteristics": ["gradual normalization", "balance sheet reduction", "quick pivot"]
    },
    "covid_inflation": {
        "period": ("2020-03-15", "2024-12-31"),
        "description": "COVID crisis to inflation fight",
        "phases": {
            "emergency": ("2020-03-15", "2020-06-10"),   # Emergency cuts
            "support": ("2020-07-29", "2021-11-03"),     # Sustained accommodation
            "pivot": ("2021-11-03", "2022-03-16"),       # Preparing for hikes
            "tightening": ("2022-03-16", "2023-07-26"),  # 525bp hikes
            "pause": ("2023-09-20", "2024-12-31")        # Higher for longer
        },
        "characteristics": ["fastest cuts", "massive QE", "fastest hikes since 1980s"]
    }
}

# Average cycle characteristics
AVERAGE_CYCLE_METRICS = {
    "total_duration": 72,           # 72 meetings (18 years) peak-to-peak
    "tightening_phase": 12,         # 12 meetings (3 years) average
    "easing_phase": 8,              # 8 meetings (2 years) average
    "accommodation_phase": 20,      # 20 meetings (5 years) average
    "rate_change_per_cycle": 500    # 500bp peak-to-trough average
}

# ============================================================================
# TREND DETECTION PARAMETERS
# ============================================================================

# Change point detection settings
CHANGEPOINT_METHODS = {
    "pelt": {
        "penalty": 10,              # Higher = fewer change points
        "min_size": 6,              # Minimum segment size (1.5 years)
        "model": "rbf"              # Radial basis function
    },
    "binseg": {
        "n_bkps": 5,                # Number of breakpoints to find
        "min_size": 6
    },
    "window": {
        "width": 12,                # Rolling window (3 years)
        "model": "l2"               # L2 cost function
    }
}

# Trend strength classification
TREND_STRENGTH = {
    "very_strong": 0.8,     # R² > 0.8
    "strong": 0.6,          # R² > 0.6
    "moderate": 0.4,        # R² > 0.4
    "weak": 0.2,            # R² > 0.2
    "negligible": 0.0       # R² < 0.2
}

# Trend persistence thresholds
PERSISTENCE_THRESHOLDS = {
    "highly_persistent": 24,    # 6+ years same direction
    "persistent": 12,           # 3+ years
    "moderately_persistent": 6, # 1.5+ years
    "transient": 3              # <9 months
}

# ============================================================================
# CYCLE DETECTION PARAMETERS
# ============================================================================

# Periodicity detection (in meetings)
TYPICAL_PERIODICITIES = {
    "short_cycle": (8, 16),     # 2-4 years (short business cycle)
    "medium_cycle": (16, 32),   # 4-8 years (typical business cycle)
    "long_cycle": (32, 64)      # 8-16 years (long wave)
}

# Peak/trough detection settings
PEAK_TROUGH_CONFIG = {
    "prominence": 5,        # Minimum prominence for peak detection
    "distance": 6,          # Minimum distance between peaks (1.5 years)
    "width": 3              # Minimum peak width
}

# Cycle similarity metrics
CYCLE_SIMILARITY_WEIGHTS = {
    "duration": 0.3,            # How long was the cycle
    "amplitude": 0.3,           # How large were rate changes
    "shape": 0.2,               # Similar trajectory
    "economic_context": 0.2     # Similar economic conditions
}

# ============================================================================
# REACTION FUNCTION ANALYSIS
# ============================================================================

# Fed's reaction to economic variables
# Classic Taylor Rule: r = r* + 1.5*(π - π*) + 0.5*(y - y*)
# Where: r = Fed Funds, π = inflation, y = output gap

TAYLOR_RULE_PARAMS = {
    "neutral_rate": 2.5,        # R-star estimate
    "inflation_target": 2.0,    # Fed's target
    "inflation_coefficient": 1.5,   # Taylor's original
    "output_coefficient": 0.5       # Taylor's original
}

# Variables Fed responds to
REACTION_VARIABLES = {
    "inflation": {
        "weight": 0.5,
        "lag": 0,               # Fed responds contemporaneously
        "expected_sign": "positive"  # Higher inflation → higher rates
    },
    "unemployment": {
        "weight": 0.3,
        "lag": 0,
        "expected_sign": "negative"  # Higher unemployment → lower rates
    },
    "gdp_growth": {
        "weight": 0.2,
        "lag": 1,               # Fed responds with 1 meeting lag
        "expected_sign": "positive"  # Higher growth → higher rates
    }
}

# Asymmetry in Fed response
# Fed typically cuts faster than it hikes
ASYMMETRY_PATTERNS = {
    "cutting_speed": 50,        # 50bp average cut per meeting
    "hiking_speed": 25,         # 25bp average hike per meeting
    "cutting_threshold": 0.5,   # Cuts when growth < 0.5%
    "hiking_threshold": 3.0     # Hikes when inflation > 3%
}

# ============================================================================
# FORECAST BIAS TRACKING
# ============================================================================

# Common Fed forecast biases
FORECAST_BIAS_TYPES = {
    "optimism_bias": {
        "description": "Systematically over-predicts growth, under-predicts unemployment",
        "typical_error": "+0.5% GDP, -0.3% unemployment"
    },
    "inflation_underestimation": {
        "description": "Tends to underestimate inflation during shocks",
        "typical_error": "-1.0% to -2.0% during supply shocks"
    },
    "mean_reversion_bias": {
        "description": "Assumes variables return to normal faster than they do",
        "typical_error": "Forecasts converge to longer-run too quickly"
    },
    "recent_bias": {
        "description": "Over-weights recent data (recency bias)",
        "typical_error": "Slow to recognize turning points"
    }
}

# Forecast error thresholds
FORECAST_ERROR_THRESHOLDS = {
    "accurate": 0.5,        # Within 0.5pp
    "moderate": 1.0,        # Within 1.0pp
    "large": 2.0,           # Within 2.0pp
    "very_large": 2.0       # Over 2.0pp
}

# Systematic bias detection
BIAS_DETECTION_CONFIG = {
    "min_observations": 12,     # Need 3+ years
    "significance_level": 0.05, # 5% significance
    "bias_threshold": 0.5       # Mean error > 0.5pp = bias
}

# ============================================================================
# PREDICTIVE INDICATORS
# ============================================================================

# Leading indicators of policy changes
LEADING_INDICATORS = {
    "sentiment_shift": {
        "description": "Change in hawkish/dovish language",
        "lead_time": 2,         # 2 meetings (~6 months) before action
        "threshold": 10,        # 10-point score change
        "reliability": 0.75     # 75% accuracy
    },
    "forecast_revision": {
        "description": "Large revisions to inflation/GDP forecasts",
        "lead_time": 1,         # 1 meeting (~3 months)
        "threshold": 0.5,       # 0.5pp revision
        "reliability": 0.65
    },
    "inflation_persistence": {
        "description": "Inflation above target for 3+ consecutive quarters",
        "lead_time": 3,         # 3 meetings (~9 months) before tightening
        "threshold": 2.5,       # Inflation > 2.5%
        "reliability": 0.80
    },
    "unemployment_gap": {
        "description": "Unemployment significantly below NAIRU",
        "lead_time": 4,         # 4 meetings (~12 months)
        "threshold": 0.5,       # 0.5pp below NAIRU
        "reliability": 0.70
    },
    "yield_curve_inversion": {
        "description": "2y-10y spread negative",
        "lead_time": 6,         # 6 meetings (~18 months) before recession
        "threshold": -0.25,     # Spread < -25bp
        "reliability": 0.85
    }
}

# Indicator combinations (multiple signals)
INDICATOR_COMBINATIONS = {
    "strong_tightening_signal": [
        "sentiment_shift",
        "inflation_persistence",
        "unemployment_gap"
    ],
    "strong_easing_signal": [
        "sentiment_shift",
        "yield_curve_inversion",
        "forecast_revision"
    ]
}

# ============================================================================
# PATTERN RECOGNITION
# ============================================================================

# Common Fed policy patterns
POLICY_PATTERNS = {
    "measured_pace": {
        "description": "Gradual 25bp moves at consecutive meetings",
        "example": "2004-2006 Greenspan",
        "characteristics": [25, 25, 25, 25]  # bp per meeting
    },
    "front_loaded": {
        "description": "Large initial moves, then pause",
        "example": "2022-2023 Powell",
        "characteristics": [50, 75, 75, 75, 50]  # bp per meeting
    },
    "emergency_cuts": {
        "description": "Rapid, large cuts",
        "example": "2008 GFC, 2020 COVID",
        "characteristics": [50, 75, 50]  # bp per meeting or inter-meeting
    },
    "skip_and_hike": {
        "description": "Pause to assess, then resume",
        "example": "2023 June pause",
        "characteristics": [25, 0, 25, 0, 25]
    }
}

# ============================================================================
# GRANGER CAUSALITY SETTINGS
# ============================================================================

# Test if variable X "Granger causes" variable Y
# i.e., Does past X help predict Y?
GRANGER_CONFIG = {
    "max_lags": 4,              # Test up to 4 meetings lag
    "significance": 0.05,       # 5% significance level
    "test_pairs": [
        ("inflation", "fed_funds"),
        ("unemployment", "fed_funds"),
        ("sentiment_score", "fed_funds"),
        ("gdp_growth", "fed_funds")
    ]
}

# ============================================================================
# VISUALIZATION SETTINGS
# ============================================================================

VIZ_CONFIG = {
    "figure_size": (14, 8),
    "dpi": 100,
    "style": "seaborn-v0_8-whitegrid",
    "colors": {
        "cycle_phase": {
            "expansion_early": "#2ecc71",
            "expansion_mid": "#f39c12",
            "expansion_late": "#e74c3c",
            "slowdown": "#95a5a6",
            "recession": "#34495e"
        },
        "trend": {
            "hawkish": "#d62728",
            "dovish": "#2ca02c",
            "neutral": "#7f7f7f"
        }
    }
}

# ============================================================================
# OUTPUT SCHEMA
# ============================================================================

TREND_ANALYSIS_SCHEMA = {
    "long_term_trend": {
        "direction": "str",         # hawkish_trend, dovish_trend, cyclical
        "strength": "str",          # very_strong, strong, moderate, weak
        "duration": "int",          # Meetings in trend
        "changepoints": "list",     # Detected turning points
        "r_squared": "float"        # Trend fit quality
    },
    "current_cycle": {
        "phase": "str",             # expansion_early, mid, late, slowdown, recession
        "duration": "int",          # Meetings in current phase
        "similar_historical": "list",
        "expected_next_phase": "str"
    },
    "reaction_function": {
        "inflation_sensitivity": "float",
        "unemployment_sensitivity": "float",
        "asymmetry": "str",         # cuts_faster, hikes_faster, symmetric
        "taylor_rule_deviation": "float"
    },
    "forecast_bias": {
        "systematic_bias": "bool",
        "bias_type": "str",         # optimism, pessimism, inflation_under
        "mean_error": "float",
        "confidence": "float"
    },
    "predictive_signals": {
        "active_indicators": "list",
        "predicted_action": "str",  # hike, cut, unchanged
        "confidence": "float",
        "time_horizon": "int"       # Meetings until action
    }
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_config() -> List[str]:
    """Validate trend tracker configuration and return list of issues."""
    issues = []
    
    # Check analysis periods
    for period_name, period_data in ANALYSIS_PERIODS.items():
        if period_data["years"] <= 0:
            issues.append(f"Analysis period {period_name} must have positive years")
    
    # Check cycle thresholds
    cycle_thresholds = CYCLE_DETECTION["thresholds"]
    if cycle_thresholds["significance"] <= 0 or cycle_thresholds["significance"] >= 1:
        issues.append("Cycle significance threshold must be between 0 and 1")
    
    return issues


def get_config_info() -> Dict[str, any]:
    """Get current configuration information."""
    return {
        "analysis_periods": list(ANALYSIS_PERIODS.keys()),
        "pattern_types": list(PATTERN_DETECTION["types"].keys()),
        "cycle_indicators": list(CYCLE_DETECTION["indicators"].keys()),
        "historical_benchmarks": list(HISTORICAL_BENCHMARKS.keys()),
        "log_level": LOG_LEVEL
    }


def is_fully_configured() -> bool:
    """Check if trend tracker is fully configured."""
    issues = validate_config()
    return len(issues) == 0
