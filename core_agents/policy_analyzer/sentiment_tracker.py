"""
Sentiment Tracker

Analyzes Fed sentiment evolution over time across multiple FOMC meetings.
Tracks hawkish/dovish trends and detects shifts in policy stance.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from scipy import stats

try:
    # Try relative imports first (when used as module)
    from .policy_analyzer_config import (
        STANCE_THRESHOLDS,
        SENTIMENT_MA_WINDOWS,
        TREND_THRESHOLDS,
        STANCE_SHIFT_THRESHOLD
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from policy_analyzer_config import (
        STANCE_THRESHOLDS,
        SENTIMENT_MA_WINDOWS,
        TREND_THRESHOLDS,
        STANCE_SHIFT_THRESHOLD
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentTracker:
    """
    Track Fed sentiment over time and identify trends.
    """
    
    def __init__(self):
        """Initialize sentiment tracker."""
        logger.info("Initialized Sentiment Tracker")
    
    def create_sentiment_timeseries(
        self,
        meeting_data: List[Dict]
    ) -> pd.DataFrame:
        """
        Create time series from multiple meeting sentiment analyses.
        
        Args:
            meeting_data: List of dicts with 'date', 'sentiment', 'score'
        
        Returns:
            DataFrame with sentiment time series
        """
        logger.info(f"Creating sentiment time series from {len(meeting_data)} meetings")
        
        if not meeting_data:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(meeting_data)
        
        # Ensure date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)
        
        # Calculate moving averages
        if 'score' in df.columns:
            for window_name, window_size in SENTIMENT_MA_WINDOWS.items():
                if len(df) >= window_size:
                    df[f'ma_{window_name}'] = df['score'].rolling(window=window_size, min_periods=1).mean()
        
        return df
    
    def classify_stance(self, score: float) -> Dict:
        """
        Classify policy stance based on sentiment score.
        
        Args:
            score: Sentiment score (hawkish_count - dovish_count)
        
        Returns:
            Dictionary with classification
        """
        if score < STANCE_THRESHOLDS['highly_dovish']:
            classification = "highly_dovish"
            description = "Very dovish - strong emphasis on supporting economy"
        elif score < STANCE_THRESHOLDS['dovish']:
            classification = "dovish"
            description = "Dovish - leaning toward easier policy"
        elif score <= STANCE_THRESHOLDS['neutral']:
            classification = "neutral"
            description = "Neutral - balanced view"
        elif score <= STANCE_THRESHOLDS['hawkish']:
            classification = "hawkish"
            description = "Hawkish - leaning toward tighter policy"
        else:
            classification = "highly_hawkish"
            description = "Very hawkish - strong emphasis on fighting inflation"
        
        return {
            'classification': classification,
            'score': score,
            'description': description
        }
    
    def detect_trend(
        self,
        df: pd.DataFrame,
        recent_meetings: int = 6
    ) -> Dict:
        """
        Detect sentiment trend over recent meetings.
        
        Args:
            df: Sentiment time series DataFrame
            recent_meetings: Number of recent meetings to analyze
        
        Returns:
            Dictionary with trend analysis
        """
        logger.info(f"Detecting sentiment trend over {recent_meetings} meetings")
        
        if len(df) < 2:
            return {
                'direction': 'unknown',
                'strength': 'unknown',
                'slope': 0,
                'r_squared': 0
            }
        
        # Get recent data
        recent_df = df.tail(recent_meetings)
        
        if len(recent_df) < 2:
            return {
                'direction': 'insufficient_data',
                'strength': 'unknown',
                'slope': 0,
                'r_squared': 0
            }
        
        # Fit linear trend
        x = np.arange(len(recent_df))
        y = recent_df['score'].values
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        r_squared = r_value ** 2
        
        # Classify trend
        if slope > TREND_THRESHOLDS['strong_hawkish_trend']:
            direction = "strong_hawkish_trend"
            strength = "strong"
        elif slope > TREND_THRESHOLDS['moderate_hawkish_trend']:
            direction = "moderate_hawkish_trend"
            strength = "moderate"
        elif slope < TREND_THRESHOLDS['strong_dovish_trend']:
            direction = "strong_dovish_trend"
            strength = "strong"
        elif slope < TREND_THRESHOLDS['moderate_dovish_trend']:
            direction = "moderate_dovish_trend"
            strength = "moderate"
        else:
            direction = "stable"
            strength = "weak"
        
        return {
            'direction': direction,
            'strength': strength,
            'slope': round(float(slope), 2),
            'r_squared': round(float(r_squared), 3),
            'p_value': round(float(p_value), 4),
            'duration': len(recent_df),
            'interpretation': self._interpret_trend(direction, slope, r_squared)
        }
    
    def _interpret_trend(self, direction: str, slope: float, r_squared: float) -> str:
        """Generate human-readable trend interpretation."""
        
        if direction == "stable":
            return f"Sentiment is stable (slope: {slope:.2f})"
        
        trend_word = "becoming more hawkish" if slope > 0 else "becoming more dovish"
        strength_word = "strongly" if abs(slope) > 0.5 else "moderately"
        confidence = "high confidence" if r_squared > 0.7 else "moderate confidence"
        
        return f"Sentiment is {strength_word} {trend_word} (slope: {slope:.2f}, {confidence})"
    
    def detect_shifts(
        self,
        df: pd.DataFrame
    ) -> List[Dict]:
        """
        Detect significant shifts in sentiment.
        
        Args:
            df: Sentiment time series DataFrame
        
        Returns:
            List of detected shifts with metadata
        """
        logger.info("Detecting sentiment shifts")
        
        if len(df) < 2:
            return []
        
        shifts = []
        
        for i in range(1, len(df)):
            score_change = df.iloc[i]['score'] - df.iloc[i-1]['score']
            
            if abs(score_change) >= STANCE_SHIFT_THRESHOLD:
                # Significant shift detected
                prev_stance = self.classify_stance(df.iloc[i-1]['score'])
                new_stance = self.classify_stance(df.iloc[i]['score'])
                
                shift = {
                    'date': df.iloc[i]['date'] if 'date' in df.columns else i,
                    'previous_score': df.iloc[i-1]['score'],
                    'new_score': df.iloc[i]['score'],
                    'change': score_change,
                    'previous_stance': prev_stance['classification'],
                    'new_stance': new_stance['classification'],
                    'magnitude': 'large' if abs(score_change) >= 20 else 'moderate'
                }
                
                shifts.append(shift)
        
        logger.info(f"Detected {len(shifts)} significant sentiment shifts")
        return shifts
    
    def calculate_volatility(
        self,
        df: pd.DataFrame,
        window: int = 6
    ) -> Dict:
        """
        Calculate sentiment volatility (how much it varies).
        
        Args:
            df: Sentiment time series DataFrame
            window: Rolling window size
        
        Returns:
            Dictionary with volatility metrics
        """
        logger.info("Calculating sentiment volatility")
        
        if len(df) < window:
            return {
                'volatility': None,
                'interpretation': 'Insufficient data'
            }
        
        # Standard deviation of recent scores
        recent_df = df.tail(window)
        volatility = recent_df['score'].std()
        
        # Classify volatility
        if volatility < 3:
            level = "very_stable"
            interp = "Sentiment very consistent across meetings"
        elif volatility < 6:
            level = "stable"
            interp = "Sentiment fairly consistent"
        elif volatility < 10:
            level = "moderate"
            interp = "Sentiment shows moderate variation"
        else:
            level = "volatile"
            interp = "Sentiment varies significantly between meetings"
        
        return {
            'volatility': round(float(volatility), 2),
            'level': level,
            'interpretation': interp,
            'window': window
        }
    
    def compare_periods(
        self,
        df: pd.DataFrame,
        period1_end: int,
        period2_end: int,
        period_length: int = 6
    ) -> Dict:
        """
        Compare sentiment between two periods.
        
        Args:
            df: Sentiment time series DataFrame
            period1_end: End index for period 1
            period2_end: End index for period 2
            period_length: Length of each period
        
        Returns:
            Dictionary comparing the two periods
        """
        logger.info(f"Comparing periods: {period1_end} vs {period2_end}")
        
        # Extract periods
        period1 = df.iloc[max(0, period1_end-period_length):period1_end]
        period2 = df.iloc[max(0, period2_end-period_length):period2_end]
        
        if period1.empty or period2.empty:
            return {'error': 'Insufficient data for comparison'}
        
        # Calculate statistics
        p1_mean = period1['score'].mean()
        p2_mean = period2['score'].mean()
        change = p2_mean - p1_mean
        
        # Statistical significance
        if len(period1) >= 3 and len(period2) >= 3:
            t_stat, p_value = stats.ttest_ind(period1['score'], period2['score'])
            significant = p_value < 0.05
        else:
            t_stat, p_value, significant = None, None, False
        
        return {
            'period1_mean': round(float(p1_mean), 2),
            'period2_mean': round(float(p2_mean), 2),
            'change': round(float(change), 2),
            'statistically_significant': significant,
            'p_value': round(float(p_value), 4) if p_value else None,
            'interpretation': self._interpret_period_comparison(change, significant)
        }
    
    def _interpret_period_comparison(self, change: float, significant: bool) -> str:
        """Interpret period comparison."""
        
        if abs(change) < 2:
            return "Sentiment largely unchanged between periods"
        
        direction = "more hawkish" if change > 0 else "more dovish"
        magnitude = "significantly" if abs(change) > 10 else "moderately"
        significance = " (statistically significant)" if significant else ""
        
        return f"Sentiment {magnitude} {direction} in later period{significance}"
    
    def get_current_stance(
        self,
        df: pd.DataFrame
    ) -> Dict:
        """
        Get current policy stance with confidence.
        
        Args:
            df: Sentiment time series DataFrame
        
        Returns:
            Dictionary with current stance analysis
        """
        if df.empty:
            return {'error': 'No data'}
        
        # Latest score
        latest_score = df.iloc[-1]['score']
        latest_stance = self.classify_stance(latest_score)
        
        # Check consistency over recent meetings
        if len(df) >= 3:
            recent_scores = df.tail(3)['score']
            recent_stances = [self.classify_stance(s)['classification'] for s in recent_scores]
            consistency = len([s for s in recent_stances if s == latest_stance['classification']]) / len(recent_stances)
        else:
            consistency = 1.0
        
        # Confidence based on consistency
        if consistency >= 0.9:
            confidence = "very_high"
        elif consistency >= 0.75:
            confidence = "high"
        elif consistency >= 0.5:
            confidence = "moderate"
        else:
            confidence = "low"
        
        return {
            'classification': latest_stance['classification'],
            'score': latest_score,
            'description': latest_stance['description'],
            'confidence': confidence,
            'consistency': round(consistency, 2),
            'recent_meetings': len(df.tail(3))
        }


def analyze_sentiment_evolution(meeting_data: List[Dict]) -> Dict:
    """
    Convenience function for complete sentiment evolution analysis.
    
    Args:
        meeting_data: List of meeting sentiment data
    
    Returns:
        Complete sentiment analysis
    """
    tracker = SentimentTracker()
    
    # Create time series
    df = tracker.create_sentiment_timeseries(meeting_data)
    
    if df.empty:
        return {'error': 'No data'}
    
    # Perform analyses
    current_stance = tracker.get_current_stance(df)
    trend = tracker.detect_trend(df)
    shifts = tracker.detect_shifts(df)
    volatility = tracker.calculate_volatility(df)
    
    return {
        'current_stance': current_stance,
        'trend': trend,
        'significant_shifts': shifts,
        'volatility': volatility,
        'num_meetings': len(df),
        'date_range': {
            'start': df.iloc[0]['date'].strftime('%Y-%m-%d') if 'date' in df.columns and not df.empty else None,
            'end': df.iloc[-1]['date'].strftime('%Y-%m-%d') if 'date' in df.columns and not df.empty else None
        }
    }
