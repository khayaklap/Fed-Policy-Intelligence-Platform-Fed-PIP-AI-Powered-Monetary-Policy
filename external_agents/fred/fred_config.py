"""
Configuration for FRED Agent

Handles API keys, constants, and configuration settings.
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

# API Configuration
FRED_API_KEY = os.getenv("FRED_API_KEY", "")
if FRED_API_KEY and len(FRED_API_KEY) < 30:
    warnings.warn("FRED_API_KEY appears to be invalid (too short).")
elif not FRED_API_KEY:
    warnings.warn(
        "No FRED_API_KEY provided. Get your free API key at: "
        "https://fred.stlouisfed.org/docs/api/api_key.html"
    )

# A2A Server Configuration
A2A_HOST = os.getenv("FRED_AGENT_HOST", "0.0.0.0")
A2A_PORT = int(os.getenv("FRED_AGENT_PORT", "8001"))

# Validate port range
if not (1024 <= A2A_PORT <= 65535):
    warnings.warn(f"A2A port {A2A_PORT} may not be in valid range (1024-65535)")

# Cache Configuration
CACHE_TTL_SECONDS = 3600  # 1 hour cache for FRED data
MAX_CACHE_SIZE = 1000

# Async Configuration
ASYNC_TIMEOUT_SECONDS = 30  # HTTP request timeout for async calls
ASYNC_MAX_CONCURRENT_REQUESTS = 20  # Max concurrent API requests

# Rate Limits (FRED API limits)
FRED_RATE_LIMIT_NO_KEY = 120  # 120 requests per minute without key
FRED_RATE_LIMIT_WITH_KEY = 120  # 120 requests per minute with key
RATE_LIMIT_CALLS = 120  # Legacy constant for backward compatibility
RATE_LIMIT_PERIOD = 60  # seconds

# FRED Series IDs - Official series from FRED database
FRED_SERIES_MAP: Dict[str, Dict[str, str]] = {
    # GDP & Growth
    "gdp_real": {
        "series_id": "GDPC1",
        "name": "Real Gross Domestic Product",
        "units": "Billions of Chained 2017 Dollars",
        "frequency": "Quarterly"
    },
    "gdp_nominal": {
        "series_id": "GDP",
        "name": "Gross Domestic Product",
        "units": "Billions of Dollars",
        "frequency": "Quarterly"
    },
    "gdp_growth": {
        "series_id": "A191RL1Q225SBEA",
        "name": "Real GDP Growth Rate",
        "units": "Percent Change from Preceding Period",
        "frequency": "Quarterly"
    },
    
    # Inflation Measures
    "pce": {
        "series_id": "PCEPI",
        "name": "Personal Consumption Expenditures Price Index",
        "units": "Index 2017=100",
        "frequency": "Monthly"
    },
    "pce_core": {
        "series_id": "PCEPILFE",
        "name": "Personal Consumption Expenditures Excluding Food and Energy (Core PCE)",
        "units": "Index 2017=100",
        "frequency": "Monthly"
    },
    "cpi": {
        "series_id": "CPIAUCSL",
        "name": "Consumer Price Index for All Urban Consumers: All Items",
        "units": "Index 1982-84=100",
        "frequency": "Monthly"
    },
    "cpi_core": {
        "series_id": "CPILFESL",
        "name": "Consumer Price Index for All Urban Consumers: All Items Less Food and Energy",
        "units": "Index 1982-84=100",
        "frequency": "Monthly"
    },
    
    # Employment & Labor Market
    "unemployment": {
        "series_id": "UNRATE",
        "name": "Unemployment Rate",
        "units": "Percent",
        "frequency": "Monthly"
    },
    "nonfarm_payrolls": {
        "series_id": "PAYEMS",
        "name": "All Employees, Total Nonfarm",
        "units": "Thousands of Persons",
        "frequency": "Monthly"
    },
    "labor_force_participation": {
        "series_id": "CIVPART",
        "name": "Labor Force Participation Rate",
        "units": "Percent",
        "frequency": "Monthly"
    },
    "average_hourly_earnings": {
        "series_id": "CES0500000003",
        "name": "Average Hourly Earnings of All Employees, Total Private",
        "units": "Dollars per Hour",
        "frequency": "Monthly"
    },
    
    # Interest Rates
    "fed_funds": {
        "series_id": "FEDFUNDS",
        "name": "Federal Funds Effective Rate",
        "units": "Percent",
        "frequency": "Monthly"
    },
    "treasury_10y": {
        "series_id": "DGS10",
        "name": "10-Year Treasury Constant Maturity Rate",
        "units": "Percent",
        "frequency": "Daily"
    },
    "treasury_2y": {
        "series_id": "DGS2",
        "name": "2-Year Treasury Constant Maturity Rate",
        "units": "Percent",
        "frequency": "Daily"
    },
    "treasury_3m": {
        "series_id": "DGS3MO",
        "name": "3-Month Treasury Constant Maturity Rate",
        "units": "Percent",
        "frequency": "Daily"
    },
    
    # Monetary Aggregates
    "m2": {
        "series_id": "M2SL",
        "name": "M2 Money Stock",
        "units": "Billions of Dollars",
        "frequency": "Monthly"
    },
    "bank_reserves": {
        "series_id": "TOTRESNS",
        "name": "Total Reserves of Depository Institutions",
        "units": "Billions of Dollars",
        "frequency": "Monthly"
    },
    
    # Housing
    "housing_starts": {
        "series_id": "HOUST",
        "name": "Housing Starts: Total: New Privately Owned Housing Units Started",
        "units": "Thousands of Units",
        "frequency": "Monthly"
    },
    "home_sales": {
        "series_id": "HSN1F",
        "name": "New One Family Houses Sold: United States",
        "units": "Thousands",
        "frequency": "Monthly"
    },
    "case_shiller": {
        "series_id": "CSUSHPINSA",
        "name": "S&P/Case-Shiller U.S. National Home Price Index",
        "units": "Index Jan 2000=100",
        "frequency": "Monthly"
    },
    
    # Consumer Sentiment
    "consumer_sentiment": {
        "series_id": "UMCSENT",
        "name": "University of Michigan: Consumer Sentiment",
        "units": "Index 1966:Q1=100",
        "frequency": "Monthly"
    },
    "consumer_confidence": {
        "series_id": "CSCICP03USM665S",
        "name": "Consumer Opinion Surveys: Confidence Indicators: Composite Indicators",
        "units": "Index",
        "frequency": "Monthly"
    }
}

# Indicator Categories for grouped queries
INDICATOR_CATEGORIES: Dict[str, List[str]] = {
    "inflation": ["pce", "pce_core", "cpi", "cpi_core"],
    "growth": ["gdp_real", "gdp_nominal", "gdp_growth"],
    "employment": ["unemployment", "nonfarm_payrolls", "labor_force_participation", "average_hourly_earnings"],
    "interest_rates": ["fed_funds", "treasury_10y", "treasury_2y", "treasury_3m"],
    "monetary": ["m2", "bank_reserves"],
    "housing": ["housing_starts", "home_sales", "case_shiller"],
    "sentiment": ["consumer_sentiment", "consumer_confidence"]
}

# Default date ranges
DEFAULT_START_DATE = "2005-01-01"  # Match FOMC document coverage

# API Rate Limits
# FRED API: 120 requests per minute for registered users
RATE_LIMIT_CALLS = 120
RATE_LIMIT_PERIOD = 60  # seconds

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
