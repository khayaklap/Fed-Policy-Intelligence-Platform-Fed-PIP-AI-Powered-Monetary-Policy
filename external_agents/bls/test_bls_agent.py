"""
BLS Agent Tests

Test the BLS agent locally and via A2A protocol.
"""

import asyncio
import pytest

# Handle relative imports for package usage and absolute for direct execution
try:
    from .bls_agent import create_bls_agent
except ImportError:
    from bls_agent import create_bls_agent

from google.adk.runners import InMemoryRunner
from google.adk.a2a import RemoteA2aAgent


# ============================================================================
# Direct Agent Tests (without A2A)
# ============================================================================

@pytest.mark.asyncio
async def test_bls_agent_cpi_components():
    """Test CPI component breakdown query."""
    agent = create_bls_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        "What CPI components drove inflation in 2022? Break down food, energy, and shelter."
    )
    
    print("\n" + "="*60)
    print("Test: CPI Components 2022")
    print("="*60)
    print(response)
    assert response is not None


@pytest.mark.asyncio
async def test_bls_agent_ppi_leading_indicator():
    """Test PPI as leading indicator."""
    agent = create_bls_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        "Show me PPI final demand data from 2021-2023. Did it peak before CPI?"
    )
    
    print("\n" + "="*60)
    print("Test: PPI Leading Indicator")
    print("="*60)
    print(response)
    assert response is not None


@pytest.mark.asyncio
async def test_bls_agent_eci_wage_pressure():
    """Test Employment Cost Index for wage pressures."""
    agent = create_bls_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        "What's the current Employment Cost Index? Is there wage-price spiral risk?"
    )
    
    print("\n" + "="*60)
    print("Test: ECI Wage Pressure")
    print("="*60)
    print(response)
    assert response is not None


@pytest.mark.asyncio
async def test_bls_agent_inflation_drivers():
    """Test comprehensive inflation driver analysis."""
    agent = create_bls_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        "What's driving inflation right now? Give me a comprehensive breakdown."
    )
    
    print("\n" + "="*60)
    print("Test: Inflation Drivers Analysis")
    print("="*60)
    print(response)
    assert response is not None


@pytest.mark.asyncio
async def test_bls_agent_shelter_inflation():
    """Test specific focus on shelter (largest CPI component)."""
    agent = create_bls_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        "How is shelter inflation trending? Compare rent vs owners' equivalent rent."
    )
    
    print("\n" + "="*60)
    print("Test: Shelter Inflation Deep Dive")
    print("="*60)
    print(response)
    assert response is not None


@pytest.mark.asyncio
async def test_bls_agent_goods_vs_services():
    """Test goods vs services inflation split."""
    agent = create_bls_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        "Compare goods vs services inflation. Which is driving overall CPI?"
    )
    
    print("\n" + "="*60)
    print("Test: Goods vs Services")
    print("="*60)
    print(response)
    assert response is not None


# ============================================================================
# A2A Integration Tests (requires server running)
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires A2A server running on localhost:8002")
async def test_bls_agent_via_a2a():
    """
    Test consuming BLS agent via A2A protocol.
    
    Prerequisites:
    1. Start BLS agent A2A server: python bls_agent.py
    2. Server should be running on localhost:8002
    """
    # Connect to remote BLS agent
    bls_remote = RemoteA2aAgent(
        agent_card_url="http://localhost:8002/agent_card.json"
    )
    
    # Create orchestrator using remote BLS agent
    from google.adk.agents import LlmAgent
    from google.adk.models.google_llm import Gemini
    from google.adk.tools import AgentTool
    
    orchestrator = LlmAgent(
        name="test_orchestrator",
        model=Gemini(model="gemini-2.5-flash-lite"),
        description="Test orchestrator using remote BLS agent",
        instruction="Use the BLS agent to answer detailed inflation questions",
        sub_agents=[AgentTool(bls_remote)]
    )
    
    runner = InMemoryRunner(agent=orchestrator)
    
    response = await runner.run_debug(
        "What drove the 2022 inflation surge? Use the BLS agent for component breakdown."
    )
    
    print("\n" + "="*60)
    print("Test: A2A Remote Agent")
    print("="*60)
    print(response)
    assert response is not None


# ============================================================================
# Tool-level Tests
# ============================================================================

def test_get_cpi_components_tool():
    """Test CPI components tool directly."""
    try:
        from .bls_tools import get_cpi_components
    except ImportError:
        from bls_tools import get_cpi_components
    
    result = get_cpi_components(
        start_year=2022,
        end_year=2023,
        components=["food", "energy", "housing"]
    )
    
    print("\n" + "="*60)
    print("Test: Direct Tool Call - CPI Components")
    print("="*60)
    print(f"Period: {result['period']}")
    print(f"\nComponents analyzed: {list(result['components'].keys())}")
    
    if 'energy' in result['components']:
        energy = result['components']['energy'].get('cpi_energy', {})
        if energy:
            print(f"\nEnergy inflation:")
            print(f"  Latest: {energy['latest']['yoy']}% YoY ({energy['latest']['date']})")
            print(f"  Peak: {energy['peak']['yoy']}% YoY ({energy['peak']['date']})")
    
    if 'housing' in result['components']:
        shelter = result['components']['housing'].get('cpi_shelter', {})
        if shelter:
            print(f"\nShelter inflation:")
            print(f"  Latest: {shelter['latest']['yoy']}% YoY ({shelter['latest']['date']})")
            print(f"  Peak: {shelter['peak']['yoy']}% YoY ({shelter['peak']['date']})")
    
    print(f"\nSummary: {result['summary']}")
    
    assert 'components' in result
    assert len(result['components']) > 0


