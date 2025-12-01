"""
Comparative Analyzer Configuration

Defines Fed policy episodes, comparison dimensions, similarity metrics,
and pattern recognition parameters.
"""

import os
from dotenv import load_dotenv
from typing import Dict, List, Tuple

# Load environment variables
load_dotenv()

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============================================================================
# NOTABLE FED POLICY EPISODES
# ============================================================================

# Major Fed policy episodes for comparison
POLICY_EPISODES = {
    "volcker_disinflation_1979_1982": {
        "name": "Volcker Disinflation",
        "period": ("1979-08-01", "1982-12-31"),
        "chair": "Paul Volcker",
        "context": "Breaking double-digit inflation",
        "key_features": {
            "peak_rate": 20.0,
            "rate_change": 1100,  # basis points
            "duration_months": 40,
            "recession": True,
            "inflation_start": 11.3,
            "inflation_end": 3.8,
            "unemployment_peak": 10.8
        },
        "characteristics": ["very_aggressive", "recession_tolerated", "inflation_priority"],
        "outcome": "Successful disinflation but severe recession"
    },
    
    "greenspan_1987_crisis": {
        "name": "1987 Stock Market Crash Response",
        "period": ("1987-10-19", "1988-03-31"),
        "chair": "Alan Greenspan",
        "context": "Black Monday - 22% stock market crash",
        "key_features": {
            "rate_change": -50,
            "duration_months": 5,
            "recession": False,
            "stock_drop": -22.6
        },
        "characteristics": ["swift_response", "liquidity_support", "greenspan_put"],
        "outcome": "Soft landing, no recession"
    },
    
    "dotcom_tightening_1999_2000": {
        "name": "Dot-com Bubble Tightening",
        "period": ("1999-06-30", "2000-05-16"),
        "chair": "Alan Greenspan",
        "context": "Preventing tech bubble overheating",
        "key_features": {
            "peak_rate": 6.5,
            "rate_change": 175,
            "duration_months": 11,
            "recession": False  # Bubble burst anyway
        },
        "characteristics": ["gradual_hikes", "bubble_concerns", "asymmetric_easing"],
        "outcome": "Bubble burst despite tightening"
    },
    
    "dotcom_bust_easing_2001": {
        "name": "Dot-com Bust & 9/11 Response",
        "period": ("2001-01-03", "2003-06-25"),
        "chair": "Alan Greenspan",
        "context": "Recession + 9/11 attacks",
        "key_features": {
            "rate_change": -475,
            "duration_months": 30,
            "recession": True,
            "rate_low": 1.0
        },
        "characteristics": ["aggressive_cuts", "post_911_support", "prolonged_ease"],
        "outcome": "Recovery by 2003"
    },
    
    "housing_boom_tightening_2004_2006": {
        "name": "Housing Boom Normalization",
        "period": ("2004-06-30", "2006-06-29"),
        "chair": "Alan Greenspan / Ben Bernanke",
        "context": "Normalizing after dot-com bust",
        "key_features": {
            "peak_rate": 5.25,
            "rate_change": 425,
            "duration_months": 24,
            "num_hikes": 17,
            "hike_size": 25  # Every meeting
        },
        "characteristics": ["measured_pace", "telegraphed", "17_consecutive_hikes"],
        "outcome": "Housing bubble built up"
    },
    
    "gfc_response_2007_2008": {
        "name": "Great Financial Crisis Response",
        "period": ("2007-09-18", "2008-12-16"),
        "chair": "Ben Bernanke",
        "context": "Financial system collapse",
        "key_features": {
            "rate_change": -500,
            "duration_months": 15,
            "recession": True,
            "rate_low": 0.00,  # Zero lower bound
            "unemployment_peak": 10.0,
            "qe": True
        },
        "characteristics": ["emergency_cuts", "zero_bound", "unconventional_policy", "QE"],
        "outcome": "Financial system stabilized"
    },
    
    "gfc_recovery_2009_2015": {
        "name": "GFC Recovery - Zero Bound Era",
        "period": ("2009-01-01", "2015-12-15"),
        "chair": "Ben Bernanke / Janet Yellen",
        "context": "Prolonged accommodation at zero",
        "key_features": {
            "rate": 0.00,
            "duration_months": 84,  # 7 years
            "qe_rounds": 3,
            "balance_sheet_peak": 4500  # billions
        },
        "characteristics": ["zero_bound", "QE1_QE2_QE3", "forward_guidance", "patient"],
        "outcome": "Slow but steady recovery"
    },
    
    "normalization_2015_2018": {
        "name": "Post-GFC Normalization",
        "period": ("2015-12-16", "2018-12-19"),
        "chair": "Janet Yellen / Jerome Powell",
        "context": "Gradual normalization",
        "key_features": {
            "peak_rate": 2.50,
            "rate_change": 225,
            "duration_months": 36,
            "num_hikes": 9,
            "balance_sheet_reduction": True
        },
        "characteristics": ["gradual", "data_dependent", "balance_sheet_runoff"],
        "outcome": "Paused then pivoted to cuts"
    },
    
    "2019_pivot": {
        "name": "2019 Mid-Cycle Adjustment",
        "period": ("2019-01-30", "2019-10-30"),
        "chair": "Jerome Powell",
        "context": "Growth concerns, trade war",
        "key_features": {
            "rate_change": -75,
            "num_cuts": 3,
            "duration_months": 9
        },
        "characteristics": ["insurance_cuts", "mid_cycle_adjustment", "dovish_pivot"],
        "outcome": "Soft landing achieved"
    },
    
    "covid_response_2020": {
        "name": "COVID-19 Emergency Response",
        "period": ("2020-03-03", "2020-04-29"),
        "chair": "Jerome Powell",
        "context": "Pandemic, economic shutdown",
        "key_features": {
            "rate_change": -150,
            "duration_days": 13,  # Fastest ever
            "rate_low": 0.00,
            "emergency_meetings": 2,
            "qe": "unlimited"
        },
        "characteristics": ["fastest_ever", "emergency_action", "unlimited_QE", "whatever_it_takes"],
        "outcome": "Financial markets stabilized quickly"
    },
    
    "covid_recovery_2020_2021": {
        "name": "COVID Recovery - Extended Ease",
        "period": ("2020-06-01", "2021-11-03"),
        "chair": "Jerome Powell",
        "context": "Supporting recovery",
        "key_features": {
            "rate": 0.00,
            "duration_months": 17,
            "qe_pace": 120,  # billions per month
            "forward_guidance": "transitory_inflation"
        },
        "characteristics": ["patient", "transitory_view", "maximum_employment_focus"],
        "outcome": "Strong recovery but inflation surge"
    },
    
    "inflation_fight_2022_2023": {
        "name": "2022-2023 Inflation Fight",
        "period": ("2022-03-16", "2023-07-26"),
        "chair": "Jerome Powell",
        "context": "Highest inflation since 1980s",
        "key_features": {
            "peak_rate": 5.50,
            "rate_change": 525,
            "duration_months": 16,
            "num_hikes": 11,
            "max_hike": 75,  # 4 consecutive 75bp hikes
            "inflation_peak": 9.1
        },
        "characteristics": ["fastest_since_volcker", "front_loaded", "75bp_hikes", "data_dependent"],
        "outcome": "Inflation declining, no recession (yet)"
    },
    
    "higher_for_longer_2023_2024": {
        "name": "Higher for Longer",
        "period": ("2023-09-20", "2024-12-31"),
        "chair": "Jerome Powell",
        "context": "Maintaining restrictive stance",
        "key_features": {
            "rate": 5.50,
            "duration_months": 15,
            "stance": "restrictive"
        },
        "characteristics": ["patient", "data_dependent", "restrictive_stance"],
        "outcome": "TBD - ongoing"
    }
}

