"""
Report Generator Configuration

Defines report templates, output formats, styling, and metadata.
"""

import os
from dotenv import load_dotenv
from typing import Dict, List

# Load environment variables
load_dotenv()

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============================================================================
# REPORT TYPES
# ============================================================================

REPORT_TYPES = {
    "comprehensive_analysis": {
        "name": "Comprehensive Fed Policy Analysis",
        "description": "Full analysis using all agents",
        "sections": [
            "executive_summary",
            "current_policy_stance",
            "recent_trends",
            "long_term_patterns",
            "historical_comparisons",
            "economic_context",
            "predictive_indicators",
            "recommendations"
        ],
        "agents_used": ["document_processor", "policy_analyzer", "trend_tracker", "comparative_analyzer", "fred", "bls", "treasury"],
        "typical_length": "15-25 pages"
    },
    
    "episode_comparison": {
        "name": "Fed Policy Episode Comparison",
        "description": "Compare two or more historical episodes",
        "sections": [
            "executive_summary",
            "episode_overview",
            "detailed_comparison",
            "similarity_analysis",
            "lessons_learned",
            "implications"
        ],
        "agents_used": ["comparative_analyzer", "document_processor"],
        "typical_length": "8-12 pages"
    },
    
    "quick_summary": {
        "name": "Fed Policy Quick Summary",
        "description": "Executive summary of current stance",
        "sections": [
            "current_stance",
            "recent_actions",
            "key_metrics",
            "outlook"
        ],
        "agents_used": ["document_processor", "policy_analyzer"],
        "typical_length": "2-3 pages"
    },
    
    "trend_analysis": {
        "name": "Long-Term Fed Policy Trends",
        "description": "Multi-year trend analysis",
        "sections": [
            "executive_summary",
            "trend_overview",
            "structural_breaks",
            "policy_cycles",
            "reaction_function",
            "forecast_accuracy",
            "implications"
        ],
        "agents_used": ["trend_tracker", "document_processor", "fred"],
        "typical_length": "10-15 pages"
    },
    
    "meeting_analysis": {
        "name": "FOMC Meeting Analysis",
        "description": "Deep dive on specific meeting",
        "sections": [
            "meeting_summary",
            "policy_decision",
            "sentiment_analysis",
            "economic_projections",
            "market_reaction",
            "historical_context"
        ],
        "agents_used": ["document_processor", "policy_analyzer", "treasury"],
        "typical_length": "5-8 pages"
    }
}

# ============================================================================
# REPORT SECTIONS
# ============================================================================

SECTION_TEMPLATES = {
    "executive_summary": {
        "title": "Executive Summary",
        "max_length": 500,  # words
        "key_points": 5,
        "include_visualization": False
    },
    
    "current_policy_stance": {
        "title": "Current Policy Stance",
        "subsections": ["Fed Funds Rate", "Recent Actions", "Forward Guidance", "Sentiment"],
        "include_visualization": True,
        "viz_type": "gauge_chart"
    },
    
    "recent_trends": {
        "title": "Recent Policy Trends (1.5-6 years)",
        "subsections": ["Sentiment Evolution", "Regime Changes", "Policy Appropriateness"],
        "include_visualization": True,
        "viz_type": "time_series"
    },
    
    "long_term_patterns": {
        "title": "Long-Term Patterns (6-20 years)",
        "subsections": ["Structural Breaks", "Policy Cycles", "Reaction Function"],
        "include_visualization": True,
        "viz_type": "cycle_chart"
    },
    
    "historical_comparisons": {
        "title": "Historical Comparisons",
        "subsections": ["Similar Episodes", "Pattern Identification", "Lessons Learned"],
        "include_visualization": True,
        "viz_type": "comparison_table"
    },
    
    "economic_context": {
        "title": "Economic Context",
        "subsections": ["Inflation", "Unemployment", "GDP Growth", "Market Expectations"],
        "include_visualization": True,
        "viz_type": "dashboard"
    },
    
    "predictive_indicators": {
        "title": "Predictive Indicators",
        "subsections": ["Leading Indicators", "Next Move Prediction", "Confidence"],
        "include_visualization": True,
        "viz_type": "indicator_panel"
    },
    
    "recommendations": {
        "title": "Key Takeaways & Recommendations",
        "key_points": 5,
        "include_visualization": False
    }
}

# ============================================================================
# OUTPUT FORMATS
# ============================================================================

