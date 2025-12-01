"""
Policy Analyzer Tools

ADK tools for analyzing Fed policy stance evolution, regime changes,
and sentiment trends over time.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from google.adk.tools.tool_context import ToolContext

try:
    # Try relative imports first (when used as module)
    from .sentiment_tracker import SentimentTracker, analyze_sentiment_evolution
    from .regime_detector import RegimeDetector, detect_policy_regimes
    from .stance_classifier import StanceClassifier, classify_policy_stance
except ImportError:
    # Fall back to absolute imports (when run directly)
    from sentiment_tracker import SentimentTracker, analyze_sentiment_evolution
    from regime_detector import RegimeDetector, detect_policy_regimes
    from stance_classifier import StanceClassifier, classify_policy_stance

logger = logging.getLogger(__name__)


def analyze_sentiment_trend(
    meeting_data: List[Dict],
    recent_meetings: int = 12,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Analyze Fed sentiment trend across multiple FOMC meetings.
    
    Tracks hawkish/dovish evolution, detects significant shifts,
    and identifies current trend direction.
    
    Args:
        meeting_data: List of dicts with 'date', 'sentiment', 'score' from Document Processor
        recent_meetings: Number of recent meetings to analyze (default: 12 = ~3 years)
        tool_context: ADK tool context
    
    Returns:
        Dictionary with sentiment trend analysis
    
    Example:
        >>> analyze_sentiment_trend([
        ...     {'date': '2021-06-16', 'sentiment': 'dovish', 'score': -8},
        ...     {'date': '2021-11-03', 'sentiment': 'neutral', 'score': 2},
        ...     {'date': '2022-03-16', 'sentiment': 'hawkish', 'score': 12},
        ...     {'date': '2022-06-15', 'sentiment': 'hawkish', 'score': 18}
        ... ])
        {
            'current_stance': {
                'classification': 'hawkish',
                'score': 18,
                'confidence': 'high'
            },
            'trend': {
                'direction': 'strong_hawkish_trend',
                'slope': 8.5,  # Score increase per meeting
                'interpretation': 'Sentiment strongly becoming more hawkish'
            },
            'significant_shifts': [
                {
                    'date': '2022-03-16',
                    'change': 10,  # From 2 to 12
                    'previous_stance': 'neutral',
                    'new_stance': 'hawkish'
                }
            ],
            'volatility': {
                'level': 'moderate',
                'interpretation': 'Sentiment shows moderate variation'
            }
        }
    """
    logger.info(f"Analyzing sentiment trend across {len(meeting_data)} meetings")
    
    try:
        # Limit to recent meetings
        recent_data = meeting_data[-recent_meetings:] if len(meeting_data) > recent_meetings else meeting_data
        
        # Perform analysis
        result = analyze_sentiment_evolution(recent_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing sentiment trend: {e}")
        return {'error': str(e)}


def detect_regime_changes(
    meeting_data: List[Dict],
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Detect Fed policy regime changes (accommodative → tightening → neutral, etc.).
    
    Identifies when the Fed shifts between different policy regimes and
    compares current regime to historical episodes.
    
    Args:
        meeting_data: List of dicts with 'date', 'action', 'sentiment'
        tool_context: ADK tool context
    
    Returns:
        Dictionary with regime analysis and changes
    
    Example:
        >>> detect_regime_changes([
        ...     {'date': '2020-03-15', 'action': 'decrease', 'sentiment': 'dovish'},
        ...     {'date': '2020-04-29', 'action': 'unchanged', 'sentiment': 'dovish'},
        ...     {'date': '2022-03-16', 'action': 'increase', 'sentiment': 'hawkish'},
        ...     {'date': '2022-05-04', 'action': 'increase', 'sentiment': 'hawkish'}
        ... ])
        {
            'current_regime': {
                'regime': 'tightening',
                'description': 'Raising rates to combat inflation',
                'duration': 7,  # meetings in current regime
                'stability': 'established'
            },
            'regime_changes': [
                {
                    'date': '2022-03-16',
                    'previous_regime': 'accommodative',
                    'new_regime': 'tightening',
                    'type': 'shift_to_tightening'
                }
            ],
            'historical_comparison': {
                'most_similar': {
                    'episode': '2022_inflation_fight',
                    'description': 'Fastest tightening since 1980s',
                    'similarity': 0.9
                }
            }
        }
    """
    logger.info(f"Detecting regime changes in {len(meeting_data)} meetings")
    
    try:
        result = detect_policy_regimes(meeting_data)
        return result
        
    except Exception as e:
        logger.error(f"Error detecting regime changes: {e}")
        return {'error': str(e)}


def classify_policy_stance_tool(
    meeting_data: List[Dict],
    economic_data: Optional[Dict] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Classify overall Fed policy stance combining multiple signals.
    
    Integrates:
    - Policy actions (rate changes)
    - Sentiment (hawkish/dovish language)
    - Interest rate levels
    - Economic conditions (inflation, unemployment, growth)
    
    Args:
        meeting_data: List of meeting data
        economic_data: Optional dict with 'fed_funds', 'real_rate', 'inflation', 
                      'unemployment', 'gdp_growth'
        tool_context: ADK tool context
    
    Returns:
        Dictionary with stance classification and appropriateness assessment
    
    Example:
        >>> classify_policy_stance_tool(
        ...     meeting_data=[...],
        ...     economic_data={
        ...         'fed_funds': 5.25,
        ...         'real_rate': 2.0,
        ...         'inflation': 3.2,
        ...         'unemployment': 3.7,
        ...         'gdp_growth': 2.1
        ...     }
        ... )
        {
            'overall_stance': {
                'stance': 'restrictive',
                'overall_score': 8.5,
                'description': 'Tight policy - slowing economy to control inflation',
                'confidence': 'high'
            },
            'conditions_comparison': {
                'appropriate_stance': 'restrictive',
                'alignment': 'well_aligned',
                'interpretation': 'Policy stance is appropriate for current conditions'
            },
            'trajectory': {
                'trajectory': 'tightening',
                'description': 'Policy has shifted toward restriction'
            }
        }
    """
    logger.info("Classifying overall policy stance")
    
    try:
        result = classify_policy_stance(meeting_data, economic_data)
        return result
        
    except Exception as e:
        logger.error(f"Error classifying stance: {e}")
        return {'error': str(e)}


def compare_policy_periods(
    period1_data: List[Dict],
    period2_data: List[Dict],
    period1_label: str = "Period 1",
    period2_label: str = "Period 2",
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Compare Fed policy stance between two time periods.
    
    Useful for comparing:
    - Current policy vs historical episode
    - Pre-shock vs post-shock periods
    - Different Fed chairs
    
    Args:
        period1_data: Meeting data for first period
        period2_data: Meeting data for second period
        period1_label: Label for first period
        period2_label: Label for second period
        tool_context: ADK tool context
    
    Returns:
        Dictionary comparing the two periods
    
    Example:
        >>> compare_policy_periods(
        ...     period1_data=meetings_2020_2021,  # COVID response
        ...     period2_data=meetings_2022_2023,  # Inflation fight
        ...     period1_label="COVID Response",
        ...     period2_label="Inflation Fight"
        ... )
        {
            'period1': {
                'label': 'COVID Response',
                'regime': 'accommodative',
                'avg_sentiment_score': -12,
                'actions': ['decrease', 'unchanged', 'unchanged']
            },
            'period2': {
                'label': 'Inflation Fight',
                'regime': 'tightening',
                'avg_sentiment_score': 16,
                'actions': ['increase', 'increase', 'increase']
            },
            'comparison': {
                'sentiment_shift': 28,  # From -12 to +16
                'regime_change': 'accommodative → tightening',
                'interpretation': 'Complete policy reversal from maximum support to aggressive tightening'
            }
        }
    """
    logger.info(f"Comparing {period1_label} vs {period2_label}")
    
    try:
        tracker = SentimentTracker()
        detector = RegimeDetector()
        
        # Analyze period 1
        p1_regime = detector.get_current_regime(period1_data)
        p1_df = tracker.create_sentiment_timeseries(period1_data)
        p1_avg_score = p1_df['score'].mean() if not p1_df.empty and 'score' in p1_df.columns else 0
        p1_actions = [m.get('action') for m in period1_data if m.get('action')]
        
        # Analyze period 2
        p2_regime = detector.get_current_regime(period2_data)
        p2_df = tracker.create_sentiment_timeseries(period2_data)
        p2_avg_score = p2_df['score'].mean() if not p2_df.empty and 'score' in p2_df.columns else 0
        p2_actions = [m.get('action') for m in period2_data if m.get('action')]
        
        # Compare
        sentiment_shift = p2_avg_score - p1_avg_score
        
        if abs(sentiment_shift) > 15:
            interpretation = "Complete policy reversal"
        elif abs(sentiment_shift) > 8:
            interpretation = "Significant policy shift"
        elif abs(sentiment_shift) > 3:
            interpretation = "Moderate policy shift"
        else:
            interpretation = "Relatively stable policy"
        
        if sentiment_shift > 0:
            interpretation += " toward more hawkish stance"
        elif sentiment_shift < 0:
            interpretation += " toward more dovish stance"
        
        return {
            'period1': {
                'label': period1_label,
                'regime': p1_regime.get('regime', 'unknown'),
                'avg_sentiment_score': round(float(p1_avg_score), 2),
                'num_meetings': len(period1_data),
                'actions': p1_actions
            },
            'period2': {
                'label': period2_label,
                'regime': p2_regime.get('regime', 'unknown'),
                'avg_sentiment_score': round(float(p2_avg_score), 2),
                'num_meetings': len(period2_data),
                'actions': p2_actions
            },
            'comparison': {
                'sentiment_shift': round(float(sentiment_shift), 2),
                'regime_change': f"{p1_regime.get('regime', '?')} → {p2_regime.get('regime', '?')}",
                'interpretation': interpretation
            }
        }
        
    except Exception as e:
        logger.error(f"Error comparing periods: {e}")
        return {'error': str(e)}


def get_current_policy_assessment(
    recent_meetings: List[Dict],
    economic_data: Optional[Dict] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Get comprehensive current policy assessment.
    
    Combines all analysis components for complete current state picture.
    
    Args:
        recent_meetings: List of recent meeting data (recommend 12-24 meetings)
        economic_data: Optional current economic conditions
        tool_context: ADK tool context
    
    Returns:
        Comprehensive policy assessment
    
    Example:
        >>> get_current_policy_assessment(
        ...     recent_meetings=last_12_meetings,
        ...     economic_data={'inflation': 3.2, 'unemployment': 3.7, ...}
        ... )
        {
            'summary': 'Fed in restrictive regime, hawkish stance well-aligned with conditions',
            'current_stance': {...},
            'current_regime': {...},
            'sentiment_trend': {...},
            'appropriateness': {...}
        }
    """
    logger.info("Generating current policy assessment")
    
    try:
        # Get all analyses
        stance = classify_policy_stance_tool(recent_meetings, economic_data)
        regime = detect_regime_changes(recent_meetings)
        sentiment = analyze_sentiment_trend(recent_meetings)
        
        # Generate summary
        current_regime_name = regime.get('current_regime', {}).get('regime', 'unknown')
        current_stance_name = stance.get('overall_stance', {}).get('stance', 'unknown')
        
        if stance.get('conditions_comparison'):
            alignment = stance['conditions_comparison'].get('alignment', 'unknown')
            summary = f"Fed in {current_regime_name} regime, {current_stance_name} stance {alignment} with conditions"
        else:
            summary = f"Fed in {current_regime_name} regime, {current_stance_name} stance"
        
        return {
            'summary': summary,
            'current_stance': stance.get('overall_stance'),
            'current_regime': regime.get('current_regime'),
            'sentiment_trend': sentiment.get('trend'),
            'appropriateness': stance.get('conditions_comparison'),
            'recent_shifts': sentiment.get('significant_shifts', []),
            'num_meetings_analyzed': len(recent_meetings)
        }
        
    except Exception as e:
        logger.error(f"Error generating assessment: {e}")
        return {'error': str(e)}


# Export all tools
__all__ = [
    'analyze_sentiment_trend',
    'detect_regime_changes',
    'classify_policy_stance_tool',
    'compare_policy_periods',
    'get_current_policy_assessment'
]
