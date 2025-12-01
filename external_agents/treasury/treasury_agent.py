"""
Treasury Agent - ADK Integration

U.S. Treasury yield curve and TIPS agent for market-based inflation expectations
and monetary policy stance assessment. Exposes tools via A2A protocol.
"""

import asyncio
import logging
from typing import Optional
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool
from google.adk.a2a import to_a2a
from google.genai import types

# Handle relative imports for package usage and absolute for direct execution
try:
    from .treasury_tools import (
        get_yield_curve_data,
        get_market_inflation_expectations,
        analyze_monetary_policy_stance,
        detect_yield_curve_inversion,
        compare_fed_forecast_vs_market,
        get_yield_curve_evolution
    )
    from .treasury_config import A2A_HOST, A2A_PORT
except ImportError:
    # Fallback for direct execution
    from treasury_tools import (
        get_yield_curve_data,
        get_market_inflation_expectations,
        analyze_monetary_policy_stance,
        detect_yield_curve_inversion,
        compare_fed_forecast_vs_market,
        get_yield_curve_evolution
    )
    from treasury_config import A2A_HOST, A2A_PORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configure retry options for Gemini
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


def create_treasury_agent(model: str = "gemini-2.5-flash-lite") -> LlmAgent:
    """
    Create the Treasury market data agent with all tools.
    
    Args:
        model: Gemini model to use
    
    Returns:
        Configured LlmAgent
    """
    logger.info("Creating Treasury agent")
    
    agent = LlmAgent(
        name="treasury_market_agent",
        model=Gemini(model=model, retry_options=retry_config),
        description="""
        U.S. Treasury Market Data Agent
        
        Provides Treasury yield curves, TIPS breakeven inflation rates, and
        monetary policy stance analysis:
        - Treasury yield curves (all maturities: 1M to 30Y)
        - TIPS breakeven rates (market-implied inflation expectations)
        - Real yields (inflation-adjusted returns)
        - Yield curve inversion detection (recession indicator)
        - Monetary policy stance assessment
        
        Use this agent to:
        • Get market-based inflation expectations (TIPS breakevens)
        • Assess if Fed policy is restrictive or accommodative (real yields)
        • Detect recession signals (yield curve inversions)
        • Compare Fed forecasts with market expectations
        • Analyze yield curve evolution during policy changes
        """,
        instruction="""
        You are the Treasury Market Data Agent. Your role is to provide yield curve
        data, market-based inflation expectations, and monetary policy analysis.
        
        Key Expertise Areas:
        
        1. YIELD CURVE ANALYSIS:
           - Normal curve: long-term > short-term (healthy growth)
           - Flat curve: uncertainty about future
           - Inverted curve: recession signal (short > long)
           - 2s10s spread: most watched (2-year vs 10-year)
           - Historical: Every recession since 1970 preceded by inversion
        
        2. TIPS BREAKEVEN INFLATION:
           - Breakeven = Nominal yield - TIPS yield
           - Represents market's average inflation expectation
           - 10Y breakeven: most liquid and watched
           - 5y5y forward: Fed's preferred "anchoring" measure
           - Well-anchored around 2% = Fed credibility intact
           - Rising above 2.5% = De-anchoring concerns
        
        3. REAL YIELDS (Policy Stance):
           - Real yield = TIPS yield = inflation-adjusted return
           - Compare to neutral rate (R-star ≈ 0.5%)
           - Real yield > R-star = restrictive policy
           - Real yield < R-star = accommodative policy
           - Current 10Y real yield vs neutral tells policy stance
        
        4. RECESSION INDICATORS:
           - 2s10s inversion: Lead time 6-18 months
           - 3m10y inversion: Alternative measure
           - Inversion + un-inversion = recession often follows
        
        5. FED CREDIBILITY:
           - Compare Fed forecasts with TIPS breakevens
           - Market > Fed = skepticism about inflation control
           - Fed > Market = potential over-tightening risk
           - Convergence = aligned expectations
        
        Common Queries & How to Answer:
        
        "Is the yield curve inverted?"
        → Use detect_yield_curve_inversion() for detailed analysis
        
        "What does the market expect for inflation?"
        → Use get_market_inflation_expectations() for TIPS breakevens
        
        "Is Fed policy restrictive?"
        → Use analyze_monetary_policy_stance() with real yields
        
        "Compare Fed vs market inflation expectations"
        → Use compare_fed_forecast_vs_market()
        
        "How did the yield curve change during 2022 tightening?"
        → Use get_yield_curve_evolution()
        
        Always Provide:
        - Specific yields and spreads with units (%, bp)
        - Trend: rising, falling, stable?
        - Context: is this high/low historically?
        - Fed policy implications
        - Recession probability when relevant
        
        Key Relationships:
        - Nominal yield = Real yield + Breakeven inflation
        - If TIPS breakeven rising → inflation expectations increasing
        - If real yields rising → policy tightening
        - If curve inverts → recession signal
        
        Data Quality Notes:
        - Source: U.S. Treasury via FRED
        - Frequency: Daily (business days)
        - TIPS: Can be negative during low inflation periods
        - Weekends/holidays: No data, use prior business day
        """,
        tools=[
            FunctionTool(get_yield_curve_data),
            FunctionTool(get_market_inflation_expectations),
            FunctionTool(analyze_monetary_policy_stance),
            FunctionTool(detect_yield_curve_inversion),
            FunctionTool(compare_fed_forecast_vs_market),
            FunctionTool(get_yield_curve_evolution)
        ]
    )
    
    logger.info("Treasury agent created successfully")
    return agent


