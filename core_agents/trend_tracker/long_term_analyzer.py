"""
Long-Term Analyzer

Analyzes multi-year Fed policy trends using advanced time-series methods.
Identifies structural breaks, persistent patterns, and long-term shifts.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from scipy import stats, signal
from sklearn.linear_model import LinearRegression

# Change point detection
try:
    import ruptures as rpt
    RUPTURES_AVAILABLE = True
except ImportError:
    RUPTURES_AVAILABLE = False
    logging.warning("ruptures not installed - change point detection limited")

try:
    # Try relative imports first (when used as module)
    from .trend_tracker_config import (
        TIME_HORIZONS,
        CHANGEPOINT_METHODS,
        TREND_STRENGTH,
        PERSISTENCE_THRESHOLDS
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from trend_tracker_config import (
        TIME_HORIZONS,
        CHANGEPOINT_METHODS,
        TREND_STRENGTH,
        PERSISTENCE_THRESHOLDS
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LongTermAnalyzer:
    """
    Analyze long-term Fed policy trends.
    """
    
    def __init__(self):
        """Initialize long-term analyzer."""
        logger.info("Initialized Long-Term Analyzer")
    
    def analyze_long_term_trend(
        self,
        meeting_data: List[Dict],
        variable: str = 'score',
        min_meetings: int = 24
    ) -> Dict:
        """
        Analyze long-term trend in policy variable.
        
        Args:
            meeting_data: List of meeting data
            variable: Variable to analyze ('score', 'fed_funds', etc.)
            min_meetings: Minimum meetings required
        
        Returns:
            Dictionary with trend analysis
        """
        logger.info(f"Analyzing long-term trend in {variable}")
        
        if len(meeting_data) < min_meetings:
            return {
                'error': f'Insufficient data (need {min_meetings}, got {len(meeting_data)})'
            }
        
        df = pd.DataFrame(meeting_data)
        
        if variable not in df.columns:
            return {'error': f'Variable {variable} not found in data'}
        
        # Remove NaN values
        df = df.dropna(subset=[variable])
        
        # Fit overall trend
        X = np.arange(len(df)).reshape(-1, 1)
        y = df[variable].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        y_pred = model.predict(X)
        slope = model.coef_[0]
        intercept = model.intercept_
        
        # Calculate R²
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Classify trend strength
        strength = self._classify_trend_strength(r_squared)
        
        # Determine direction
        if abs(slope) < 0.1:
            direction = "no_trend"
        elif slope > 0:
            direction = "hawkish_trend"
        else:
            direction = "dovish_trend"
        
        # Detect change points
        changepoints = self.detect_changepoints(df, variable)
        
        # Calculate persistence
        persistence = self._calculate_persistence(df, variable, slope)
        
        return {
            'variable': variable,
            'direction': direction,
            'slope': round(float(slope), 4),
            'intercept': round(float(intercept), 2),
            'r_squared': round(float(r_squared), 3),
            'strength': strength,
            'persistence': persistence,
            'changepoints': changepoints,
            'num_meetings': len(df),
            'interpretation': self._interpret_trend(direction, strength, slope, r_squared)
        }
    
    def detect_changepoints(
        self,
        df: pd.DataFrame,
        variable: str,
        method: str = 'pelt'
    ) -> List[Dict]:
        """
        Detect structural breaks/changepoints in time series.
        
        Args:
            df: DataFrame with data
            variable: Variable to analyze
            method: Detection method ('pelt', 'binseg', 'window')
        
        Returns:
            List of detected changepoints
        """
        logger.info(f"Detecting changepoints using {method}")
        
        if not RUPTURES_AVAILABLE:
            logger.warning("Ruptures not available, using simple method")
            return self._simple_changepoint_detection(df, variable)
        
        signal_data = df[variable].values
        
        try:
            if method == 'pelt':
                # PELT (Pruned Exact Linear Time)
                algo = rpt.Pelt(
                    model=CHANGEPOINT_METHODS['pelt']['model'],
                    min_size=CHANGEPOINT_METHODS['pelt']['min_size']
                )
                result = algo.fit_predict(
                    signal_data,
                    pen=CHANGEPOINT_METHODS['pelt']['penalty']
                )
            
            elif method == 'binseg':
                # Binary Segmentation
                algo = rpt.Binseg(
                    model="l2",
                    min_size=CHANGEPOINT_METHODS['binseg']['min_size']
                )
                result = algo.fit_predict(
                    signal_data,
                    n_bkps=CHANGEPOINT_METHODS['binseg']['n_bkps']
                )
            
            else:
                # Window-based
                algo = rpt.Window(
                    width=CHANGEPOINT_METHODS['window']['width'],
                    model=CHANGEPOINT_METHODS['window']['model']
                )
                result = algo.fit_predict(
                    signal_data,
                    n_bkps=5
                )
            
            # Convert to changepoint dicts
            changepoints = []
            for idx in result[:-1]:  # Last point is end of series
                if idx < len(df):
                    cp_date = df.iloc[idx]['date'] if 'date' in df.columns else idx
                    value_before = signal_data[max(0, idx-1)]
                    value_after = signal_data[min(idx, len(signal_data)-1)]
                    
                    changepoints.append({
                        'index': int(idx),
                        'date': cp_date,
                        'value_before': round(float(value_before), 2),
                        'value_after': round(float(value_after), 2),
                        'change': round(float(value_after - value_before), 2)
                    })
            
            logger.info(f"Detected {len(changepoints)} changepoints")
            return changepoints
        
        except Exception as e:
            logger.error(f"Change point detection failed: {e}")
            return self._simple_changepoint_detection(df, variable)
    
    def _simple_changepoint_detection(
        self,
        df: pd.DataFrame,
        variable: str
    ) -> List[Dict]:
        """
        Simple changepoint detection using rolling statistics.
        Fallback when ruptures not available.
        """
        signal_data = df[variable].values
        window = 6  # 1.5 years
        
        # Calculate rolling mean
        rolling_mean = pd.Series(signal_data).rolling(window=window, min_periods=1).mean()
        
        # Find large changes in rolling mean
        mean_changes = np.abs(np.diff(rolling_mean))
        threshold = np.percentile(mean_changes, 80)  # Top 20%
        
        changepoints = []
        for i, change in enumerate(mean_changes):
            if change > threshold and i > window:
                if 'date' in df.columns and i < len(df):
                    cp_date = df.iloc[i]['date']
                else:
                    cp_date = i
                
                changepoints.append({
                    'index': int(i),
                    'date': cp_date,
                    'value_before': round(float(signal_data[i-1]), 2),
                    'value_after': round(float(signal_data[i]), 2),
                    'change': round(float(signal_data[i] - signal_data[i-1]), 2)
                })
        
        return changepoints
    
    def _classify_trend_strength(self, r_squared: float) -> str:
        """Classify trend strength based on R²."""
        
        if r_squared >= TREND_STRENGTH['very_strong']:
            return "very_strong"
        elif r_squared >= TREND_STRENGTH['strong']:
            return "strong"
        elif r_squared >= TREND_STRENGTH['moderate']:
            return "moderate"
        elif r_squared >= TREND_STRENGTH['weak']:
            return "weak"
        else:
            return "negligible"
    
    def _calculate_persistence(
        self,
        df: pd.DataFrame,
        variable: str,
        overall_slope: float
    ) -> Dict:
        """
        Calculate how persistent the trend is.
        
        Measures how long the trend continues in same direction.
        """
        values = df[variable].values
        
        # Count consecutive periods with same sign as overall slope
        current_streak = 0
        max_streak = 0
        
        for i in range(1, len(values)):
            change = values[i] - values[i-1]
            
            # Check if change aligns with overall slope
            if (overall_slope > 0 and change > 0) or (overall_slope < 0 and change < 0):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        # Classify persistence
        if max_streak >= PERSISTENCE_THRESHOLDS['highly_persistent']:
            level = "highly_persistent"
        elif max_streak >= PERSISTENCE_THRESHOLDS['persistent']:
            level = "persistent"
        elif max_streak >= PERSISTENCE_THRESHOLDS['moderately_persistent']:
            level = "moderately_persistent"
        else:
            level = "transient"
        
        return {
            'max_streak': max_streak,
            'level': level,
            'consistency': round(max_streak / len(values), 2)
        }
    
    def _interpret_trend(
        self,
        direction: str,
        strength: str,
        slope: float,
        r_squared: float
    ) -> str:
        """Generate interpretation of trend."""
        
        if direction == "no_trend":
            return f"No clear trend (R²={r_squared:.2f})"
        
        strength_word = strength.replace('_', ' ')
        direction_word = direction.replace('_', ' ')
        
        return (
            f"{strength_word.capitalize()} {direction_word} "
            f"(slope={slope:.3f}, R²={r_squared:.2f})"
        )
    
    def analyze_volatility(
        self,
        meeting_data: List[Dict],
        variable: str = 'score',
        windows: List[int] = [6, 12, 24]
    ) -> Dict:
        """
        Analyze volatility across different time windows.
        
        Args:
            meeting_data: List of meeting data
            variable: Variable to analyze
            windows: Window sizes to analyze
        
        Returns:
            Dictionary with volatility analysis
        """
        logger.info(f"Analyzing volatility in {variable}")
        
        df = pd.DataFrame(meeting_data)
        
        if variable not in df.columns:
            return {'error': f'Variable {variable} not found'}
        
        volatility = {}
        
        for window in windows:
            if len(df) >= window:
                rolling_std = df[variable].rolling(window=window).std()
                
                volatility[f'window_{window}'] = {
                    'mean_volatility': round(float(rolling_std.mean()), 2),
                    'max_volatility': round(float(rolling_std.max()), 2),
                    'current_volatility': round(float(rolling_std.iloc[-1]), 2) if len(rolling_std) > 0 else None
                }
        
        # Overall volatility trend
        if len(df) >= 12:
            recent_vol = df[variable].tail(12).std()
            historical_vol = df[variable].std()
            
            if recent_vol > historical_vol * 1.2:
                trend = "increasing"
            elif recent_vol < historical_vol * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "unknown"
        
        return {
            'by_window': volatility,
            'overall_trend': trend,
            'interpretation': self._interpret_volatility(trend, volatility)
        }
    
    def _interpret_volatility(self, trend: str, volatility: Dict) -> str:
        """Interpret volatility analysis."""
        
        if not volatility:
            return "Insufficient data for volatility analysis"
        
        # Get most recent window
        latest_window = sorted(volatility.keys())[-1]
        latest_vol = volatility[latest_window]['current_volatility']
        
        if latest_vol is None:
            return "Current volatility unavailable"
        
        if latest_vol > 10:
            level = "very high"
        elif latest_vol > 6:
            level = "high"
        elif latest_vol > 3:
            level = "moderate"
        else:
            level = "low"
        
        return f"Current volatility is {level} and {trend}"
    
    def detect_regime_persistence(
        self,
        meeting_data: List[Dict]
    ) -> Dict:
        """
        Detect how long Fed stays in each regime.
        
        Analyzes regime persistence patterns.
        """
        logger.info("Analyzing regime persistence")
        
        df = pd.DataFrame(meeting_data)
        
        if 'regime' not in df.columns:
            return {'error': 'Regime data not available'}
        
        # Count regime durations
        regime_durations = {}
        current_regime = None
        duration = 0
        
        for regime in df['regime']:
            if regime == current_regime:
                duration += 1
            else:
                if current_regime is not None:
                    if current_regime not in regime_durations:
                        regime_durations[current_regime] = []
                    regime_durations[current_regime].append(duration)
                
                current_regime = regime
                duration = 1
        
        # Add last regime
        if current_regime is not None:
            if current_regime not in regime_durations:
                regime_durations[current_regime] = []
            regime_durations[current_regime].append(duration)
        
        # Calculate statistics
        regime_stats = {}
        for regime, durations in regime_durations.items():
            regime_stats[regime] = {
                'average_duration': round(np.mean(durations), 1),
                'median_duration': round(np.median(durations), 1),
                'max_duration': max(durations),
                'min_duration': min(durations),
                'num_occurrences': len(durations)
            }
        
        return {
            'regime_statistics': regime_stats,
            'interpretation': self._interpret_regime_persistence(regime_stats)
        }
    
    def _interpret_regime_persistence(self, stats: Dict) -> str:
        """Interpret regime persistence patterns."""
        
        if not stats:
            return "No regime data available"
        
        # Find most persistent regime
        most_persistent = max(
            stats.items(),
            key=lambda x: x[1]['average_duration']
        )
        
        return (
            f"{most_persistent[0]} regime most persistent "
            f"(avg: {most_persistent[1]['average_duration']} meetings)"
        )


def analyze_long_term_patterns(meeting_data: List[Dict]) -> Dict:
    """
    Convenience function for complete long-term analysis.
    
    Args:
        meeting_data: List of meeting data
    
    Returns:
        Complete long-term analysis
    """
    analyzer = LongTermAnalyzer()
    
    # Analyze multiple variables
    results = {}
    
    # Sentiment score trend
    if any('score' in m for m in meeting_data):
        results['sentiment_trend'] = analyzer.analyze_long_term_trend(
            meeting_data,
            variable='score'
        )
    
    # Fed Funds trend (if available)
    if any('fed_funds' in m for m in meeting_data):
        results['fed_funds_trend'] = analyzer.analyze_long_term_trend(
            meeting_data,
            variable='fed_funds'
        )
    
    # Volatility analysis
    if any('score' in m for m in meeting_data):
        results['volatility'] = analyzer.analyze_volatility(
            meeting_data,
            variable='score'
        )
    
    # Regime persistence
    if any('regime' in m for m in meeting_data):
        results['regime_persistence'] = analyzer.detect_regime_persistence(
            meeting_data
        )
    
    return results
