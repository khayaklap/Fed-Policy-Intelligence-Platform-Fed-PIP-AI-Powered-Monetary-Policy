"""
Comparative Analyzer

Historical Fed policy episode comparison agent.
"""

__version__ = "1.0.0"

# Handle relative imports for package usage and absolute for direct execution
try:
    # Import main components
    from .comparative_analyzer_agent import ComparativeAnalyzerAgent
    from .comparative_analyzer_config import (
        COMPARISON_METRICS,
        HISTORICAL_EPISODES,
        SIMILARITY_THRESHOLDS,
        EPISODE_CATEGORIES,
        validate_config,
        get_config_info,
        is_fully_configured
    )
    from .comparative_analyzer_tools import (
        compare_policy_episodes,
        find_historical_analogues,
        analyze_episode_outcomes,
        rank_episode_similarities,
        get_comparison_summary
    )
except ImportError:
    # Fallback for direct execution
    from comparative_analyzer_agent import ComparativeAnalyzerAgent
    from comparative_analyzer_config import (
        COMPARISON_METRICS,
        HISTORICAL_EPISODES,
        SIMILARITY_THRESHOLDS,
        EPISODE_CATEGORIES,
        validate_config,
        get_config_info,
        is_fully_configured
    )
    from comparative_analyzer_tools import (
        compare_policy_episodes,
        find_historical_analogues,
        analyze_episode_outcomes,
        rank_episode_similarities,
        get_comparison_summary
    )

__all__ = [
    # Main agent
    "ComparativeAnalyzerAgent",
    
    # Configuration
    "COMPARISON_METRICS",
    "HISTORICAL_EPISODES",
    "SIMILARITY_THRESHOLDS",
    "EPISODE_CATEGORIES",
    "validate_config",
    "get_config_info",
    "is_fully_configured",
    
    # Tool functions
    "compare_policy_episodes",
    "find_historical_analogues",
    "analyze_episode_outcomes",
    "rank_episode_similarities",
    "get_comparison_summary"
]