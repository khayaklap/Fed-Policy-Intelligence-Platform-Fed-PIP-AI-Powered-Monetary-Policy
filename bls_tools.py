"""
BLS Agent Tools

Individual tool functions for detailed inflation and labor cost analysis.
Each function provides specific BLS data capability.
"""

import logging
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from google.adk.tools.tool_context import ToolContext

# Handle relative imports for package usage and absolute for direct execution
try:
    from .bls_api_wrapper import get_bls_wrapper
    from .bls_config import BLS_SERIES_MAP, CPI_COMPONENTS, DEFAULT_START_YEAR
except ImportError:
    from bls_api_wrapper import get_bls_wrapper
    from bls_config import BLS_SERIES_MAP, CPI_COMPONENTS, DEFAULT_START_YEAR

logger = logging.getLogger(__name__)


def get_cpi_components(
    start_year: int = 2020,
    end_year: Optional[int] = None,
    components: Optional[List[str]] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Get detailed CPI component breakdown to identify inflation drivers.
    
    This is crucial for understanding what's driving inflation:
    - Is it energy? (volatile, temporary)
    - Is it shelter? (sticky, persistent)
    - Is it services? (wage-driven)
    - Is it goods? (supply chain)
    
    Args:
        start_year: Start year for data
        end_year: End year (default: current year)
        components: List of component categories to fetch
                   (default: ["food", "energy", "housing", "services"])
        tool_context: ADK tool context
    
    Returns:
        Dictionary with component data and analysis
    
    Example:
        >>> get_cpi_components(start_year=2022, components=["food", "energy", "housing"])
        {
            'period': '2022-2024',
            'components': {
                'food': {
                    'latest': {'date': '2024-10', 'yoy': 2.1},
                    'peak': {'date': '2022-08', 'yoy': 11.4},
                    'series': [...]
                },
                'energy': {...},
                'housing': {...}
            },
            'summary': 'Energy drove peak inflation in mid-2022, now moderating. 
                       Shelter inflation remains elevated at 4.5% YoY.'
        }
    """
    bls = get_bls_wrapper()
    
    if end_year is None:
        end_year = datetime.now().year
    
    if components is None:
        components = ["food", "energy", "housing", "services"]
    
    logger.info(f"Fetching CPI components: {components} from {start_year}-{end_year}")
    
    results = {
        'period': f"{start_year}-{end_year}",
        'components': {}
    }
    
    for component_category in components:
        if component_category not in CPI_COMPONENTS:
            logger.warning(f"Unknown component category: {component_category}")
            continue
        
        # Get all series for this component
        series_keys = CPI_COMPONENTS[component_category]
        series_ids = [BLS_SERIES_MAP[key]['series_id'] for key in series_keys if key in BLS_SERIES_MAP]
        
        if not series_ids:
            continue
        
        # Fetch data
        component_data = bls.get_multiple_series(series_ids, start_year, end_year)
        
        # Process each sub-component
        component_results = {}
        
        for series_key in series_keys:
            if series_key not in BLS_SERIES_MAP:
                continue
            
            series_id = BLS_SERIES_MAP[series_key]['series_id']
            series_name = BLS_SERIES_MAP[series_key]['name']
            
            df = component_data.get(series_id)
            if df is None or df.empty:
                continue
            
            # Calculate YoY
            df_yoy = bls.calculate_yoy_change(df)
            df_yoy = df_yoy.dropna(subset=['yoy_change'])
            
            if df_yoy.empty:
                continue
            
            # Latest value
            latest = df_yoy.iloc[-1]
            
            # Peak inflation (max YoY)
            peak_idx = df_yoy['yoy_change'].idxmax()
            peak = df_yoy.loc[peak_idx]
            
            # Trough (min YoY)
            trough_idx = df_yoy['yoy_change'].idxmin()
            trough = df_yoy.loc[trough_idx]
            
            component_results[series_key] = {
                'series_id': series_id,
                'name': series_name,
                'latest': {
                    'date': latest['date'].strftime('%Y-%m'),
                    'value': float(latest['value']),
                    'yoy': round(float(latest['yoy_change']), 2)
                },
                'peak': {
                    'date': peak['date'].strftime('%Y-%m'),
                    'yoy': round(float(peak['yoy_change']), 2)
                },
                'trough': {
                    'date': trough['date'].strftime('%Y-%m'),
                    'yoy': round(float(trough['yoy_change']), 2)
                },
                'mean_yoy': round(float(df_yoy['yoy_change'].mean()), 2)
            }
        
        results['components'][component_category] = component_results
    
    # Generate summary
    summary_parts = []
    
    if 'energy' in results['components']:
        energy_data = results['components']['energy'].get('cpi_energy', {})
        if energy_data:
            latest_energy = energy_data['latest']['yoy']
            peak_energy = energy_data['peak']['yoy']
            summary_parts.append(
                f"Energy: peaked at {peak_energy}% YoY, now {latest_energy}%"
            )
    
    if 'housing' in results['components']:
        shelter_data = results['components']['housing'].get('cpi_shelter', {})
        if shelter_data:
            latest_shelter = shelter_data['latest']['yoy']
            summary_parts.append(
                f"Shelter (largest component): {latest_shelter}% YoY"
            )
    
    if 'services' in results['components']:
        services_data = results['components']['services'].get('cpi_core_services', {})
        if services_data:
            latest_services = services_data['latest']['yoy']
            summary_parts.append(
                f"Core services: {latest_services}% YoY (wage-driven)"
            )
    
    results['summary'] = ". ".join(summary_parts) if summary_parts else "No summary available"
    
    return results


def get_ppi_data(
    start_year: int = 2020,
    end_year: Optional[int] = None,
    stage: str = "final_demand",
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Get Producer Price Index (PPI) data - a leading indicator for CPI.
    
    PPI measures wholesale prices and often predicts CPI movements:
    - Rising PPI → CPI likely to follow (producers pass costs to consumers)
    - Falling PPI → CPI disinflationary pressures ahead
    
    Args:
        start_year: Start year
        end_year: End year (default: current)
        stage: Production stage ("final_demand", "intermediate", "crude")
        tool_context: ADK tool context
    
    Returns:
        Dictionary with PPI data and relationship to CPI
    
    Example:
        >>> get_ppi_data(start_year=2022, stage="final_demand")
        {
            'stage': 'final_demand',
            'latest': {'date': '2024-10', 'yoy': 1.8},
            'peak': {'date': '2022-06', 'yoy': 11.3},
            'interpretation': 'PPI peaked 6 months before CPI, now signaling 
                              continued disinflation'
        }
    """
    bls = get_bls_wrapper()
    
    if end_year is None:
        end_year = datetime.now().year
    
    # Map stage to series
    stage_map = {
        "final_demand": "ppi_final_demand",
        "final_goods": "ppi_final_goods",
        "intermediate": "ppi_intermediate",
        "crude": "ppi_crude"
    }
    
    if stage not in stage_map:
        raise ValueError(f"Invalid stage: {stage}. Choose from: {list(stage_map.keys())}")
    
    series_key = stage_map[stage]
    series_id = BLS_SERIES_MAP[series_key]['series_id']
    series_name = BLS_SERIES_MAP[series_key]['name']
    
    logger.info(f"Fetching PPI data: {stage} from {start_year}-{end_year}")
    
    # Fetch data
    df = bls.get_series(series_id, start_year, end_year)
    df_yoy = bls.calculate_yoy_change(df)
    df_yoy = df_yoy.dropna(subset=['yoy_change'])
    
    if df_yoy.empty:
        return {'error': f'No data available for {stage}'}
    
    # Latest
    latest = df_yoy.iloc[-1]
    
    # Peak
    peak_idx = df_yoy['yoy_change'].idxmax()
    peak = df_yoy.loc[peak_idx]
    
    # Recent trend (last 6 months)
    recent_df = df_yoy.tail(6)
    recent_trend = "rising" if recent_df['yoy_change'].iloc[-1] > recent_df['yoy_change'].iloc[0] else "falling"
    
    return {
        'stage': stage,
        'series_id': series_id,
        'name': series_name,
        'period': f"{start_year}-{end_year}",
        'latest': {
            'date': latest['date'].strftime('%Y-%m'),
            'value': float(latest['value']),
            'yoy': round(float(latest['yoy_change']), 2)
        },
        'peak': {
            'date': peak['date'].strftime('%Y-%m'),
            'yoy': round(float(peak['yoy_change']), 2)
        },
        'mean_yoy': round(float(df_yoy['yoy_change'].mean()), 2),
        'recent_trend': recent_trend,
        'interpretation': f"PPI {stage} is currently {latest['yoy_change']:.1f}% YoY and {recent_trend}. "
                         f"Peaked at {peak['yoy_change']:.1f}% in {peak['date'].strftime('%Y-%m')}. "
                         f"This suggests {'continued inflationary pressure' if recent_trend == 'rising' else 'disinflationary pressures ahead'} for CPI."
    }


def get_employment_cost_index(
    start_year: int = 2020,
    end_year: Optional[int] = None,
    component: str = "total_comp",
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Get Employment Cost Index (ECI) - comprehensive measure of labor costs.
    
    ECI is the Fed's preferred measure of wage pressures:
    - Rising ECI → wage-price spiral risk
    - Moderating ECI → inflation pressure easing
    - Quarterly data, less volatile than average hourly earnings
    
    Args:
        start_year: Start year
        end_year: End year (default: current)
        component: "total_comp", "wages_salaries", or "benefits"
        tool_context: ADK tool context
    
    Returns:
        Dictionary with ECI data and wage pressure analysis
    
    Example:
        >>> get_employment_cost_index(start_year=2021, component="wages_salaries")
        {
            'component': 'wages_salaries',
            'latest': {'date': '2024-Q3', 'yoy': 3.9},
            'peak': {'date': '2022-Q4', 'yoy': 5.1},
            'wage_pressure': 'moderating',
            'interpretation': 'Wage growth cooling from peak, reducing 
                              wage-price spiral risk'
        }
    """
    bls = get_bls_wrapper()
    
    if end_year is None:
        end_year = datetime.now().year
    
    # Map component to series
    component_map = {
        "total_comp": "eci_total_comp",
        "wages_salaries": "eci_wages_salaries",
        "benefits": "eci_benefits"
    }
    
    if component not in component_map:
        raise ValueError(f"Invalid component: {component}. Choose from: {list(component_map.keys())}")
    
    series_key = component_map[component]
    series_id = BLS_SERIES_MAP[series_key]['series_id']
    series_name = BLS_SERIES_MAP[series_key]['name']
    
    logger.info(f"Fetching ECI data: {component} from {start_year}-{end_year}")
    
    # Fetch data
    df = bls.get_series(series_id, start_year, end_year)
    
    # ECI is quarterly, so YoY is 4 periods
    df['yoy_change'] = df['value'].pct_change(periods=4) * 100
    df_yoy = df.dropna(subset=['yoy_change'])
    
    if df_yoy.empty:
        return {'error': f'No data available for {component}'}
    
    # Latest
    latest = df_yoy.iloc[-1]
    
    # Peak
    peak_idx = df_yoy['yoy_change'].idxmax()
    peak = df_yoy.loc[peak_idx]
    
    # Assess wage pressure
    latest_yoy = latest['yoy_change']
    if latest_yoy > 4.5:
        wage_pressure = "high"
    elif latest_yoy > 3.5:
        wage_pressure = "elevated"
    elif latest_yoy > 2.5:
        wage_pressure = "moderate"
    else:
        wage_pressure = "low"
    
    # Trend
    if len(df_yoy) >= 4:
        recent_avg = df_yoy.tail(4)['yoy_change'].mean()
        prior_avg = df_yoy.iloc[-8:-4]['yoy_change'].mean() if len(df_yoy) >= 8 else None
        
        if prior_avg:
            trend = "accelerating" if recent_avg > prior_avg else "moderating"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    return {
        'component': component,
        'series_id': series_id,
        'name': series_name,
        'frequency': 'Quarterly',
        'period': f"{start_year}-{end_year}",
        'latest': {
            'date': f"{latest['year']}-Q{latest['period'].replace('Q0', '')}",
            'value': float(latest['value']),
            'yoy': round(float(latest['yoy_change']), 2)
        },
        'peak': {
            'date': f"{peak['year']}-Q{peak['period'].replace('Q0', '')}",
            'yoy': round(float(peak['yoy_change']), 2)
        },
        'wage_pressure': wage_pressure,
        'trend': trend,
        'interpretation': f"ECI {component} at {latest_yoy:.1f}% YoY indicates {wage_pressure} wage pressure. "
                         f"Trend is {trend} from peak of {peak['yoy_change']:.1f}% in {peak['year']}-Q{peak['period'].replace('Q0', '')}. "
                         f"{'Wage-price spiral risk elevated' if wage_pressure in ['high', 'elevated'] else 'Wage pressures moderating'}."
    }


def compare_inflation_measures(
    start_year: int = 2020,
    end_year: Optional[int] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Compare different inflation measures side-by-side.
    
    Compares:
    - CPI (All Items) - headline inflation
    - CPI Core - excludes food/energy
    - PPI - producer prices (leading indicator)
    - Import Prices - global price pressures
    
    Args:
        start_year: Start year
        end_year: End year (default: current)
        tool_context: ADK tool context
    
    Returns:
        Dictionary comparing all measures
    
    Example:
        >>> compare_inflation_measures(start_year=2021)
        {
            'period': '2021-2024',
            'comparison': {
                'cpi_all': {'latest_yoy': 3.2, 'peak': 9.1},
                'cpi_core': {'latest_yoy': 4.0, 'peak': 6.6},
                'ppi': {'latest_yoy': 1.8, 'peak': 11.3}
            },
            'insights': [
                'Core CPI remains above headline (services-driven)',
                'PPI peaked first, signaling disinflation pipeline'
            ]
        }
    """
    bls = get_bls_wrapper()
    
    if end_year is None:
        end_year = datetime.now().year
    
    logger.info(f"Comparing inflation measures from {start_year}-{end_year}")
    
    # Series to compare
    series_to_compare = {
        'cpi_all': 'cpi_all',
        'cpi_core': 'cpi_core',
        'ppi': 'ppi_final_demand',
        'import_prices': 'import_prices'
    }
    
    series_ids = [BLS_SERIES_MAP[key]['series_id'] for key in series_to_compare.values() if key in BLS_SERIES_MAP]
    
    # Fetch all series
    all_data = bls.get_multiple_series(series_ids, start_year, end_year)
    
    comparison = {}
    
    for display_name, series_key in series_to_compare.items():
        if series_key not in BLS_SERIES_MAP:
            continue
        
        series_id = BLS_SERIES_MAP[series_key]['series_id']
        series_name = BLS_SERIES_MAP[series_key]['name']
        
        df = all_data.get(series_id)
        if df is None or df.empty:
            continue
        
        # Calculate YoY (quarterly for ECI/productivity, monthly otherwise)
        if 'Q' in df.iloc[0]['period']:
            df['yoy_change'] = df['value'].pct_change(periods=4) * 100
        else:
            df['yoy_change'] = df['value'].pct_change(periods=12) * 100
        
        df_yoy = df.dropna(subset=['yoy_change'])
        
        if df_yoy.empty:
            continue
        
        latest = df_yoy.iloc[-1]
        peak_idx = df_yoy['yoy_change'].idxmax()
        peak = df_yoy.loc[peak_idx]
        
        comparison[display_name] = {
            'name': series_name,
            'latest_yoy': round(float(latest['yoy_change']), 2),
            'peak_yoy': round(float(peak['yoy_change']), 2),
            'peak_date': peak['date'].strftime('%Y-%m') if 'date' in peak and pd.notna(peak['date']) else f"{peak['year']}-{peak['period']}"
        }
    
    # Generate insights
    insights = []
    
    if 'cpi_all' in comparison and 'cpi_core' in comparison:
        if comparison['cpi_core']['latest_yoy'] > comparison['cpi_all']['latest_yoy']:
            insights.append("Core CPI exceeds headline - services/shelter driving inflation")
        else:
            insights.append("Headline CPI exceeds core - energy/food volatility")
    
    if 'ppi' in comparison and 'cpi_all' in comparison:
        ppi_peak_date = comparison['ppi']['peak_date']
        cpi_peak_date = comparison['cpi_all']['peak_date']
        if ppi_peak_date < cpi_peak_date:
            insights.append("PPI peaked before CPI - producer costs led consumer prices")
    
    return {
        'period': f"{start_year}-{end_year}",
        'comparison': comparison,
        'insights': insights
    }


def analyze_inflation_drivers(
    as_of_date: Optional[str] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Comprehensive analysis of what's driving inflation at a point in time.
    
    This is the "killer app" tool - answers the key question:
    "What's driving inflation right now?"
    
    Analyzes:
    - CPI component breakdown (largest contributors)
    - Goods vs Services split
    - Leading indicators (PPI, import prices)
    - Wage pressures (ECI)
    
    Args:
        as_of_date: Date for analysis (default: latest available)
        tool_context: ADK tool context
    
    Returns:
        Comprehensive inflation driver analysis
    
    Example:
        >>> analyze_inflation_drivers(as_of_date="2022-12-01")
        {
            'analysis_date': '2022-12-01',
            'headline_inflation': 7.1,
            'core_inflation': 6.0,
            'primary_drivers': [
                {'component': 'shelter', 'contribution': 2.8, 'percentage': 40},
                {'component': 'energy', 'contribution': 1.6, 'percentage': 23}
            ],
            'assessment': 'Broad-based inflation with shelter now primary driver',
            'outlook': 'Energy moderating, but shelter sticky'
        }
    """
    bls = get_bls_wrapper()
    
    # Determine analysis period
    if as_of_date:
        import pandas as pd
        target_date = pd.to_datetime(as_of_date)
        end_year = target_date.year
        start_year = end_year - 2
    else:
        end_year = datetime.now().year
        start_year = end_year - 2
    
    logger.info(f"Analyzing inflation drivers as of {as_of_date or 'latest'}")
    
    # Get key components
    components = ["food", "energy", "housing", "transportation", "services"]
    component_data = get_cpi_components(start_year, end_year, components)
    
    # Get overall CPI
    cpi_all_id = BLS_SERIES_MAP['cpi_all']['series_id']
    cpi_core_id = BLS_SERIES_MAP['cpi_core']['series_id']
    
    overall_data = bls.get_multiple_series([cpi_all_id, cpi_core_id], start_year, end_year)
    
    cpi_all_df = bls.calculate_yoy_change(overall_data[cpi_all_id])
    cpi_core_df = bls.calculate_yoy_change(overall_data[cpi_core_id])
    
    # Latest values
    headline_inflation = round(float(cpi_all_df.iloc[-1]['yoy_change']), 1)
    core_inflation = round(float(cpi_core_df.iloc[-1]['yoy_change']), 1)
    
    # Identify primary drivers (simplified - actual would use contribution methodology)
    drivers = []
    
    for category, cat_data in component_data['components'].items():
        for series_key, series_data in cat_data.items():
            if 'latest' in series_data:
                yoy = series_data['latest']['yoy']
                if abs(yoy) > 2.0:  # Significant inflation
                    drivers.append({
                        'component': series_data['name'],
                        'yoy': yoy,
                        'category': category
                    })
    
    # Sort by magnitude
    drivers.sort(key=lambda x: abs(x['yoy']), reverse=True)
    top_drivers = drivers[:5]
    
    # Assessment
    if headline_inflation > 5:
        assessment = "High inflation"
    elif headline_inflation > 3:
        assessment = "Elevated inflation above Fed target"
    elif headline_inflation > 2:
        assessment = "Moderate inflation near Fed target"
    else:
        assessment = "Low inflation"
    
    return {
        'analysis_date': as_of_date or 'latest',
        'headline_inflation': headline_inflation,
        'core_inflation': core_inflation,
        'spread': round(headline_inflation - core_inflation, 1),
        'primary_drivers': top_drivers,
        'assessment': assessment,
        'component_summary': component_data['summary']
    }


# Export all tool functions
__all__ = [
    'get_cpi_components',
    'get_ppi_data',
    'get_employment_cost_index',
    'compare_inflation_measures',
    'analyze_inflation_drivers'
]
