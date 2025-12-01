"""
BLS API Wrapper

Handles all interactions with the Bureau of Labor Statistics API:
- Data fetching with caching
- JSON payload construction
- Response parsing and transformation
- Year-over-year calculations
- Error handling
"""

import logging
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Union
from cachetools import TTLCache

# Handle relative imports for package usage and absolute for direct execution
try:
    from .bls_config import (
        BLS_API_KEY,
        BLS_API_URL,
        BLS_API_V1_URL,
        BLS_SERIES_MAP,
        CACHE_TTL_SECONDS,
        MAX_CACHE_SIZE,
        DEFAULT_START_YEAR
    )
except ImportError:
    from bls_config import (
        BLS_API_KEY,
        BLS_API_URL,
        BLS_API_V1_URL,
        BLS_SERIES_MAP,
        CACHE_TTL_SECONDS,
        MAX_CACHE_SIZE,
        DEFAULT_START_YEAR
    )

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BLSAPIWrapper:
    """
    Wrapper for BLS API with caching, error handling, and data transformation.
    
    BLS API Documentation: https://www.bls.gov/developers/api_signature_v2.htm
    """
    
    def __init__(self, api_key: str = BLS_API_KEY):
        """
        Initialize BLS API wrapper.
        
        Args:
            api_key: BLS API key (optional but recommended for higher limits)
        """
        self.api_key = api_key
        self.cache = TTLCache(maxsize=MAX_CACHE_SIZE, ttl=CACHE_TTL_SECONDS)
        
        # Use v2 API if we have a key, v1 otherwise
        self.api_url = BLS_API_URL if api_key else BLS_API_V1_URL
        self.api_version = "v2" if api_key else "v1"
        
        logger.info(f"BLS API wrapper initialized (API version: {self.api_version})")
        if not api_key:
            logger.warning("No BLS API key provided - using v1 API with lower rate limits")
    
    def get_series(
        self,
        series_id: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Get a BLS time series.
        
        Args:
            series_id: BLS series identifier (e.g., 'CUUR0000SA0')
            start_year: Start year (default: 2005)
            end_year: End year (default: current year)
            **kwargs: Additional parameters (catalog, calculations, annualaverage)
        
        Returns:
            DataFrame with columns: date, value, year, period, periodName
        """
        if start_year is None:
            start_year = DEFAULT_START_YEAR
        if end_year is None:
            end_year = datetime.now().year
        
        cache_key = f"{series_id}_{start_year}_{end_year}"
        
        if cache_key in self.cache:
            logger.debug(f"Cache hit for {series_id}")
            return self.cache[cache_key]
        
        try:
            logger.info(f"Fetching {series_id} from BLS API ({start_year}-{end_year})")
            
            # Construct API payload
            payload = {
                "seriesid": [series_id],
                "startyear": str(start_year),
                "endyear": str(end_year)
            }
            
            # Add API key if available
            if self.api_key:
                payload["registrationkey"] = self.api_key
            
            # Add optional parameters
            if kwargs.get("catalog"):
                payload["catalog"] = True
            if kwargs.get("calculations"):
                payload["calculations"] = True
            if kwargs.get("annualaverage"):
                payload["annualaverage"] = True
            
            # Make API request
            headers = {"Content-type": "application/json"}
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            if data.get("status") != "REQUEST_SUCCEEDED":
                error_msg = data.get("message", ["Unknown error"])[0]
                raise ValueError(f"BLS API error: {error_msg}")
            
            # Extract series data
            series_data = data["Results"]["series"][0]["data"]
            
            # Convert to DataFrame
            df = pd.DataFrame(series_data)
            
            # Parse dates
            df['date'] = pd.to_datetime(
                df['year'] + '-' + df['period'].str.replace('M', ''),
                format='%Y-%m',
                errors='coerce'
            )
            
            # Convert value to float
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            
            # Sort by date
            df = df.sort_values('date').reset_index(drop=True)
            
            # Cache the result
            self.cache[cache_key] = df
            
            return df
            
        except requests.RequestException as e:
            logger.error(f"HTTP error fetching {series_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching {series_id}: {e}")
            raise
    
    def get_multiple_series(
        self,
        series_ids: List[str],
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Get multiple BLS series in a single request (more efficient).
        
        Args:
            series_ids: List of BLS series identifiers
            start_year: Start year
            end_year: End year
        
        Returns:
            Dictionary mapping series_id to DataFrame
        """
        if start_year is None:
            start_year = DEFAULT_START_YEAR
        if end_year is None:
            end_year = datetime.now().year
        
        # BLS API allows max 50 series per request (v2) or 25 (v1)
        max_series = 50 if self.api_key else 25
        
        if len(series_ids) > max_series:
            logger.warning(f"Requesting {len(series_ids)} series, will batch into multiple requests")
        
        all_results = {}
        
        # Batch requests
        for i in range(0, len(series_ids), max_series):
            batch = series_ids[i:i+max_series]
            
            try:
                logger.info(f"Fetching batch of {len(batch)} series")
                
                payload = {
                    "seriesid": batch,
                    "startyear": str(start_year),
                    "endyear": str(end_year)
                }
                
                if self.api_key:
                    payload["registrationkey"] = self.api_key
                
                headers = {"Content-type": "application/json"}
                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("status") != "REQUEST_SUCCEEDED":
                    error_msg = data.get("message", ["Unknown error"])[0]
                    raise ValueError(f"BLS API error: {error_msg}")
                
                # Parse each series
                for series_obj in data["Results"]["series"]:
                    series_id = series_obj["seriesID"]
                    series_data = series_obj["data"]
                    
                    df = pd.DataFrame(series_data)
                    df['date'] = pd.to_datetime(
                        df['year'] + '-' + df['period'].str.replace('M', ''),
                        format='%Y-%m',
                        errors='coerce'
                    )
                    df['value'] = pd.to_numeric(df['value'], errors='coerce')
                    df = df.sort_values('date').reset_index(drop=True)
                    
                    all_results[series_id] = df
                
            except Exception as e:
                logger.error(f"Error fetching batch: {e}")
                # Continue with next batch
        
        return all_results
    
    def calculate_yoy_change(
        self,
        df: pd.DataFrame,
        periods: int = 12
    ) -> pd.DataFrame:
        """
        Calculate year-over-year percent change.
        
        Args:
            df: DataFrame with 'value' column
            periods: Number of periods for YoY (12 for monthly)
        
        Returns:
            DataFrame with additional 'yoy_change' column
        """
        df = df.copy()
        df['yoy_change'] = df['value'].pct_change(periods=periods) * 100
        return df
    
    def calculate_mom_change(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate month-over-month percent change.
        
        Args:
            df: DataFrame with 'value' column
        
        Returns:
            DataFrame with additional 'mom_change' column
        """
        df = df.copy()
        df['mom_change'] = df['value'].pct_change(periods=1) * 100
        return df
    
    def get_latest_value(
        self,
        series_id: str
    ) -> Dict:
        """
        Get the most recent value for a series.
        
        Args:
            series_id: BLS series identifier
        
        Returns:
            Dictionary with latest value and metadata
        """
        # Get last 2 years of data to ensure we have recent values
        current_year = datetime.now().year
        df = self.get_series(series_id, start_year=current_year - 2, end_year=current_year)
        
        if df.empty:
            return None
        
        # Get latest non-null value
        df_valid = df[df['value'].notna()]
        if df_valid.empty:
            return None
        
        latest = df_valid.iloc[-1]
        
        # Calculate changes if we have enough data
        yoy_change = None
        mom_change = None
        
        if len(df_valid) >= 12:
            df_with_yoy = self.calculate_yoy_change(df_valid)
            yoy_change = df_with_yoy.iloc[-1]['yoy_change']
        
        if len(df_valid) >= 2:
            df_with_mom = self.calculate_mom_change(df_valid)
            mom_change = df_with_mom.iloc[-1]['mom_change']
        
        return {
            'series_id': series_id,
            'date': latest['date'].strftime('%Y-%m-%d') if pd.notna(latest['date']) else None,
            'value': float(latest['value']),
            'year': latest['year'],
            'period': latest['period'],
            'period_name': latest.get('periodName', ''),
            'yoy_change': float(yoy_change) if pd.notna(yoy_change) else None,
            'mom_change': float(mom_change) if pd.notna(mom_change) else None
        }
    
    def get_component_breakdown(
        self,
        component_ids: List[str],
        start_year: int,
        end_year: int
    ) -> Dict[str, pd.DataFrame]:
        """
        Get breakdown of CPI components with YoY changes.
        
        Args:
            component_ids: List of component series IDs
            start_year: Start year
            end_year: End year
        
        Returns:
            Dictionary of DataFrames with YoY changes
        """
        # Fetch all series
        series_data = self.get_multiple_series(component_ids, start_year, end_year)
        
        # Calculate YoY for each
        result = {}
        for series_id, df in series_data.items():
            df_with_yoy = self.calculate_yoy_change(df)
            result[series_id] = df_with_yoy
        
        return result
    
    def compare_components(
        self,
        component_map: Dict[str, str],
        start_year: int,
        end_year: int,
        as_of_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Compare multiple CPI components at a point in time.
        
        Args:
            component_map: Dict mapping component names to series IDs
            start_year: Start year for data
            end_year: End year for data
            as_of_date: Specific date to compare (default: latest)
        
        Returns:
            DataFrame comparing all components
        """
        series_ids = list(component_map.values())
        series_data = self.get_multiple_series(series_ids, start_year, end_year)
        
        comparison = []
        
        for name, series_id in component_map.items():
            df = series_data.get(series_id)
            if df is None or df.empty:
                continue
            
            df_with_yoy = self.calculate_yoy_change(df)
            
            # Get value at specific date or latest
            if as_of_date:
                target_date = pd.to_datetime(as_of_date)
                df_filtered = df_with_yoy[df_with_yoy['date'] <= target_date]
                if not df_filtered.empty:
                    row = df_filtered.iloc[-1]
                else:
                    continue
            else:
                row = df_with_yoy.iloc[-1]
            
            comparison.append({
                'component': name,
                'series_id': series_id,
                'date': row['date'].strftime('%Y-%m-%d') if pd.notna(row['date']) else None,
                'value': float(row['value']) if pd.notna(row['value']) else None,
                'yoy_change': float(row['yoy_change']) if pd.notna(row['yoy_change']) else None
            })
        
        return pd.DataFrame(comparison)


# Singleton instance
_bls_wrapper = None

def get_bls_wrapper() -> BLSAPIWrapper:
    """Get or create singleton BLS API wrapper instance."""
    global _bls_wrapper
    if _bls_wrapper is None:
        _bls_wrapper = BLSAPIWrapper()
    return _bls_wrapper
