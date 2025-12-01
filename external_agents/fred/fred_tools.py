"""
FRED Agent Tools

Individual tool functions that will be wrapped as ADK FunctionTools.
Each function provides specific FRED data retrieval capability.
"""

import logging
from typing import Dict, List, Optional
from google.adk.tools.tool_context import ToolContext

# Handle relative imports for package usage and absolute for direct execution
try:
    from .fred_api_wrapper import get_fred_wrapper
    from .fred_config import FRED_SERIES_MAP, INDICATOR_CATEGORIES, DEFAULT_START_DATE
except ImportError:
    from fred_api_wrapper import get_fred_wrapper
    from fred_config import FRED_SERIES_MAP, INDICATOR_CATEGORIES, DEFAULT_START_DATE

logger = logging.getLogger(__name__)




def _to_float(value):
    """Safely convert value to float"""
    try:
        if isinstance(value, (int, float)):
            return float(value)
        elif hasattr(value, 'item'):  # numpy/pandas scalar
            return float(value.item())
        else:
            return float(value)
    except (ValueError, TypeError):
        return 0.0


def get_gdp_data(
    start_date: str = DEFAULT_START_DATE,
    end_date: Optional[str] = None,
    metric: str = "real",  # "real", "nominal", or "growth"
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Get GDP data from FRED.
    
    Args:
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format (default: latest)
        metric: Type of GDP metric ("real", "nominal", "growth")
        tool_context: ADK tool context (optional)
    
    Returns:
        Dictionary with GDP data and metadata
    
    Example:
        >>> get_gdp_data(start_date="2020-01-01", metric="growth")
        {
            'metric': 'growth',
            'series_id': 'A191RL1Q225SBEA',
            'name': 'Real GDP Growth Rate',
            'dates': ['2020-01-01', '2020-04-01', ...],
            'values': [2.3, -31.2, 33.8, ...],
            'units': 'Percent Change from Preceding Period'
        }
    """
    fred = get_fred_wrapper()
    
    # Map metric to series
    metric_map = {
        "real": "gdp_real",
        "nominal": "gdp_nominal",
        "growth": "gdp_growth"
    }
    
    if metric not in metric_map:
        raise ValueError(f"Invalid metric: {metric}. Choose from: {list(metric_map.keys())}")
    
    series_key = metric_map[metric]
    series_id = FRED_SERIES_MAP[series_key]['series_id']
    series_name = FRED_SERIES_MAP[series_key]['name']
    units = FRED_SERIES_MAP[series_key]['units']
    
    logger.info(f"Fetching {metric} GDP data from {start_date} to {end_date}")
    
    # For real/nominal GDP, calculate growth if requested
    if metric in ["real", "nominal"]:
        data = fred.get_series_range(series_id, start_date, end_date, transform='growth')
    else:
        data = fred.get_series_range(series_id, start_date, end_date)
    
    return {
        'metric': metric,
        'series_id': series_id,
        'name': series_name,
        'units': units,
        'start_date': start_date,
        'end_date': end_date or 'latest',
        'frequency': 'Quarterly',
        'dates': data['dates'],
        'values': data['values'],
        'statistics': {
            'mean': data['mean'],
            'min': data['min'],
            'max': data['max'],
            'latest': data['latest']
        }
    }


def get_inflation_data(
    start_date: str = DEFAULT_START_DATE,
    end_date: Optional[str] = None,
    measure: str = "pce_core",  # "pce", "pce_core", "cpi", "cpi_core"
    yoy: bool = True,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Get inflation data from FRED.
    
    This is the Fed's preferred inflation measure (Core PCE).
    
    Args:
        start_date: Start date
        end_date: End date (default: latest)
        measure: Inflation measure to use
        yoy: Return year-over-year percent change (default: True)
        tool_context: ADK tool context
    
    Returns:
        Dictionary with inflation data
    
    Example:
        >>> get_inflation_data(start_date="2020-01-01", measure="pce_core")
        {
            'measure': 'pce_core',
            'name': 'Core PCE Price Index',
            'yoy_change': True,
            'dates': ['2021-01-01', '2021-02-01', ...],
            'values': [1.4, 1.5, 1.8, ...],  # YoY % change
            'units': 'Percent'
        }
    """
    fred = get_fred_wrapper()
    
    valid_measures = ["pce", "pce_core", "cpi", "cpi_core"]
    if measure not in valid_measures:
        raise ValueError(f"Invalid measure: {measure}. Choose from: {valid_measures}")
    
    series_id = FRED_SERIES_MAP[measure]['series_id']
    series_name = FRED_SERIES_MAP[measure]['name']
    
    logger.info(f"Fetching {measure} inflation data (YoY={yoy})")
    
    # Get data with YoY transformation if requested
    transform = 'yoy' if yoy else None
    data = fred.get_series_range(series_id, start_date, end_date, transform=transform)
    
    return {
        'measure': measure,
        'series_id': series_id,
        'name': series_name,
        'yoy_change': yoy,
        'units': 'Percent' if yoy else FRED_SERIES_MAP[measure]['units'],
        'start_date': start_date,
        'end_date': end_date or 'latest',
        'frequency': 'Monthly',
        'dates': data['dates'],
        'values': data['values'],
        'statistics': {
            'mean': data['mean'],
            'min': data['min'],
            'max': data['max'],
            'latest': data['latest']
        },
        'note': 'Core PCE is the Federal Reserve\'s preferred inflation measure' if measure == 'pce_core' else None
    }


def get_employment_data(
    start_date: str = DEFAULT_START_DATE,
    end_date: Optional[str] = None,
    indicators: Optional[List[str]] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Get comprehensive employment data from FRED.
    
    Args:
        start_date: Start date
        end_date: End date (default: latest)
        indicators: List of indicators to fetch (default: all employment indicators)
        tool_context: ADK tool context
    
    Returns:
        Dictionary with employment data for all requested indicators
    
    Example:
        >>> get_employment_data(start_date="2020-01-01", indicators=["unemployment", "nonfarm_payrolls"])
        {
            'start_date': '2020-01-01',
            'end_date': '2024-12-01',
            'indicators': {
                'unemployment': {
                    'series_id': 'UNRATE',
                    'name': 'Unemployment Rate',
                    'values': [...],
                    'latest': {'date': '2024-12-01', 'value': float(3.7)}
                },
                'nonfarm_payrolls': {...}
            }
        }
    """
    fred = get_fred_wrapper()
    
    if indicators is None:
        indicators = INDICATOR_CATEGORIES['employment']
    
    logger.info(f"Fetching employment data for: {indicators}")
    
    results = {
        'start_date': start_date,
        'end_date': end_date or 'latest',
        'indicators': {}
    }
    
    for indicator in indicators:
        if indicator not in FRED_SERIES_MAP:
            logger.warning(f"Unknown indicator: {indicator}, skipping")
            continue
        
        series_id = FRED_SERIES_MAP[indicator]['series_id']
        series_name = FRED_SERIES_MAP[indicator]['name']
        units = FRED_SERIES_MAP[indicator]['units']
        
        try:
            data = fred.get_series_range(series_id, start_date, end_date)
            
            results['indicators'][indicator] = {
                'series_id': series_id,
                'name': series_name,
                'units': units,
                'dates': data['dates'],
                'values': data['values'],
                'statistics': {
                    'mean': data['mean'],
                    'min': data['min'],
                    'max': data['max'],
                    'latest': data['latest']
                }
            }
        except Exception as e:
            logger.error(f"Error fetching {indicator}: {e}")
            results['indicators'][indicator] = {'error': str(e)}
    
    return results


def get_interest_rates(
    start_date: str = DEFAULT_START_DATE,
    end_date: Optional[str] = None,
    rates: Optional[List[str]] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Get interest rate data from FRED.
    
    Args:
        start_date: Start date
        end_date: End date (default: latest)
        rates: List of rates to fetch (default: fed_funds, 10y, 2y, 3m)
        tool_context: ADK tool context
    
    Returns:
        Dictionary with interest rate data
    
    Example:
        >>> get_interest_rates(start_date="2020-01-01")
        {
            'start_date': '2020-01-01',
            'rates': {
                'fed_funds': {...},
                'treasury_10y': {...},
                'treasury_2y': {...}
            },
            'yield_curve': {
                '2s10s_spread': 0.45,  # 10Y - 2Y spread
                'inverted': False
            }
        }
    """
    fred = get_fred_wrapper()
    
    if rates is None:
        rates = ["fed_funds", "treasury_10y", "treasury_2y", "treasury_3m"]
    
    logger.info(f"Fetching interest rate data for: {rates}")
    
    results = {
        'start_date': start_date,
        'end_date': end_date or 'latest',
        'rates': {}
    }
    
    for rate in rates:
        if rate not in FRED_SERIES_MAP:
            logger.warning(f"Unknown rate: {rate}, skipping")
            continue
        
        series_id = FRED_SERIES_MAP[rate]['series_id']
        series_name = FRED_SERIES_MAP[rate]['name']
        
        try:
            data = fred.get_series_range(series_id, start_date, end_date)
            
            results['rates'][rate] = {
                'series_id': series_id,
                'name': series_name,
                'units': 'Percent',
                'dates': data['dates'],
                'values': data['values'],
                'statistics': {
                    'mean': data['mean'],
                    'min': data['min'],
                    'max': data['max'],
                    'latest': data['latest']
                }
            }
        except Exception as e:
            logger.error(f"Error fetching {rate}: {e}")
            results['rates'][rate] = {'error': str(e)}
    
    # Calculate yield curve metrics if we have the data
    if 'treasury_10y' in results['rates'] and 'treasury_2y' in results['rates']:
        latest_10y = results['rates']['treasury_10y']['statistics']['latest']['value']
        latest_2y = results['rates']['treasury_2y']['statistics']['latest']['value']
        spread_2s10s = latest_10y - latest_2y
        
        results['yield_curve'] = {
            '2s10s_spread': round(spread_2s10s, 2),
            'inverted': spread_2s10s < 0,
            'interpretation': 'Yield curve is inverted (recession signal)' if spread_2s10s < 0 
                            else 'Normal yield curve (positive slope)'
        }
    
    return results


def get_economic_snapshot(
    as_of_date: Optional[str] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Get a comprehensive snapshot of all major economic indicators.
    
    This is useful for understanding economic conditions at a specific point in time,
    which can be compared with Fed policy decisions or projections.
    
    Args:
        as_of_date: Date for snapshot (default: latest available)
        tool_context: ADK tool context
    
    Returns:
        Dictionary with snapshot of all major indicators
    
    Example:
        >>> get_economic_snapshot(as_of_date="2022-12-31")
        {
            'snapshot_date': '2022-12-31',
            'inflation': {
                'pce_core': {'value': float(4.7), 'date': '2022-12-31'},
                'cpi': {'value': float(6.5), 'date': '2022-12-31'}
            },
            'growth': {...},
            'employment': {...},
            'interest_rates': {...}
        }
    """
    fred = get_fred_wrapper()
    
    logger.info(f"Generating economic snapshot for {as_of_date or 'latest'}")
    
    snapshot = fred.get_economic_snapshot(as_of_date)
    
    # Organize by category
    categorized = {
        'snapshot_date': snapshot['date'],
        'inflation': {},
        'growth': {},
        'employment': {},
        'interest_rates': {},
        'other': {}
    }
    
    for indicator, data in snapshot['indicators'].items():
        if indicator in INDICATOR_CATEGORIES['inflation']:
            categorized['inflation'][indicator] = data
        elif indicator in INDICATOR_CATEGORIES['growth']:
            categorized['growth'][indicator] = data
        elif indicator in INDICATOR_CATEGORIES['employment']:
            categorized['employment'][indicator] = data
        elif indicator in INDICATOR_CATEGORIES['interest_rates']:
            categorized['interest_rates'][indicator] = data
        else:
            categorized['other'][indicator] = data
    
    return categorized


def compare_to_fed_projection(
    indicator: str,
    projection_value: float,
    projection_date: str,
    actual_date: str,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Compare Fed SEP projection with actual outcome from FRED data.
    
    This is a key function for analyzing Fed forecast accuracy.
    
    Args:
        indicator: Economic indicator ("inflation", "gdp_growth", "unemployment")
        projection_value: Fed's projected value
        projection_date: When Fed made the projection
        actual_date: Date to check actual outcome
        tool_context: ADK tool context
    
    Returns:
        Dictionary with comparison results
    
    Example:
        >>> compare_to_fed_projection(
        ...     indicator="inflation",
        ...     projection_value=2.0,
        ...     projection_date="2021-06-01",
        ...     actual_date="2021-12-31"
        ... )
        {
            'indicator': 'inflation',
            'fed_projection': 2.0,
            'actual_outcome': 5.8,
            'forecast_error': -3.8,
            'error_percentage': -190.0,
            'interpretation': 'Fed significantly underestimated inflation'
        }
    """
    fred = get_fred_wrapper()
    
    # Map indicator to FRED series
    indicator_map = {
        "inflation": "pce_core",
        "gdp_growth": "gdp_growth",
        "unemployment": "unemployment"
    }
    
    if indicator not in indicator_map:
        raise ValueError(f"Invalid indicator: {indicator}")
    
    series_key = indicator_map[indicator]
    series_id = FRED_SERIES_MAP[series_key]['series_id']
    
    logger.info(f"Comparing Fed projection for {indicator} with actual data")
    
    # Get actual value
    actual_data = fred.get_latest_value(series_id, as_of_date=actual_date)
    
    if not actual_data:
        return {
            'error': f'No actual data available for {indicator} on {actual_date}'
        }
    
    actual_value = actual_data['value']
    forecast_error = actual_value - projection_value
    error_percentage = (forecast_error / projection_value) * 100 if projection_value != 0 else None
    
    # Interpret the error
    if abs(forecast_error) < 0.5:
        interpretation = "Fed forecast was accurate"
    elif forecast_error > 0:
        interpretation = f"Fed underestimated {indicator} by {abs(forecast_error):.1f} points"
    else:
        interpretation = f"Fed overestimated {indicator} by {abs(forecast_error):.1f} points"
    
    return {
        'indicator': indicator,
        'projection_date': projection_date,
        'actual_date': actual_date,
        'fed_projection': projection_value,
        'actual_outcome': actual_value,
        'forecast_error': round(forecast_error, 2),
        'error_percentage': round(error_percentage, 1) if error_percentage else None,
        'interpretation': interpretation,
        'units': FRED_SERIES_MAP[series_key]['units']
    }


# Export all tool functions
__all__ = [
    'get_gdp_data',
    'get_inflation_data',
    'get_employment_data',
    'get_interest_rates',
    'get_economic_snapshot',
    'compare_to_fed_projection'
]
