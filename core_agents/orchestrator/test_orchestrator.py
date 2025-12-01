"""
Integration Test for Real Orchestrator

Tests actual multi-agent coordination (not simulated!).
"""

import asyncio
import pytest
try:
    # Try relative imports first (when used as module)
    from .orchestrator_agent import RealOrchestrator
except ImportError:
    # Fall back to absolute imports (when run directly)
    from orchestrator_agent import RealOrchestrator

# Mark all tests as async
pytestmark = pytest.mark.asyncio


async def test_fred_agent_only():
    """Test calling FRED agent alone."""
    print("\n" + "="*80)
    print("TEST 1: FRED Agent Only")
    print("="*80)
    
    orchestrator = RealOrchestrator()
    
    result = await orchestrator.process_query(
        "What was Core PCE inflation in 2022?"
    )
    
    print(f"Status: {result['status']}")
    print(f"Agents used: {result['results']['agents_used']}")
    print(f"\nResponse:\n{result['response']}")
    
    assert result['status'] == 'success'
    assert 'fred' in result['results']['agents_used']


async def test_bls_agent_only():
    """Test calling BLS agent alone."""
    print("\n" + "="*80)
    print("TEST 2: BLS Agent Only")
    print("="*80)
    
    orchestrator = RealOrchestrator()
    
    result = await orchestrator.process_query(
        "What drove 2022 inflation? Break down CPI components."
    )
    
    print(f"Status: {result['status']}")
    print(f"Agents used: {result['results']['agents_used']}")
    print(f"\nResponse:\n{result['response']}")
    
    assert result['status'] == 'success'
    assert 'bls' in result['results']['agents_used']


async def test_treasury_agent_only():
    """Test calling Treasury agent alone."""
    print("\n" + "="*80)
    print("TEST 3: Treasury Agent Only")
    print("="*80)
    
    orchestrator = RealOrchestrator()
    
    result = await orchestrator.process_query(
        "Is the yield curve inverted? Check recession signals."
    )
    
    print(f"Status: {result['status']}")
    print(f"Agents used: {result['results']['agents_used']}")
    print(f"\nResponse:\n{result['response']}")
    
    assert result['status'] == 'success'
    assert 'treasury' in result['results']['agents_used']


async def test_fred_plus_bls():
    """Test coordinating FRED + BLS agents."""
    print("\n" + "="*80)
    print("TEST 4: FRED + BLS (2 Agent Coordination)")
    print("="*80)
    
    orchestrator = RealOrchestrator()
    
    result = await orchestrator.process_query(
        "Analyze 2022 inflation comprehensively: get actual inflation from FRED and component breakdown from BLS"
    )
    
    print(f"Status: {result['status']}")
    print(f"Agents used: {result['results']['agents_used']}")
    print(f"\nResponse:\n{result['response']}")
    
    assert result['status'] == 'success'
    assert 'fred' in result['results']['agents_used']
    assert 'bls' in result['results']['agents_used']


async def test_fred_bls_treasury():
    """Test coordinating all 3 external agents."""
    print("\n" + "="*80)
    print("TEST 5: FRED + BLS + Treasury (3 Agent Coordination)")
    print("="*80)
    
    orchestrator = RealOrchestrator()
    
    result = await orchestrator.process_query(
        "Complete inflation analysis: FRED for actual, BLS for drivers, Treasury for market expectations"
    )
    
    print(f"Status: {result['status']}")
    print(f"Agents used: {result['results']['agents_used']}")
    print(f"\nResponse:\n{result['response']}")
    
    assert result['status'] == 'success'
    assert 'fred' in result['results']['agents_used']
    assert 'bls' in result['results']['agents_used']
    assert 'treasury' in result['results']['agents_used']


async def test_forecast_validation():
    """Test comprehensive forecast validation (multiple agents)."""
    print("\n" + "="*80)
    print("TEST 6: Forecast Validation (Multi-Agent Use Case)")
    print("="*80)
    
    orchestrator = RealOrchestrator()
    
    result = await orchestrator.analyze_fed_forecast_accuracy(
        forecast_date="2021-06-16",
        indicator="inflation",
        projected_value=2.0,
        actual_date="2021-12-31"
    )
    
    print(f"Fed Forecast: {result['forecast']}")
    print(f"Actual Outcome: {result['actual']}")
    print(f"Market Expected: {result['market_expected']}")
    print(f"\nAnalysis:\n{result['analysis']}")
    
    assert result['forecast']['projected'] == 2.0


async def test_error_handling():
    """Test error handling when agent fails."""
    print("\n" + "="*80)
    print("TEST 7: Error Handling")
    print("="*80)
    
    orchestrator = RealOrchestrator()
    
    # Create task that will likely timeout or fail
    result = await orchestrator.process_query(
        "Test query with invalid parameters"
    )
    
    print(f"Status: {result['status']}")
    print(f"Response: {result.get('response', result.get('error'))}")
    
    # Should handle gracefully, not crash
    assert result is not None


async def test_parallel_execution():
    """Test that external agents execute in parallel."""
    print("\n" + "="*80)
    print("TEST 8: Parallel Execution Performance")
    print("="*80)
    
    import time
    
    orchestrator = RealOrchestrator()
    
    start = time.time()
    
    result = await orchestrator.process_query(
        "Get data from FRED, BLS, and Treasury simultaneously"
    )
    
    elapsed = time.time() - start
    
    print(f"Time elapsed: {elapsed:.2f}s")
    print(f"Agents used: {result['results']['agents_used']}")
    
    # With parallel execution, should be faster than sequential
    # (assuming each agent takes ~5s, parallel should be ~5-7s not 15s)
    assert elapsed < 15  # Generous timeout


# Integration test suite
async def run_all_tests():
    """Run all integration tests."""
    print("\n" + "="*80)
    print("REAL ORCHESTRATOR INTEGRATION TEST SUITE")
    print("="*80)
    print("\nThis tests ACTUAL multi-agent coordination (not simulated!)")
    print("Make sure external agents are running on ports 8001, 8002, 8003")
    print()
    
    tests = [
        ("FRED only", test_fred_agent_only),
        ("BLS only", test_bls_agent_only),
        ("Treasury only", test_treasury_agent_only),
        ("FRED + BLS", test_fred_plus_bls),
        ("FRED + BLS + Treasury", test_fred_bls_treasury),
        ("Forecast Validation", test_forecast_validation),
        ("Error Handling", test_error_handling),
        ("Parallel Execution", test_parallel_execution)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\nRunning: {test_name}")
            await test_func()
            print(f"✅ PASSED: {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name}")
            print(f"   Error: {e}")
            failed += 1
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED - Real orchestrator working!")
    else:
        print(f"\n⚠️  {failed} test(s) failed - check agent availability")


if __name__ == "__main__":
    # Run with: python test_real_orchestrator.py
    asyncio.run(run_all_tests())
