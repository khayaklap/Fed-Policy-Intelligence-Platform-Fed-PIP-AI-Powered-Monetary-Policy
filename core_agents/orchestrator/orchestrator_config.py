"""
Fed-PIP Orchestrator Configuration

Complete configuration for multi-agent coordination including:
- Agent registry (9 agents with capabilities)
- External agent endpoints (FRED, BLS, Treasury)
- Query routing rules and keywords
- Workflow templates
- Performance settings
- Error handling strategies
- State management options

Last updated: November 2024
Status: Production Ready
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass

# ============================================================================
# EXTERNAL AGENT ENDPOINTS (A2A Protocol)
# ============================================================================

EXTERNAL_AGENT_ENDPOINTS = {
    "fred_agent": {
        "url": os.getenv("FRED_AGENT_URL", "http://localhost:8001"),
        "health_check": "/health",
        "timeout": 30,  # seconds
        "enabled": True
    },
    "bls_agent": {
        "url": os.getenv("BLS_AGENT_URL", "http://localhost:8002"),
        "health_check": "/health",
        "timeout": 30,
        "enabled": True
    },
    "treasury_agent": {
        "url": os.getenv("TREASURY_AGENT_URL", "http://localhost:8003"),
        "health_check": "/health",
        "timeout": 30,
        "enabled": True
    }
}

# Quick access to URLs only
EXTERNAL_AGENTS = {
    name: config["url"]
    for name, config in EXTERNAL_AGENT_ENDPOINTS.items()
    if config["enabled"]
}

# ============================================================================
# AGENT REGISTRY - Complete Capabilities Catalog
# ============================================================================

AGENT_REGISTRY = {
    # ========================================================================
    # CORE AGENTS (Direct Python Import)
    # ========================================================================
    
    "document_processor": {
        "type": "core",
        "description": "Parse and analyze FOMC documents (68 PDFs)",
        "module": "core_agents.document_processor.document_processor_tools",
        "capabilities": [
            "parse_fomc_minutes",           # Parse meeting minutes
            "extract_sep_forecast",         # Extract SEP forecasts
            "parse_monetary_policy_report", # Parse MPR
            "identify_dissents",            # Find dissenting votes
            "extract_policy_actions"        # Extract rate decisions
        ],
        "data_sources": [
            "39 FOMC Minutes (2019-2024)",
            "10 Monetary Policy Reports",
            "19 Summary of Economic Projections"
        ],
        "required_for": [
            "meeting_analysis",
            "document_parsing",
            "policy_action_extraction"
        ],
        "data_provided": [
            "meeting_sentiment",
            "policy_actions",
            "forecasts",
            "vote_counts",
            "dissents"
        ],
        "typical_response_time": "fast",  # <1 second
        "example_use": "Parse December 2024 FOMC minutes"
    },
    
    "policy_analyzer": {
        "type": "core",
        "description": "Analyze short-term policy trends (1.5-6 years)",
        "module": "core_agents.policy_analyzer.policy_analyzer_tools",
        "capabilities": [
            "classify_policy_stance",       # Dovish/neutral/hawkish
            "detect_regime_change",         # Major policy pivots
            "analyze_sentiment_evolution",  # Sentiment over time
            "track_forward_guidance",       # Communication analysis
            "assess_policy_appropriateness" # Is policy right?
        ],
        "required_for": [
            "recent_trends",
            "current_stance",
            "regime_analysis"
        ],
        "data_provided": [
            "sentiment_trends",
            "regime_changes",
            "policy_stance",
            "hawkish_dovish_score"
        ],
        "typical_response_time": "fast",  # 1-2 seconds
        "example_use": "What's Fed's current stance?"
    },
    
    "trend_tracker": {
        "type": "core",
        "description": "Analyze long-term patterns (6-20 years)",
        "module": "core_agents.trend_tracker.trend_tracker_tools",
        "capabilities": [
            "detect_structural_breaks",     # PELT change points
            "identify_policy_cycles",       # Easing/tightening cycles
            "estimate_taylor_rule",         # Taylor Rule α, β
            "track_forecast_bias",          # Systematic errors
            "generate_predictions"          # Next meeting prediction
        ],
        "advanced_methods": [
            "PELT (Pruned Exact Linear Time)",
            "Taylor Rule econometric estimation",
            "Statistical hypothesis testing"
        ],
        "required_for": [
            "long_term_analysis",
            "cycle_detection",
            "predictions"
        ],
        "data_provided": [
            "structural_breaks",
            "policy_cycles",
            "taylor_rule_params",
            "forecast_bias",
            "predictions"
        ],
        "typical_response_time": "medium",  # 2-5 seconds
        "example_use": "Detect structural breaks in Fed policy"
    },
    
    "comparative_analyzer": {
        "type": "core",
        "description": "Compare episodes and identify patterns (13 episodes, 1979-2024)",
        "module": "core_agents.comparative_analyzer.comparative_analyzer_tools",
        "capabilities": [
            "compare_episodes",             # DTW comparison
            "identify_patterns",            # Pattern matching
            "rank_similar_episodes",        # Find most similar
            "compare_fed_chairs",           # Chair-to-chair comparison
            "extract_lessons"               # Historical lessons
        ],
        "advanced_methods": [
            "Dynamic Time Warping (DTW)",
            "Pattern similarity scoring",
            "Historical episode taxonomy"
        ],
        "episodes_covered": [
            "Volcker Disinflation (1979-1982)",
            "Greenspan Era (1987-2006)",
            "GFC Response (2008-2010)",
            "COVID Response (2020-2022)",
            "2022 Inflation Fight (2022-2024)",
            # ... 8 more episodes
        ],
        "required_for": [
            "historical_context",
            "pattern_matching",
            "lessons_learned"
        ],
        "data_provided": [
            "episode_comparisons",
            "similarity_scores",
            "historical_patterns",
            "lessons"
        ],
        "typical_response_time": "fast",  # <1 second
        "example_use": "Compare GFC vs COVID Fed responses"
    },
    
    "report_generator": {
        "type": "core",
        "description": "Generate professional reports (PDF, DOCX, HTML)",
        "module": "core_agents.report_generator.report_generator_tools",
        "capabilities": [
            "generate_comprehensive_report", # Full analysis report
            "generate_episode_report",      # Episode comparison
            "generate_quick_summary",       # Brief summary
            "export_to_pdf",                # PDF export
            "export_to_docx"                # Word export
        ],
        "output_formats": [
            "PDF (reportlab)",
            "DOCX (python-docx)",
            "HTML (Jinja2)",
            "Markdown"
        ],
        "required_for": [
            "report_creation",
            "document_export"
        ],
        "data_provided": [
            "formatted_reports",
            "exported_files"
        ],
        "typical_response_time": "slow",  # 5-10 seconds
        "example_use": "Generate PDF report on 2022 inflation"
    },
    
    # ========================================================================
    # EXTERNAL AGENTS (A2A Protocol)
    # ========================================================================
    
    "fred_agent": {
        "type": "external",
        "description": "Federal Reserve Economic Data (22 series)",
        "endpoint": EXTERNAL_AGENTS.get("fred_agent"),
        "capabilities": [
            "get_gdp_data",                 # Real, nominal, growth
            "get_inflation_data",           # PCE, Core PCE (Fed's target!)
            "get_employment_data",          # Unemployment, NFP
            "get_interest_rates",           # Fed Funds, yields
            "get_economic_snapshot",        # All indicators
            "compare_to_fed_projection"     # KILLER APP: SEP vs actual
        ],
        "series_count": 22,
        "key_series": [
            "Core PCE (PCEPILFE) - Fed's preferred inflation measure",
            "Real GDP (GDPC1)",
            "Unemployment Rate (UNRATE)",
            "Federal Funds Rate (FEDFUNDS)",
            "10Y Treasury (DGS10)"
        ],
        "required_for": [
            "economic_context",
            "inflation_analysis",
            "macro_data",
            "forecast_validation"
        ],
        "data_provided": [
            "gdp",
            "inflation",
            "unemployment",
            "interest_rates",
            "economic_snapshot"
        ],
        "typical_response_time": "medium",  # 2-3 seconds (API call)
        "example_use": "Get Core PCE inflation 2022"
    },
    
    "bls_agent": {
        "type": "external",
        "description": "Bureau of Labor Statistics (32 series)",
        "endpoint": EXTERNAL_AGENTS.get("bls_agent"),
        "capabilities": [
            "get_cpi_components",           # Food, energy, shelter breakdown
            "get_ppi_data",                 # Producer prices (leading indicator)
            "get_employment_cost_index",    # Wage pressure (Fed watches!)
            "compare_inflation_measures",   # CPI vs Core vs PPI
            "analyze_inflation_drivers"     # KILLER APP: What's driving inflation?
        ],
        "series_count": 32,
        "key_series": [
            "CPI All Items (CPIAUCSL)",
            "CPI Shelter (32% of CPI weight!)",
            "PPI Final Demand (leads CPI by 3-6 months)",
            "Employment Cost Index (wage-price spiral indicator)",
            "Import/Export Prices"
        ],
        "inflation_taxonomy": {
            "headline": "All items",
            "core": "Ex food & energy (Fed's focus)",
            "core_services": "Most persistent",
            "core_goods": "Supply chain sensitive"
        },
        "persistence_classification": {
            "transitory": ["energy", "food", "used_cars"],  # <6 months
            "sticky": ["shelter", "core_services"]          # 6-18+ months
        },
        "required_for": [
            "inflation_components",
            "labor_market",
            "price_indices",
            "inflation_drivers"
        ],
        "data_provided": [
            "cpi_components",
            "ppi",
            "eci",
            "inflation_drivers"
        ],
        "typical_response_time": "medium",  # 2-3 seconds (API call)
        "example_use": "What's driving inflation in 2022?"
    },
    
    "treasury_agent": {
        "type": "external",
        "description": "US Treasury Market Data (24 series)",
        "endpoint": EXTERNAL_AGENTS.get("treasury_agent"),
        "capabilities": [
            "get_yield_curve_data",         # 1M-30Y yields
            "get_market_inflation_expectations",  # TIPS breakevens
            "analyze_monetary_policy_stance",     # Real yields vs R-star
            "detect_yield_curve_inversion",       # Recession signal
            "compare_fed_forecast_vs_market",     # KILLER APP: Fed credibility
            "get_yield_curve_evolution"           # Historical changes
        ],
        "series_count": 24,
        "key_series": [
            "11 Nominal Yields (1M-30Y)",
            "5 TIPS Yields (5Y-30Y)",
            "3 Pre-calculated Breakevens (5Y, 10Y, 5y5y forward)",
            "2 Pre-calculated Spreads (10Y-2Y, 10Y-3M)"
        ],
        "economic_concepts": {
            "yield_curve": {
                "normal": "Long > Short (healthy growth)",
                "flat": "Uncertainty",
                "inverted": "Recession signal (every recession since 1970!)"
            },
            "tips_breakeven": {
                "definition": "Nominal - TIPS = market inflation expectation",
                "10Y_most_liquid": "Most watched by Fed",
                "5y5y_forward": "Fed's anchoring measure"
            },
            "real_yields": {
                "definition": "TIPS yield = inflation-adjusted return",
                "r_star": "≈0.5% neutral rate",
                "restrictive": "Real yield > R-star",
                "accommodative": "Real yield < R-star"
            }
        },
        "recession_signal": {
            "indicator": "2s10s yield curve inversion",
            "threshold": "-10 basis points",
            "lead_time": "6-18 months before recession",
            "historical_accuracy": "Every recession since 1970"
        },
        "required_for": [
            "market_expectations",
            "yield_curve_analysis",
            "inflation_expectations",
            "fed_credibility",
            "recession_signals"
        ],
        "data_provided": [
            "yield_curve",
            "tips_breakevens",
            "real_yields",
            "inversion_status",
            "market_expectations"
        ],
        "typical_response_time": "medium",  # 2-3 seconds (API call)
        "example_use": "Is yield curve inverted?"
    }
}

# ============================================================================
# QUERY ROUTING - Keywords and Patterns
# ============================================================================

ROUTING_KEYWORDS = {
    # Core Agents
    "document_processor": {
        "primary": [
            "parse", "analyze document", "fomc minutes", "sep", 
            "monetary policy report", "read", "extract", "meeting"
        ],
        "secondary": [
            "statement", "press conference", "document", "transcript",
            "minutes", "dissent", "vote"
        ]
    },
    
    "policy_analyzer": {
        "primary": [
            "recent trend", "sentiment", "regime", "stance", 
            "hawkish", "dovish", "current policy", "pivot"
        ],
        "secondary": [
            "last few years", "short term", "recent", "lately",
            "forward guidance", "communication"
        ]
    },
    
    "trend_tracker": {
        "primary": [
            "long term", "cycle", "structural break", "taylor rule", 
            "prediction", "forecast bias", "change point"
        ],
        "secondary": [
            "historical", "decades", "multi-year", "pattern over time",
            "easing cycle", "tightening cycle"
        ]
    },
    
    "comparative_analyzer": {
        "primary": [
            "compare", "similar", "pattern", "lesson", 
            "historical comparison", "chair comparison", "episode"
        ],
        "secondary": [
            "like", "versus", "vs", "past episode", "previous",
            "1970s", "2008", "gfc", "covid"
        ]
    },
    
    "report_generator": {
        "primary": [
            "generate report", "create report", "comprehensive analysis", 
            "summary", "export", "document"
        ],
        "secondary": [
            "pdf", "word", "write up", "brief", "formatted"
        ]
    },
    
    # External Agents
    "fred_agent": {
        "primary": [
            "inflation", "unemployment", "gdp", "fed funds", 
            "economic data", "macro", "pce", "core pce"
        ],
        "secondary": [
            "growth", "employment", "interest rate", "treasury yield",
            "money supply", "economic indicator"
        ]
    },
    
    "bls_agent": {
        "primary": [
            "cpi", "ppi", "employment cost", "wages", "labor", 
            "inflation components", "what's driving", "drivers"
        ],
        "secondary": [
            "jobs", "price index", "shelter", "energy",
            "food prices", "wage pressure"
        ]
    },
    
    "treasury_agent": {
        "primary": [
            "yield curve", "market expectations", "treasury", "tips", 
            "breakeven", "inversion", "recession signal"
        ],
        "secondary": [
            "yields", "rates", "spread", "term structure",
            "real yields", "inflation expectations"
        ]
    }
}

# ============================================================================
# QUERY TYPES - Predefined Query Patterns
# ============================================================================

QUERY_TYPES = {
    "meeting_analysis": {
        "description": "Analyze specific FOMC meeting",
        "required_agents": ["document_processor"],
        "optional_agents": ["policy_analyzer", "comparative_analyzer"],
        "typical_response_time": "fast",
        "example": "Analyze the November 2024 FOMC meeting"
    },
    
    "current_stance": {
        "description": "What's current Fed policy stance",
        "required_agents": ["document_processor", "policy_analyzer"],
        "optional_agents": ["fred_agent", "bls_agent"],
        "typical_response_time": "fast",
        "example": "What is the Fed's current policy stance?"
    },
    
    "trend_analysis": {
        "description": "Analyze policy trends over time",
        "required_agents": ["policy_analyzer", "trend_tracker"],
        "optional_agents": ["document_processor"],
        "typical_response_time": "medium",
        "example": "How has Fed policy evolved over the past 5 years?"
    },
    
    "historical_comparison": {
        "description": "Compare to historical episodes",
        "required_agents": ["comparative_analyzer"],
        "optional_agents": ["trend_tracker", "policy_analyzer"],
        "typical_response_time": "fast",
        "example": "How does current policy compare to 2008 GFC?"
    },
    
    "forecast_validation": {
        "description": "Validate Fed forecast accuracy",
        "required_agents": ["fred_agent", "treasury_agent"],
        "optional_agents": ["bls_agent", "comparative_analyzer", "policy_analyzer"],
        "typical_response_time": "medium",
        "example": "Was Fed's 2021 inflation forecast accurate?",
        "unique_capability": "KILLER APP - No other platform has this"
    },
    
    "inflation_analysis": {
        "description": "Comprehensive inflation analysis",
        "required_agents": ["fred_agent", "bls_agent"],
        "optional_agents": ["treasury_agent", "policy_analyzer"],
        "typical_response_time": "medium",
        "example": "What's driving current inflation?"
    },
    
    "economic_context": {
        "description": "Current economic conditions",
        "required_agents": ["fred_agent", "bls_agent"],
        "optional_agents": ["treasury_agent", "policy_analyzer"],
        "typical_response_time": "medium",
        "example": "What are current inflation and unemployment levels?"
    },
    
    "comprehensive_analysis": {
        "description": "Complete Fed policy analysis",
        "required_agents": [
            "document_processor", "policy_analyzer", 
            "trend_tracker", "comparative_analyzer"
        ],
        "optional_agents": [
            "fred_agent", "bls_agent", "treasury_agent", 
            "report_generator"
        ],
        "typical_response_time": "slow",
        "example": "Give me a comprehensive analysis of Fed policy"
    }
}

# ============================================================================
# PERFORMANCE & EXECUTION SETTINGS
# ============================================================================

PERFORMANCE_CONFIG = {
    # Parallel execution
    "enable_parallel_execution": True,
    "max_parallel_agents": 5,          # Max agents simultaneously
    "parallel_threshold": 2,           # Min agents for parallel mode
    
    # Timeouts
    "timeout_per_agent": 30,           # seconds per agent
    "total_workflow_timeout": 120,     # seconds total (2 minutes)
    "connection_timeout": 5,           # seconds for connection
    "read_timeout": 30,                # seconds for reading response
    
    # Caching
    "enable_caching": True,
    "cache_ttl": 1800,                 # seconds (30 minutes)
    "cache_max_size": 1000,            # max cached items
    
    # Retry logic
    "enable_retry": True,
    "max_retries": 2,
    "retry_delay": 1,                  # seconds between retries
    "retry_backoff": 2,                # exponential backoff multiplier
    
    # Connection pooling
    "connection_pool_size": 10,
    "connection_pool_maxsize": 20
}

# ============================================================================
# ERROR HANDLING STRATEGIES
# ============================================================================

ERROR_HANDLING = {
    # Retry behavior
    "retry_on_failure": True,
    "retry_on_timeout": True,
    "max_retries": 2,
    
    # Fallback strategies
    "fallback_strategy": "skip_agent",  # Options: "skip_agent", "stop_workflow", "use_cached"
    "allow_partial_results": True,      # Continue even if some agents fail
    "minimum_successful_agents": 1,     # Minimum agents for valid result
    
    # Logging
    "log_errors": True,
    "log_warnings": True,
    "log_retries": True,
    
    # User feedback
    "inform_user_of_failures": True,
    "include_error_details": False      # Don't expose internal errors to user
}

# ============================================================================
# STATE MANAGEMENT
# ============================================================================

STATE_CONFIG = {
    # Enable/disable state
    "enable_state": True,
    
    # Backend options: "memory", "redis", "database"
    "state_backend": "memory",
    
    # State persistence
    "state_ttl": 3600,                 # seconds (1 hour)
    "max_conversation_length": 50,     # max messages in history
    "save_intermediate_results": True,
    
    # Redis config (if using Redis backend)
    "redis_host": os.getenv("REDIS_HOST", "localhost"),
    "redis_port": int(os.getenv("REDIS_PORT", "6379")),
    "redis_db": int(os.getenv("REDIS_DB", "0")),
    
    # Database config (if using database backend)
    "database_url": os.getenv("DATABASE_URL", "sqlite:///orchestrator_state.db")
}

# ============================================================================
# OUTPUT FORMATTING
# ============================================================================

OUTPUT_PREFERENCES = {
    # Format options: "structured", "conversational", "minimal"
    "default_format": "structured",
    
    # Metadata inclusion
    "include_metadata": True,
    "include_agent_attribution": True,
    "include_confidence_scores": True,
    "include_timestamps": True,
    
    # Response enrichment
    "include_sources": True,
    "include_related_queries": False,
    "include_visualization_suggestions": False
}

# ============================================================================
# COORDINATION MODES
# ============================================================================

COORDINATION_MODES = {
    "sequential": {
        "description": "Execute agents one after another",
        "when_to_use": "When each agent depends on previous results",
        "pros": ["Simple", "Clear dependencies", "Easy debugging"],
        "cons": ["Slower", "No parallelization"],
        "estimated_time_multiplier": 1.0
    },
    
    "parallel": {
        "description": "Execute independent agents simultaneously",
        "when_to_use": "When agents don't depend on each other",
        "pros": ["Faster (2-3x)", "Efficient resource use"],
        "cons": ["More complex", "Requires coordination"],
        "estimated_time_multiplier": 0.4  # 40% of sequential time
    },
    
    "adaptive": {
        "description": "Dynamically adjust based on results",
        "when_to_use": "When next step depends on current results",
        "pros": ["Flexible", "Efficient", "Smart"],
        "cons": ["Most complex", "Unpredictable timing"],
        "estimated_time_multiplier": 0.6
    }
}

# Default coordination mode
DEFAULT_COORDINATION_MODE = "parallel"  # Parallel is faster and default

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": ["console", "file"],
    "file_path": "logs/orchestrator.log",
    "max_file_size": 10 * 1024 * 1024,  # 10 MB
    "backup_count": 5
}

# ============================================================================
# FEATURE FLAGS
# ============================================================================

FEATURE_FLAGS = {
    "enable_forecast_validation": True,  # KILLER APP
    "enable_parallel_execution": True,
    "enable_caching": True,
    "enable_state_persistence": True,
    "enable_advanced_routing": True,
    "enable_confidence_scoring": True,
    "enable_query_suggestions": False,  # Future feature
    "enable_streaming_responses": False  # Future feature
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_agent_endpoint(agent_name: str) -> Optional[str]:
    """Get endpoint URL for external agent."""
    return EXTERNAL_AGENTS.get(agent_name)

def get_agent_capabilities(agent_name: str) -> List[str]:
    """Get list of capabilities for an agent."""
    if agent_name in AGENT_REGISTRY:
        return AGENT_REGISTRY[agent_name].get("capabilities", [])
    return []

def is_external_agent(agent_name: str) -> bool:
    """Check if agent is external (A2A) or core (direct import)."""
    if agent_name in AGENT_REGISTRY:
        return AGENT_REGISTRY[agent_name].get("type") == "external"
    return False

def get_required_agents_for_query_type(query_type: str) -> List[str]:
    """Get required agents for a query type."""
    if query_type in QUERY_TYPES:
        return QUERY_TYPES[query_type].get("required_agents", [])
    return []

def get_optional_agents_for_query_type(query_type: str) -> List[str]:
    """Get optional agents for a query type."""
    if query_type in QUERY_TYPES:
        return QUERY_TYPES[query_type].get("optional_agents", [])
    return []

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate configuration on import."""
    # Check external agent URLs are set
    for agent_name, endpoint in EXTERNAL_AGENTS.items():
        if not endpoint:
            print(f"Warning: {agent_name} endpoint not set")
    
    # Check performance settings are reasonable
    if PERFORMANCE_CONFIG["timeout_per_agent"] > PERFORMANCE_CONFIG["total_workflow_timeout"]:
        print("Warning: timeout_per_agent > total_workflow_timeout")
    
    # Check parallel settings
    if PERFORMANCE_CONFIG["max_parallel_agents"] < 1:
        print("Warning: max_parallel_agents should be >= 1")

# Run validation on import
validate_config()
