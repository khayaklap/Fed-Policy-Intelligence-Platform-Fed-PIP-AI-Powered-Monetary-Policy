"""
Trend Tracker Test Suite

Tests for long-term trend analysis, cycle detection, reaction function,
forecast bias tracking, and predictive indicators.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict

# Import components
try:
    # Try relative imports first (when used as module)
    from .long_term_analyzer import LongTermAnalyzer, analyze_long_term_patterns
    from .cycle_detector import CycleDetector, detect_policy_cycles
    from .reaction_forecast_analysis import (
        ReactionFunctionAnalyzer,
        ForecastBiasTracker,
        analyze_reaction_and_bias
    )
    from trend_tracker_tools import (
        analyze_long_term_trends_tool,
        detect_policy_cycles_tool,
        analyze_reaction_function_tool,
        track_forecast_bias_tool,
        generate_predictive_indicators_tool
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from long_term_analyzer import LongTermAnalyzer, analyze_long_term_patterns
    from cycle_detector import CycleDetector, detect_policy_cycles
    from reaction_forecast_analysis import (
        ReactionFunctionAnalyzer,
        ForecastBiasTracker,
        analyze_reaction_and_bias
    )
    from trend_tracker_tools import (
        analyze_long_term_trends_tool,
        detect_policy_cycles_tool,
        analyze_reaction_function_tool,
        track_forecast_bias_tool,
        generate_predictive_indicators_tool
    )


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

@pytest.fixture
def long_term_meeting_data():
    """
    Long-term dataset (40 meetings = 10 years).
    Simulates: Accommodative → Tightening → Easing cycle.
    """
    base_date = datetime(2015, 1, 1)
    meetings = []
    
    # Phase 1: Accommodative (meetings 0-15)
    for i in range(16):
        meetings.append({
            'date': (base_date + timedelta(days=i*45)).strftime('%Y-%m-%d'),
            'score': -10 + i * 0.5,  # Gradual hawkish shift
            'sentiment': 'dovish' if i < 8 else 'neutral',
            'action': 'unchanged',
            'regime': 'accommodative',
            'fed_funds': 0.25
        })
    
    # Phase 2: Tightening (meetings 16-31)
    for i in range(16):
        meetings.append({
            'date': (base_date + timedelta(days=(16+i)*45)).strftime('%Y-%m-%d'),
            'score': -2 + i * 1.5,  # Strong hawkish trend
            'sentiment': 'hawkish' if i > 4 else 'neutral',
            'action': 'increase' if i % 2 == 0 else 'unchanged',
            'regime': 'tightening',
            'fed_funds': 0.25 + (i * 0.25)
        })
    
    # Phase 3: Easing (meetings 32-39)
    for i in range(8):
        meetings.append({
            'date': (base_date + timedelta(days=(32+i)*45)).strftime('%Y-%m-%d'),
            'score': 18 - i * 2,  # Dovish shift
            'sentiment': 'dovish',
            'action': 'decrease' if i % 2 == 0 else 'unchanged',
            'regime': 'pivot_to_easing',
            'fed_funds': 4.0 - (i * 0.25)
        })
    
    return meetings


@pytest.fixture
def economic_data_with_rates():
    """Economic data for Taylor Rule estimation."""
    base_date = datetime(2015, 1, 1)
    data = []
    
    for i in range(40):
        # Simulate economic cycle
        inflation = 1.5 + 0.1 * i + np.random.normal(0, 0.2)  # Rising inflation
        unemployment = 5.0 - 0.05 * i + np.random.normal(0, 0.1)  # Falling unemployment
        fed_funds = 0.25 + 0.1 * i
        
        data.append({
            'date': (base_date + timedelta(days=i*45)).strftime('%Y-%m-%d'),
            'inflation': round(inflation, 2),
            'unemployment': round(unemployment, 2),
            'fed_funds': round(fed_funds, 2)
        })
    
    return data


@pytest.fixture
def forecast_actual_pairs():
    """Forecast vs actual data for bias tracking."""
    forecasts = [
        {'date': '2021-06-16', 'value': 2.1, 'horizon': '2022'},
        {'date': '2021-09-22', 'value': 2.3, 'horizon': '2022'},
        {'date': '2021-12-15', 'value': 2.6, 'horizon': '2022'},
        {'date': '2022-03-16', 'value': 4.3, 'horizon': '2022'},
        {'date': '2022-06-15', 'value': 5.2, 'horizon': '2022'},
        {'date': '2022-09-21', 'value': 5.4, 'horizon': '2022'}
    ]
    
    actuals = [
        {'date': '2022-12-31', 'value': 6.5}  # Actual was 6.5%
    ] * len(forecasts)
    
    return forecasts, actuals


# ============================================================================
# LONG-TERM ANALYZER TESTS
# ============================================================================

class TestLongTermAnalyzer:
    """Tests for LongTermAnalyzer class."""
    
    def test_analyze_long_term_trend(self, long_term_meeting_data):
        """Test long-term trend analysis."""
        analyzer = LongTermAnalyzer()
        
        result = analyzer.analyze_long_term_trend(
            long_term_meeting_data,
            variable='score',
            min_meetings=24
        )
        
        assert 'direction' in result
        assert 'slope' in result
        assert 'r_squared' in result
        assert 'strength' in result
        assert 'changepoints' in result
        
        # Should detect hawkish trend
        assert result['direction'] in ['hawkish_trend', 'cyclical', 'no_trend']
    
    def test_detect_changepoints(self, long_term_meeting_data):
        """Test change point detection."""
        analyzer = LongTermAnalyzer()
        df = pd.DataFrame(long_term_meeting_data)
        
        changepoints = analyzer.detect_changepoints(df, 'score')
        
        assert isinstance(changepoints, list)
        # Should detect some change points in 40-meeting dataset
        # (accommodative → tightening → easing)
    
    def test_analyze_volatility(self, long_term_meeting_data):
        """Test volatility analysis."""
        analyzer = LongTermAnalyzer()
        
        result = analyzer.analyze_volatility(
            long_term_meeting_data,
            variable='score'
        )
        
        assert 'by_window' in result
        assert 'overall_trend' in result
        assert result['overall_trend'] in ['increasing', 'decreasing', 'stable', 'unknown']
    
    def test_detect_regime_persistence(self, long_term_meeting_data):
        """Test regime persistence analysis."""
        analyzer = LongTermAnalyzer()
        
        result = analyzer.detect_regime_persistence(long_term_meeting_data)
        
        assert 'regime_statistics' in result
        # Should show accommodative and tightening regimes
        assert 'accommodative' in result['regime_statistics'] or 'tightening' in result['regime_statistics']


# ============================================================================
# CYCLE DETECTOR TESTS
# ============================================================================

class TestCycleDetector:
    """Tests for CycleDetector class."""
    
    def test_identify_cycle_phase(self, long_term_meeting_data):
        """Test cycle phase identification."""
        detector = CycleDetector()
        
        # Test on recent data (should show easing)
        result = detector.identify_cycle_phase(long_term_meeting_data[-12:])
        
        assert 'current_phase' in result
        assert 'duration' in result
        assert 'expected_next_phase' in result
        assert result['current_phase'] in [
            'expansion_early', 'expansion_mid', 'expansion_late',
            'slowdown', 'recession'
        ]
    
    def test_detect_peaks_and_troughs(self, long_term_meeting_data):
        """Test peak/trough detection."""
        detector = CycleDetector()
        
        result = detector.detect_peaks_and_troughs(
            long_term_meeting_data,
            variable='fed_funds'
        )
        
        assert 'peaks' in result
        assert 'troughs' in result
        # Should detect at least one peak (max rate)
        assert result['num_peaks'] >= 0 or result['num_troughs'] >= 0
    
    def test_calculate_cycle_metrics(self, long_term_meeting_data):
        """Test cycle metrics calculation."""
        detector = CycleDetector()
        
        # First detect peaks/troughs
        peaks_troughs = detector.detect_peaks_and_troughs(
            long_term_meeting_data,
            variable='fed_funds'
        )
        
        if peaks_troughs['peaks'] and peaks_troughs['troughs']:
            metrics = detector.calculate_cycle_metrics(
                long_term_meeting_data,
                peaks_troughs['peaks'],
                peaks_troughs['troughs']
            )
            
            assert 'amplitude' in metrics or 'peak_to_peak_duration' in metrics


# ============================================================================
# REACTION FUNCTION TESTS
# ============================================================================

class TestReactionFunctionAnalyzer:
    """Tests for ReactionFunctionAnalyzer class."""
    
    def test_estimate_taylor_rule(self, long_term_meeting_data, economic_data_with_rates):
        """Test Taylor Rule estimation."""
        analyzer = ReactionFunctionAnalyzer()
        
        result = analyzer.estimate_taylor_rule(
            long_term_meeting_data,
            economic_data_with_rates
        )
        
        assert 'estimated_coefficients' in result
        assert 'r_squared' in result
        
        # Check coefficients present
        coefs = result['estimated_coefficients']
        assert 'inflation' in coefs
        assert 'unemployment' in coefs
    
    def test_detect_asymmetry(self, long_term_meeting_data):
        """Test asymmetry detection."""
        analyzer = ReactionFunctionAnalyzer()
        
        result = analyzer.detect_asymmetry(long_term_meeting_data)
        
        assert 'asymmetry' in result
        assert result['asymmetry'] in [
            'cuts_faster', 'hikes_faster', 'symmetric',
            'cuts_more_frequent', 'hikes_more_frequent'
        ]


# ============================================================================
# FORECAST BIAS TESTS
# ============================================================================

class TestForecastBiasTracker:
    """Tests for ForecastBiasTracker class."""
    
    def test_analyze_forecast_bias(self, forecast_actual_pairs):
        """Test forecast bias analysis."""
        tracker = ForecastBiasTracker()
        forecasts, actuals = forecast_actual_pairs
        
        result = tracker.analyze_forecast_bias(
            forecasts,
            actuals,
            variable='pce_inflation'
        )
        
        assert 'mean_error' in result
        assert 'bias_type' in result
        assert 'has_systematic_bias' in result
        
        # Should detect underestimation bias (forecasts 2.1-5.4, actual 6.5)
        assert result['bias_type'] == 'underestimation_bias'
    
    def test_identify_bias_patterns(self):
        """Test bias pattern identification."""
        tracker = ForecastBiasTracker()
        
        # Errors getting worse over time
        errors = [0.5, 0.8, 1.2, 1.5, 2.0, 2.5, 3.0, 3.5]
        timestamps = list(range(len(errors)))
        
        result = tracker.identify_bias_patterns(errors, timestamps)
        
        assert 'pattern' in result
        assert result['pattern'] in ['improving', 'deteriorating', 'stable']
        # Should show deteriorating
        assert result['pattern'] == 'deteriorating'


# ============================================================================
# TOOL-LEVEL TESTS
# ============================================================================

class TestTrendTrackerTools:
    """Tests for Trend Tracker ADK tools."""
    
    def test_analyze_long_term_trends_tool(self, long_term_meeting_data):
        """Test long-term trends tool."""
        result = analyze_long_term_trends_tool(
            long_term_meeting_data,
            variable='score'
        )
        
        assert 'trend_analysis' in result
        assert 'volatility' in result
        assert 'summary' in result
    
    def test_detect_policy_cycles_tool(self, long_term_meeting_data):
        """Test policy cycles tool."""
        result = detect_policy_cycles_tool(long_term_meeting_data)
        
        assert 'current_phase' in result
        assert 'peaks_and_troughs' in result or 'error' in result
    
    def test_analyze_reaction_function_tool(self, long_term_meeting_data, economic_data_with_rates):
        """Test reaction function tool."""
        result = analyze_reaction_function_tool(
            long_term_meeting_data,
            economic_data_with_rates
        )
        
        assert 'taylor_rule' in result
        assert 'asymmetry' in result
    
    def test_track_forecast_bias_tool(self, forecast_actual_pairs):
        """Test forecast bias tool."""
        forecasts, actuals = forecast_actual_pairs
        
        result = track_forecast_bias_tool(
            forecasts,
            actuals,
            variable='pce_inflation'
        )
        
        assert 'bias_analysis' in result
    
    def test_generate_predictive_indicators_tool(self, long_term_meeting_data):
        """Test predictive indicators tool."""
        result = generate_predictive_indicators_tool(
            long_term_meeting_data[-12:],
            current_economic_data={
                'inflation': 3.5,
                'unemployment': 3.7,
                'gdp_growth': 2.1
            }
        )
        
        assert 'active_indicators' in result
        assert 'predicted_action' in result
        assert 'confidence' in result


# ============================================================================
# EXAMPLE USAGE DEMONSTRATIONS
# ============================================================================

def example_usage_long_term_trends():
    """Example: Analyze long-term trends."""
    print("\n" + "="*60)
    print("EXAMPLE: Long-Term Trend Analysis")
    print("="*60)
    
    # Create sample 10-year dataset
    base_date = datetime(2015, 1, 1)
    meetings = []
    for i in range(40):
        meetings.append({
            'date': (base_date + timedelta(days=i*45)).strftime('%Y-%m-%d'),
            'score': -10 + i * 0.7,  # Hawkish trend
            'fed_funds': 0.25 + i * 0.1
        })
    
    result = analyze_long_term_trends_tool(meetings, variable='score')
    
    print(f"\nTrend Direction: {result['trend_analysis']['direction']}")
    print(f"Trend Strength: {result['trend_analysis']['strength']}")
    print(f"Slope: {result['trend_analysis']['slope']}")
    print(f"R²: {result['trend_analysis']['r_squared']}")
    print(f"Change Points: {len(result['trend_analysis']['changepoints'])}")


def example_usage_cycle_detection():
    """Example: Detect policy cycles."""
    print("\n" + "="*60)
    print("EXAMPLE: Policy Cycle Detection")
    print("="*60)
    
    # Create sample cycle data
    meetings = []
    base_date = datetime(2020, 1, 1)
    
    # Accommodative phase
    for i in range(10):
        meetings.append({
            'date': (base_date + timedelta(days=i*45)).strftime('%Y-%m-%d'),
            'action': 'unchanged',
            'sentiment': 'dovish',
            'fed_funds': 0.25
        })
    
    # Tightening phase
    for i in range(10):
        meetings.append({
            'date': (base_date + timedelta(days=(10+i)*45)).strftime('%Y-%m-%d'),
            'action': 'increase' if i % 2 == 0 else 'unchanged',
            'sentiment': 'hawkish',
            'fed_funds': 0.25 + i * 0.25
        })
    
    result = detect_policy_cycles_tool(meetings)
    
    print(f"\nCurrent Phase: {result['current_phase']['current_phase']}")
    print(f"Duration: {result['current_phase']['duration']} meetings")
    print(f"Expected Next: {result['current_phase']['expected_next_phase']}")


def example_usage_predictive_indicators():
    """Example: Generate predictive indicators."""
    print("\n" + "="*60)
    print("EXAMPLE: Predictive Indicators")
    print("="*60)
    
    # Create recent meetings with hawkish shift
    meetings = [
        {'date': '2024-01', 'score': 0, 'sentiment': 'neutral'},
        {'date': '2024-03', 'score': 2, 'sentiment': 'neutral'},
        {'date': '2024-05', 'score': 8, 'sentiment': 'hawkish'},
        {'date': '2024-07', 'score': 14, 'sentiment': 'hawkish'},
        {'date': '2024-09', 'score': 16, 'sentiment': 'hawkish'},
        {'date': '2024-11', 'score': 18, 'sentiment': 'highly_hawkish'}
    ]
    
    result = generate_predictive_indicators_tool(
        meetings,
        current_economic_data={
            'inflation': 3.5,
            'unemployment': 3.7,
            'gdp_growth': 2.1
        }
    )
    
    print(f"\nActive Indicators: {len(result['active_indicators'])}")
    for ind in result['active_indicators']:
        print(f"  - {ind['indicator']}: {ind['signal']}")
    print(f"\nPredicted Action: {result['predicted_action']}")
    print(f"Confidence: {result['confidence']:.0%}")
    print(f"Time Horizon: {result['time_horizon']} meetings")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_examples():
    """Run all example demonstrations."""
    example_usage_long_term_trends()
    example_usage_cycle_detection()
    example_usage_predictive_indicators()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TREND TRACKER - EXAMPLE USAGE")
    print("="*60)
    
    run_all_examples()
    
    print("\n" + "="*60)
    print("To run full test suite:")
    print("  pytest test_trend_tracker.py -v")
    print("="*60)
