"""
Configuration for Treasury Agent

Handles API keys, Treasury/TIPS series IDs, and configuration settings.
Uses FRED API as primary data source for reliability.
"""

import os
import warnings
from dotenv import load_dotenv
from typing import Dict, List

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    warnings.warn(f"Could not load .env file: {e}")

# API Configuration (using FRED API for Treasury data)
FRED_API_KEY = os.getenv("FRED_API_KEY", "")
if FRED_API_KEY and len(FRED_API_KEY) < 30:
    warnings.warn("FRED_API_KEY appears to be invalid (too short).")
elif not FRED_API_KEY:
    warnings.warn(
        "No FRED_API_KEY provided. Get your free API key at: "
        "https://fred.stlouisfed.org/docs/api/api_key.html"
    )

# A2A Server Configuration
A2A_HOST = os.getenv("TREASURY_AGENT_HOST", "0.0.0.0")
A2A_PORT = int(os.getenv("TREASURY_AGENT_PORT", "8003"))

# Validate port range
if not (1024 <= A2A_PORT <= 65535):
    warnings.warn(f"A2A port {A2A_PORT} may not be in valid range (1024-65535)")

# Cache Configuration
CACHE_TTL_SECONDS = 3600  # 1 hour cache
MAX_CACHE_SIZE = 1000

# Async Configuration
ASYNC_TIMEOUT_SECONDS = 30  # HTTP request timeout for async calls
ASYNC_MAX_CONCURRENT_REQUESTS = 20  # Max concurrent API requests

# Rate Limits (FRED API limits)
FRED_RATE_LIMIT_NO_KEY = 120  # 120 requests per minute without key
FRED_RATE_LIMIT_WITH_KEY = 120  # 120 requests per minute with key

# ============================================================================
# TREASURY YIELD SERIES (Nominal)
# ============================================================================

TREASURY_YIELDS: Dict[str, Dict[str, str]] = {
    # Short-term (money market)
    "1m": {
        "series_id": "DGS1MO",
        "name": "1-Month Treasury Constant Maturity Rate",
        "maturity_years": 0.083,
        "category": "short_term"
    },
    "3m": {
        "series_id": "DGS3MO",
        "name": "3-Month Treasury Constant Maturity Rate",
        "maturity_years": 0.25,
        "category": "short_term"
    },
    "6m": {
        "series_id": "DGS6MO",
        "name": "6-Month Treasury Constant Maturity Rate",
        "maturity_years": 0.5,
        "category": "short_term"
    },
    
    # Medium-term
    "1y": {
        "series_id": "DGS1",
        "name": "1-Year Treasury Constant Maturity Rate",
        "maturity_years": 1.0,
        "category": "medium_term"
    },
    "2y": {
        "series_id": "DGS2",
        "name": "2-Year Treasury Constant Maturity Rate",
        "maturity_years": 2.0,
        "category": "medium_term",
        "note": "Key for 2s10s spread (recession indicator)"
    },
    "3y": {
        "series_id": "DGS3",
        "name": "3-Year Treasury Constant Maturity Rate",
        "maturity_years": 3.0,
        "category": "medium_term"
    },
    "5y": {
        "series_id": "DGS5",
        "name": "5-Year Treasury Constant Maturity Rate",
        "maturity_years": 5.0,
        "category": "medium_term",
        "note": "Key for 5-year TIPS breakeven"
    },
    "7y": {
        "series_id": "DGS7",
        "name": "7-Year Treasury Constant Maturity Rate",
        "maturity_years": 7.0,
        "category": "medium_term"
    },
    
    # Long-term
    "10y": {
        "series_id": "DGS10",
        "name": "10-Year Treasury Constant Maturity Rate",
        "maturity_years": 10.0,
        "category": "long_term",
        "note": "Most liquid benchmark, key for 2s10s spread"
    },
    "20y": {
        "series_id": "DGS20",
        "name": "20-Year Treasury Constant Maturity Rate",
        "maturity_years": 20.0,
        "category": "long_term"
    },
    "30y": {
        "series_id": "DGS30",
        "name": "30-Year Treasury Constant Maturity Rate",
        "maturity_years": 30.0,
        "category": "long_term",
        "note": "Long end of curve"
    }
}

