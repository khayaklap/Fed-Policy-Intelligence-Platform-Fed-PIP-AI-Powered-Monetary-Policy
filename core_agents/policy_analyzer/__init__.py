"""
Policy Analyzer

Short-term Fed policy trend analysis agent (1.5-6 years).
"""

__version__ = "1.0.0"

# Handle relative imports for package usage and absolute for direct execution
try:
    # Import main components
    from .policy_analyzer_agent import PolicyAnalyzerAgent
    from .policy_analyzer_config import (
        POLICY_STANCE_INDICATORS,
        REGIME_CHANGE_THRESHOLDS,
        SENTIMENT_KEYWORDS,
        ANALYSIS_TIMEFRAMES,
        validate_config,
        get_config_info,
        is_fully_configured
    )
    from .policy_analyzer_tools import (
        analyze_policy_stance,
        detect_regime_changes,
        track_sentiment_trends,
        compare_policy_periods,
        get_policy_summary
    )
except ImportError:
    # Fallback for direct execution
    from policy_analyzer_agent import PolicyAnalyzerAgent
    from policy_analyzer_config import (
        POLICY_STANCE_INDICATORS,
        REGIME_CHANGE_THRESHOLDS,
        SENTIMENT_KEYWORDS,
        ANALYSIS_TIMEFRAMES,
        validate_config,
        get_config_info,
        is_fully_configured
    )
    from policy_analyzer_tools import (
        analyze_policy_stance,
        detect_regime_changes,
        track_sentiment_trends,
        compare_policy_periods,
        get_policy_summary
    )

__all__ = [
    # Main agent
    "PolicyAnalyzerAgent",
    
    # Configuration
    "POLICY_STANCE_INDICATORS",
    "REGIME_CHANGE_THRESHOLDS", 
    "SENTIMENT_KEYWORDS",
    "ANALYSIS_TIMEFRAMES",
    "validate_config",
    "get_config_info",
    "is_fully_configured",
    
    # Tool functions
    "analyze_policy_stance",
    "detect_regime_changes",
    "track_sentiment_trends",
    "compare_policy_periods",
    "get_policy_summary"
]