# ============================================================================
# COMPARISON DIMENSIONS
# ============================================================================

# Dimensions for comparing episodes
COMPARISON_DIMENSIONS = {
    "speed": {
        "description": "How quickly Fed acted",
        "metrics": ["rate_change_per_month", "time_to_peak", "emergency_meetings"],
        "weight": 0.20
    },
    "magnitude": {
        "description": "Size of policy response",
        "metrics": ["total_rate_change", "peak_rate", "qe_amount"],
        "weight": 0.25
    },
    "duration": {
        "description": "How long episode lasted",
        "metrics": ["duration_months", "time_at_peak", "persistence"],
        "weight": 0.15
    },
    "economic_context": {
        "description": "Similar economic conditions",
        "metrics": ["inflation", "unemployment", "gdp_growth", "recession"],
        "weight": 0.20
    },
    "policy_tools": {
        "description": "Tools used",
        "metrics": ["conventional", "qe", "forward_guidance", "emergency_facilities"],
        "weight": 0.10
    },
    "outcome": {
        "description": "Results achieved",
        "metrics": ["soft_landing", "recession", "inflation_controlled", "financial_stability"],
        "weight": 0.10
    }
}

# ============================================================================
# SIMILARITY METRICS
# ============================================================================

# Methods for calculating episode similarity
SIMILARITY_METHODS = {
    "euclidean": {
        "description": "Euclidean distance in feature space",
        "normalize": True,
        "best_for": "Overall similarity"
    },
    "cosine": {
        "description": "Cosine similarity of feature vectors",
        "normalize": False,
        "best_for": "Pattern similarity regardless of scale"
    },
    "dtw": {
        "description": "Dynamic Time Warping - temporal alignment",
        "normalize": True,
        "best_for": "Time series with different lengths"
    },
    "correlation": {
        "description": "Pearson correlation",
        "normalize": False,
        "best_for": "Co-movement patterns"
    }
}

