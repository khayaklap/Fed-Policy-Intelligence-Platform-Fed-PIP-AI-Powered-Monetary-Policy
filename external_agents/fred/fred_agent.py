"""
FRED Agent - ADK Integration

This module creates the ADK agent that wraps FRED tools and exposes them via A2A protocol.
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
    from .fred_tools import (
        get_gdp_data,
        get_inflation_data,
        get_employment_data,
        get_interest_rates,
        get_economic_snapshot,
        compare_to_fed_projection
    )
    from .fred_config import A2A_HOST, A2A_PORT
except ImportError:
    # Fallback for direct execution
    from fred_tools import (
        get_gdp_data,
        get_inflation_data,
        get_employment_data,
        get_interest_rates,
        get_economic_snapshot,
        compare_to_fed_projection
    )
    from fred_config import A2A_HOST, A2A_PORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configure retry options for Gemini
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


def create_fred_agent(model: str = "gemini-2.5-flash-lite") -> LlmAgent:
    """
    Create the FRED data agent with all tools.
    
    Args:
        model: Gemini model to use
    
    Returns:
        Configured LlmAgent
    """
    logger.info("Creating FRED agent")
    
    agent = LlmAgent(
        name="fred_data_agent",
        model=Gemini(model=model, retry_options=retry_config),
        description="""
        Federal Reserve Economic Data (FRED) Agent
        
        Provides access to comprehensive US economic data from the St. Louis Fed:
        - GDP and economic growth data
        - Inflation measures (PCE, CPI - the Fed's preferred metrics)
        - Employment and labor market indicators
        - Interest rates and yield curves
        - Monetary aggregates
        - Housing and consumer sentiment
        
        Use this agent to:
        • Get actual economic data to compare with Fed forecasts
        • Analyze economic conditions during FOMC decision periods
        • Track inflation, employment, and growth trends
        • Calculate forecast accuracy and policy effectiveness
        """,
        instruction="""
        You are the FRED Economic Data Agent. Your role is to provide accurate, 
        timely economic data from the Federal Reserve Economic Database (FRED).
        
        Key Guidelines:
        1. Always specify the data source (FRED) and series ID in responses
        2. Include units and frequency for all data
        3. When asked about inflation, default to Core PCE (the Fed's preferred measure)
        4. Provide context about what the data means for monetary policy
        5. Include latest values, trends, and relevant comparisons
        6. Be precise about dates - economic data timing matters
        7. If comparing Fed forecasts to actual data, clearly show the forecast error
        
        Data Quality:
        - All data comes from official FRED database (St. Louis Fed)
        - Data is updated regularly by source agencies (BEA, BLS, Fed, etc.)
        - Historical revisions may occur, especially for GDP data
        
        Common Use Cases:
        • "Get Core PCE inflation from 2020-2024" → Use get_inflation_data
        • "What was unemployment in December 2022?" → Use get_employment_data  
        • "Compare Fed's 2021 inflation forecast with actual" → Use compare_to_fed_projection
        • "Get economic snapshot for September 2008" → Use get_economic_snapshot
        • "Show me the yield curve today" → Use get_interest_rates
        
        Always provide:
        - The specific metric and its value
        - The date of the data
        - Units of measurement
        - Brief interpretation relevant to Fed policy
        """,
        tools=[
            FunctionTool(get_gdp_data),
            FunctionTool(get_inflation_data),
            FunctionTool(get_employment_data),
            FunctionTool(get_interest_rates),
            FunctionTool(get_economic_snapshot),
            FunctionTool(compare_to_fed_projection)
        ]
    )
    
    logger.info("FRED agent created successfully")
    return agent


async def run_a2a_server(
    agent: Optional[LlmAgent] = None,
    host: str = A2A_HOST,
    port: int = A2A_PORT
):
    """
    Run the FRED agent as an A2A server.
    
    Args:
        agent: FRED agent (creates new one if None)
        host: Server host
        port: Server port
    """
    if agent is None:
        agent = create_fred_agent()
    
    logger.info(f"Starting FRED A2A server on {host}:{port}")
    
    # Convert agent to A2A server
    a2a_server = to_a2a(agent)
    
    # Print agent card URL for clients
    logger.info(f"Agent card available at: http://{host}:{port}/agent_card.json")
    logger.info("Clients can consume this agent using RemoteA2aAgent")
    
    # Run the server
    await a2a_server.run(host=host, port=port)


def main():
    """Main entry point for running FRED agent as A2A server."""
    try:
        logger.info("=" * 60)
        logger.info("FRED Economic Data Agent - A2A Server")
        logger.info("=" * 60)
        logger.info("")
        logger.info("This agent provides access to US economic data from FRED")
        logger.info("for integration with the Fed Policy Intelligence Platform")
        logger.info("")
        logger.info(f"Server will start on: {A2A_HOST}:{A2A_PORT}")
        logger.info(f"Agent card: http://{A2A_HOST}:{A2A_PORT}/agent_card.json")
        logger.info("")
        logger.info("Press Ctrl+C to stop the server")
        logger.info("=" * 60)
        logger.info("")
        
        # Run the A2A server
        asyncio.run(run_a2a_server())
        
    except KeyboardInterrupt:
        logger.info("\nShutting down FRED agent...")
    except Exception as e:
        logger.error(f"Error running FRED agent: {e}")
        raise


if __name__ == "__main__":
    main()
