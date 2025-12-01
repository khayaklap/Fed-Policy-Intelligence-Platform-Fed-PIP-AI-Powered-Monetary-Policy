"""
Updated Orchestrator Agent - Uses REAL Agent Coordination

This replaces the simulated orchestrator with true multi-agent integration.
"""

import asyncio
import logging
from typing import Dict, List, Optional
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool
from google.genai import types

# Import REAL coordinator (not simulated!)
try:
    # Try relative imports first (when used as module)
    from .agent_coordinator import create_real_coordinator
    
    # Import existing components (these are already good)
    from .query_router import QueryRouter
    from .orchestrator_config import AGENT_REGISTRY, ORCHESTRATOR_CONFIG
except ImportError:
    # Fall back to absolute imports (when run directly)
    from agent_coordinator import create_real_coordinator
    
    # Import existing components (these are already good)
    from query_router import QueryRouter
    from orchestrator_config import AGENT_REGISTRY, ORCHESTRATOR_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configure retry options
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


class RealOrchestrator:
    """
    Real orchestrator that coordinates 9 agents.
    
    NO SIMULATION - This actually calls all agents!
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize orchestrator with real agent coordination.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or ORCHESTRATOR_CONFIG
        
        # Initialize query router (this is already good!)
        self.router = QueryRouter(self.config)
        
        # Initialize REAL coordinator (not simulated!)
        self.coordinator = create_real_coordinator(self.config)
        
        logger.info("Real orchestrator initialized (no simulation)")
    
    async def process_query(self, query: str) -> Dict:
        """
        Process a query using real multi-agent coordination.
        
        Args:
            query: Natural language query
        
        Returns:
            Response with results from all relevant agents
        """
        logger.info(f"Processing query: {query}")
        
        # Step 1: Route query to determine which agents to use
        routing = self.router.route_query(query)
        
        logger.info(f"Routing selected {len(routing['selected_agents'])} agents: {routing['selected_agents']}")
        
        # Step 2: Create task for coordinator
        task = {
            'query': query,
            'agents_needed': routing['selected_agents'],
            'query_type': routing['query_type'],
            'complexity': routing['complexity'],
            'parameters': routing.get('parameters', {})
        }
        
        # Step 3: Coordinate agents (THIS IS REAL!)
        try:
            results = await self.coordinator.coordinate_agents(task)
            
            return {
                'status': 'success',
                'query': query,
                'routing': routing,
                'results': results,
                'response': results.get('synthesized', 'No synthesis available')
            }
            
        except Exception as e:
            logger.error(f"Error coordinating agents: {e}")
            return {
                'status': 'error',
                'query': query,
                'error': str(e)
            }
    
    async def analyze_fed_forecast_accuracy(
        self,
        forecast_date: str,
        indicator: str,
        projected_value: float,
        actual_date: str
    ) -> Dict:
        """
        Comprehensive forecast accuracy analysis using multiple agents.
        
        THIS IS A REAL USE CASE showing multi-agent coordination!
        
        Args:
            forecast_date: When Fed made forecast (e.g., "2021-06-16")
            indicator: What was forecast ("inflation", "unemployment", "gdp_growth")
            projected_value: Fed's projection (e.g., 2.0)
            actual_date: When to check actual (e.g., "2021-12-31")
        
        Returns:
            Comprehensive analysis from 4+ agents
        """
        query = f"Analyze Fed's {indicator} forecast accuracy"
        
        task = {
            'query': query,
            'agents_needed': ['document_processor', 'fred', 'bls', 'treasury', 'comparative_analyzer'],
            'query_type': 'forecast_comparison',
            'parameters': {
                'forecast_date': forecast_date,
                'indicator': indicator,
                'projection_value': projected_value,
                'actual_date': actual_date
            }
        }
        
        results = await self.coordinator.coordinate_agents(task)
        
        # Extract key findings
        fed_data = results['results'].get('fred', {}).get('data', {})
        treasury_data = results['results'].get('treasury', {}).get('data', {})
        bls_data = results['results'].get('bls', {}).get('data', {})
        
        return {
            'forecast': {
                'date': forecast_date,
                'indicator': indicator,
                'projected': projected_value
            },
            'actual': fed_data,
            'market_expected': treasury_data,
            'drivers': bls_data,
            'analysis': results.get('synthesized'),
            'full_results': results
        }


# Tool functions for ADK integration
async def analyze_inflation_episode_tool(
    start_date: str,
    end_date: str,
    episode_name: Optional[str] = None
) -> Dict:
    """
    Analyze an inflation episode using all relevant agents.
    
    Example:
        >>> analyze_inflation_episode_tool("2021-01-01", "2023-12-31", "2022_inflation_surge")
    
    Calls:
        - FRED: Actual inflation data
        - BLS: Component breakdown
        - Treasury: Market expectations
        - Policy Analyzer: Fed's response
        - Comparative Analyzer: Historical comparison
    """
    orchestrator = RealOrchestrator()
    
    task = {
        'query': f"Comprehensive analysis of inflation from {start_date} to {end_date}",
        'agents_needed': ['fred', 'bls', 'treasury', 'policy_analyzer', 'comparative_analyzer'],
        'query_type': 'comprehensive_analysis',
        'parameters': {
            'start_date': start_date,
            'end_date': end_date,
            'episode_name': episode_name
        }
    }
    
    return await orchestrator.coordinator.coordinate_agents(task)


async def validate_fed_forecast_tool(
    forecast_date: str,
    indicator: str,
    projected_value: float,
    actual_date: str
) -> Dict:
    """
    Validate a Fed forecast using actual data.
    
    Example:
        >>> validate_fed_forecast_tool(
        ...     forecast_date="2021-06-16",
        ...     indicator="inflation",
        ...     projected_value=2.0,
        ...     actual_date="2021-12-31"
        ... )
    
    Calls:
        - Document Processor: Extract SEP forecast
        - FRED: Get actual outcome
        - Treasury: Get market expectations
        - BLS: Explain what drove difference
    """
    orchestrator = RealOrchestrator()
    return await orchestrator.analyze_fed_forecast_accuracy(
        forecast_date, indicator, projected_value, actual_date
    )


async def compare_policy_periods_tool(
    period1_start: str,
    period1_end: str,
    period2_start: str,
    period2_end: str
) -> Dict:
    """
    Compare two policy periods across all dimensions.
    
    Example:
        >>> compare_policy_periods_tool(
        ...     "2008-01-01", "2009-12-31",  # GFC
        ...     "2020-01-01", "2021-12-31"   # COVID
        ... )
    
    Calls:
        - FRED: Economic data for both periods
        - Policy Analyzer: Fed's stance in each
        - Comparative Analyzer: Historical comparison
        - Trend Tracker: Long-term context
    """
    orchestrator = RealOrchestrator()
    
    task = {
        'query': f"Compare policy periods: {period1_start}-{period1_end} vs {period2_start}-{period2_end}",
        'agents_needed': ['fred', 'policy_analyzer', 'comparative_analyzer', 'trend_tracker'],
        'query_type': 'period_comparison',
        'parameters': {
            'period1_start': period1_start,
            'period1_end': period1_end,
            'period2_start': period2_start,
            'period2_end': period2_end
        }
    }
    
    return await orchestrator.coordinator.coordinate_agents(task)


async def analyze_current_conditions_tool() -> Dict:
    """
    Comprehensive analysis of current economic/policy conditions.
    
    Calls ALL agents to get complete picture:
        - FRED: Latest economic data
        - BLS: Current inflation drivers
        - Treasury: Market expectations & recession signals
        - Policy Analyzer: Current Fed stance
        - Trend Tracker: Where we are in the cycle
    """
    orchestrator = RealOrchestrator()
    
    task = {
        'query': "Comprehensive analysis of current economic and policy conditions",
        'agents_needed': ['fred', 'bls', 'treasury', 'policy_analyzer', 'trend_tracker'],
        'query_type': 'current_conditions',
        'parameters': {}
    }
    
    return await orchestrator.coordinator.coordinate_agents(task)


async def generate_comprehensive_report_tool(
    topic: str,
    start_date: str,
    end_date: str,
    report_type: str = "comprehensive"
) -> Dict:
    """
    Generate comprehensive report using all agents.
    
    Example:
        >>> generate_comprehensive_report_tool(
        ...     topic="2022 Inflation Analysis",
        ...     start_date="2022-01-01",
        ...     end_date="2022-12-31",
        ...     report_type="comprehensive"
        ... )
    
    Calls:
        - All 6 core agents
        - All 3 external agents
        - Report Generator for final output
    """
    orchestrator = RealOrchestrator()
    
    task = {
        'query': f"Generate comprehensive report: {topic}",
        'agents_needed': [
            'document_processor', 'policy_analyzer', 'trend_tracker',
            'comparative_analyzer', 'fred', 'bls', 'treasury'
        ],
        'query_type': 'report_generation',
        'parameters': {
            'topic': topic,
            'start_date': start_date,
            'end_date': end_date,
            'report_type': report_type
        }
    }
    
    return await orchestrator.coordinator.coordinate_agents(task)


def create_orchestrator_agent(model: str = "gemini-2.5-flash-lite") -> LlmAgent:
    """
    Create orchestrator LLM agent with real coordination tools.
    
    Args:
        model: Gemini model to use
    
    Returns:
        Configured orchestrator agent
    """
    logger.info("Creating real orchestrator agent")
    
    agent = LlmAgent(
        name="fed_pip_orchestrator",
        model=Gemini(model=model, retry_options=retry_config),
        description="""
        Fed Policy Intelligence Platform Orchestrator
        
        Coordinates 9 specialized agents to provide comprehensive Fed analysis:
        
        CORE AGENTS (6):
        - Document Processor: Parse 68 FOMC documents
        - Policy Analyzer: Classify stance, detect regime changes
        - Trend Tracker: Long-term patterns, Taylor Rule
        - Comparative Analyzer: Historical comparisons, 13 episodes
        - Report Generator: Professional PDF/DOCX reports
        - [Orchestrator: This agent]
        
        EXTERNAL DATA AGENTS (3):
        - FRED: 22 series - actual economic outcomes
        - BLS: 32 series - inflation component breakdown
        - Treasury: 24 series - market expectations, yield curve
        
        Use this orchestrator for multi-dimensional analysis that requires
        combining insights from multiple agents.
        """,
        instruction="""
        You are the Fed Policy Intelligence Platform orchestrator.
        
        Your role is to coordinate multiple specialized agents to answer
        complex queries about Fed monetary policy.
        
        When to use which tool:
        
        1. analyze_inflation_episode_tool:
           - User asks about a specific time period's inflation
           - Need comprehensive multi-agent analysis
           - Example: "Analyze 2022 inflation surge"
        
        2. validate_fed_forecast_tool:
           - User asks about Fed forecast accuracy
           - Need to compare projection vs actual vs market
           - Example: "Was the Fed's 2021 forecast accurate?"
        
        3. compare_policy_periods_tool:
           - User wants to compare two historical periods
           - Example: "Compare GFC vs COVID response"
        
        4. analyze_current_conditions_tool:
           - User asks "what's happening now?"
           - Need snapshot across all dimensions
        
        5. generate_comprehensive_report_tool:
           - User wants formal report/analysis
           - Example: "Generate report on 2022-2023 tightening cycle"
        
        Key Capabilities:
        - Combines actual data (FRED), components (BLS), market expectations (Treasury)
        - Compares Fed forecasts with outcomes
        - Historical pattern matching
        - Policy stance evolution
        - Recession signal detection
        
        Always explain which agents were used and why.
        """,
        tools=[
            FunctionTool(analyze_inflation_episode_tool),
            FunctionTool(validate_fed_forecast_tool),
            FunctionTool(compare_policy_periods_tool),
            FunctionTool(analyze_current_conditions_tool),
            FunctionTool(generate_comprehensive_report_tool)
        ]
    )
    
    logger.info("Real orchestrator agent created successfully")
    return agent


async def main():
    """Example usage of real orchestrator."""
    orchestrator = RealOrchestrator()
    
    # Example 1: Simple query
    print("Example 1: Simple inflation query")
    result = await orchestrator.process_query("What was inflation in 2022?")
    print(result.get('response'))
    print()
    
    # Example 2: Forecast validation
    print("Example 2: Validate Fed's 2021 forecast")
    result = await orchestrator.analyze_fed_forecast_accuracy(
        forecast_date="2021-06-16",
        indicator="inflation",
        projected_value=2.0,
        actual_date="2021-12-31"
    )
    print(result.get('analysis'))
    print()


if __name__ == "__main__":
    asyncio.run(main())