# Similarity thresholds
SIMILARITY_THRESHOLDS = {
    "very_similar": 0.85,       # >85% similar
    "similar": 0.70,            # 70-85% similar
    "somewhat_similar": 0.50,   # 50-70% similar
    "dissimilar": 0.50          # <50% similar
}

# ============================================================================
# FED CHAIRS COMPARISON
# ============================================================================

# Fed Chairs and their tenures
FED_CHAIRS = {
    "paul_volcker": {
        "name": "Paul Volcker",
        "tenure": ("1979-08-06", "1987-08-11"),
        "notable_for": ["Breaking inflation", "Aggressive tightening", "Recession tolerance"],
        "style": "Decisive, inflation hawk, willing to inflict pain",
        "key_episodes": ["volcker_disinflation_1979_1982"]
    },
    "alan_greenspan": {
        "name": "Alan Greenspan",
        "tenure": ("1987-08-11", "2006-01-31"),
        "notable_for": ["Long tenure", "Asymmetric easing", "Measured pace", "Greenspan put"],
        "style": "Data-dependent, gradual, Fed put originator",
        "key_episodes": [
            "greenspan_1987_crisis",
            "dotcom_tightening_1999_2000",
            "dotcom_bust_easing_2001",
            "housing_boom_tightening_2004_2006"
        ]
    },
    "ben_bernanke": {
        "name": "Ben Bernanke",
        "tenure": ("2006-02-01", "2014-01-31"),
        "notable_for": ["GFC response", "QE pioneer", "Unconventional tools"],
        "style": "Academic, innovative, willing to experiment",
        "key_episodes": [
            "housing_boom_tightening_2004_2006",  # Inherited
            "gfc_response_2007_2008",
            "gfc_recovery_2009_2015"
        ]
    },
    "janet_yellen": {
        "name": "Janet Yellen",
        "tenure": ("2014-02-03", "2018-02-03"),
        "notable_for": ["Patient normalization", "Labor market focus", "Gradual hikes"],
        "style": "Cautious, labor-focused, gradual",
        "key_episodes": [
            "gfc_recovery_2009_2015",  # Continued
            "normalization_2015_2018"
        ]
    },
    "jerome_powell": {
        "name": "Jerome Powell",
        "tenure": ("2018-02-05", "present"),
        "notable_for": ["COVID response", "Inflation fight", "Communication clarity"],
        "style": "Pragmatic, clear communicator, data-dependent",
        "key_episodes": [
            "normalization_2015_2018",  # Continued
            "2019_pivot",
            "covid_response_2020",
            "covid_recovery_2020_2021",
            "inflation_fight_2022_2023",
            "higher_for_longer_2023_2024"
        ]
    }
}

# ============================================================================
# PATTERN TYPES
# ============================================================================

# Common Fed policy patterns to identify
PATTERN_TYPES = {
    "v_shaped_response": {
        "description": "Rapid cuts followed by rapid hikes",
        "examples": ["2020 COVID"],
        "signature": "Sharp down, sharp up"
    },
    "gradual_tightening": {
        "description": "Slow, steady rate increases",
        "examples": ["2004-2006", "2015-2018"],
        "signature": "25bp every other meeting"
    },
    "emergency_easing": {
        "description": "Fast, large cuts during crisis",
        "examples": ["2008 GFC", "2020 COVID"],
        "signature": "Multiple 50-75bp cuts"
    },
    "extended_pause": {
        "description": "Long period at same rate",
        "examples": ["2009-2015 zero bound"],
        "signature": "Unchanged for 12+ meetings"
    },
    "pivot": {
        "description": "Sharp reversal in policy direction",
        "examples": ["2019 mid-cycle", "2021-2022"],
        "signature": "From hikes to cuts or vice versa"
    },
    "overshooting": {
        "description": "Fed goes too far, then reverses",
        "examples": ["2018 over-tightening"],
        "signature": "Peak then quick reversal"
    }
}

# ============================================================================
# LESSON CATEGORIES
# ============================================================================

