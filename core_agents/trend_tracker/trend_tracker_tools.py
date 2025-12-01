"""
Trend Tracker Tools

ADK tools for long-term Fed policy analysis: trends, cycles, reaction function,
forecast bias, and predictive indicators.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from google.adk.tools.tool_context import ToolContext

try:
    # Try relative imports first (when used as module)
    from .long_term_analyzer import LongTermAnalyzer, analyze_long_term_patterns
    from .cycle_detector import CycleDetector, detect_policy_cycles
    from .reaction_forecast_analysis import (
        ReactionFunctionAnalyzer,
        ForecastBiasTracker,
        analyze_reaction_and_bias
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

logger = logging.getLogger(__name__)


def analyze_long_term_trends_tool(
    meeting_data: List[Dict],
    variable: str = 'score',
    min_meetings: int = 24,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Analyze long-term Fed policy trends (6+ years).
    
    Identifies structural breaks, persistent patterns, and multi-year shifts
    in Fed policy stance using change point detection and trend analysis.
    
    Args:
        meeting_data: List of meeting data (recommend 24+ meetings)
        variable: Variable to analyze ('score', 'fed_funds', etc.)
        min_meetings: Minimum meetings required (default: 24 = 6 years)
        tool_context: ADK tool context
    
    Returns:
        Dictionary with long-term trend analysis
    
    Example:
        >>> analyze_long_term_trends_tool(
        ...     meetings_2005_2025,  # 20 years of data
        ...     variable='score'
        ... )
        {
            'direction': 'cyclical',  # or hawkish_trend, dovish_trend
            'strength': 'moderate',
            'changepoints': [
                {'date': '2008-09-15', 'type': 'major_shift'},  # GFC
                {'date': '2020-03-15', 'type': 'major_shift'},  # COVID
                {'date': '2022-03-16', 'type': 'major_shift'}   # Inflation fight
            ],
            'persistence': 'moderately_persistent',
            'volatility': {
                'overall_trend': 'increasing',
                'interpretation': 'Policy volatility rising'
            }
        }
    """
    logger.info(f"Analyzing long-term trends in {variable}")
    
    try:
        analyzer = LongTermAnalyzer()
        
        # Main trend analysis
        trend = analyzer.analyze_long_term_trend(meeting_data, variable, min_meetings)
        
        if 'error' in trend:
            return trend
        
        # Volatility analysis
        volatility = analyzer.analyze_volatility(meeting_data, variable)
        
        # Regime persistence (if regime data available)
        if any('regime' in m for m in meeting_data):
            regime_persistence = analyzer.detect_regime_persistence(meeting_data)
        else:
            regime_persistence = None
        
        return {
            'trend_analysis': trend,
            'volatility': volatility,
            'regime_persistence': regime_persistence,
            'summary': f"{trend['strength'].replace('_', ' ').title()} {trend['direction'].replace('_', ' ')} detected across {trend['num_meetings']} meetings"
        }
        
    except Exception as e:
        logger.error(f"Error in long-term trend analysis: {e}")
        return {'error': str(e)}


