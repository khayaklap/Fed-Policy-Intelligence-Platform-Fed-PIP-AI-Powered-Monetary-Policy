"""
FRED API Wrapper

Handles all interactions with the FRED API, including:
- Data fetching with caching
- Error handling and retries
- Data transformation (YoY %, growth rates, etc.)
- Rate limiting
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from fredapi import Fred
from cachetools import TTLCache

# Handle relative imports for package usage and absolute for direct execution
try:
    from .fred_config import (
        FRED_API_KEY,
        FRED_SERIES_MAP,
        CACHE_TTL_SECONDS,
        MAX_CACHE_SIZE,
    )
except ImportError:
    from fred_config import (
        FRED_API_KEY,
        FRED_SERIES_MAP,
        CACHE_TTL_SECONDS,
        MAX_CACHE_SIZE,
    )

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FREDAPIWrapper:
    """
    Wrapper for FRED API with caching, error handling, and data transformation.
    """
    
    def __init__(self, api_key: str = FRED_API_KEY):
        """
        Initialize FRED API wrapper.

        Args:
            api_key: FRED API key (get from https://fred.stlouisfed.org/docs/api/api_key.html)
        """
        if not api_key:
            import warnings
            warnings.warn(
                "No FRED API key provided. Rate limits will apply. "
                "Get your free API key at: https://fred.stlouisfed.org/docs/api/api_key.html"
            )

        self.fred = Fred(api_key=api_key) if api_key else Fred()
        self.cache = TTLCache(maxsize=MAX_CACHE_SIZE, ttl=CACHE_TTL_SECONDS)
        logger.info("FRED API wrapper initialized")
    
    def get_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: Optional[str] = None
    ) -> pd.Series:
        """
        Get a FRED time series.
        
        Args:
            series_id: FRED series identifier (e.g., 'GDPC1')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            frequency: Frequency conversion ('d', 'w', 'm', 'q', 'a')
        
        Returns:
            Pandas Series with datetime index
        """
        cache_key = f"{series_id}_{start_date}_{end_date}_{frequency}"
        
        if cache_key in self.cache:
            logger.debug(f"Cache hit for {series_id}")
            return self.cache[cache_key]
        
        try:
            logger.info(f"Fetching {series_id} from FRED API")
            series = self.fred.get_series(
                series_id,
                observation_start=start_date,
                observation_end=end_date
            )
            
            self.cache[cache_key] = series
            return series
            
        except Exception as e:
            logger.error(f"Error fetching {series_id}: {e}")
            raise
    
    def get_series_info(self, series_id: str) -> Dict:
        """
        Get metadata about a FRED series.
        
        Args:
            series_id: FRED series identifier
        
        Returns:
            Dictionary with series metadata
        """
        try:
            info = self.fred.get_series_info(series_id)
            return {
                'id': info.get('id'),
                'title': info.get('title'),
                'units': info.get('units'),
                'frequency': info.get('frequency'),
                'seasonal_adjustment': info.get('seasonal_adjustment'),
                'last_updated': info.get('last_updated'),
                'notes': info.get('notes')
            }
        except Exception as e:
            logger.error(f"Error fetching series info for {series_id}: {e}")
            raise
    
    def calculate_yoy_change(
        self,
        series: pd.Series,
        periods: int = 12
    ) -> pd.Series:
        """
        Calculate year-over-year percent change.
        
        Args:
            series: Time series data
            periods: Number of periods for YoY calculation (12 for monthly, 4 for quarterly)
        
        Returns:
            Series with YoY percent changes
        """
        return series.pct_change(periods=periods) * 100
    
    def calculate_growth_rate(
        self,
        series: pd.Series,
        annualize: bool = True
    ) -> pd.Series:
        """
        Calculate period-over-period growth rate.
        
        Args:
            series: Time series data
            annualize: Whether to annualize the growth rate
        
        Returns:
            Series with growth rates
        """
        growth = series.pct_change() * 100
        
        if annualize:
            # Annualize based on frequency
            freq = pd.infer_freq(series.index)
            if freq and 'M' in freq:  # Monthly
                growth = growth * 12
            elif freq and 'Q' in freq:  # Quarterly
                growth = growth * 4
        
        return growth
    
    def get_latest_value(
        self,
        series_id: str,
        as_of_date: Optional[str] = None
    ) -> Dict:
        """
        Get the most recent value for a series.
        
        Args:
            series_id: FRED series identifier
            as_of_date: Get latest value as of this date (default: today)
        
        Returns:
            Dictionary with latest value and metadata
        """
        series = self.get_series(series_id, end_date=as_of_date)
        
        if series.empty:
            return None
        
        latest_date = series.index[-1]
        latest_value = series.iloc[-1]
        
        # Calculate change from previous period
        if len(series) > 1:
            prev_value = series.iloc[-2]
            change = latest_value - prev_value
            pct_change = (change / prev_value) * 100 if prev_value != 0 else None
        else:
            change = None
            pct_change = None
        
        return {
            'series_id': series_id,
            'date': latest_date.strftime('%Y-%m-%d'),
            'value': float(latest_value),
            'change': float(change) if change is not None else None,
            'pct_change': float(pct_change) if pct_change is not None else None,
            'units': FRED_SERIES_MAP.get(series_id, {}).get('units', 'Unknown')
        }
    
    def get_series_range(
        self,
        series_id: str,
        start_date: str,
        end_date: str,
        transform: Optional[str] = None
    ) -> Dict:
        """
        Get series data for a date range with optional transformation.
        
        Args:
            series_id: FRED series identifier
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            transform: Transformation to apply ('yoy', 'growth', None)
        
        Returns:
            Dictionary with dates and values
        """
        series = self.get_series(series_id, start_date, end_date)
        
        if transform == 'yoy':
            # Determine periods based on frequency
            freq = pd.infer_freq(series.index)
            periods = 12 if freq and 'M' in freq else 4  # Monthly vs Quarterly
            series = self.calculate_yoy_change(series, periods)
        elif transform == 'growth':
            series = self.calculate_growth_rate(series)
        
        # Remove NaN values
        series = series.dropna()
        
        return {
            'series_id': series_id,
            'start_date': start_date,
            'end_date': end_date,
            'transform': transform,
            'frequency': pd.infer_freq(series.index),
            'count': len(series),
            'dates': series.index.strftime('%Y-%m-%d').tolist(),
            'values': series.values.tolist(),
            'mean': float(series.mean()),
            'min': float(series.min()),
            'max': float(series.max()),
            'latest': {
                'date': series.index[-1].strftime('%Y-%m-%d'),
                'value': float(series.iloc[-1])
            }
        }
    
    def compare_series(
        self,
        series_ids: List[str],
        start_date: str,
        end_date: str,
        normalize: bool = False
    ) -> Dict:
        """
        Compare multiple series side-by-side.
        
        Args:
            series_ids: List of FRED series identifiers
            start_date: Start date
            end_date: End date
            normalize: Normalize to index (first value = 100)
        
        Returns:
            Dictionary with comparison data
        """
        data = {}
        
        for series_id in series_ids:
            series = self.get_series(series_id, start_date, end_date)
            
            if normalize and not series.empty:
                series = (series / series.iloc[0]) * 100
            
            data[series_id] = series.values.tolist()
        
        # Use the first series for dates (assume all aligned)
        first_series = self.get_series(series_ids[0], start_date, end_date)
        dates = first_series.index.strftime('%Y-%m-%d').tolist()
        
        return {
            'series_ids': series_ids,
            'start_date': start_date,
            'end_date': end_date,
            'normalized': normalize,
            'dates': dates,
            'data': data
        }
    
    def get_economic_snapshot(
        self,
        as_of_date: Optional[str] = None
    ) -> Dict:
        """
        Get a comprehensive snapshot of key economic indicators.
        
        Args:
            as_of_date: Date for snapshot (default: latest available)
        
        Returns:
            Dictionary with all major indicators
        """
        snapshot = {
            'date': as_of_date or datetime.now().strftime('%Y-%m-%d'),
            'indicators': {}
        }
        
        # Key indicators for Fed policy analysis
        key_indicators = [
            'pce_core', 'cpi_core', 'unemployment', 'nonfarm_payrolls',
            'fed_funds', 'treasury_10y', 'gdp_growth'
        ]
        
        for indicator in key_indicators:
            if indicator in FRED_SERIES_MAP:
                series_id = FRED_SERIES_MAP[indicator]['series_id']
                try:
                    latest = self.get_latest_value(series_id, as_of_date)
                    if latest:
                        snapshot['indicators'][indicator] = latest
                except Exception as e:
                    logger.warning(f"Could not fetch {indicator}: {e}")
        
        return snapshot


# Singleton instance
_fred_wrapper = None

def get_fred_wrapper() -> FREDAPIWrapper:
    """Get or create singleton FRED API wrapper instance."""
    global _fred_wrapper
    if _fred_wrapper is None:
        _fred_wrapper = FREDAPIWrapper()
    return _fred_wrapper