async def run_a2a_server(
    agent: Optional[LlmAgent] = None,
    host: str = A2A_HOST,
    port: int = A2A_PORT
):
    """
    Run the Treasury agent as an A2A server.
    
    Args:
        agent: Treasury agent (creates new one if None)
        host: Server host
        port: Server port
    """
    if agent is None:
        agent = create_treasury_agent()
    
    logger.info(f"Starting Treasury A2A server on {host}:{port}")
    
    # Convert agent to A2A server
    a2a_server = to_a2a(agent)
    
    # Print agent card URL for clients
    logger.info(f"Agent card available at: http://{host}:{port}/agent_card.json")
    logger.info("Clients can consume this agent using RemoteA2aAgent")
    
    # Run the server
    await a2a_server.run(host=host, port=port)


def main():
    """Main entry point for running Treasury agent as A2A server."""
    try:
        logger.info("=" * 60)
        logger.info("Treasury Market Data Agent - A2A Server")
        logger.info("=" * 60)
        logger.info("")
        logger.info("This agent provides yield curves, TIPS breakevens, and")
        logger.info("monetary policy analysis for the Fed Policy Intelligence Platform")
        logger.info("")
        logger.info(f"Server will start on: {A2A_HOST}:{A2A_PORT}")
        logger.info(f"Agent card: http://{A2A_HOST}:{A2A_PORT}/agent_card.json")
        logger.info("")
        logger.info("Key capabilities:")
        logger.info("  • Treasury yield curves (1M to 30Y)")
        logger.info("  • TIPS breakeven inflation (market expectations)")
        logger.info("  • Real yields & policy stance assessment")
        logger.info("  • Yield curve inversion detection")
        logger.info("  • Fed forecast vs market comparison")
        logger.info("")
        logger.info("Press Ctrl+C to stop the server")
        logger.info("=" * 60)
        logger.info("")
        
        # Run the A2A server
        asyncio.run(run_a2a_server())
        
    except KeyboardInterrupt:
        logger.info("\nShutting down Treasury agent...")
    except Exception as e:
        logger.error(f"Error running Treasury agent: {e}")
        raise


if __name__ == "__main__":
    main()