def detect_policy_cycles_tool(
    meeting_data: List[Dict],
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Detect Fed policy cycles and identify current cycle phase.
    
    Analyzes policy cycles (expansion → slowdown → recession → recovery),
    finds peaks/troughs in rates, and compares to historical cycles.
    
    Args:
        meeting_data: List of meeting data (recommend 24+ meetings)
        tool_context: ADK tool context
    
    Returns:
        Dictionary with cycle analysis
    
    Example:
        >>> detect_policy_cycles_tool(meetings_2015_2024)
        {
            'current_phase': {
                'phase': 'expansion_late',
                'duration': 8,  # 8 meetings in this phase
                'expected_next_phase': 'slowdown',
                'confidence': 'high'
            },
            'peaks_and_troughs': {
                'peaks': [
                    {'date': '2006-06-29', 'value': 5.25},
                    {'date': '2018-12-19', 'value': 2.50},
                    {'date': '2023-07-26', 'value': 5.50}
                ],
                'troughs': [
                    {'date': '2008-12-16', 'value': 0.00},
                    {'date': '2020-03-15', 'value': 0.00}
                ]
            },
            'cycle_metrics': {
                'peak_to_peak_duration': 60,  # meetings
                'amplitude': 5.50,  # percentage points
                'comparison_to_average': {
                    'duration': 'shorter_than_average',
                    'amplitude': 'larger_than_average'
                }
            },
            'historical_comparison': {
                'most_similar': 'covid_inflation',
                'similarity': 0.75
            }
        }
    """
    logger.info("Detecting policy cycles")
    
    try:
        result = detect_policy_cycles(meeting_data)
        return result
        
    except Exception as e:
        logger.error(f"Error in cycle detection: {e}")
        return {'error': str(e)}


def analyze_reaction_function_tool(
    meeting_data: List[Dict],
    economic_data: Optional[List[Dict]] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Analyze Fed's reaction function - how Fed responds to economic data.
    
    Estimates Taylor Rule parameters and detects asymmetries in Fed response
    (e.g., cuts faster than it hikes).
    
    Args:
        meeting_data: Meeting data with policy actions
        economic_data: Economic data (inflation, unemployment, GDP)
        tool_context: ADK tool context
    
    Returns:
        Dictionary with reaction function analysis
    
    Example:
        >>> analyze_reaction_function_tool(
        ...     meetings_2010_2024,
        ...     economic_data=[
        ...         {'date': '2010-01', 'fed_funds': 0.25, 'inflation': 1.5, 'unemployment': 9.8},
        ...         {'date': '2010-02', 'fed_funds': 0.25, 'inflation': 1.6, 'unemployment': 9.7},
        ...         ...
        ...     ]
        ... )
        {
            'taylor_rule': {
                'estimated_coefficients': {
                    'inflation': 1.8,  # Fed responds strongly to inflation
                    'unemployment': -0.6,  # Moderately to unemployment
                    'intercept': 2.3
                },
                'r_squared': 0.65,
                'interpretation': 'Fed more aggressive on inflation than Taylor'
            },
            'asymmetry': {
                'pattern': 'cuts_faster',
                'num_increases': 9,
                'num_decreases': 7,
                'interpretation': 'Fed cuts faster than it hikes (typical)'
            }
        }
    """
    logger.info("Analyzing reaction function")
    
    try:
        analyzer = ReactionFunctionAnalyzer()
        
        results = {}
        
        # Taylor Rule estimation
        if economic_data and len(economic_data) >= 12:
            results['taylor_rule'] = analyzer.estimate_taylor_rule(
                meeting_data,
                economic_data
            )
        else:
            results['taylor_rule'] = {
                'error': 'Need economic data with inflation & unemployment'
            }
        
        # Asymmetry detection
        results['asymmetry'] = analyzer.detect_asymmetry(meeting_data)
        
        return results
        
    except Exception as e:
        logger.error(f"Error in reaction function analysis: {e}")
        return {'error': str(e)}


def track_forecast_bias_tool(
    forecasts: List[Dict],
    actuals: List[Dict],
    variable: str = 'pce_inflation',
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Track systematic bias in Fed forecasts.
    
    Identifies if Fed consistently over/under-estimates economic variables
    and detects patterns in forecast errors.
    
    Args:
        forecasts: List of Fed forecasts [{'date': ..., 'value': ...}, ...]
        actuals: List of actual outcomes [{'date': ..., 'value': ...}, ...]
        variable: Variable being forecasted
        tool_context: ADK tool context
    
    Returns:
        Dictionary with forecast bias analysis
    
    Example:
        >>> track_forecast_bias_tool(
        ...     forecasts=[
        ...         {'date': '2021-06', 'value': 2.1, 'horizon': '2022'},
        ...         {'date': '2021-12', 'value': 2.6, 'horizon': '2022'},
        ...         {'date': '2022-03', 'value': 4.3, 'horizon': '2022'}
        ...     ],
        ...     actuals=[
        ...         {'date': '2022-12', 'value': 6.5}
        ...     ],
        ...     variable='pce_inflation'
        ... )
        {
            'bias_analysis': {
                'has_systematic_bias': True,
                'bias_type': 'underestimation_bias',
                'mean_error': -2.8,  # Forecasts 2.8pp too low on average
                'mae': 2.8,
                'interpretation': 'Fed systematically underestimates inflation'
            },
            'pattern': {
                'pattern': 'deteriorating',
                'trend_slope': 0.45,  # Errors getting worse over time
                'interpretation': 'Forecast accuracy deteriorating'
            }
        }
    """
    logger.info(f"Tracking forecast bias for {variable}")
    
    try:
        tracker = ForecastBiasTracker()
        
        # Bias analysis
        bias_analysis = tracker.analyze_forecast_bias(forecasts, actuals, variable)
        
        # Pattern analysis (if we have errors)
        if 'mean_error' in bias_analysis:
            # Extract errors
            errors = []
            timestamps = []
            for f, a in zip(forecasts, actuals):
                if 'value' in f and 'value' in a:
                    errors.append(a['value'] - f['value'])
                    timestamps.append(f.get('date', len(timestamps)))
            
            if len(errors) >= 8:
                pattern = tracker.identify_bias_patterns(errors, timestamps)
            else:
                pattern = {'note': 'Need 8+ observations for pattern analysis'}
        else:
            pattern = None
        
        return {
            'bias_analysis': bias_analysis,
            'pattern': pattern
        }
        
    except Exception as e:
        logger.error(f"Error in forecast bias tracking: {e}")
        return {'error': str(e)}


def generate_predictive_indicators_tool(
    recent_meetings: List[Dict],
    current_economic_data: Optional[Dict] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Generate predictive indicators for future Fed policy actions.
    
    Identifies leading signals that historically precede policy changes,
    such as sentiment shifts, forecast revisions, or economic imbalances.
    
    Args:
        recent_meetings: Recent meeting data (12+ meetings recommended)
        current_economic_data: Current economic conditions
        tool_context: ADK tool context
    
    Returns:
        Dictionary with predictive indicators
    
    Example:
        >>> generate_predictive_indicators_tool(
        ...     recent_meetings=last_12_meetings,
        ...     current_economic_data={
        ...         'inflation': 3.5,
        ...         'unemployment': 3.7,
        ...         'gdp_growth': 2.1
        ...     }
        ... )
        {
            'active_indicators': [
                {
                    'indicator': 'inflation_persistence',
                    'status': 'triggered',
                    'signal': 'Inflation above 2.5% for 4 consecutive quarters',
                    'lead_time': 3,  # meetings
                    'reliability': 0.80,
                    'implication': 'Tightening likely in 3 meetings'
                },
                {
                    'indicator': 'sentiment_shift',
                    'status': 'triggered',
                    'signal': '12-point hawkish shift in last 2 meetings',
                    'lead_time': 2,
                    'reliability': 0.75,
                    'implication': 'Rate hike likely in 2 meetings'
                }
            ],
            'predicted_action': 'hike',
            'confidence': 0.85,
            'time_horizon': 2,  # meetings until action
            'interpretation': 'High confidence rate hike expected in ~2 meetings (6 months)'
        }
    """
    logger.info("Generating predictive indicators")
    
    try:
        from trend_tracker_config import LEADING_INDICATORS
        
        if len(recent_meetings) < 6:
            return {'error': 'Need at least 6 recent meetings'}
        
        active_indicators = []
        
        # Check sentiment shift
        if len(recent_meetings) >= 3:
            recent_scores = [m.get('score', 0) for m in recent_meetings[-3:]]
            older_scores = [m.get('score', 0) for m in recent_meetings[-6:-3]] if len(recent_meetings) >= 6 else []
            
            if older_scores:
                recent_avg = sum(recent_scores) / len(recent_scores)
                older_avg = sum(older_scores) / len(older_scores)
                shift = recent_avg - older_avg
                
                if abs(shift) >= LEADING_INDICATORS['sentiment_shift']['threshold']:
                    active_indicators.append({
                        'indicator': 'sentiment_shift',
                        'status': 'triggered',
                        'signal': f'{abs(shift):.0f}-point {"hawkish" if shift > 0 else "dovish"} shift',
                        'lead_time': LEADING_INDICATORS['sentiment_shift']['lead_time'],
                        'reliability': LEADING_INDICATORS['sentiment_shift']['reliability'],
                        'implication': f'{"Rate hike" if shift > 0 else "Rate cut"} likely in {LEADING_INDICATORS["sentiment_shift"]["lead_time"]} meetings'
                    })
        
        # Check inflation persistence (if economic data available)
        if current_economic_data and 'inflation' in current_economic_data:
            inflation = current_economic_data['inflation']
            threshold = LEADING_INDICATORS['inflation_persistence']['threshold']
            
            if inflation > threshold:
                active_indicators.append({
                    'indicator': 'inflation_persistence',
                    'status': 'triggered',
                    'signal': f'Inflation at {inflation}% > {threshold}%',
                    'lead_time': LEADING_INDICATORS['inflation_persistence']['lead_time'],
                    'reliability': LEADING_INDICATORS['inflation_persistence']['reliability'],
                    'implication': f'Tightening likely in {LEADING_INDICATORS["inflation_persistence"]["lead_time"]} meetings'
                })
        
        # Check unemployment gap
        if current_economic_data and 'unemployment' in current_economic_data:
            unemployment = current_economic_data['unemployment']
            nairu = 4.0  # Estimate
            gap = nairu - unemployment
            threshold = LEADING_INDICATORS['unemployment_gap']['threshold']
            
            if gap > threshold:
                active_indicators.append({
                    'indicator': 'unemployment_gap',
                    'status': 'triggered',
                    'signal': f'Unemployment {gap:.1f}pp below NAIRU',
                    'lead_time': LEADING_INDICATORS['unemployment_gap']['lead_time'],
                    'reliability': LEADING_INDICATORS['unemployment_gap']['reliability'],
                    'implication': f'Tightening likely in {LEADING_INDICATORS["unemployment_gap"]["lead_time"]} meetings'
                })
        
        # Determine overall prediction
        if not active_indicators:
            predicted_action = 'unchanged'
            confidence = 0.5
            time_horizon = None
        else:
            # Most indicators suggest tightening or easing?
            tightening_signals = sum(1 for ind in active_indicators if 'hike' in ind['implication'].lower() or 'tighten' in ind['implication'].lower())
            easing_signals = sum(1 for ind in active_indicators if 'cut' in ind['implication'].lower() or 'ease' in ind['implication'].lower())
            
            if tightening_signals > easing_signals:
                predicted_action = 'hike'
            elif easing_signals > tightening_signals:
                predicted_action = 'cut'
            else:
                predicted_action = 'uncertain'
            
            # Confidence based on number and reliability of indicators
            avg_reliability = sum(ind['reliability'] for ind in active_indicators) / len(active_indicators)
            signal_strength = min(len(active_indicators) / 3, 1.0)  # Max at 3 indicators
            confidence = avg_reliability * signal_strength
            
            # Time horizon = shortest lead time
            time_horizon = min(ind['lead_time'] for ind in active_indicators)
        
        return {
            'active_indicators': active_indicators,
            'predicted_action': predicted_action,
            'confidence': round(confidence, 2),
            'time_horizon': time_horizon,
            'interpretation': _interpret_prediction(predicted_action, confidence, time_horizon, len(active_indicators))
        }
        
    except Exception as e:
        logger.error(f"Error generating predictive indicators: {e}")
        return {'error': str(e)}


def _interpret_prediction(
    action: str,
    confidence: float,
    time_horizon: Optional[int],
    num_indicators: int
) -> str:
    """Interpret predictive indicator results."""
    
    if action == 'unchanged':
        return "No strong signals for policy change detected"
    
    if confidence >= 0.75:
        conf_word = "High confidence"
    elif confidence >= 0.5:
        conf_word = "Moderate confidence"
    else:
        conf_word = "Low confidence"
    
    if time_horizon:
        return f"{conf_word} {action} expected in ~{time_horizon} meetings ({time_horizon * 1.5:.0f} months) based on {num_indicators} indicators"
    else:
        return f"{conf_word} {action} expected based on {num_indicators} indicators"


# Export all tools
__all__ = [
    'analyze_long_term_trends_tool',
    'detect_policy_cycles_tool',
    'analyze_reaction_function_tool',
    'track_forecast_bias_tool',
    'generate_predictive_indicators_tool'
]