# Categorize lessons learned from episodes
LESSON_CATEGORIES = {
    "timing": {
        "description": "When to act",
        "key_lessons": [
            "Act early for inflation (1970s lesson)",
            "Act big and fast in crisis (GFC, COVID)",
            "Don't tighten into weakness (2018)"
        ]
    },
    "magnitude": {
        "description": "How much to move",
        "key_lessons": [
            "Front-load when behind curve (2022)",
            "Gradual when uncertain (2015-2018)",
            "Unlimited firepower in crisis (COVID)"
        ]
    },
    "communication": {
        "description": "How to signal",
        "key_lessons": [
            "Forward guidance critical (post-GFC)",
            "'Transitory' mistake (2021)",
            "Clear communication reduces volatility"
        ]
    },
    "tools": {
        "description": "Which tools to use",
        "key_lessons": [
            "QE works at zero bound (GFC)",
            "Conventional tools preferred when available",
            "Emergency facilities for financial stress"
        ]
    },
    "mistakes": {
        "description": "What went wrong",
        "key_lessons": [
            "Too slow to recognize inflation (2021)",
            "Tightened too much (2018)",
            "Not aggressive enough (1970s)"
        ]
    }
}

# ============================================================================
# COMPARATIVE METRICS
# ============================================================================

# Metrics for comparing episodes quantitatively
COMPARATIVE_METRICS = {
    "policy_response_index": {
        "formula": "(rate_change / duration) * urgency_factor",
        "description": "Speed and size of response",
        "higher_is": "more_aggressive"
    },
    "effectiveness_score": {
        "formula": "(outcome_quality * 100) / (economic_cost + volatility)",
        "description": "Results achieved vs costs",
        "higher_is": "more_effective"
    },
    "similarity_score": {
        "formula": "weighted_average(dimension_similarities)",
        "description": "Overall similarity between episodes",
        "range": (0, 1)
    }
}

# ============================================================================
# INTERNATIONAL COMPARISONS
# ============================================================================

# Other central banks for comparison
CENTRAL_BANKS = {
    "ecb": {
        "name": "European Central Bank",
        "notable_episodes": ["eurozone_crisis", "negative_rates", "ltro"],
        "key_differences": ["Multiple countries", "Negative rates", "LTRO tool"]
    },
    "boj": {
        "name": "Bank of Japan",
        "notable_episodes": ["lost_decades", "yield_curve_control"],
        "key_differences": ["Persistent deflation", "Yield curve control", "30+ years low rates"]
    },
    "boe": {
        "name": "Bank of England",
        "notable_episodes": ["brexit_response", "inflation_surge"],
        "key_differences": ["Brexit impact", "Sterling concerns", "Similar to Fed"]
    }
}

# ============================================================================
# VISUALIZATION SETTINGS
# ============================================================================

VIZ_CONFIG = {
    "comparison_chart": {
        "type": "radar",  # Radar chart for multi-dimensional comparison
        "dimensions": 6,
        "figure_size": (10, 10)
    },
    "timeline_chart": {
        "type": "line",
        "figure_size": (14, 6),
        "overlay": True  # Multiple episodes on same chart
    },
    "similarity_matrix": {
        "type": "heatmap",
        "colormap": "RdYlGn",
        "figure_size": (12, 10)
    }
}

# ============================================================================
# OUTPUT SCHEMA
# ============================================================================

COMPARISON_SCHEMA = {
    "episode_comparison": {
        "episode1": "str",
        "episode2": "str",
        "overall_similarity": "float",
        "dimension_scores": "dict",
        "key_similarities": "list",
        "key_differences": "list",
        "lessons": "list"
    },
    "pattern_match": {
        "current_episode": "str",
        "matched_patterns": "list",
        "confidence": "float",
        "implications": "str"
    },
    "chair_comparison": {
        "chair1": "str",
        "chair2": "str",
        "style_differences": "list",
        "effectiveness": "dict",
        "notable_episodes": "dict"
    }
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_config() -> List[str]:
    """Validate comparative analyzer configuration and return list of issues."""
    issues = []
    
    # Check similarity thresholds
    similarity_thresholds = SIMILARITY_CALCULATION["thresholds"]
    if similarity_thresholds["high"] <= similarity_thresholds["medium"]:
        issues.append("High similarity threshold must be greater than medium")
    
    if similarity_thresholds["medium"] <= similarity_thresholds["low"]:
        issues.append("Medium similarity threshold must be greater than low")
    
    # Check episode weights
    weights = EPISODE_MATCHING["weights"]
    total_weight = sum(weights.values())
    if abs(total_weight - 1.0) > 0.01:
        issues.append(f"Episode matching weights should sum to 1.0, got {total_weight}")
    
    return issues


def get_config_info() -> Dict[str, any]:
    """Get current configuration information."""
    return {
        "comparison_metrics": list(COMPARISON_METRICS.keys()),
        "historical_episodes": list(HISTORICAL_EPISODES.keys()),
        "similarity_methods": list(SIMILARITY_CALCULATION["methods"].keys()),
        "log_level": LOG_LEVEL
    }


def is_fully_configured() -> bool:
    """Check if comparative analyzer is fully configured."""
    issues = validate_config()
    return len(issues) == 0