OUTPUT_FORMATS = {
    "pdf": {
        "extension": ".pdf",
        "mime_type": "application/pdf",
        "engine": "reportlab",  # or "weasyprint"
        "features": ["pagination", "table_of_contents", "headers_footers", "images"]
    },
    
    "docx": {
        "extension": ".docx",
        "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "engine": "python-docx",
        "features": ["styles", "table_of_contents", "headers_footers", "images", "tables"]
    },
    
    "html": {
        "extension": ".html",
        "mime_type": "text/html",
        "engine": "jinja2",
        "features": ["responsive", "interactive_charts", "css_styling", "navigation"]
    },
    
    "markdown": {
        "extension": ".md",
        "mime_type": "text/markdown",
        "engine": "markdown",
        "features": ["github_flavored", "tables", "code_blocks"]
    },
    
    "json": {
        "extension": ".json",
        "mime_type": "application/json",
        "engine": "json",
        "features": ["structured_data", "machine_readable"]
    }
}

# ============================================================================
# STYLING
# ============================================================================

# Document styling
DOCUMENT_STYLE = {
    "font_family": "Arial",
    "font_size": 11,
    "line_spacing": 1.15,
    "margins": {
        "top": 1.0,      # inches
        "bottom": 1.0,
        "left": 1.0,
        "right": 1.0
    },
    "colors": {
        "primary": "#1f77b4",      # Blue
        "secondary": "#ff7f0e",    # Orange
        "success": "#2ca02c",      # Green
        "danger": "#d62728",       # Red
        "warning": "#ff9800",      # Amber
        "info": "#17a2b8",         # Teal
        "text": "#333333",
        "background": "#ffffff"
    }
}

# Header/Footer style
HEADER_FOOTER = {
    "include_header": True,
    "include_footer": True,
    "header_text": "Fed Policy Intelligence Report",
    "footer_text": "Generated by Fed-PIP",
    "include_page_numbers": True,
    "include_date": True
}

# Chart styling
CHART_STYLE = {
    "style": "seaborn-v0_8-darkgrid",
    "figure_size": (10, 6),
    "dpi": 300,
    "title_size": 14,
    "label_size": 11,
    "legend_size": 10,
    "color_palette": "Set2"
}

# Table styling
TABLE_STYLE = {
    "format": "grid",  # grid, simple, fancy_grid, etc.
    "header_style": "bold",
    "align": "left",
    "max_col_width": 40
}

# ============================================================================
# METADATA
# ============================================================================

REPORT_METADATA = {
    "author": "Fed Policy Intelligence Platform",
    "organization": "Fed-PIP",
    "version": "1.0.0",
    "website": "https://github.com/fed-pip",
    "disclaimer": "This report is generated automatically based on publicly available Fed data. It is for informational purposes only and should not be considered investment advice."
}

# ============================================================================
# CHART TYPES
# ============================================================================

CHART_TYPES = {
    "time_series": {
        "description": "Time series line chart",
        "library": "matplotlib",
        "use_for": ["sentiment_over_time", "rate_path", "inflation_trend"]
    },
    
    "comparison_table": {
        "description": "Tabular comparison",
        "library": "tabulate",
        "use_for": ["episode_comparison", "dimension_scores"]
    },
    
    "gauge_chart": {
        "description": "Current stance gauge",
        "library": "plotly",
        "use_for": ["hawkish_dovish_meter", "appropriateness_score"]
    },
    
    "cycle_chart": {
        "description": "Policy cycle visualization",
        "library": "matplotlib",
        "use_for": ["peak_trough_detection", "cycle_phases"]
    },
    
    "dashboard": {
        "description": "Multi-metric dashboard",
        "library": "matplotlib",
        "use_for": ["economic_indicators", "key_metrics"]
    },
    
    "indicator_panel": {
        "description": "Leading indicator status",
        "library": "matplotlib",
        "use_for": ["predictive_signals", "confidence_scores"]
    },
    
    "bar_chart": {
        "description": "Categorical comparison",
        "library": "matplotlib",
        "use_for": ["action_counts", "chair_comparison"]
    },
    
    "heatmap": {
        "description": "Correlation matrix",
        "library": "seaborn",
        "use_for": ["episode_similarity", "dimension_comparison"]
    }
}

# ============================================================================
# DATA AGGREGATION
# ============================================================================