# ============================================================================
# TIPS YIELDS (for calculating breakeven inflation)
# ============================================================================

TIPS_YIELDS: Dict[str, Dict[str, str]] = {
    "5y_tips": {
        "series_id": "DFII5",
        "name": "5-Year Treasury Inflation-Indexed Security, Constant Maturity",
        "maturity_years": 5.0,
        "nominal_series": "5y"
    },
    "7y_tips": {
        "series_id": "DFII7",
        "name": "7-Year Treasury Inflation-Indexed Security, Constant Maturity",
        "maturity_years": 7.0,
        "nominal_series": "7y"
    },
    "10y_tips": {
        "series_id": "DFII10",
        "name": "10-Year Treasury Inflation-Indexed Security, Constant Maturity",
        "maturity_years": 10.0,
        "nominal_series": "10y",
        "note": "Most liquid TIPS, widely watched by Fed"
    },
    "20y_tips": {
        "series_id": "DFII20",
        "name": "20-Year Treasury Inflation-Indexed Security, Constant Maturity",
        "maturity_years": 20.0,
        "nominal_series": "20y"
    },
    "30y_tips": {
        "series_id": "DFII30",
        "name": "30-Year Treasury Inflation-Indexed Security, Constant Maturity",
        "maturity_years": 30.0,
        "nominal_series": "30y"
    }
}

# ============================================================================
# BREAKEVEN INFLATION RATES (Pre-calculated by FRED)
# ============================================================================
# These are already calculated: Nominal yield - TIPS yield
# Useful as verification/backup

BREAKEVEN_SERIES: Dict[str, Dict[str, str]] = {
    "5y_breakeven": {
        "series_id": "T5YIE",
        "name": "5-Year Breakeven Inflation Rate",
        "maturity_years": 5.0,
        "note": "Market-implied average inflation over next 5 years"
    },
    "10y_breakeven": {
        "series_id": "T10YIE",
        "name": "10-Year Breakeven Inflation Rate",
        "maturity_years": 10.0,
        "note": "Most widely watched inflation expectation measure"
    },
    "5y5y_forward": {
        "series_id": "T5YIFR",
        "name": "5-Year, 5-Year Forward Inflation Expectation Rate",
        "maturity_years": None,
        "note": "Expected inflation 5-10 years ahead - Fed's anchoring measure"
    }
}

# ============================================================================
# FED FUNDS & POLICY RATES
# ============================================================================

POLICY_RATES: Dict[str, Dict[str, str]] = {
    "fed_funds_effective": {
        "series_id": "FEDFUNDS",
        "name": "Federal Funds Effective Rate",
        "note": "Actual Fed Funds rate"
    },
    "fed_funds_target_upper": {
        "series_id": "DFEDTARU",
        "name": "Federal Funds Target Range - Upper Limit",
        "note": "Fed's target upper bound"
    },
    "fed_funds_target_lower": {
        "series_id": "DFEDTARL",
        "name": "Federal Funds Target Range - Lower Limit",
        "note": "Fed's target lower bound"
    }
}

# ============================================================================
# YIELD CURVE SPREADS (Pre-calculated by FRED)
# ============================================================================

YIELD_SPREADS: Dict[str, Dict[str, str]] = {
    "10y_2y": {
        "series_id": "T10Y2Y",
        "name": "10-Year Treasury Minus 2-Year Treasury",
        "note": "Most watched recession indicator - inversion signals recession"
    },
    "10y_3m": {
        "series_id": "T10Y3M",
        "name": "10-Year Treasury Minus 3-Month Treasury",
        "note": "Alternative recession indicator"
    }
}

# ============================================================================
# YIELD CURVE CONFIGURATIONS
# ============================================================================

