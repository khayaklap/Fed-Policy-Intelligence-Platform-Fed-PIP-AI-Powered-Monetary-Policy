"""
Report Generator

Professional Fed policy report generation agent.
"""

__version__ = "1.0.0"

# Handle relative imports for package usage and absolute for direct execution
try:
    # Import main components
    from .report_generator_agent import ReportGeneratorAgent
    from .report_generator_config import (
        REPORT_TEMPLATES,
        OUTPUT_FORMATS,
        CHART_CONFIGURATIONS,
        STYLE_GUIDELINES,
        validate_config,
        get_config_info,
        is_fully_configured
    )
    from .report_generator_tools import (
        generate_policy_report,
        create_executive_summary,
        build_data_visualizations,
        format_report_output,
        get_report_metadata
    )
except ImportError:
    # Fallback for direct execution
    from report_generator_agent import ReportGeneratorAgent
    from report_generator_config import (
        REPORT_TEMPLATES,
        OUTPUT_FORMATS,
        CHART_CONFIGURATIONS,
        STYLE_GUIDELINES,
        validate_config,
        get_config_info,
        is_fully_configured
    )
    from report_generator_tools import (
        generate_policy_report,
        create_executive_summary,
        build_data_visualizations,
        format_report_output,
        get_report_metadata
    )

__all__ = [
    # Main agent
    "ReportGeneratorAgent",
    
    # Configuration
    "REPORT_TEMPLATES",
    "OUTPUT_FORMATS",
    "CHART_CONFIGURATIONS",
    "STYLE_GUIDELINES",
    "validate_config",
    "get_config_info",
    "is_fully_configured",
    
    # Tool functions
    "generate_policy_report",
    "create_executive_summary",
    "build_data_visualizations",
    "format_report_output",
    "get_report_metadata"
]