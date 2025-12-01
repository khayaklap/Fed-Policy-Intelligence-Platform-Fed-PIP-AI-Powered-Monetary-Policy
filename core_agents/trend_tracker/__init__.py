"""
Trend Tracker

Long-term Fed policy pattern analysis agent (6-20 years).
"""

__version__ = "1.0.0"

# Handle relative imports for package usage and absolute for direct execution
try:
    # Import main components
    from .trend_tracker_agent import TrendTrackerAgent
    from .trend_tracker_config import (
        TREND_ANALYSIS_PERIODS,
        PATTERN_DETECTION_THRESHOLDS,
        CYCLE_INDICATORS,
        HISTORICAL_BENCHMARKS,
        validate_config,
        get_config_info,
        is_fully_configured
    )
    from .trend_tracker_tools import (
        analyze_long_term_trends,
        detect_policy_cycles,
        identify_historical_patterns,
        track_regime_evolution,
        get_trend_summary
    )
except ImportError:
    # Fallback for direct execution
    from trend_tracker_agent import TrendTrackerAgent
    from trend_tracker_config import (
        TREND_ANALYSIS_PERIODS,
        PATTERN_DETECTION_THRESHOLDS,
        CYCLE_INDICATORS,
        HISTORICAL_BENCHMARKS,
        validate_config,
        get_config_info,
        is_fully_configured
    )
    from trend_tracker_tools import (
        analyze_long_term_trends,
        detect_policy_cycles,
        identify_historical_patterns,
        track_regime_evolution,
        get_trend_summary
    )

__all__ = [
    # Main agent
    "TrendTrackerAgent",
    
    # Configuration
    "TREND_ANALYSIS_PERIODS",
    "PATTERN_DETECTION_THRESHOLDS",
    "CYCLE_INDICATORS",
    "HISTORICAL_BENCHMARKS",
    "validate_config",
    "get_config_info",
    "is_fully_configured",
    
    # Tool functions
    "analyze_long_term_trends",
    "detect_policy_cycles",
    "identify_historical_patterns",
    "track_regime_evolution",
    "get_trend_summary"
]