DATA_SOURCES = {
    "document_processor": {
        "provides": ["meeting_sentiment", "policy_actions", "forecasts"],
        "required_for": ["meeting_analysis", "quick_summary"]
    },
    
    "policy_analyzer": {
        "provides": ["sentiment_trends", "regime_changes", "policy_stance"],
        "required_for": ["comprehensive_analysis", "trend_analysis"]
    },
    
    "trend_tracker": {
        "provides": ["long_term_trends", "cycles", "reaction_function", "forecast_bias"],
        "required_for": ["comprehensive_analysis", "trend_analysis"]
    },
    
    "comparative_analyzer": {
        "provides": ["episode_comparisons", "pattern_matches", "lessons_learned"],
        "required_for": ["episode_comparison", "historical_comparisons"]
    },
    
    "fred": {
        "provides": ["inflation", "unemployment", "gdp", "fed_funds"],
        "required_for": ["economic_context"]
    },
    
    "bls": {
        "provides": ["cpi", "pce", "employment"],
        "required_for": ["economic_context"]
    },
    
    "treasury": {
        "provides": ["yield_curve", "market_expectations"],
        "required_for": ["economic_context"]
    }
}

# ============================================================================
# EXPORT SETTINGS
# ============================================================================

EXPORT_SETTINGS = {
    "default_format": "pdf",
    "default_filename": "fed_policy_report",
    "include_timestamp": True,
    "compression": False,
    "embed_images": True,
    "embed_fonts": True
}

# PDF-specific settings
PDF_SETTINGS = {
    "page_size": "letter",  # letter, A4
    "orientation": "portrait",
    "compression": True,
    "bookmarks": True,
    "embed_fonts": True
}

# DOCX-specific settings
DOCX_SETTINGS = {
    "page_size": "letter",
    "orientation": "portrait",
    "template": None,  # Path to .docx template
    "track_changes": False
}

# HTML-specific settings
HTML_SETTINGS = {
    "responsive": True,
    "include_css": True,
    "include_javascript": True,
    "bootstrap": True,
    "print_stylesheet": True
}

# ============================================================================
# TEMPLATES
# ============================================================================

# Jinja2 template paths (if using templates)
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

TEMPLATES = {
    "comprehensive_analysis": "comprehensive_analysis.html",
    "episode_comparison": "episode_comparison.html",
    "quick_summary": "quick_summary.html",
    "email_summary": "email_summary.html"
}

# ============================================================================
# VALIDATION
# ============================================================================

# Report validation rules
VALIDATION_RULES = {
    "min_sections": 2,
    "max_sections": 15,
    "min_length": 100,      # words
    "max_length": 50000,    # words
    "require_executive_summary": True,
    "require_metadata": True
}

# ============================================================================
# CACHING
# ============================================================================

CACHE_SETTINGS = {
    "enabled": True,
    "ttl": 3600,  # seconds (1 hour)
    "max_size": 100,  # MB
    "cache_dir": "/tmp/fed_pip_cache"
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_config() -> List[str]:
    """Validate report generator configuration and return list of issues."""
    issues = []
    
    # Check output directory
    import os
    if not os.path.exists(OUTPUT_CONFIG["base_dir"]):
        issues.append(f"Output directory does not exist: {OUTPUT_CONFIG['base_dir']}")
    
    # Check chart dimensions
    chart_config = CHART_CONFIG["default_style"]
    if chart_config["figure_size"][0] <= 0 or chart_config["figure_size"][1] <= 0:
        issues.append("Chart figure size must be positive")
    
    # Check cache configuration
    cache_config = CACHE_CONFIG
    if cache_config["max_size"] <= 0:
        issues.append("Cache max size must be positive")
    
    if cache_config["ttl"] <= 0:
        issues.append("Cache TTL must be positive")
    
    return issues


def get_config_info() -> Dict[str, any]:
    """Get current configuration information."""
    import os
    return {
        "report_templates": list(REPORT_TEMPLATES.keys()),
        "output_formats": list(OUTPUT_CONFIG["formats"].keys()),
        "chart_types": list(CHART_CONFIG["types"].keys()),
        "output_dir_exists": os.path.exists(OUTPUT_CONFIG["base_dir"]),
        "cache_enabled": CACHE_CONFIG["enabled"],
        "log_level": LOG_LEVEL
    }


def is_fully_configured() -> bool:
    """Check if report generator is fully configured."""
    issues = validate_config()
    critical_issues = [issue for issue in issues if "does not exist" in issue]
    return len(critical_issues) == 0
