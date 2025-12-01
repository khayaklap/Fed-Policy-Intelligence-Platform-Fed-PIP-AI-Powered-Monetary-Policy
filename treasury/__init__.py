"""
Treasury Agent

US Treasury Department data integration agent.
"""

__version__ = "1.0.0"

# Handle relative imports for package usage and absolute for direct execution
try:
    # Import main components for easier external access
    from .treasury_agent import create_treasury_agent, run_a2a_server
    from .treasury_api_wrapper import TreasuryAPIWrapper, get_treasury_wrapper
    from .treasury_config import (
        TREASURY_YIELDS,
        TIPS_YIELDS,
        BREAKEVEN_SERIES,
        YIELD_CURVE_MATURITIES,
        A2A_HOST,
        A2A_PORT,
        ASYNC_TIMEOUT_SECONDS,
        ASYNC_MAX_CONCURRENT_REQUESTS,
        FRED_RATE_LIMIT_NO_KEY,
        FRED_RATE_LIMIT_WITH_KEY,
        get_api_info,
        validate_config,
        is_fully_loaded
    )

    # Import all tool functions
    from .treasury_tools import (
        get_yield_curve_data,
        get_market_inflation_expectations,
        analyze_monetary_policy_stance,
        detect_yield_curve_inversion,
        compare_fed_forecast_vs_market,
        get_yield_curve_evolution
    )
except ImportError:
    # Fallback for direct execution
    from treasury_agent import create_treasury_agent, run_a2a_server
    from treasury_api_wrapper import TreasuryAPIWrapper, get_treasury_wrapper
    from treasury_config import (
        TREASURY_YIELDS,
        TIPS_YIELDS,
        BREAKEVEN_SERIES,
        YIELD_CURVE_MATURITIES,
        A2A_HOST,
        A2A_PORT,
        ASYNC_TIMEOUT_SECONDS,
        ASYNC_MAX_CONCURRENT_REQUESTS,
        FRED_RATE_LIMIT_NO_KEY,
        FRED_RATE_LIMIT_WITH_KEY,
        get_api_info,
        validate_config,
        is_fully_loaded
    )

    from treasury_tools import (
        get_yield_curve_data,
        get_market_inflation_expectations,
        analyze_monetary_policy_stance,
        detect_yield_curve_inversion,
        compare_fed_forecast_vs_market,
        get_yield_curve_evolution
    )

__all__ = [
    # Main agent components
    "create_treasury_agent",
    "run_a2a_server",

    # API wrapper
    "TreasuryAPIWrapper",
    "get_treasury_wrapper",

    # Configuration
    "TREASURY_YIELDS",
    "TIPS_YIELDS",
    "BREAKEVEN_SERIES",
    "YIELD_CURVE_MATURITIES",
    "A2A_HOST",
    "A2A_PORT",
    "ASYNC_TIMEOUT_SECONDS",
    "ASYNC_MAX_CONCURRENT_REQUESTS",
    "FRED_RATE_LIMIT_NO_KEY",
    "FRED_RATE_LIMIT_WITH_KEY",
    "get_api_info",
    "validate_config",
    "is_fully_loaded",

    # Tool functions
    "get_yield_curve_data",
    "get_market_inflation_expectations",
    "analyze_monetary_policy_stance",
    "detect_yield_curve_inversion",
    "compare_fed_forecast_vs_market",
    "get_yield_curve_evolution"
]