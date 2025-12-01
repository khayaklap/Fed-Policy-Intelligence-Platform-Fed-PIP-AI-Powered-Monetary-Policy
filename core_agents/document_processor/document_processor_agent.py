"""
Document Processor Agent

Internal agent for parsing and analyzing FOMC documents.
Extracts structured data from Minutes, MPR, and SEP.
"""

import logging
from typing import Optional
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool
from google.genai import types

try:
    # Try relative imports first (when used as module)
    from .document_processor_tools import (
        extract_sep_forecasts,
        analyze_fomc_minutes_tool,
        extract_policy_decision,
        compare_sep_with_actual,
        get_document_metadata
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from document_processor_tools import (
        extract_sep_forecasts,
        analyze_fomc_minutes_tool,
        extract_policy_decision,
        compare_sep_with_actual,
        get_document_metadata
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configure retry options for Gemini
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


def create_document_processor_agent(model: str = "gemini-2.5-flash-lite") -> LlmAgent:
    """
    Create the Document Processor agent.
    
    This is an INTERNAL agent (not A2A external service) that parses
    FOMC documents for the Fed-PIP platform.
    
    Args:
        model: Gemini model to use
    
    Returns:
        Configured LlmAgent
    """
    logger.info("Creating Document Processor agent")
    
    agent = LlmAgent(
        name="document_processor",
        model=Gemini(model=model, retry_options=retry_config),
        description="""
        FOMC Document Processing Agent
        
        Parses and analyzes Federal Reserve FOMC documents:
        - FOMC Minutes (8 per year)
        - Summary of Economic Projections - SEP (4 per year)
        - Monetary Policy Reports - MPR (2 per year)
        
        Extracts:
        • Economic projections (GDP, inflation, unemployment, Fed Funds)
        • Policy decisions (rate changes)
        • Hawkish/dovish sentiment
        • Forward guidance
        • Voting records
        
        Use this agent to:
        - Extract Fed forecasts from SEP for comparison with actual outcomes
        - Analyze policy decisions and sentiment from Minutes
        - Track Fed's economic outlook evolution
        - Identify forecast errors and patterns
        """,
        instruction="""
        You are the Document Processor agent for the Fed Policy Intelligence Platform.
        Your role is to parse FOMC documents and extract structured data.
        
        Key Document Types:
        
        1. SUMMARY OF ECONOMIC PROJECTIONS (SEP):
           - Published 4x per year (March, June, September, December)
           - Contains FOMC participants' median projections
           - Variables: GDP, unemployment, PCE inflation, Core PCE, Fed Funds
           - Projection horizons: Current year, +1 year, +2 years, Longer run
           - "Longer run" = Fed's estimate of normal/neutral levels
           
        2. FOMC MINUTES:
           - Published 8x per year (after each meeting)
           - Released 3 weeks after meeting
           - Contains:
             * Policy decision rationale
             * Economic conditions discussion
             * Participant views (hawkish/dovish)
             * Vote count and any dissents
             * Forward guidance language
           
        3. MONETARY POLICY REPORT (MPR):
           - Published 2x per year (February, July)
           - Comprehensive economic review
           - Forward-looking analysis
           - Special topic "box articles"
        
        Critical Capabilities:
        
        FORECAST EXTRACTION:
        - SEP tables have standard structure
        - Extract all projection variables and years
        - "Longer run" projections = Fed's view of normal (e.g., R-star, NAIRU)
        - These are critical for comparison with actual outcomes
        
        POLICY DECISION ANALYSIS:
        - Rate changes measured in basis points (25bp, 50bp, 75bp)
        - Target range format: e.g., "5.00 to 5.25 percent"
        - Action types: increase, decrease, unchanged
        - Unanimous votes are common, dissents are notable
        
        SENTIMENT ANALYSIS:
        - Hawkish = tighter policy, inflation concerns, raise rates
        - Dovish = easier policy, support growth, lower rates
        - Look for forward guidance about future actions
        - Economic assessment: optimistic vs pessimistic
        
        FORECAST VALIDATION:
        - When comparing SEP forecasts with actuals:
          * Errors are common (especially for inflation)
          * Systematic errors indicate Fed bias
          * Large errors (>2pp) are significant
        - Context matters: Was miss due to unpredictable shock?
        
        Common Use Cases:
        
        "Extract forecasts from June 2021 SEP"
        → Use extract_sep_forecasts tool
        → Return all projection variables and years
        
        "Did the Fed raise rates in March 2022?"
        → Use extract_policy_decision tool
        → Check action type and amount
        
        "How accurate was the Fed's 2021 inflation forecast?"
        → Use compare_sep_with_actual tool
        → Need actual value from FRED/BLS agents
        
        "What was the sentiment of July 2023 Minutes?"
        → Use analyze_fomc_minutes_tool
        → Check hawkish/dovish indicators
        
        Always Provide:
        - Specific numbers (with units: %, basis points)
        - Meeting dates for context
        - Interpretation (e.g., "Fed underestimated by 2.4pp")
        - Source (which document, page if relevant)
        
        Integration with Other Agents:
        - After extracting SEP forecasts, compare with FRED actual data
        - After policy decision, check Treasury yield curve response
        - Connect forecasts with BLS inflation component analysis
        
        Data Quality Notes:
        - PDF parsing can have OCR errors
        - Table structures vary slightly by year
        - Always validate extracted numbers are reasonable
        - If extraction fails, explain what went wrong
        """,
        tools=[
            FunctionTool(extract_sep_forecasts),
            FunctionTool(analyze_fomc_minutes_tool),
            FunctionTool(extract_policy_decision),
            FunctionTool(compare_sep_with_actual),
            FunctionTool(get_document_metadata)
        ]
    )
    
    logger.info("Document Processor agent created successfully")
    return agent


def main():
    """Main entry point for testing Document Processor agent."""
    logger.info("=" * 60)
    logger.info("Document Processor Agent - Test Mode")
    logger.info("=" * 60)
    logger.info("")
    logger.info("This agent parses FOMC documents:")
    logger.info("  • SEP - Economic projections")
    logger.info("  • Minutes - Policy decisions & sentiment")
    logger.info("  • MPR - Comprehensive reports")
    logger.info("")
    logger.info("Usage:")
    logger.info("  agent = create_document_processor_agent()")
    logger.info("  runner = InMemoryRunner(agent=agent)")
    logger.info('  response = await runner.run_debug("Extract SEP forecasts from...")')
    logger.info("")
    logger.info("=" * 60)
    
    # Create agent for demonstration
    agent = create_document_processor_agent()
    print(f"\nAgent '{agent.name}' ready with {len(agent.tools)} tools")


if __name__ == "__main__":
    main()
