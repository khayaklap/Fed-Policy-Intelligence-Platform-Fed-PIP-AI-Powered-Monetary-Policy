"""
Treasury Agent Tools

Tools for yield curve analysis, TIPS breakevens (market inflation expectations),
and monetary policy stance assessment.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from google.adk.tools.tool_context import ToolContext

# Handle relative imports for package usage and absolute for direct execution
try:
    from .treasury_api_wrapper import get_treasury_wrapper
    from .treasury_config import YIELD_CURVE_MATURITIES
except ImportError:
    from treasury_api_wrapper import get_treasury_wrapper
    from treasury_config import YIELD_CURVE_MATURITIES

logger = logging.getLogger(__name__)


def get_yield_curve_data(
    date: Optional[str] = None,
    maturities: Optional[List[str]] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Get Treasury yield curve for a specific date.
    
    The yield curve shows interest rates across different maturities.
    Shape indicates economic expectations:
    - Normal (upward sloping) = healthy growth expectations
    - Flat = uncertainty
    - Inverted = recession expectations
    
    Args:
        date: Date in 'YYYY-MM-DD' format (default: latest)
        maturities: List of maturities like ["3m", "2y", "10y"] (default: all)
        tool_context: ADK tool context
    
    Returns:
        Dictionary with yield curve data and analysis
    
    Example:
        >>> get_yield_curve_data(date="2022-12-31")
        {
            'date': '2022-12-31',
            'yields': {
                '3m': {'yield': 4.42, 'maturity_years': 0.25},
                '2y': {'yield': 4.43, 'maturity_years': 2.0},
                '10y': {'yield': 3.88, 'maturity_years': 10.0}
            },
            'curve_characteristics': {
                '2s10s_spread': -0.55,
                '2s10s_inverted': True,
                'curve_status': 'inverted',
                'recession_signal': True
            }
        }
    """
    treasury = get_treasury_wrapper()
    
    logger.info(f"Fetching yield curve for {date or 'latest'}")
    
    result = treasury.get_yield_curve(date=date, maturities=maturities)
    
    if 'error' in result:
        return result
    
    # Add interpretation
    curve_char = result['curve_characteristics']
    
    if curve_char.get('recession_signal'):
        result['interpretation'] = (
            f"Yield curve is inverted (2s10s: {curve_char.get('2s10s_spread', 'N/A')}bp), "
            f"signaling recession concerns. Historically, inversions precede recessions by 6-18 months."
        )
    elif curve_char.get('curve_status') == 'flat':
        result['interpretation'] = (
            f"Yield curve is flat (2s10s: {curve_char.get('2s10s_spread', 'N/A')}bp), "
            f"indicating uncertainty about growth outlook."
        )
    else:
        result['interpretation'] = (
            f"Yield curve has normal upward slope (2s10s: {curve_char.get('2s10s_spread', 'N/A')}bp), "
            f"indicating healthy growth expectations."
        )
    
    return result


