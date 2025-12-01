"""
FRED Agent Tests

Test the FRED agent locally and via A2A protocol.
"""

import asyncio
import pytest

# Handle relative imports for package usage and absolute for direct execution
try:
    from .fred_agent import create_fred_agent
except ImportError:
    from fred_agent import create_fred_agent

from google.adk.runners import InMemoryRunner
from google.adk.a2a import RemoteA2aAgent


# ============================================================================
# Direct Agent Tests (without A2A)
# ============================================================================

@pytest.mark.asyncio
async def test_fred_agent_inflation_query():
    """Test querying inflation data directly."""
    agent = create_fred_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        "What was Core PCE inflation in December 2022?"
    )
    
    print("\n" + "="*60)
    print("Test: Inflation Query")
    print("="*60)
    print(response)
    assert response is not None


@pytest.mark.asyncio
async def test_fred_agent_employment_query():
    """Test querying employment data."""
    agent = create_fred_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        "Get unemployment rate and nonfarm payrolls for 2023"
    )
    
    print("\n" + "="*60)
    print("Test: Employment Query")
    print("="*60)
    print(response)
    assert response is not None


@pytest.mark.asyncio
async def test_fred_agent_forecast_comparison():
    """Test comparing Fed forecast with actual data."""
    agent = create_fred_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        """
        The Fed projected 2.0% PCE inflation for 2021 in their June 2021 forecast.
        What was the actual inflation for 2021? Calculate the forecast error.
        """
    )
    
    print("\n" + "="*60)
    print("Test: Forecast Comparison")
    print("="*60)
    print(response)
    assert response is not None


@pytest.mark.asyncio
async def test_fred_agent_economic_snapshot():
    """Test getting economic snapshot."""
    agent = create_fred_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        "Give me an economic snapshot for September 2008"
    )
    
    print("\n" + "="*60)
    print("Test: Economic Snapshot (2008 Crisis)")
    print("="*60)
    print(response)
    assert response is not None


@pytest.mark.asyncio
async def test_fred_agent_yield_curve():
    """Test yield curve query."""
    agent = create_fred_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        "Show me the current yield curve. Is it inverted?"
    )
    
    print("\n" + "="*60)
    print("Test: Yield Curve")
    print("="*60)
    print(response)
    assert response is not None


# ============================================================================
# A2A Integration Tests (requires server running)
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires A2A server running on localhost:8001")
async def test_fred_agent_via_a2a():
    """
    Test consuming FRED agent via A2A protocol.
    
    Prerequisites:
    1. Start FRED agent A2A server: python fred_agent.py
    2. Server should be running on localhost:8001
    """
    # Connect to remote FRED agent
    fred_remote = RemoteA2aAgent(
        agent_card_url="http://localhost:8001/agent_card.json"
    )
    
    # Create a simple orchestrator that uses the remote FRED agent
    from google.adk.agents import LlmAgent
    from google.adk.models.google_llm import Gemini
    from google.adk.tools import AgentTool
    
    orchestrator = LlmAgent(
        name="test_orchestrator",
        model=Gemini(model="gemini-2.5-flash-lite"),
        description="Test orchestrator using remote FRED agent",
        instruction="Use the FRED agent to answer economic data questions",
        sub_agents=[AgentTool(fred_remote)]
    )
    
    runner = InMemoryRunner(agent=orchestrator)
    
    response = await runner.run_debug(
        "What was inflation in 2022? Use the FRED data agent."
    )
    
    print("\n" + "="*60)
    print("Test: A2A Remote Agent")
    print("="*60)
    print(response)
    assert response is not None


# ============================================================================
# Tool-level Tests
# ============================================================================

def test_get_inflation_data_tool():
    """Test inflation data tool directly."""
    try:
        from .fred_tools import get_inflation_data
    except ImportError:
        from fred_tools import get_inflation_data
    
    result = get_inflation_data(
        start_date="2022-01-01",
        end_date="2022-12-31",
        measure="pce_core",
        yoy=True
    )
    
    print("\n" + "="*60)
    print("Test: Direct Tool Call - Inflation Data")
    print("="*60)
    print(f"Measure: {result['measure']}")
    print(f"Period: {result['start_date']} to {result['end_date']}")
    print(f"Data points: {len(result['values'])}")
    print(f"Latest: {result['statistics']['latest']}")
    print(f"Mean: {result['statistics']['mean']:.2f}%")
    print(f"Max: {result['statistics']['max']:.2f}%")
    
    assert result['measure'] == 'pce_core'
    assert len(result['values']) > 0


def test_compare_to_fed_projection_tool():
    """Test Fed projection comparison tool."""
    try:
        from .fred_tools import compare_to_fed_projection
    except ImportError:
        from fred_tools import compare_to_fed_projection
    
    result = compare_to_fed_projection(
        indicator="inflation",
        projection_value=2.0,
        projection_date="2021-06-01",
        actual_date="2021-12-31"
    )
    
    print("\n" + "="*60)
    print("Test: Fed Forecast Accuracy")
    print("="*60)
    print(f"Indicator: {result['indicator']}")
    print(f"Fed Projection: {result['fed_projection']}%")
    print(f"Actual Outcome: {result['actual_outcome']}%")
    print(f"Forecast Error: {result['forecast_error']} percentage points")
    print(f"Interpretation: {result['interpretation']}")
    
    assert result['forecast_error'] is not None


def test_economic_snapshot_tool():
    """Test economic snapshot tool."""
    try:
        from .fred_tools import get_economic_snapshot
    except ImportError:
        from fred_tools import get_economic_snapshot
    
    result = get_economic_snapshot(as_of_date="2020-03-01")
    
    print("\n" + "="*60)
    print("Test: Economic Snapshot - COVID Start")
    print("="*60)
    print(f"Snapshot Date: {result['snapshot_date']}")
    print("\nInflation:")
    for key, value in result.get('inflation', {}).items():
        print(f"  {key}: {value}")
    print("\nEmployment:")
    for key, value in result.get('employment', {}).items():
        print(f"  {key}: {value}")
    
    assert result['snapshot_date'] is not None


# ============================================================================
# Interactive Demo (not a test, run manually)
# ============================================================================

async def interactive_demo():
    """
    Interactive demo of FRED agent capabilities.
    
    Run with: python -c "from test_fred_agent import interactive_demo; import asyncio; asyncio.run(interactive_demo())"
    """
    agent = create_fred_agent()
    runner = InMemoryRunner(agent=agent)
    
    print("\n" + "="*80)
    print("FRED AGENT INTERACTIVE DEMO")
    print("="*80)
    
    queries = [
        "What was the inflation rate in 2022?",
        "Show me unemployment trends from 2020 to 2024",
        "Get an economic snapshot for March 2020 (COVID crisis)",
        "What's the current yield curve spread between 2-year and 10-year Treasury?",
        "Compare GDP growth in 2008 crisis vs 2020 COVID crisis"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*80}")
        print(f"Query {i}: {query}")
        print('='*80)
        
        response = await runner.run_debug(query)
        print(response)
        print()
        
        # Small delay to avoid rate limits
        await asyncio.sleep(2)


if __name__ == "__main__":
    # Run interactive demo
    print("Running FRED Agent Interactive Demo...")
    asyncio.run(interactive_demo())