def test_get_ppi_data_tool():
    """Test PPI tool directly."""
    try:
        from .bls_tools import get_ppi_data
    except ImportError:
        from bls_tools import get_ppi_data
    
    result = get_ppi_data(
        start_year=2021,
        end_year=2023,
        stage="final_demand"
    )
    
    print("\n" + "="*60)
    print("Test: Direct Tool Call - PPI Data")
    print("="*60)
    print(f"Stage: {result['stage']}")
    print(f"Latest: {result['latest']['yoy']}% YoY ({result['latest']['date']})")
    print(f"Peak: {result['peak']['yoy']}% YoY ({result['peak']['date']})")
    print(f"Recent trend: {result['recent_trend']}")
    print(f"\nInterpretation: {result['interpretation']}")
    
    assert result['stage'] == 'final_demand'
    assert 'latest' in result


def test_employment_cost_index_tool():
    """Test ECI tool directly."""
    try:
        from .bls_tools import get_employment_cost_index
    except ImportError:
        from bls_tools import get_employment_cost_index
    
    result = get_employment_cost_index(
        start_year=2020,
        end_year=2024,
        component="total_comp"
    )
    
    print("\n" + "="*60)
    print("Test: Direct Tool Call - Employment Cost Index")
    print("="*60)
    print(f"Component: {result['component']}")
    print(f"Latest: {result['latest']['yoy']}% YoY ({result['latest']['date']})")
    print(f"Peak: {result['peak']['yoy']}% YoY ({result['peak']['date']})")
    print(f"Wage pressure: {result['wage_pressure']}")
    print(f"Trend: {result['trend']}")
    print(f"\nInterpretation: {result['interpretation']}")
    
    assert result['component'] == 'total_comp'
    assert 'wage_pressure' in result


def test_compare_inflation_measures_tool():
    """Test inflation measures comparison."""
    try:
        from .bls_tools import compare_inflation_measures
    except ImportError:
        from bls_tools import compare_inflation_measures
    
    result = compare_inflation_measures(
        start_year=2021,
        end_year=2023
    )
    
    print("\n" + "="*60)
    print("Test: Inflation Measures Comparison")
    print("="*60)
    print(f"Period: {result['period']}\n")
    
    for measure, data in result['comparison'].items():
        print(f"{measure}:")
        print(f"  Name: {data['name']}")
        print(f"  Latest: {data['latest_yoy']}% YoY")
        print(f"  Peak: {data['peak_yoy']}% YoY ({data['peak_date']})")
        print()
    
    if result['insights']:
        print("Insights:")
        for insight in result['insights']:
            print(f"  • {insight}")
    
    assert 'comparison' in result
    assert len(result['comparison']) > 0


def test_analyze_inflation_drivers_tool():
    """Test comprehensive inflation driver analysis."""
    try:
        from .bls_tools import analyze_inflation_drivers
    except ImportError:
        from bls_tools import analyze_inflation_drivers
    
    result = analyze_inflation_drivers(as_of_date="2022-12-01")
    
    print("\n" + "="*60)
    print("Test: Inflation Drivers Analysis - December 2022")
    print("="*60)
    print(f"Analysis date: {result['analysis_date']}")
    print(f"Headline inflation: {result['headline_inflation']}%")
    print(f"Core inflation: {result['core_inflation']}%")
    print(f"Spread: {result['spread']}pp")
    print(f"\nAssessment: {result['assessment']}")
    
    if result['primary_drivers']:
        print(f"\nTop inflation drivers:")
        for i, driver in enumerate(result['primary_drivers'][:5], 1):
            print(f"  {i}. {driver['component']}: {driver['yoy']}% YoY ({driver['category']})")
    
    print(f"\nComponent summary: {result['component_summary']}")
    
    assert 'headline_inflation' in result
    assert 'primary_drivers' in result


# ============================================================================
# Interactive Demo (not a test, run manually)
# ============================================================================

async def interactive_demo():
    """
    Interactive demo of BLS agent capabilities.
    
    Run with: python -c "from test_bls_agent import interactive_demo; import asyncio; asyncio.run(interactive_demo())"
    """
    agent = create_bls_agent()
    runner = InMemoryRunner(agent=agent)
    
    print("\n" + "="*80)
    print("BLS AGENT INTERACTIVE DEMO")
    print("="*80)
    
    queries = [
        "What components drove the 2022 inflation surge?",
        "Compare PPI vs CPI trends - did PPI lead?",
        "What's the current Employment Cost Index? Are wage pressures moderating?",
        "Break down shelter inflation: rent vs owners' equivalent rent",
        "Analyze current inflation drivers - what's behind the numbers?",
        "Compare goods vs services inflation over the past 2 years"
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
    print("Running BLS Agent Interactive Demo...")
    asyncio.run(interactive_demo())