# Standard yield curve points for plotting
YIELD_CURVE_MATURITIES = ["1m", "3m", "6m", "1y", "2y", "3y", "5y", "7y", "10y", "20y", "30y"]

# Key spreads for analysis
KEY_SPREADS = {
    "2s10s": {"short": "2y", "long": "10y", "name": "2s10s Spread"},
    "3m10y": {"short": "3m", "long": "10y", "name": "3m10y Spread"},
    "5s30s": {"short": "5y", "long": "30y", "name": "5s30s Spread"}
}

# ============================================================================
# POLICY ANALYSIS THRESHOLDS
# ============================================================================

# Neutral real rate (R-star) estimates
NEUTRAL_REAL_RATE = 0.5  # Current FOMC median estimate
NEUTRAL_REAL_RATE_RANGE = (0.0, 1.0)  # Uncertainty range

# Recession indicator thresholds
INVERSION_THRESHOLD = -0.10  # 10bp inverted = strong recession signal

# Monetary policy stance assessment (based on 10Y real yield)
POLICY_STANCE_THRESHOLDS = {
    "highly_accommodative": -1.0,    # Real yield < -1%
    "accommodative": 0.0,             # Real yield < 0%
    "neutral": NEUTRAL_REAL_RATE,    # Around R-star
    "restrictive": 1.5,              # Real yield > R-star + 1%
    "highly_restrictive": 2.5        # Real yield > R-star + 2%
}

# Inflation expectation assessment (based on 10Y breakeven)
INFLATION_EXPECTATION_THRESHOLDS = {
    "well_anchored": (1.75, 2.25),      # Around Fed's 2% target
    "moderately_anchored": (1.5, 2.75),  # Somewhat elevated but ok
    "de_anchoring": 3.0,                 # Above 3% = concern
    "unanchored": 3.5                    # Above 3.5% = serious concern
}

# Yield curve steepness
CURVE_STEEPNESS_THRESHOLDS = {
    "deeply_inverted": -0.50,    # Very steep inversion
    "inverted": -0.10,           # Mild inversion
    "flat": 0.25,                # Nearly flat
    "normal": 1.0,               # Normal positive slope
    "steep": 2.0                 # Very steep
}

# ============================================================================
# DATA QUALITY NOTES
# ============================================================================

DATA_NOTES = {
    "frequency": "Daily for most series",
    "source": "U.S. Department of Treasury via FRED",
    "updates": "Daily, typically by 6pm ET",
    "holidays": "No data on weekends and federal holidays",
    "tips_note": "TIPS yields can be negative during low inflation/high demand periods",
    "breakeven_interpretation": "Breakeven = nominal yield - TIPS yield = market-implied inflation expectation",
    "real_yield_interpretation": "Real yield = nominal yield - breakeven inflation = inflation-adjusted return"
}

# Default parameters
DEFAULT_START_DATE = "2005-01-01"  # Match FOMC coverage

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_api_info() -> Dict[str, any]:
    """Get current API configuration information."""
    return {
        "has_api_key": bool(FRED_API_KEY),
        "api_key_length": len(FRED_API_KEY) if FRED_API_KEY else 0,
        "host": A2A_HOST,
        "port": A2A_PORT,
        "rate_limit": FRED_RATE_LIMIT_WITH_KEY if FRED_API_KEY else FRED_RATE_LIMIT_NO_KEY
    }


def validate_config() -> List[str]:
    """Validate configuration and return list of issues."""
    issues = []
    
    if not FRED_API_KEY:
        issues.append("No FRED API key provided - API rate limits will apply")
    elif len(FRED_API_KEY) < 30:
        issues.append("FRED API key appears to be invalid (too short)")
    
    if not (1024 <= A2A_PORT <= 65535):
        issues.append(f"A2A port {A2A_PORT} may not be valid (should be 1024-65535)")
    
    return issues


def is_fully_loaded() -> bool:
    """Check if all required configuration is properly loaded."""
    issues = validate_config()
    critical_issues = [issue for issue in issues if "invalid" in issue.lower() or "not be valid" in issue]
    return len(critical_issues) == 0
