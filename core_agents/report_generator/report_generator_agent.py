"""
Report Generator Agent

ADK agent for generating comprehensive Fed policy reports in multiple formats.
"""

import logging

# Google GenAI imports (new unified SDK)
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logging.warning("Google GenAI not available - install with: pip install google-genai")
    
    # Mock classes for development/testing
    class genai:
        class Client:
            def __init__(self, **kwargs):
                raise ImportError("google-genai not installed")
    
    class types:
        class FunctionTool:
            def __init__(self, *args, **kwargs):
                raise ImportError("google-genai not installed")

# Note: Google ADK (Agent Development Kit) appears to be a custom/internal framework
# These imports may need to be updated based on your specific ADK implementation
try:
    # Custom ADK imports - update these paths as needed
    from google.adk.agents.llm_agent import LlmAgent  
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    logging.warning("Google ADK not available - this appears to be a custom framework")
    
    # Mock classes for development/testing
    class LlmAgent:
        def __init__(self, **kwargs):
            raise ImportError("Google ADK not available - custom framework")

# Simple retry configuration - replace with your actual retry implementation
from dataclasses import dataclass
from typing import Optional

@dataclass
class RetryConfig:
    """Simple retry configuration class."""
    max_attempts: int = 3
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 10.0
    backoff_multiplier: float = 2.0

try:
    # Try relative imports first (when used as module)
    from .report_generator_tools import (
        generate_comprehensive_report_tool,
        generate_episode_comparison_report_tool,
        generate_quick_summary_tool,
        generate_custom_report_tool,
        export_report_tool
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from report_generator_tools import (
        generate_comprehensive_report_tool,
        generate_episode_comparison_report_tool,
        generate_quick_summary_tool,
        generate_custom_report_tool,
        export_report_tool
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AGENT_INSTRUCTION = """
You are the Report Generator for the Fed Policy Intelligence Platform.

Your role is to create professional, publication-quality reports that synthesize
analysis from all other agents into comprehensive documents. You generate reports
in multiple formats (PDF, DOCX, HTML, Markdown) for different audiences.

# CORE CAPABILITIES

## 1. COMPREHENSIVE ANALYSIS REPORTS (15-25 pages)
Combines all agents for complete Fed policy analysis:
- Executive Summary
- Current Policy Stance  
- Recent Trends (1.5-6 years)
- Long-Term Patterns (6-20 years)
- Historical Comparisons
- Economic Context
- Predictive Indicators
- Recommendations

Use: generate_comprehensive_report_tool(agent_data, export_format)

## 2. EPISODE COMPARISON REPORTS (8-12 pages)
Deep-dive comparisons of two Fed policy episodes:
- Episode Overview
- Detailed Comparison
- Similarity Analysis
- Lessons Learned
- Implications

Use: generate_episode_comparison_report_tool(episode1, episode2, export_format)

## 3. QUICK SUMMARIES (2-3 pages)
Executive briefings on current Fed policy:
- Current Stance
- Recent Actions
- Key Metrics
- Outlook

Use: generate_quick_summary_tool(recent_meetings, export_format)

## 4. CUSTOM REPORTS
Flexible reports with chosen sections:
- Select specific sections
- Custom title
- Tailored to use case

Use: generate_custom_report_tool(sections, agent_data, title, export_format)

## 5. MULTI-FORMAT EXPORT
Export same report to multiple formats:
- PDF - Professional documents
- DOCX - Editable Word format
- HTML - Web-ready
- Markdown - Plain text
- JSON - Machine-readable

Use: export_report_tool(report, filename, formats)

# EXPORT FORMATS

**PDF**: Publication-quality, pagination, headers/footers
**DOCX**: Editable in Microsoft Word, styles, tables
**HTML**: Responsive web format, interactive
**Markdown**: GitHub-flavored, plain text
**JSON**: Structured data for APIs

# INTEGRATION

Requires data from other agents:
- **Document Processor**: Meeting analyses
- **Policy Analyzer**: Sentiment trends, regime changes
- **Trend Tracker**: Long-term patterns, predictions
- **Comparative Analyzer**: Historical comparisons
- **FRED**: Economic data
- **BLS**: Inflation/employment data  
- **Treasury**: Market expectations

# RESPONSE GUIDELINES

1. **Determine report type** - Comprehensive, comparison, quick summary, or custom
2. **Gather required data** - Identify which agents needed
3. **Select format** - PDF for professional, Markdown for quick, etc.
4. **Generate report** - Call appropriate tool
5. **Provide summary** - Key findings from report
6. **Give access** - Provide file path for download

Remember: You create publication-quality reports that decision-makers rely on.
Make them comprehensive, professional, and actionable.
"""

def create_report_generator_agent():
    """Create and return the Report Generator ADK agent."""
    logger.info("Creating Report Generator agent")
    
    # Check if required dependencies are available
    if not ADK_AVAILABLE:
        raise ImportError("Google ADK not installed - this appears to be a custom framework. Contact your ADK provider for installation instructions.")
    if not GENAI_AVAILABLE:
        raise ImportError("Google GenAI not installed. Install with: pip install google-genai")
    
    retry_config = RetryConfig(
        max_attempts=3,
        initial_delay_seconds=1.0,
        max_delay_seconds=10.0,
        backoff_multiplier=2.0
    )
    
    # Create GenAI client for model access
    genai_client = genai.Client()
    
    agent = LlmAgent(
        name="report_generator",
        model=genai_client,  # Use the GenAI client
        description="Fed Policy Report Generation Agent",
        instruction=AGENT_INSTRUCTION,
        tools=[
            types.FunctionTool(generate_comprehensive_report_tool),
            types.FunctionTool(generate_episode_comparison_report_tool),
            types.FunctionTool(generate_quick_summary_tool),
            types.FunctionTool(generate_custom_report_tool),
            types.FunctionTool(export_report_tool)
        ],
        retry_config=retry_config
    )
    
    logger.info("Report Generator agent created successfully")
    return agent

if __name__ == "__main__":
    agent = create_report_generator_agent()
    print("Report Generator Agent initialized!")
