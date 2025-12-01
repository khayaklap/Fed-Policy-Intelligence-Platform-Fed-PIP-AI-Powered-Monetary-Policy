"""
Treasury Agent Tests

Test the Treasury agent locally and via A2A protocol.
"""

import asyncio
import pytest

# Handle relative imports for package usage and absolute for direct execution
try:
    from .treasury_agent import create_treasury_agent
except ImportError:
    from treasury_agent import create_treasury_agent

from google.adk.runners import InMemoryRunner
from google.adk.a2a import RemoteA2aAgent


# ============================================================================
# Direct Agent Tests (without A2A)
# ============================================================================

@pytest.mark.asyncio
async def test_treasury_agent_yield_curve():
    """Test yield curve query."""
    agent = create_treasury_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        "What is the current Treasury yield curve? Is it inverted?"
    )
    
    print("\n" + "="*60)
    print("Test: Current Yield Curve")
    print("="*60)
    print(response)
    assert response is not None


@pytest.mark.asyncio
async def test_treasury_agent_tips_breakeven():
    """Test TIPS breakeven inflation expectations."""
    agent = create_treasury_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        "What are current market inflation expectations based on 10-year TIPS breakeven?"
    )
    
    print("\n" + "="*60)
    print("Test: Market Inflation Expectations")
    print("="*60)
    print(response)
    assert response is not None


@pytest.mark.asyncio
async def test_treasury_agent_policy_stance():
    """Test monetary policy stance analysis."""
    agent = create_treasury_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        "Analyze the current monetary policy stance using real yields. Is policy restrictive?"
    )
    
    print("\n" + "="*60)
    print("Test: Monetary Policy Stance")
    print("="*60)
    print(response)
    assert response is not None


@pytest.mark.asyncio
async def test_treasury_agent_inversion_detection():
    """Test yield curve inversion detection."""
    agent = create_treasury_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        "Analyze the 2s10s yield spread over the past 2 years. Has it been inverted? What does this mean for recession risk?"
    )
    
    print("\n" + "="*60)
    print("Test: Yield Curve Inversion Analysis")
    print("="*60)
    print(response)
    assert response is not None


@pytest.mark.asyncio
async def test_treasury_agent_historical_curve():
    """Test historical yield curve for specific date."""
    agent = create_treasury_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        "What was the Treasury yield curve on September 15, 2008 (Lehman crisis)?"
    )
    
    print("\n" + "="*60)
    print("Test: Historical Yield Curve (2008 Crisis)")
    print("="*60)
    print(response)
    assert response is not None


@pytest.mark.asyncio
async def test_treasury_agent_fed_vs_market():
    """Test Fed forecast vs market expectations comparison."""
    agent = create_treasury_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        """
        In June 2021, the Fed projected long-term inflation of 2.0%.
        What did the market expect at that time based on 10-year TIPS breakeven?
        Were they aligned?
        """
    )
    
    print("\n" + "="*60)
    print("Test: Fed vs Market Expectations (June 2021)")
    print("="*60)
    print(response)
    assert response is not None


# ============================================================================
# A2A Integration Tests (requires server running)
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires A2A server running on localhost:8003")
async def test_treasury_agent_via_a2a():
    """
    Test consuming Treasury agent via A2A protocol.
    
    Prerequisites:
    1. Start Treasury agent A2A server: python treasury_agent.py
    2. Server should be running on localhost:8003
    """
    # Connect to remote Treasury agent
    treasury_remote = RemoteA2aAgent(
        agent_card_url="http://localhost:8003/agent_card.json"
    )
    
    # Create orchestrator using remote Treasury agent
    from google.adk.agents import LlmAgent
    from google.adk.models.google_llm import Gemini
    from google.adk.tools import AgentTool
    
    orchestrator = LlmAgent(
        name="test_orchestrator",
        model=Gemini(model="gemini-2.5-flash-lite"),
        description="Test orchestrator using remote Treasury agent",
        instruction="Use the Treasury agent to answer yield curve and market questions",
        sub_agents=[AgentTool(treasury_remote)]
    )
    
    runner = InMemoryRunner(agent=orchestrator)
    
    response = await runner.run_debug(
        "Is the yield curve currently inverted? Use the Treasury agent."
    )
    
    print("\n" + "="*60)
    print("Test: A2A Remote Agent")
    print("="*60)
    print(response)
    assert response is not None


# ============================================================================
# Tool-level Tests
# ============================================================================

def test_get_yield_curve_tool():
    """Test yield curve tool directly."""
    try:
        from .treasury_tools import get_yield_curve_data
    except ImportError:
        from treasury_tools import get_yield_curve_data
    
    result = get_yield_curve_data()
    
    print("\n" + "="*60)
    print("Test: Direct Tool Call - Yield Curve")
    print("="*60)
    print(f"Date: {result['date']}")
    
    if 'yields' in result:
        print("\nKey yields:")
        for maturity in ['3m', '2y', '10y', '30y']:
            if maturity in result['yields']:
                y = result['yields'][maturity]
                print(f"  {maturity}: {y['yield']:.2f}%")
    
    if 'curve_characteristics' in result:
        char = result['curve_characteristics']
        print(f"\n2s10s spread: {char.get('2s10s_spread', 'N/A')}bp")
        print(f"Inverted: {char.get('2s10s_inverted', 'N/A')}")
        print(f"Status: {char.get('curve_status', 'N/A')}")
    
    print(f"\nInterpretation: {result.get('interpretation', 'N/A')}")
    
    assert 'yields' in result or 'error' in result