def get_market_inflation_expectations(
    maturity: str = "10y",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Get market-implied inflation expectations via TIPS breakeven rates.
    
    CRITICAL FOR FED ANALYSIS:
    - Breakeven = Nominal yield - TIPS yield
    - Represents market's average inflation expectation over maturity period
    - Fed watches 5y5y forward (inflation 5-10 years ahead) for credibility
    - Well-anchored around 2% = Fed credibility intact
    - Rising above 2.5% = De-anchoring risk
    
    Args:
        maturity: "5y", "10y", "20y", or "30y"
        start_date: Start date for time series (default: 2 years ago)
        end_date: End date (default: today)
        tool_context: ADK tool context
    
    Returns:
        Dictionary with breakeven data and interpretation
    
    Example:
        >>> get_market_inflation_expectations(maturity="10y")
        {
            'maturity': '10y',
            'latest': {
                'date': '2024-11-29',
                'nominal_yield': 4.25,
                'tips_yield': 1.95,
                'breakeven': 2.30
            },
            'expectation_status': 'moderately_anchored',
            'interpretation': 'Inflation expectations somewhat elevated but contained'
        }
    """
    treasury = get_treasury_wrapper()
    
    logger.info(f"Fetching {maturity} market inflation expectations")
    
    result = treasury.get_tips_breakeven(
        maturity=maturity,
        start_date=start_date,
        end_date=end_date
    )
    
    if 'error' in result:
        return result
    
    # Add Fed policy context
    latest_breakeven = result['latest']['breakeven']
    
    if result['expectation_status'] == 'well_anchored':
        result['fed_implication'] = "Market inflation expectations well-anchored - Fed credibility strong"
    elif result['expectation_status'] == 'de_anchoring':
        result['fed_implication'] = "Inflation expectations de-anchoring - Fed may need to tighten more"
    elif result['expectation_status'] == 'unanchored':
        result['fed_implication'] = "Severe credibility risk - Fed behind the curve"
    elif result['expectation_status'] == 'below_target':
        result['fed_implication'] = "Deflation concerns - Fed may need more stimulus"
    else:
        result['fed_implication'] = "Inflation expectations moderately elevated - Fed monitoring closely"
    
    return result


def analyze_monetary_policy_stance(
    date: Optional[str] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Assess current monetary policy stance using real yields.
    
    Real yield = inflation-adjusted return = how tight/loose policy really is
    
    Key Concept:
    - Neutral real rate (R-star) ≈ 0.5% (FOMC estimate)
    - Real yield > R-star = restrictive (slowing economy)
    - Real yield < R-star = accommodative (stimulating economy)
    
    Args:
        date: Date for analysis (default: latest)
        tool_context: ADK tool context
    
    Returns:
        Dictionary with policy stance assessment
    
    Example:
        >>> analyze_monetary_policy_stance()
        {
            'date': '2024-11-29',
            'real_yields': {
                '10y': {'real_yield': 2.15}
            },
            'policy_stance': 'restrictive',
            'policy_interpretation': 'Elevated real rates - restrictive monetary policy',
            'neutral_rate_reference': 0.5,
            'analysis': 'Real yields 165bp above neutral - policy is restrictive'
        }
    """
    treasury = get_treasury_wrapper()
    
    logger.info(f"Analyzing monetary policy stance for {date or 'latest'}")
    
    result = treasury.calculate_real_yields(date=date)
    
    if 'error' in result:
        return result
    
    # Add detailed analysis
    if '10y' in result['real_yields']:
        real_10y = result['real_yields']['10y']['real_yield']
        neutral = result['neutral_rate_reference']
        spread_to_neutral = real_10y - neutral
        
        result['spread_to_neutral'] = round(spread_to_neutral, 2)
        
        if abs(spread_to_neutral) < 0.25:
            result['analysis'] = f"Real yields near neutral ({neutral}%) - balanced policy"
        elif spread_to_neutral > 0:
            result['analysis'] = (
                f"Real yields {int(spread_to_neutral * 100)}bp above neutral - "
                f"policy is {'restrictive' if spread_to_neutral > 1.0 else 'mildly restrictive'}"
            )
        else:
            result['analysis'] = (
                f"Real yields {int(abs(spread_to_neutral) * 100)}bp below neutral - "
                f"policy is {'accommodative' if abs(spread_to_neutral) > 1.0 else 'mildly accommodative'}"
            )
    
    return result


def detect_yield_curve_inversion(
    spread_type: str = "2s10s",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Detect yield curve inversions - a key recession predictor.
    
    RECESSION INDICATOR:
    - Inversion = short-term yields > long-term yields
    - 2s10s most watched (2-year vs 10-year)
    - Historical record: Every recession since 1970 preceded by inversion
    - Lead time: Typically 6-18 months before recession
    
    Args:
        spread_type: "2s10s" or "3m10y" (both are recession indicators)
        start_date: Start date for analysis (default: 2 years ago)
        end_date: End date (default: today)
        tool_context: ADK tool context
    
    Returns:
        Dictionary with inversion analysis and recession probability
    
    Example:
        >>> detect_yield_curve_inversion(spread_type="2s10s")
        {
            'spread_type': '2s10s',
            'latest': {'date': '2024-11-29', 'spread': 0.35},
            'inversion_analysis': {
                'currently_inverted': False,
                'inversion_days': 245,
                'inversion_percentage': 33.7
            },
            'recession_signal': False,
            'interpretation': 'Curve has normalized after 245 days inverted. 
                              Recession risk elevated but not imminent.'
        }
    """
    treasury = get_treasury_wrapper()
    
    logger.info(f"Analyzing {spread_type} spread for inversions")
    
    result = treasury.get_yield_spread_history(
        spread_type=spread_type,
        start_date=start_date,
        end_date=end_date
    )
    
    if 'error' in result:
        return result
    
    # Add interpretation
    inv_analysis = result['inversion_analysis']
    currently_inverted = inv_analysis['currently_inverted']
    inv_days = inv_analysis['inversion_days']
    inv_pct = inv_analysis['inversion_percentage']
    
    if currently_inverted:
        result['interpretation'] = (
            f"Yield curve is currently inverted ({result['latest']['spread']:.2f}bp). "
            f"Has been inverted for {inv_days} days ({inv_pct}% of period). "
            f"This historically precedes recessions by 6-18 months."
        )
        result['recession_probability'] = "elevated"
    elif inv_days > 0:
        result['interpretation'] = (
            f"Yield curve has normalized (current spread: {result['latest']['spread']:.2f}bp) "
            f"after being inverted for {inv_days} days. "
            f"Recession risk remains elevated for 6-12 months after un-inversion."
        )
        result['recession_probability'] = "moderate"
    else:
        result['interpretation'] = (
            f"Yield curve is normal (spread: {result['latest']['spread']:.2f}bp). "
            f"No inversion detected in the analysis period. "
            f"Recession risk is low based on yield curve."
        )
        result['recession_probability'] = "low"
    
    return result


def compare_fed_forecast_vs_market(
    fed_inflation_forecast: float,
    forecast_date: str,
    forecast_horizon: str = "10y",
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Compare Fed's inflation forecast with market expectations (TIPS breakeven).
    
    KEY ANALYSIS:
    - Fed forecast vs Market expectation = credibility check
    - If market > Fed → Market skeptical of Fed's ability to control inflation
    - If Fed > Market → Fed may be too hawkish, recession risk
    - Convergence = Alignment of expectations
    
    Args:
        fed_inflation_forecast: Fed's projected inflation (from SEP)
        forecast_date: Date when Fed made forecast
        forecast_horizon: Maturity to compare ("5y" or "10y")
        tool_context: ADK tool context
    
    Returns:
        Dictionary comparing Fed vs market expectations
    
    Example:
        >>> compare_fed_forecast_vs_market(
        ...     fed_inflation_forecast=2.0,
        ...     forecast_date="2021-06-01",
        ...     forecast_horizon="10y"
        ... )
        {
            'fed_forecast': 2.0,
            'market_expectation': 2.4,
            'divergence': 0.4,
            'interpretation': 'Market expects higher inflation than Fed - 
                              credibility concerns or Fed behind curve'
        }
    """
    treasury = get_treasury_wrapper()
    
    logger.info(f"Comparing Fed forecast ({fed_inflation_forecast}%) with market expectations")
    
    # Get market expectation at forecast date
    # Use a small window around the forecast date
    from datetime import datetime, timedelta
    forecast_dt = datetime.strptime(forecast_date, '%Y-%m-%d')
    start = (forecast_dt - timedelta(days=5)).strftime('%Y-%m-%d')
    end = (forecast_dt + timedelta(days=5)).strftime('%Y-%m-%d')
    
    breakeven_data = treasury.get_tips_breakeven(
        maturity=forecast_horizon,
        start_date=start,
        end_date=end
    )
    
    if 'error' in breakeven_data:
        return breakeven_data
    
    # Get closest market expectation to forecast date
    market_expectation = breakeven_data['latest']['breakeven']
    
    # Calculate divergence
    divergence = market_expectation - fed_inflation_forecast
    
    # Interpret
    if abs(divergence) < 0.25:
        interpretation = (
            f"Fed and market expectations aligned (difference: {divergence:.2f}pp). "
            f"Strong policy credibility."
        )
        credibility = "strong"
    elif divergence > 0.5:
        interpretation = (
            f"Market expects significantly higher inflation than Fed ({divergence:.2f}pp above). "
            f"Market skeptical of Fed's ability to control inflation or Fed behind curve."
        )
        credibility = "weak"
    elif divergence > 0.25:
        interpretation = (
            f"Market expects moderately higher inflation than Fed ({divergence:.2ff}pp above). "
            f"Some credibility concerns or Fed viewed as optimistic."
        )
        credibility = "moderate"
    elif divergence < -0.5:
        interpretation = (
            f"Fed expects significantly higher inflation than market ({abs(divergence):.2f}pp below). "
            f"Fed may be too hawkish - recession risk."
        )
        credibility = "moderate"
    else:
        interpretation = (
            f"Fed expects moderately higher inflation than market ({abs(divergence):.2f}pp below). "
            f"Fed taking conservative approach."
        )
        credibility = "strong"
    
    return {
        'forecast_date': forecast_date,
        'horizon': forecast_horizon,
        'fed_forecast': fed_inflation_forecast,
        'market_expectation': round(market_expectation, 2),
        'divergence': round(divergence, 2),
        'interpretation': interpretation,
        'fed_credibility': credibility,
        'market_data': breakeven_data['latest']
    }


def get_yield_curve_evolution(
    start_date: str,
    end_date: str,
    key_dates: Optional[List[str]] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Track yield curve evolution over time - useful for Fed policy analysis.
    
    Shows how market expectations changed during:
    - FOMC tightening cycles
    - Economic shocks
    - Policy regime changes
    
    Args:
        start_date: Start date for analysis
        end_date: End date for analysis  
        key_dates: Optional list of specific dates to highlight (FOMC meetings)
        tool_context: ADK tool context
    
    Returns:
        Dictionary with yield curve evolution data
    
    Example:
        >>> get_yield_curve_evolution(
        ...     start_date="2022-01-01",
        ...     end_date="2022-12-31",
        ...     key_dates=["2022-03-16", "2022-06-15", "2022-09-21", "2022-12-14"]
        ... )
        {
            'period': '2022-01-01 to 2022-12-31',
            'snapshots': [
                {'date': '2022-03-16', 'yields': {...}, 'event': 'First 25bp hike'},
                {'date': '2022-06-15', 'yields': {...}, 'event': 'First 75bp hike'},
                ...
            ],
            'evolution': 'Curve inverted in July 2022 as Fed hiked aggressively'
        }
    """
    treasury = get_treasury_wrapper()
    
    logger.info(f"Analyzing yield curve evolution from {start_date} to {end_date}")
    
    # Get snapshots at key dates
    snapshots = []
    
    if key_dates:
        dates_to_analyze = key_dates
    else:
        # Sample quarterly if no specific dates given
        from datetime import datetime, timedelta
        import pandas as pd
        date_range = pd.date_range(start_date, end_date, freq='QS')
        dates_to_analyze = [d.strftime('%Y-%m-%d') for d in date_range]
    
    for date in dates_to_analyze:
        curve_data = treasury.get_yield_curve(date=date)
        if 'error' not in curve_data:
            snapshots.append({
                'date': date,
                'yields': curve_data['yields'],
                'curve_characteristics': curve_data['curve_characteristics']
            })
    
    if not snapshots:
        return {'error': 'No curve data available for specified period'}
    
    # Analyze evolution
    first_snapshot = snapshots[0]
    last_snapshot = snapshots[-1]
    
    # Compare first and last
    if '2y' in first_snapshot['yields'] and '2y' in last_snapshot['yields']:
        change_2y = last_snapshot['yields']['2y']['yield'] - first_snapshot['yields']['2y']['yield']
    else:
        change_2y = None
    
    if '10y' in first_snapshot['yields'] and '10y' in last_snapshot['yields']:
        change_10y = last_snapshot['yields']['10y']['yield'] - first_snapshot['yields']['10y']['yield']
    else:
        change_10y = None
    
    evolution_summary = f"Period: {start_date} to {end_date}. "
    if change_2y is not None and change_10y is not None:
        evolution_summary += (
            f"2Y yield: {first_snapshot['yields']['2y']['yield']:.2f}% → "
            f"{last_snapshot['yields']['2y']['yield']:.2f}% ({change_2y:+.2f}pp). "
            f"10Y yield: {first_snapshot['yields']['10y']['yield']:.2f}% → "
            f"{last_snapshot['yields']['10y']['yield']:.2f}% ({change_10y:+.2f}pp). "
        )
    
    # Detect inversion periods
    inversion_periods = []
    for snapshot in snapshots:
        if snapshot['curve_characteristics'].get('2s10s_inverted'):
            inversion_periods.append(snapshot['date'])
    
    if inversion_periods:
        evolution_summary += f"Curve inverted on {len(inversion_periods)} of {len(snapshots)} snapshots."
    
    return {
        'period': f"{start_date} to {end_date}",
        'snapshots': snapshots,
        'evolution_summary': evolution_summary,
        'inversion_periods': inversion_periods
    }


# Export all tool functions
__all__ = [
    'get_yield_curve_data',
    'get_market_inflation_expectations',
    'analyze_monetary_policy_stance',
    'detect_yield_curve_inversion',
    'compare_fed_forecast_vs_market',
    'get_yield_curve_evolution'
]
