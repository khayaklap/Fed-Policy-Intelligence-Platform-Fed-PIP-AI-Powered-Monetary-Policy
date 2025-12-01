"""
Treasury API Wrapper

Handles fetching Treasury yield, TIPS, and breakeven data via FRED API.
Includes yield curve construction, spread calculation, and policy analysis.
"""

import logging
import pandas as pd
import numpy as np
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from fredapi import Fred
from cachetools import TTLCache

# Handle relative imports for package usage and absolute for direct execution
try:
    from .treasury_config import (
        FRED_API_KEY,
        TREASURY_YIELDS,
        TIPS_YIELDS,
        BREAKEVEN_SERIES,
        POLICY_RATES,
        YIELD_SPREADS,
        YIELD_CURVE_MATURITIES,
        NEUTRAL_REAL_RATE,
        POLICY_STANCE_THRESHOLDS,
        INFLATION_EXPECTATION_THRESHOLDS,
        CACHE_TTL_SECONDS,
        MAX_CACHE_SIZE,
        DEFAULT_START_DATE
    )
except ImportError:
    from treasury_config import (
        FRED_API_KEY,
        TREASURY_YIELDS,
        TIPS_YIELDS,
        BREAKEVEN_SERIES,
        POLICY_RATES,
        YIELD_SPREADS,
        YIELD_CURVE_MATURITIES,
        NEUTRAL_REAL_RATE,
        POLICY_STANCE_THRESHOLDS,
        INFLATION_EXPECTATION_THRESHOLDS,
        CACHE_TTL_SECONDS,
        MAX_CACHE_SIZE,
        DEFAULT_START_DATE
    )

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TreasuryAPIWrapper:
    """
    Wrapper for Treasury data via FRED API.
    Provides yield curves, TIPS, breakevens, and policy analysis.
    """
    
    def __init__(self, api_key: str = FRED_API_KEY):
        """
        Initialize Treasury API wrapper.
        
        Args:
            api_key: FRED API key
        """
        if not api_key:
            import warnings
            warnings.warn(
                "No FRED API key provided. Rate limits will apply. "
                "Get your free API key at: https://fred.stlouisfed.org/docs/api/api_key.html"
            )
        
        self.fred = Fred(api_key=api_key) if api_key else Fred()
        self.api_key = api_key
        self.cache = TTLCache(maxsize=MAX_CACHE_SIZE, ttl=CACHE_TTL_SECONDS)
        logger.info("Treasury API wrapper initialized")
    
    async def _fetch_fred_series_async(
        self,
        session: aiohttp.ClientSession,
        series_id: str,
        start_date: str,
        end_date: str
    ) -> Optional[pd.Series]:
        """
        Async fetch of FRED series data.
        
        Args:
            session: aiohttp session
            series_id: FRED series ID
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            Pandas Series with time series data
        """
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'observation_start': start_date,
            'observation_end': end_date,
            'sort_order': 'desc',
            'limit': 100
        }
        
        try:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch {series_id}: HTTP {response.status}")
                    return None
                    
                data = await response.json()
                observations = data.get('observations', [])
                
                if not observations:
                    return pd.Series(dtype=float)
                
                # Convert to pandas Series
                dates = []
                values = []
                for obs in observations:
                    if obs['value'] != '.':  # FRED uses '.' for missing values
                        try:
                            dates.append(pd.to_datetime(obs['date']))
                            values.append(float(obs['value']))
                        except (ValueError, TypeError):
                            continue
                
                if not dates:
                    return pd.Series(dtype=float)
                
                series = pd.Series(values, index=dates)
                series.sort_index(inplace=True)
                return series
                
        except Exception as e:
            logger.error(f"Error fetching series {series_id}: {e}")
            return None
    
    async def get_yield_curve_async(
        self,
        date: Optional[str] = None,
        maturities: Optional[List[str]] = None
    ) -> Dict:
        """
        Async version: Get complete Treasury yield curve for a specific date.
        Fetches all series in parallel for better performance.
        
        Args:
            date: Date in 'YYYY-MM-DD' format (default: latest)
            maturities: List of maturities to include (default: all)
        
        Returns:
            Dictionary with yield curve data
        """
        if maturities is None:
            maturities = YIELD_CURVE_MATURITIES
        
        cache_key = f"yield_curve_{date}_{','.join(maturities)}"
        if cache_key in self.cache:
            logger.debug(f"Cache hit for yield curve {date}")
            return self.cache[cache_key]
        
        logger.info(f"Fetching yield curve for {date or 'latest'} (async)")
        
        # Prepare date range
        if date:
            target_date = pd.to_datetime(date)
            start_date = (target_date - timedelta(days=7)).strftime('%Y-%m-%d')
            end_date = (target_date + timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Prepare tasks for parallel execution
        tasks = []
        maturity_info = []
        
        async with aiohttp.ClientSession() as session:
            for maturity in maturities:
                if maturity not in TREASURY_YIELDS:
                    logger.warning(f"Unknown maturity: {maturity}")
                    continue
                
                series_id = TREASURY_YIELDS[maturity]['series_id']
                series_name = TREASURY_YIELDS[maturity]['name']
                years = TREASURY_YIELDS[maturity]['maturity_years']
                
                task = self._fetch_fred_series_async(session, series_id, start_date, end_date)
                tasks.append(task)
                maturity_info.append((maturity, series_name, years))
            
            # Execute all requests in parallel
            series_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        yields = {}
        maturity_years = []
        
        for i, (series_result, (maturity, series_name, years)) in enumerate(zip(series_results, maturity_info)):
            if isinstance(series_result, Exception):
                logger.error(f"Error fetching {maturity}: {series_result}")
                continue
            
            if series_result is None or series_result.empty:
                continue
            
            try:
                # Get value closest to target date
                if date:
                    target_date = pd.to_datetime(date)
                    series_on_or_before = series_result[series_result.index <= target_date]
                    if not series_on_or_before.empty:
                        value = series_on_or_before.iloc[-1]
                        actual_date = series_on_or_before.index[-1]
                    else:
                        continue
                else:
                    value = series_result.iloc[-1]
                    actual_date = series_result.index[-1]
                
                yields[maturity] = {
                    'name': series_name,
                    'yield': float(value),
                    'maturity_years': years,
                    'date': actual_date.strftime('%Y-%m-%d')
                }
                maturity_years.append(years)
                
            except Exception as e:
                logger.error(f"Error processing {maturity}: {e}")
        
        if not yields:
            return {'error': 'No yield data available'}
        
        # Calculate curve characteristics
        result = {
            'date': date or datetime.now().strftime('%Y-%m-%d'),
            'yields': yields,
            'curve_characteristics': self._analyze_curve_shape(yields)
        }
        
        self.cache[cache_key] = result
        return result
    
    def get_yield_curve(
        self,
        date: Optional[str] = None,
        maturities: Optional[List[str]] = None
    ) -> Dict:
        """
        Get complete Treasury yield curve for a specific date.
        
        Args:
            date: Date in 'YYYY-MM-DD' format (default: latest)
            maturities: List of maturities to include (default: all)
        
        Returns:
            Dictionary with yield curve data
        """
        if maturities is None:
            maturities = YIELD_CURVE_MATURITIES
        
        cache_key = f"yield_curve_{date}_{','.join(maturities)}"
        if cache_key in self.cache:
            logger.debug(f"Cache hit for yield curve {date}")
            return self.cache[cache_key]
        
        logger.info(f"Fetching yield curve for {date or 'latest'}")
        
        yields = {}
        maturity_years = []
        
        for maturity in maturities:
            if maturity not in TREASURY_YIELDS:
                logger.warning(f"Unknown maturity: {maturity}")
                continue
            
            series_id = TREASURY_YIELDS[maturity]['series_id']
            series_name = TREASURY_YIELDS[maturity]['name']
            years = TREASURY_YIELDS[maturity]['maturity_years']
            
            try:
                # Get data around the specified date
                if date:
                    target_date = pd.to_datetime(date)
                    start_date = (target_date - timedelta(days=7)).strftime('%Y-%m-%d')
                    end_date = (target_date + timedelta(days=1)).strftime('%Y-%m-%d')
                else:
                    # Get recent data
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                
                series = self.fred.get_series(series_id, start_date, end_date)
                
                if series.empty:
                    continue
                
                # Get value closest to target date
                if date:
                    # Find closest date on or before target
                    series_on_or_before = series[series.index <= target_date]
                    if not series_on_or_before.empty:
                        value = series_on_or_before.iloc[-1]
                        actual_date = series_on_or_before.index[-1]
                    else:
                        continue
                else:
                    value = series.iloc[-1]
                    actual_date = series.index[-1]
                
                yields[maturity] = {
                    'name': series_name,
                    'yield': float(value),
                    'maturity_years': years,
                    'date': actual_date.strftime('%Y-%m-%d')
                }
                maturity_years.append(years)
                
            except Exception as e:
                logger.error(f"Error fetching {maturity}: {e}")
        
        if not yields:
            return {'error': 'No yield data available'}
        
        # Calculate curve characteristics
        result = {
            'date': date or datetime.now().strftime('%Y-%m-%d'),
            'yields': yields,
            'curve_characteristics': self._analyze_curve_shape(yields)
        }
        
        self.cache[cache_key] = result
        return result
    
    def _analyze_curve_shape(self, yields: Dict) -> Dict:
        """Analyze yield curve shape and characteristics."""
        characteristics = {}
        
        # Calculate key spreads
        if '2y' in yields and '10y' in yields:
            spread_2s10s = yields['10y']['yield'] - yields['2y']['yield']
            characteristics['2s10s_spread'] = round(spread_2s10s, 2)
            characteristics['2s10s_inverted'] = spread_2s10s < 0
        
        if '3m' in yields and '10y' in yields:
            spread_3m10y = yields['10y']['yield'] - yields['3m']['yield']
            characteristics['3m10y_spread'] = round(spread_3m10y, 2)
            characteristics['3m10y_inverted'] = spread_3m10y < 0
        
        if '5y' in yields and '30y' in yields:
            spread_5s30s = yields['30y']['yield'] - yields['5y']['yield']
            characteristics['5s30s_spread'] = round(spread_5s30s, 2)
        
        # Overall curve assessment
        if characteristics.get('2s10s_inverted') or characteristics.get('3m10y_inverted'):
            characteristics['curve_status'] = 'inverted'
            characteristics['recession_signal'] = True
        elif characteristics.get('2s10s_spread', 0) < 0.25:
            characteristics['curve_status'] = 'flat'
            characteristics['recession_signal'] = False
        else:
            characteristics['curve_status'] = 'normal'
            characteristics['recession_signal'] = False
        
        return characteristics
    
    def get_tips_breakeven(
        self,
        maturity: str = "10y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        Get TIPS breakeven inflation rate (market-implied inflation expectation).
        
        Breakeven = Nominal yield - TIPS yield
        
        Args:
            maturity: Maturity ("5y", "10y", "20y", "30y")
            start_date: Start date (default: 2 years ago)
            end_date: End date (default: today)
        
        Returns:
            Dictionary with breakeven data and interpretation
        """
        tips_key = f"{maturity}_tips"
        
        if tips_key not in TIPS_YIELDS:
            raise ValueError(f"TIPS data not available for {maturity}")
        
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Calculating {maturity} TIPS breakeven from {start_date} to {end_date}")
        
        # Get nominal Treasury yield
        nominal_series_id = TREASURY_YIELDS[maturity]['series_id']
        nominal_data = self.fred.get_series(nominal_series_id, start_date, end_date)
        
        # Get TIPS yield
        tips_series_id = TIPS_YIELDS[tips_key]['series_id']
        tips_data = self.fred.get_series(tips_series_id, start_date, end_date)
        
        # Align dates
        combined = pd.DataFrame({
            'nominal': nominal_data,
            'tips': tips_data
        }).dropna()
        
        if combined.empty:
            return {'error': f'No TIPS data available for {maturity}'}
        
        # Calculate breakeven
        combined['breakeven'] = combined['nominal'] - combined['tips']
        
        # Latest values
        latest = combined.iloc[-1]
        latest_date = combined.index[-1]
        
        # Statistics
        mean_breakeven = combined['breakeven'].mean()
        max_breakeven = combined['breakeven'].max()
        min_breakeven = combined['breakeven'].min()
        
        # Interpret inflation expectations
        latest_breakeven = latest['breakeven']
        if INFLATION_EXPECTATION_THRESHOLDS['well_anchored'][0] <= latest_breakeven <= INFLATION_EXPECTATION_THRESHOLDS['well_anchored'][1]:
            expectation_status = "well_anchored"
            interpretation = f"Inflation expectations well-anchored around Fed's 2% target"
        elif latest_breakeven < INFLATION_EXPECTATION_THRESHOLDS['well_anchored'][0]:
            expectation_status = "below_target"
            interpretation = f"Inflation expectations below Fed's target - deflation concerns"
        elif latest_breakeven >= INFLATION_EXPECTATION_THRESHOLDS['unanchored']:
            expectation_status = "unanchored"
            interpretation = f"Inflation expectations unanchored - credibility risk"
        elif latest_breakeven >= INFLATION_EXPECTATION_THRESHOLDS['de_anchoring']:
            expectation_status = "de_anchoring"
            interpretation = f"Inflation expectations elevated - de-anchoring risk"
        else:
            expectation_status = "moderately_anchored"
            interpretation = f"Inflation expectations somewhat elevated but contained"
        
        return {
            'maturity': maturity,
            'period': f"{start_date} to {end_date}",
            'latest': {
                'date': latest_date.strftime('%Y-%m-%d'),
                'nominal_yield': round(float(latest['nominal']), 2),
                'tips_yield': round(float(latest['tips']), 2),
                'breakeven': round(float(latest['breakeven']), 2)
            },
            'statistics': {
                'mean': round(float(mean_breakeven), 2),
                'max': round(float(max_breakeven), 2),
                'min': round(float(min_breakeven), 2)
            },
            'expectation_status': expectation_status,
            'interpretation': interpretation,
            'time_series': {
                'dates': combined.index.strftime('%Y-%m-%d').tolist(),
                'breakeven': combined['breakeven'].round(2).tolist()
            }
        }
    
    def calculate_real_yields(
        self,
        date: Optional[str] = None,
        maturities: Optional[List[str]] = None
    ) -> Dict:
        """
        Calculate real yields (nominal - breakeven inflation).
        
        Real yield = inflation-adjusted return
        Key for assessing monetary policy stance
        
        Args:
            date: Date for calculation (default: latest)
            maturities: Maturities to include (default: TIPS maturities)
        
        Returns:
            Dictionary with real yields and policy stance assessment
        """
        if maturities is None:
            maturities = ["5y", "7y", "10y", "20y", "30y"]
        
        logger.info(f"Calculating real yields for {date or 'latest'}")
        
        real_yields = {}
        
        for maturity in maturities:
            tips_key = f"{maturity}_tips"
            if tips_key not in TIPS_YIELDS:
                continue
            
            try:
                # Get TIPS yield directly (this IS the real yield)
                tips_series_id = TIPS_YIELDS[tips_key]['series_id']
                
                if date:
                    target_date = pd.to_datetime(date)
                    start_date = (target_date - timedelta(days=7)).strftime('%Y-%m-%d')
                    end_date = (target_date + timedelta(days=1)).strftime('%Y-%m-%d')
                else:
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                
                series = self.fred.get_series(tips_series_id, start_date, end_date)
                
                if series.empty:
                    continue
                
                if date:
                    series_on_or_before = series[series.index <= target_date]
                    if not series_on_or_before.empty:
                        real_yield = series_on_or_before.iloc[-1]
                    else:
                        continue
                else:
                    real_yield = series.iloc[-1]
                
                real_yields[maturity] = {
                    'real_yield': round(float(real_yield), 2),
                    'maturity_years': TIPS_YIELDS[tips_key]['maturity_years']
                }
                
            except Exception as e:
                logger.error(f"Error calculating real yield for {maturity}: {e}")
        
        if not real_yields:
            return {'error': 'No real yield data available'}
        
        # Assess policy stance based on 10Y real yield
        policy_stance = "unknown"
        policy_interpretation = ""
        
        if '10y' in real_yields:
            real_10y = real_yields['10y']['real_yield']
            
            if real_10y < POLICY_STANCE_THRESHOLDS['highly_accommodative']:
                policy_stance = "highly_accommodative"
                policy_interpretation = "Deeply negative real rates - strongly stimulative"
            elif real_10y < POLICY_STANCE_THRESHOLDS['accommodative']:
                policy_stance = "accommodative"
                policy_interpretation = "Negative real rates - accommodative monetary policy"
            elif real_10y < POLICY_STANCE_THRESHOLDS['restrictive']:
                policy_stance = "neutral"
                policy_interpretation = f"Real rates near neutral (R-star ~{NEUTRAL_REAL_RATE}%)"
            elif real_10y < POLICY_STANCE_THRESHOLDS['highly_restrictive']:
                policy_stance = "restrictive"
                policy_interpretation = "Elevated real rates - restrictive monetary policy"
            else:
                policy_stance = "highly_restrictive"
                policy_interpretation = "Very high real rates - highly restrictive policy"
        
        return {
            'date': date or datetime.now().strftime('%Y-%m-%d'),
            'real_yields': real_yields,
            'policy_stance': policy_stance,
            'policy_interpretation': policy_interpretation,
            'neutral_rate_reference': NEUTRAL_REAL_RATE
        }
    
    def get_yield_spread_history(
        self,
        spread_type: str = "2s10s",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        Get historical yield spread data.
        
        Args:
            spread_type: "2s10s" or "3m10y" or "5s30s"
            start_date: Start date
            end_date: End date
        
        Returns:
            Dictionary with spread history and inversion analysis
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Fetching {spread_type} spread from {start_date} to {end_date}")
        
        # Try to get pre-calculated spread from FRED
        if spread_type == "2s10s" and "10y_2y" in YIELD_SPREADS:
            series_id = YIELD_SPREADS["10y_2y"]["series_id"]
            spread_data = self.fred.get_series(series_id, start_date, end_date)
        elif spread_type == "3m10y" and "10y_3m" in YIELD_SPREADS:
            series_id = YIELD_SPREADS["10y_3m"]["series_id"]
            spread_data = self.fred.get_series(series_id, start_date, end_date)
        else:
            # Calculate manually
            return self._calculate_spread_manually(spread_type, start_date, end_date)
        
        if spread_data.empty:
            return {'error': f'No spread data available for {spread_type}'}
        
        # Analyze inversions
        inverted_periods = spread_data[spread_data < 0]
        inversion_count = len(inverted_periods)
        currently_inverted = spread_data.iloc[-1] < 0
        
        # Latest values
        latest_spread = spread_data.iloc[-1]
        latest_date = spread_data.index[-1]
        
        return {
            'spread_type': spread_type,
            'period': f"{start_date} to {end_date}",
            'latest': {
                'date': latest_date.strftime('%Y-%m-%d'),
                'spread': round(float(latest_spread), 2)
            },
            'statistics': {
                'mean': round(float(spread_data.mean()), 2),
                'max': round(float(spread_data.max()), 2),
                'min': round(float(spread_data.min()), 2),
                'current': round(float(latest_spread), 2)
            },
            'inversion_analysis': {
                'currently_inverted': currently_inverted,
                'inversion_days': inversion_count,
                'inversion_percentage': round((inversion_count / len(spread_data)) * 100, 1)
            },
            'recession_signal': currently_inverted,
            'time_series': {
                'dates': spread_data.index.strftime('%Y-%m-%d').tolist(),
                'spread': spread_data.round(2).tolist()
            }
        }
    
    def _calculate_spread_manually(
        self,
        spread_type: str,
        start_date: str,
        end_date: str
    ) -> Dict:
        """Calculate spread manually if not pre-calculated in FRED."""
        # Parse spread type (e.g., "2s10s" -> short="2y", long="10y")
        # Simplified - would need more robust parsing
        return {'error': f'Manual calculation not implemented for {spread_type}'}


# Sync wrapper functions for backward compatibility
def get_yield_curve_sync(
    wrapper: TreasuryAPIWrapper,
    date: Optional[str] = None,
    maturities: Optional[List[str]] = None,
    use_async: bool = True
) -> Dict:
    """
    Sync wrapper for yield curve fetching with optional async acceleration.
    
    Args:
        wrapper: TreasuryAPIWrapper instance
        date: Date in 'YYYY-MM-DD' format (default: latest)
        maturities: List of maturities to include (default: all)
        use_async: If True, uses async parallel fetching for better performance
    
    Returns:
        Dictionary with yield curve data
    """
    if use_async:
        # Use async version for parallel fetching (6x faster for full yield curve)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, we need to run in a new thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        lambda: asyncio.run(wrapper.get_yield_curve_async(date, maturities))
                    )
                    return future.result()
            else:
                return loop.run_until_complete(wrapper.get_yield_curve_async(date, maturities))
        except Exception as e:
            logger.warning(f"Async fetch failed, falling back to sync: {e}")
            return wrapper.get_yield_curve(date, maturities)
    else:
        # Use original sync version
        return wrapper.get_yield_curve(date, maturities)


# Singleton instance
_treasury_wrapper = None

def get_treasury_wrapper() -> TreasuryAPIWrapper:
    """Get or create singleton Treasury API wrapper instance."""
    global _treasury_wrapper
    if _treasury_wrapper is None:
        _treasury_wrapper = TreasuryAPIWrapper()
    return _treasury_wrapper
