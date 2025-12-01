"""
Policy Analyzer Test Suite

Comprehensive tests for sentiment tracking, regime detection, and policy analysis.
"""

import pytest
import pandas as pd
from datetime import datetime
from typing import List, Dict

# Import components
try:
    # Try relative imports first (when used as module)
    from .sentiment_tracker import SentimentTracker, analyze_sentiment_evolution
    from .regime_detector import RegimeDetector, detect_policy_regimes
    from .stance_classifier import StanceClassifier, classify_policy_stance
    from .policy_analyzer_tools import (
        analyze_sentiment_trend,
        detect_regime_changes,
        classify_policy_stance_tool,
        compare_policy_periods,
        get_current_policy_assessment
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from sentiment_tracker import SentimentTracker, analyze_sentiment_evolution
    from regime_detector import RegimeDetector, detect_policy_regimes
    from stance_classifier import StanceClassifier, classify_policy_stance
    from policy_analyzer_tools import (
        analyze_sentiment_trend,
        detect_regime_changes,
        classify_policy_stance_tool,
        compare_policy_periods,
        get_current_policy_assessment
    )


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_meeting_data_2021_2022():
    """
    Sample meeting data showing 2021-2022 inflation surge evolution.
    Sentiment shifts from dovish → neutral → hawkish.
    """
    return [
        {
            'date': '2021-01-27',
            'sentiment': 'dovish',
            'score': -10,
            'action': 'unchanged'
        },
        {
            'date': '2021-03-17',
            'sentiment': 'dovish',
            'score': -8,
            'action': 'unchanged'
        },
        {
            'date': '2021-06-16',
            'sentiment': 'dovish',
            'score': -6,
            'action': 'unchanged'
        },
        {
            'date': '2021-09-22',
            'sentiment': 'neutral',
            'score': 2,
            'action': 'unchanged'
        },
        {
            'date': '2021-11-03',
            'sentiment': 'neutral',
            'score': 3,
            'action': 'unchanged'
        },
        {
            'date': '2022-01-26',
            'sentiment': 'hawkish',
            'score': 10,
            'action': 'unchanged'
        },
        {
            'date': '2022-03-16',
            'sentiment': 'hawkish',
            'score': 12,
            'action': 'increase'
        },
        {
            'date': '2022-05-04',
            'sentiment': 'hawkish',
            'score': 15,
            'action': 'increase'
        },
        {
            'date': '2022-06-15',
            'sentiment': 'highly_hawkish',
            'score': 18,
            'action': 'increase'
        },
        {
            'date': '2022-07-27',
            'sentiment': 'highly_hawkish',
            'score': 20,
            'action': 'increase'
        }
    ]


@pytest.fixture
def sample_accommodative_period():
    """COVID response period - accommodative regime."""
    return [
        {'date': '2020-03-15', 'sentiment': 'dovish', 'score': -15, 'action': 'decrease'},
        {'date': '2020-04-29', 'sentiment': 'highly_dovish', 'score': -18, 'action': 'unchanged'},
        {'date': '2020-06-10', 'sentiment': 'dovish', 'score': -12, 'action': 'unchanged'},
        {'date': '2020-07-29', 'sentiment': 'dovish', 'score': -14, 'action': 'unchanged'}
    ]


@pytest.fixture
def sample_tightening_period():
    """2022 inflation fight - tightening regime."""
    return [
        {'date': '2022-03-16', 'sentiment': 'hawkish', 'score': 12, 'action': 'increase'},
        {'date': '2022-05-04', 'sentiment': 'hawkish', 'score': 15, 'action': 'increase'},
        {'date': '2022-06-15', 'sentiment': 'highly_hawkish', 'score': 18, 'action': 'increase'},
        {'date': '2022-07-27', 'sentiment': 'highly_hawkish', 'score': 20, 'action': 'increase'}
    ]


@pytest.fixture
def sample_economic_data():
    """Sample economic conditions."""
    return {
        'fed_funds': 5.25,
        'real_rate': 2.0,
        'inflation': 3.2,
        'unemployment': 3.7,
        'gdp_growth': 2.1
    }


# ============================================================================
# SENTIMENT TRACKER TESTS
# ============================================================================

class TestSentimentTracker:
    """Tests for SentimentTracker class."""
    
    def test_create_timeseries(self, sample_meeting_data_2021_2022):
        """Test time series creation."""
        tracker = SentimentTracker()
        df = tracker.create_sentiment_timeseries(sample_meeting_data_2021_2022)
        
        assert not df.empty
        assert 'date' in df.columns
        assert 'score' in df.columns
        assert len(df) == len(sample_meeting_data_2021_2022)
        
        # Check moving averages were calculated
        assert 'ma_short_term' in df.columns
    
    def test_classify_stance(self):
        """Test stance classification."""
        tracker = SentimentTracker()
        
        # Test highly hawkish
        result = tracker.classify_stance(20)
        assert result['classification'] == 'highly_hawkish'
        
        # Test hawkish
        result = tracker.classify_stance(12)
        assert result['classification'] == 'hawkish'
        
        # Test neutral
        result = tracker.classify_stance(0)
        assert result['classification'] == 'neutral'
        
        # Test dovish
        result = tracker.classify_stance(-10)
        assert result['classification'] == 'dovish'
        
        # Test highly dovish
        result = tracker.classify_stance(-20)
        assert result['classification'] == 'highly_dovish'
    
    def test_detect_trend(self, sample_meeting_data_2021_2022):
        """Test trend detection."""
        tracker = SentimentTracker()
        df = tracker.create_sentiment_timeseries(sample_meeting_data_2021_2022)
        
        trend = tracker.detect_trend(df, recent_meetings=10)
        
        assert 'direction' in trend
        assert 'slope' in trend
        assert 'strength' in trend
        
        # Should detect hawkish trend in 2021-2022 data
        assert 'hawkish' in trend['direction']
        assert trend['slope'] > 0
    
    def test_detect_shifts(self, sample_meeting_data_2021_2022):
        """Test shift detection."""
        tracker = SentimentTracker()
        df = tracker.create_sentiment_timeseries(sample_meeting_data_2021_2022)
        
        shifts = tracker.detect_shifts(df)
        
        assert isinstance(shifts, list)
        # Should detect shift from dovish to hawkish
        assert len(shifts) > 0
        
        # Check shift structure
        if shifts:
            shift = shifts[0]
            assert 'date' in shift
            assert 'change' in shift
            assert 'previous_stance' in shift
            assert 'new_stance' in shift
    
    def test_calculate_volatility(self, sample_meeting_data_2021_2022):
        """Test volatility calculation."""
        tracker = SentimentTracker()
        df = tracker.create_sentiment_timeseries(sample_meeting_data_2021_2022)
        
        volatility = tracker.calculate_volatility(df)
        
        assert 'volatility' in volatility
        assert 'level' in volatility
        assert 'interpretation' in volatility
    
    def test_get_current_stance(self, sample_meeting_data_2021_2022):
        """Test current stance retrieval."""
        tracker = SentimentTracker()
        df = tracker.create_sentiment_timeseries(sample_meeting_data_2021_2022)
        
        stance = tracker.get_current_stance(df)
        
        assert 'classification' in stance
        assert 'confidence' in stance
        assert 'score' in stance
        
        # Latest should be highly hawkish (score: 20)
        assert stance['classification'] == 'highly_hawkish'


# ============================================================================
# REGIME DETECTOR TESTS
# ============================================================================

class TestRegimeDetector:
    """Tests for RegimeDetector class."""
    
    def test_classify_regime_tightening(self):
        """Test tightening regime classification."""
        detector = RegimeDetector()
        
        actions = ['increase', 'increase', 'increase']
        sentiments = ['hawkish', 'hawkish', 'highly_hawkish']
        
        regime = detector.classify_regime(actions, sentiments)
        
        assert regime == 'tightening'
    
    def test_classify_regime_accommodative(self):
        """Test accommodative regime classification."""
        detector = RegimeDetector()
        
        actions = ['decrease', 'unchanged', 'unchanged']
        sentiments = ['dovish', 'dovish', 'dovish']
        
        regime = detector.classify_regime(actions, sentiments)
        
        assert regime == 'accommodative'
    
    def test_classify_regime_neutral(self):
        """Test neutral regime classification."""
        detector = RegimeDetector()
        
        actions = ['unchanged', 'unchanged', 'unchanged']
        sentiments = ['neutral', 'neutral', 'neutral']
        
        regime = detector.classify_regime(actions, sentiments)
        
        assert regime == 'neutral'
    
    def test_detect_regime_changes(self, sample_meeting_data_2021_2022):
        """Test regime change detection."""
        detector = RegimeDetector()
        
        changes = detector.detect_regime_changes(sample_meeting_data_2021_2022)
        
        assert isinstance(changes, list)
        # Should detect shift from accommodative/neutral to tightening
        
        if changes:
            change = changes[0]
            assert 'date' in change
            assert 'previous_regime' in change
            assert 'new_regime' in change
            assert 'type' in change
    
    def test_get_current_regime(self, sample_tightening_period):
        """Test current regime determination."""
        detector = RegimeDetector()
        
        current = detector.get_current_regime(sample_tightening_period)
        
        assert 'regime' in current
        assert 'duration' in current
        assert 'stability' in current
        
        # Should be tightening
        assert current['regime'] == 'tightening'
    
    def test_compare_to_historical(self):
        """Test historical comparison."""
        detector = RegimeDetector()
        
        comparison = detector.compare_to_historical(
            current_regime='tightening',
            current_duration=7,
            current_sentiment='hawkish'
        )
        
        assert 'most_similar' in comparison
        assert 'similar_episodes' in comparison


# ============================================================================
# STANCE CLASSIFIER TESTS
# ============================================================================

class TestStanceClassifier:
    """Tests for StanceClassifier class."""
    
    def test_classify_overall_stance_restrictive(self):
        """Test restrictive stance classification."""
        classifier = StanceClassifier()
        
        stance = classifier.classify_overall_stance(
            policy_actions=['increase', 'increase', 'increase'],
            sentiment_scores=[12, 15, 18],
            fed_funds_rate=5.25,
            real_rate=2.0,
            inflation_rate=3.2
        )
        
        assert 'stance' in stance
        assert 'overall_score' in stance
        
        # Should be restrictive
        assert 'restrictive' in stance['stance']
    
    def test_classify_overall_stance_accommodative(self):
        """Test accommodative stance classification."""
        classifier = StanceClassifier()
        
        stance = classifier.classify_overall_stance(
            policy_actions=['decrease', 'unchanged', 'unchanged'],
            sentiment_scores=[-15, -12, -14],
            fed_funds_rate=0.25,
            real_rate=-2.0,
            inflation_rate=2.5
        )
        
        assert 'stance' in stance
        # Should be accommodative
        assert 'accommodative' in stance['stance']
    
    def test_compare_stance_to_conditions(self, sample_economic_data):
        """Test stance appropriateness assessment."""
        classifier = StanceClassifier()
        
        comparison = classifier.compare_stance_to_conditions(
            stance='restrictive',
            inflation=sample_economic_data['inflation'],
            unemployment=sample_economic_data['unemployment'],
            gdp_growth=sample_economic_data['gdp_growth']
        )
        
        assert 'appropriate_stance' in comparison
        assert 'alignment' in comparison
        assert 'interpretation' in comparison
    
    def test_score_actions(self):
        """Test action scoring."""
        classifier = StanceClassifier()
        
        # Rate increases should score positive
        score = classifier._score_actions(['increase', 'increase', 'increase'])
        assert score > 0
        
        # Rate decreases should score negative
        score = classifier._score_actions(['decrease', 'decrease'])
        assert score < 0
        
        # Unchanged should score zero
        score = classifier._score_actions(['unchanged', 'unchanged'])
        assert score == 0


# ============================================================================
# TOOL-LEVEL TESTS
# ============================================================================

class TestPolicyAnalyzerTools:
    """Tests for Policy Analyzer ADK tools."""
    
    def test_analyze_sentiment_trend_tool(self, sample_meeting_data_2021_2022):
        """Test sentiment trend analysis tool."""
        result = analyze_sentiment_trend(sample_meeting_data_2021_2022)
        
        assert 'current_stance' in result
        assert 'trend' in result
        assert 'significant_shifts' in result
        assert 'volatility' in result
    
    def test_detect_regime_changes_tool(self, sample_meeting_data_2021_2022):
        """Test regime detection tool."""
        result = detect_regime_changes(sample_meeting_data_2021_2022)
        
        assert 'current_regime' in result
        assert 'regime_changes' in result
    
    def test_classify_policy_stance_tool(self, sample_meeting_data_2021_2022, sample_economic_data):
        """Test stance classification tool."""
        result = classify_policy_stance_tool(
            sample_meeting_data_2021_2022,
            sample_economic_data
        )
        
        assert 'overall_stance' in result
        assert 'conditions_comparison' in result
        assert 'trajectory' in result
    
    def test_compare_policy_periods_tool(self, sample_accommodative_period, sample_tightening_period):
        """Test period comparison tool."""
        result = compare_policy_periods(
            sample_accommodative_period,
            sample_tightening_period,
            "COVID Response",
            "Inflation Fight"
        )
        
        assert 'period1' in result
        assert 'period2' in result
        assert 'comparison' in result
        
        # Should show significant shift
        assert abs(result['comparison']['sentiment_shift']) > 10
    
    def test_get_current_policy_assessment_tool(self, sample_meeting_data_2021_2022):
        """Test current assessment tool."""
        result = get_current_policy_assessment(sample_meeting_data_2021_2022)
        
        assert 'summary' in result
        assert 'current_stance' in result
        assert 'current_regime' in result
        assert 'sentiment_trend' in result


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple components."""
    
    def test_complete_analysis_workflow(self, sample_meeting_data_2021_2022, sample_economic_data):
        """Test complete analysis workflow."""
        
        # Step 1: Analyze sentiment
        sentiment_result = analyze_sentiment_trend(sample_meeting_data_2021_2022)
        assert sentiment_result is not None
        
        # Step 2: Detect regimes
        regime_result = detect_regime_changes(sample_meeting_data_2021_2022)
        assert regime_result is not None
        
        # Step 3: Classify stance
        stance_result = classify_policy_stance_tool(
            sample_meeting_data_2021_2022,
            sample_economic_data
        )
        assert stance_result is not None
        
        # Step 4: Get comprehensive assessment
        assessment = get_current_policy_assessment(
            sample_meeting_data_2021_2022,
            sample_economic_data
        )
        assert assessment is not None
        assert 'summary' in assessment
    
    def test_2021_2022_inflation_episode_analysis(self, sample_meeting_data_2021_2022):
        """
        Test analysis of 2021-2022 inflation episode.
        
        Should show:
        - Sentiment shift from dovish to hawkish
        - Regime change from accommodative/neutral to tightening
        - Strong hawkish trend
        """
        tracker = SentimentTracker()
        detector = RegimeDetector()
        
        # Analyze sentiment evolution
        df = tracker.create_sentiment_timeseries(sample_meeting_data_2021_2022)
        trend = tracker.detect_trend(df)
        
        # Should show hawkish trend
        assert 'hawkish' in trend['direction']
        
        # Detect regime changes
        changes = detector.detect_regime_changes(sample_meeting_data_2021_2022)
        
        # Should detect shift to tightening
        assert any('tightening' in str(change) for change in changes)


# ============================================================================
# EXAMPLE USAGE DEMONSTRATIONS
# ============================================================================

def example_usage_sentiment_analysis():
    """Example: Analyze sentiment trend."""
    print("\n" + "="*60)
    print("EXAMPLE: Sentiment Trend Analysis")
    print("="*60)
    
    # Sample data
    meetings = [
        {'date': '2021-06-16', 'sentiment': 'dovish', 'score': -8},
        {'date': '2021-11-03', 'sentiment': 'neutral', 'score': 2},
        {'date': '2022-03-16', 'sentiment': 'hawkish', 'score': 12},
        {'date': '2022-06-15', 'sentiment': 'hawkish', 'score': 18}
    ]
    
    result = analyze_sentiment_trend(meetings)
    
    print(f"\nCurrent Stance: {result['current_stance']['classification']}")
    print(f"Trend: {result['trend']['direction']}")
    print(f"Interpretation: {result['trend']['interpretation']}")
    print(f"\nSignificant Shifts: {len(result['significant_shifts'])}")


def example_usage_regime_detection():
    """Example: Detect regime changes."""
    print("\n" + "="*60)
    print("EXAMPLE: Regime Change Detection")
    print("="*60)
    
    meetings = [
        {'date': '2020-03-15', 'action': 'decrease', 'sentiment': 'dovish'},
        {'date': '2020-06-10', 'action': 'unchanged', 'sentiment': 'dovish'},
        {'date': '2022-03-16', 'action': 'increase', 'sentiment': 'hawkish'},
        {'date': '2022-06-15', 'action': 'increase', 'sentiment': 'hawkish'}
    ]
    
    result = detect_regime_changes(meetings)
    
    print(f"\nCurrent Regime: {result['current_regime']['regime']}")
    print(f"Duration: {result['current_regime']['duration']} meetings")
    print(f"\nRegime Changes Detected: {len(result['regime_changes'])}")


def example_usage_period_comparison():
    """Example: Compare two periods."""
    print("\n" + "="*60)
    print("EXAMPLE: Period Comparison")
    print("="*60)
    
    covid_period = [
        {'date': '2020-03-15', 'sentiment': 'dovish', 'score': -15, 'action': 'decrease'},
        {'date': '2020-06-10', 'sentiment': 'dovish', 'score': -12, 'action': 'unchanged'}
    ]
    
    inflation_period = [
        {'date': '2022-03-16', 'sentiment': 'hawkish', 'score': 12, 'action': 'increase'},
        {'date': '2022-06-15', 'sentiment': 'hawkish', 'score': 18, 'action': 'increase'}
    ]
    
    result = compare_policy_periods(
        covid_period,
        inflation_period,
        "COVID Response",
        "Inflation Fight"
    )
    
    print(f"\n{result['period1']['label']}:")
    print(f"  Regime: {result['period1']['regime']}")
    print(f"  Avg Score: {result['period1']['avg_sentiment_score']}")
    
    print(f"\n{result['period2']['label']}:")
    print(f"  Regime: {result['period2']['regime']}")
    print(f"  Avg Score: {result['period2']['avg_sentiment_score']}")
    
    print(f"\nSentiment Shift: {result['comparison']['sentiment_shift']}")
    print(f"Interpretation: {result['comparison']['interpretation']}")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_examples():
    """Run all example demonstrations."""
    example_usage_sentiment_analysis()
    example_usage_regime_detection()
    example_usage_period_comparison()


if __name__ == "__main__":
    # Run examples
    print("\n" + "="*60)
    print("POLICY ANALYZER - EXAMPLE USAGE")
    print("="*60)
    
    run_all_examples()
    
    print("\n" + "="*60)
    print("To run full test suite:")
    print("  pytest test_policy_analyzer.py -v")
    print("="*60)
