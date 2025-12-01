"""
FRED Agent

Federal Reserve Economic Data integration agent.
"""

__version__ = "1.0.0"

# Handle relative imports for package usage and absolute for direct execution
try:
    # Import main components for easier external access
    from .fred_agent import create_fred_agent, run_a2a_server
    from .fred_api_wrapper import FREDAPIWrapper, get_fred_wrapper
    from .fred_config import (
        FRED_SERIES_MAP, 
        INDICATOR_CATEGORIES, 
        A2A_HOST, 
        A2A_PORT,
        CACHE_TTL_SECONDS,
        MAX_CACHE_SIZE,
        ASYNC_TIMEOUT_SECONDS,
        ASYNC_MAX_CONCURRENT_REQUESTS,
        FRED_RATE_LIMIT_NO_KEY,
        FRED_RATE_LIMIT_WITH_KEY,
        get_api_info,
        validate_config,
        is_fully_loaded
    )

    # Import all tool functions
    from .fred_tools import (
        get_gdp_data,
        get_inflation_data,
        get_employment_data,
        get_interest_rates,
        get_economic_snapshot,
        compare_to_fed_projection
    )
except ImportError:
    # Fallback for direct execution
    from fred_agent import create_fred_agent, run_a2a_server
    from fred_api_wrapper import FREDAPIWrapper, get_fred_wrapper
    from fred_config import (
        FRED_SERIES_MAP, 
        INDICATOR_CATEGORIES, 
        A2A_HOST, 
        A2A_PORT,
        CACHE_TTL_SECONDS,
        MAX_CACHE_SIZE,
        ASYNC_TIMEOUT_SECONDS,
        ASYNC_MAX_CONCURRENT_REQUESTS,
        FRED_RATE_LIMIT_NO_KEY,
        FRED_RATE_LIMIT_WITH_KEY,
        get_api_info,
        validate_config,
        is_fully_loaded
    )

    from fred_tools import (
        get_gdp_data,
        get_inflation_data,
        get_employment_data,
        get_interest_rates,
        get_economic_snapshot,
        compare_to_fed_projection
    )

__all__ = [
    # Main agent components
    "create_fred_agent",
    "run_a2a_server",

    # API wrapper
    "FREDAPIWrapper",
    "get_fred_wrapper",

    # Configuration
    "FRED_SERIES_MAP",
    "INDICATOR_CATEGORIES",
    "A2A_HOST",
    "A2A_PORT",
    "CACHE_TTL_SECONDS",
    "MAX_CACHE_SIZE",
    "ASYNC_TIMEOUT_SECONDS",
    "ASYNC_MAX_CONCURRENT_REQUESTS",
    "FRED_RATE_LIMIT_NO_KEY",
    "FRED_RATE_LIMIT_WITH_KEY",
    "get_api_info",
    "validate_config",
    "is_fully_loaded",

    # Tool functions
    "get_gdp_data",
    "get_inflation_data",
    "get_employment_data",
    "get_interest_rates",
    "get_economic_snapshot",
    "compare_to_fed_projection"
]