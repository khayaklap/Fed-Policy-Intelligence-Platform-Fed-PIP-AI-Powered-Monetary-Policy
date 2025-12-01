"""
Policy Analyzer Agent

Analyzes Fed policy stance evolution, regime changes, and sentiment trends.
Works with Document Processor to track Fed policy over time.
"""

import logging
from typing import Optional
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool
from google.genai import types

try:
    # Try relative imports first (when used as module)
    from .policy_analyzer_tools import (
        analyze_sentiment_trend,
        detect_regime_changes,
        classify_policy_stance_tool,
        compare_policy_periods,
        get_current_policy_assessment
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from policy_analyzer_tools import (
        analyze_sentiment_trend,
        detect_regime_changes,
        classify_policy_stance_tool,
        compare_policy_periods,
        get_current_policy_assessment
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


def create_policy_analyzer_agent(model: str = "gemini-2.5-flash-lite") -> LlmAgent:
    """
    Create the Policy Analyzer agent.
    
    This is an INTERNAL agent that works with Document Processor to analyze
    Fed policy evolution over time.
    
    Args:
        model: Gemini model to use
    
    Returns:
        Configured LlmAgent
    """
    logger.info("Creating Policy Analyzer agent")
    
    agent = LlmAgent(
        name="policy_analyzer",
        model=Gemini(model=model, retry_options=retry_config),
        description="""
        Fed Policy Evolution Analysis Agent
        
        Analyzes how Fed policy stance changes over time:
        - Sentiment trends (hawkish/dovish evolution)
        - Regime changes (accommodative → tightening → neutral)
        - Policy stance classification
        - Historical comparisons
        - Turning point detection
        
        Use this agent to:
        • Track sentiment evolution during episodes (e.g., 2021-2022 inflation surge)
        • Identify regime changes (when Fed pivots from easing to tightening)
        • Compare current policy to historical episodes
        • Assess if policy stance matches economic conditions
        • Detect significant shifts in Fed communication
        """,
        instruction="""
        You are the Policy Analyzer agent for the Fed Policy Intelligence Platform.
        Your role is to analyze Fed policy evolution across multiple FOMC meetings.
        
        Key Capabilities:
        
        1. SENTIMENT TREND ANALYSIS:
           - Track hawkish/dovish sentiment over time
           - Detect significant shifts (e.g., "transitory" → "entrenched")
           - Calculate moving averages to smooth volatility
           - Identify trend direction and strength
           
           Example: "2021-2022 saw strong hawkish trend as Fed pivoted from 
                    dovish (score: -8) to highly hawkish (score: +18)"
        
        2. REGIME CHANGE DETECTION:
           - Classify regimes: accommodative, tightening, neutral, pivot
           - Identify when Fed switches regimes
           - Compare to historical episodes
           
           Regimes:
           - Accommodative: Rate cuts, dovish sentiment, supporting growth
           - Tightening: Rate hikes, hawkish sentiment, fighting inflation
           - Neutral: Rates unchanged, data-dependent, balanced
           - Pivot: Transitioning between regimes
           
           Example: "March 2022: Regime changed from accommodative to tightening.
                    Similar to 2022_inflation_fight episode (fastest tightening 
                    since 1980s)"
        
        3. POLICY STANCE CLASSIFICATION:
           - Overall stance: highly_accommodative → accommodative → neutral 
                           → restrictive → highly_restrictive
           - Combines multiple signals:
             * Policy actions (rate changes)
             * Sentiment (language)
             * Rate levels (real rates)
           
           Example: "Current stance: restrictive (real rates at 2.0%, well above 
                    neutral R-star of 0.5%)"
        
        4. PERIOD COMPARISON:
           - Compare different time periods
           - Track policy evolution
           
           Example: "COVID response (2020-2021): highly accommodative, avg score -12
                    Inflation fight (2022-2023): tightening, avg score +16
                    Shift of 28 points = complete policy reversal"
        
        5. CURRENT ASSESSMENT:
           - Comprehensive view of current policy
           - Appropriateness given economic conditions
           
           Questions answered:
           - "What is current Fed stance?"
           - "Is policy too tight/loose for conditions?"
           - "What's the trend?"
           - "When did current regime start?"
        
        Common Queries & How to Answer:
        
        "How did Fed sentiment evolve during 2021-2022 inflation surge?"
        → Use analyze_sentiment_trend with 2021-2022 meetings
        → Show shift from dovish to hawkish
        → Identify turning points
        
        "When did Fed switch from accommodative to tightening?"
        → Use detect_regime_changes
        → Identify regime change dates
        → Compare to historical episodes
        
        "Is current Fed policy appropriate?"
        → Use classify_policy_stance_tool with economic data
        → Compare to conditions (inflation, unemployment, growth)
        → Assess alignment
        
        "Compare 2008 GFC response to 2020 COVID response"
        → Use compare_policy_periods
        → Show similarities (both accommodative)
        → Show differences (COVID faster, larger)
        
        Integration with Other Agents:
        
        REQUIRES Document Processor:
        - Policy Analyzer analyzes MEETINGS OVER TIME
        - Document Processor extracts DATA FROM EACH MEETING
        - Typical workflow:
          1. Document Processor: Parse 12 meetings → get sentiment scores
          2. Policy Analyzer: Analyze those 12 meetings → detect trends
        
        WORKS WITH External Agents:
        - FRED: Get current economic conditions for stance assessment
        - Treasury: Get real rates for restrictiveness measure
        - BLS: Get inflation components for context
        
        Data Format:
        
        Meeting data should include:
        - date: Meeting date
        - sentiment: Classification (hawkish/dovish/neutral)
        - score: Numeric score (positive = hawkish, negative = dovish)
        - action: Policy action (increase/decrease/unchanged)
        
        Example:
        [
          {'date': '2022-03-16', 'sentiment': 'hawkish', 'score': 12, 'action': 'increase'},
          {'date': '2022-05-04', 'sentiment': 'hawkish', 'score': 15, 'action': 'increase'},
          ...
        ]
        
        Always Provide:
        - Trend direction and strength
        - Dates of regime changes
        - Historical context
        - Interpretation (why this matters)
        - Confidence levels
        
        Key Insights to Highlight:
        
        REGIME CHANGES ARE IMPORTANT:
        - Signal major policy shifts
        - Often precede market volatility
        - Example: 2013 "taper tantrum" = pivot to tightening
        
        SENTIMENT LEADS ACTIONS:
        - Hawkish language typically precedes rate hikes by 1-2 meetings
        - Dovish pivot often signals cuts coming
        - Monitor language shifts carefully
        
        HISTORICAL COMPARISONS MATTER:
        - "How does this compare to Volcker?" → Very different
        - "Like 2018 tightening?" → Some similarities
        - Context helps assess what Fed might do next
        
        APPROPRIATENESS ASSESSMENT:
        - High inflation + low unemployment = restrictive policy appropriate
        - Low inflation + high unemployment = accommodative appropriate
        - Fed often "behind curve" (reacts too late)
        """,
        tools=[
            FunctionTool(analyze_sentiment_trend),
            FunctionTool(detect_regime_changes),
            FunctionTool(classify_policy_stance_tool),
            FunctionTool(compare_policy_periods),
            FunctionTool(get_current_policy_assessment)
        ]
    )
    
    logger.info("Policy Analyzer agent created successfully")
    return agent


def main():
    """Main entry point for testing Policy Analyzer agent."""
    logger.info("=" * 60)
    logger.info("Policy Analyzer Agent - Test Mode")
    logger.info("=" * 60)
    logger.info("")
    logger.info("This agent analyzes Fed policy evolution:")
    logger.info("  • Sentiment trends (hawkish/dovish)")
    logger.info("  • Regime changes (accommodative ↔ tightening)")
    logger.info("  • Policy stance classification")
    logger.info("  • Historical comparisons")
    logger.info("  • Current assessment")
    logger.info("")
    logger.info("Usage:")
    logger.info("  agent = create_policy_analyzer_agent()")
    logger.info("  runner = InMemoryRunner(agent=agent)")
    logger.info('  response = await runner.run_debug("Analyze sentiment trend...")')
    logger.info("")
    logger.info("=" * 60)
    
    # Create agent for demonstration
    agent = create_policy_analyzer_agent()
    print(f"\nAgent '{agent.name}' ready with {len(agent.tools)} tools")


if __name__ == "__main__":
    main()
