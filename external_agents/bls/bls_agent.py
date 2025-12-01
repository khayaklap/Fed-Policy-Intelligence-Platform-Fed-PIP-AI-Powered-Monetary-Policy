"""
BLS Agent - ADK Integration

Bureau of Labor Statistics agent for detailed inflation analysis.
Exposes BLS tools via A2A protocol.
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
    from .bls_tools import (
        get_cpi_components,
        get_ppi_data,
        get_employment_cost_index,
        compare_inflation_measures,
        analyze_inflation_drivers
    )
    from .bls_config import A2A_HOST, A2A_PORT
except ImportError:
    # Fallback for direct execution
    from bls_tools import (
        get_cpi_components,
        get_ppi_data,
        get_employment_cost_index,
        compare_inflation_measures,
        analyze_inflation_drivers
    )
    from bls_config import A2A_HOST, A2A_PORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configure retry options for Gemini
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


def create_bls_agent(model: str = "gemini-2.5-flash-lite") -> LlmAgent:
    """
    Create the BLS inflation analysis agent with all tools.
    
    Args:
        model: Gemini model to use
    
    Returns:
        Configured LlmAgent
    """
    logger.info("Creating BLS agent")
    
    agent = LlmAgent(
        name="bls_inflation_agent",
        model=Gemini(model=model, retry_options=retry_config),
        description="""
        Bureau of Labor Statistics (BLS) Inflation Analysis Agent
        
        Provides detailed inflation component analysis and labor cost data:
        - CPI component breakdowns (food, energy, shelter, services, goods)
        - Producer Price Index (PPI) - leading indicator for CPI
        - Employment Cost Index (ECI) - wage pressure measurement
        - Import/Export price indices - global inflation transmission
        - Productivity and unit labor costs
        
        Use this agent to:
        • Identify what's driving inflation (energy? shelter? services?)
        • Detect early inflation signals via PPI
        • Assess wage-price spiral risks via ECI
        • Understand inflation composition (goods vs services)
        • Analyze persistence vs transitory inflation
        """,
        instruction="""
        You are the BLS Inflation Analysis Agent. Your role is to provide 
        detailed breakdowns of inflation components and labor costs.
        
        Key Expertise Areas:
        
        1. CPI COMPONENT ANALYSIS:
           - Food: volatile, weather/supply-sensitive
           - Energy: highly volatile, geopolitical
           - Shelter: ~32% of CPI, sticky/persistent, 12-18 month lag
           - Services: wage-driven, sticky
           - Goods: supply chain sensitive
        
        2. INFLATION TAXONOMY:
           - Headline CPI: includes all items
           - Core CPI: excludes food/energy (Fed's focus for persistence)
           - Core Services: most persistent component
           - Core Goods: more responsive to supply/demand
        
        3. LEADING INDICATORS:
           - PPI typically leads CPI by 3-6 months
           - Import prices transmit global inflation
           - Rising PPI → future CPI pressure
        
        4. WAGE-PRICE DYNAMICS:
           - ECI is Fed's preferred wage measure
           - Rising ECI → wage-price spiral risk
           - Compare ECI with productivity for unit labor costs
        
        Common Queries & How to Answer:
        
        "What's driving inflation?"
        → Use analyze_inflation_drivers() for comprehensive breakdown
        
        "Is inflation broadening or narrowing?"
        → Compare components over time, check if core > headline
        
        "What do leading indicators suggest?"
        → Check PPI trends, import prices
        
        "Is there wage-price spiral risk?"
        → Check ECI growth vs productivity, compare to inflation
        
        "Energy vs shelter: which matters more?"
        → Energy is volatile but transitory
        → Shelter is persistent and largest CPI component
        → Fed focuses on shelter for policy decisions
        
        Always Provide:
        - Specific percentages and year-over-year changes
        - Context: is this high/low historically?
        - Trend: rising, falling, or stable?
        - Fed policy implications
        - Persistence assessment (transitory vs sticky)
        
        Data Quality Notes:
        - CPI data: monthly, ~2-week lag from month end
        - PPI data: monthly, similar timing
        - ECI data: quarterly, more stable than monthly wages
        - All data subject to revisions (typically minor for CPI)
        """,
        tools=[
            FunctionTool(get_cpi_components),
            FunctionTool(get_ppi_data),
            FunctionTool(get_employment_cost_index),
            FunctionTool(compare_inflation_measures),
            FunctionTool(analyze_inflation_drivers)
        ]
    )
    
    logger.info("BLS agent created successfully")
    return agent


async def run_a2a_server(
    agent: Optional[LlmAgent] = None,
    host: str = A2A_HOST,
    port: int = A2A_PORT
):
    """
    Run the BLS agent as an A2A server.
    
    Args:
        agent: BLS agent (creates new one if None)
        host: Server host
        port: Server port
    """
    if agent is None:
        agent = create_bls_agent()
    
    logger.info(f"Starting BLS A2A server on {host}:{port}")
    
    # Convert agent to A2A server
    a2a_server = to_a2a(agent)
    
    # Print agent card URL for clients
    logger.info(f"Agent card available at: http://{host}:{port}/agent_card.json")
    logger.info("Clients can consume this agent using RemoteA2aAgent")
    
    # Run the server
    await a2a_server.run(host=host, port=port)


def main():
    """Main entry point for running BLS agent as A2A server."""
    try:
        logger.info("=" * 60)
        logger.info("BLS Inflation Analysis Agent - A2A Server")
        logger.info("=" * 60)
        logger.info("")
        logger.info("This agent provides detailed inflation component analysis")
        logger.info("for the Fed Policy Intelligence Platform")
        logger.info("")
        logger.info(f"Server will start on: {A2A_HOST}:{A2A_PORT}")
        logger.info(f"Agent card: http://{A2A_HOST}:{A2A_PORT}/agent_card.json")
        logger.info("")
        logger.info("Key capabilities:")
        logger.info("  • CPI component breakdowns")
        logger.info("  • Producer Price Index (leading indicator)")
        logger.info("  • Employment Cost Index (wage pressures)")
        logger.info("  • Comprehensive inflation driver analysis")
        logger.info("")
        logger.info("Press Ctrl+C to stop the server")
        logger.info("=" * 60)
        logger.info("")
        
        # Run the A2A server
        asyncio.run(run_a2a_server())
        
    except KeyboardInterrupt:
        logger.info("\nShutting down BLS agent...")
    except Exception as e:
        logger.error(f"Error running BLS agent: {e}")
        raise


if __name__ == "__main__":
    main()