def test_get_tips_breakeven_tool():
    """Test TIPS breakeven tool directly."""
    try:
        from .treasury_tools import get_market_inflation_expectations
    except ImportError:
        from treasury_tools import get_market_inflation_expectations
    
    result = get_market_inflation_expectations(maturity="10y")
    
    print("\n" + "="*60)
    print("Test: Direct Tool Call - TIPS Breakeven")
    print("="*60)
    
    if 'error' not in result:
        print(f"Maturity: {result['maturity']}")
        print(f"\nLatest ({result['latest']['date']}):")
        print(f"  Nominal yield: {result['latest']['nominal_yield']}%")
        print(f"  TIPS yield: {result['latest']['tips_yield']}%")
        print(f"  Breakeven: {result['latest']['breakeven']}%")
        print(f"\nExpectation status: {result['expectation_status']}")
        print(f"Interpretation: {result['interpretation']}")
        print(f"Fed implication: {result['fed_implication']}")
    else:
        print(f"Error: {result['error']}")
    
    assert 'latest' in result or 'error' in result


def test_analyze_policy_stance_tool():
    """Test policy stance analysis tool."""
    try:
        from .treasury_tools import analyze_monetary_policy_stance
    except ImportError:
        from treasury_tools import analyze_monetary_policy_stance
    
    result = analyze_monetary_policy_stance()
    
    print("\n" + "="*60)
    print("Test: Direct Tool Call - Policy Stance")
    print("="*60)
    
    if 'error' not in result:
        print(f"Date: {result['date']}")
        print(f"\nReal yields:")
        for maturity, data in result['real_yields'].items():
            print(f"  {maturity}: {data['real_yield']}%")
        
        print(f"\nPolicy stance: {result['policy_stance']}")
        print(f"Interpretation: {result['policy_interpretation']}")
        if 'analysis' in result:
            print(f"Analysis: {result['analysis']}")
    else:
        print(f"Error: {result['error']}")
    
    assert 'policy_stance' in result or 'error' in result


def test_detect_inversion_tool():
    """Test yield curve inversion detection."""
    try:
        from .treasury_tools import detect_yield_curve_inversion
    except ImportError:
        from treasury_tools import detect_yield_curve_inversion
    
    result = detect_yield_curve_inversion(spread_type="2s10s")
    
    print("\n" + "="*60)
    print("Test: Direct Tool Call - Inversion Detection")
    print("="*60)
    
    if 'error' not in result:
        print(f"Spread type: {result['spread_type']}")
        print(f"Period: {result['period']}")
        print(f"\nLatest ({result['latest']['date']}):")
        print(f"  Spread: {result['latest']['spread']}bp")
        
        inv = result['inversion_analysis']
        print(f"\nInversion analysis:")
        print(f"  Currently inverted: {inv['currently_inverted']}")
        print(f"  Days inverted: {inv['inversion_days']}")
        print(f"  % of period: {inv['inversion_percentage']}%")
        
        print(f"\nRecession signal: {result['recession_signal']}")
        print(f"Interpretation: {result['interpretation']}")
    else:
        print(f"Error: {result['error']}")
    
    assert 'inversion_analysis' in result or 'error' in result


def test_compare_fed_vs_market_tool():
    """Test Fed vs market forecast comparison."""
    try:
        from .treasury_tools import compare_fed_forecast_vs_market
    except ImportError:
        from treasury_tools import compare_fed_forecast_vs_market
    
    result = compare_fed_forecast_vs_market(
        fed_inflation_forecast=2.0,
        forecast_date="2021-06-15",
        forecast_horizon="10y"
    )
    
    print("\n" + "="*60)
    print("Test: Fed vs Market Comparison (June 2021)")
    print("="*60)
    
    if 'error' not in result:
        print(f"Forecast date: {result['forecast_date']}")
        print(f"Horizon: {result['horizon']}")
        print(f"\nFed forecast: {result['fed_forecast']}%")
        print(f"Market expectation: {result['market_expectation']}%")
        print(f"Divergence: {result['divergence']:+.2f}pp")
        print(f"\nFed credibility: {result['fed_credibility']}")
        print(f"Interpretation: {result['interpretation']}")
    else:
        print(f"Error: {result['error']}")
    
    assert 'divergence' in result or 'error' in result


# ============================================================================
# Interactive Demo (not a test, run manually)
# ============================================================================

async def interactive_demo():
    """
    Interactive demo of Treasury agent capabilities.
    
    Run with: python -c "from test_treasury_agent import interactive_demo; import asyncio; asyncio.run(interactive_demo())"
    """
    agent = create_treasury_agent()
    runner = InMemoryRunner(agent=agent)
    
    print("\n" + "="*80)
    print("TREASURY AGENT INTERACTIVE DEMO")
    print("="*80)
    
    queries = [
        "What is the current Treasury yield curve? Is it inverted?",
        "What do 10-year TIPS breakevens tell us about market inflation expectations?",
        "Is current monetary policy restrictive based on real yields?",
        "Analyze the 2s10s spread - is there recession risk?",
        "What was the yield curve in September 2008 during the Lehman crisis?",
        "Compare current market inflation expectations with the Fed's 2% target"
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
    print("Running Treasury Agent Interactive Demo...")
    asyncio.run(interactive_demo())
