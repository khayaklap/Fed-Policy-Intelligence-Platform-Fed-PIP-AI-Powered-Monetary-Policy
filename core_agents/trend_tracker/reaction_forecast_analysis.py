"""
Reaction Function & Forecast Bias Analysis

Analyzes how Fed responds to economic data and tracks systematic forecast errors.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats
from sklearn.linear_model import LinearRegression

try:
    # Try relative imports first (when used as module)
    from .trend_tracker_config import (
        TAYLOR_RULE_PARAMS,
        REACTION_VARIABLES,
        ASYMMETRY_PATTERNS,
        FORECAST_BIAS_TYPES,
        FORECAST_ERROR_THRESHOLDS,
        BIAS_DETECTION_CONFIG
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from trend_tracker_config import (
        TAYLOR_RULE_PARAMS,
        REACTION_VARIABLES,
        ASYMMETRY_PATTERNS,
        FORECAST_BIAS_TYPES,
        FORECAST_ERROR_THRESHOLDS,
        BIAS_DETECTION_CONFIG
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReactionFunctionAnalyzer:
    """
    Analyze Fed's reaction function - how Fed responds to economic data.
    """
    
    def __init__(self):
        """Initialize reaction function analyzer."""
        logger.info("Initialized Reaction Function Analyzer")
    
    def estimate_taylor_rule(
        self,
        meeting_data: List[Dict],
        economic_data: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Estimate Fed's Taylor Rule parameters.
        
        Taylor Rule: r = r* + α(π - π*) + β(y - y*)
        Where:
        - r = Fed Funds rate
        - r* = neutral rate
        - π = inflation
        - π* = inflation target
        - y = output gap (or unemployment gap)
        - α = inflation coefficient (typically 1.5)
        - β = output coefficient (typically 0.5)
        
        Args:
            meeting_data: Meeting data with fed_funds
            economic_data: Economic data with inflation, unemployment
        
        Returns:
            Estimated Taylor Rule parameters
        """
        logger.info("Estimating Taylor Rule")
        
        if not economic_data or len(economic_data) < 12:
            return {'error': 'Need economic data to estimate Taylor Rule'}
        
        df = pd.DataFrame(economic_data)
        
        # Required variables
        required = ['fed_funds', 'inflation', 'unemployment']
        if not all(var in df.columns for var in required):
            return {'error': f'Need {required} in economic data'}
        
        # Calculate gaps
        df['inflation_gap'] = df['inflation'] - TAYLOR_RULE_PARAMS['inflation_target']
        
        # Unemployment gap (actual - natural rate, sign reversed)
        # Lower unemployment → positive gap → higher rates
        natural_unemployment = 4.0  # Rough estimate
        df['unemployment_gap'] = -(df['unemployment'] - natural_unemployment)
        
        # Fit regression: fed_funds ~ inflation_gap + unemployment_gap
        X = df[['inflation_gap', 'unemployment_gap']].values
        y = df['fed_funds'].values
        
        model = LinearRegression(fit_intercept=True)
        model.fit(X, y)
        
        inflation_coef = model.coef_[0]
        unemployment_coef = model.coef_[1]
        intercept = model.intercept_
        
        # Predict and calculate R²
        y_pred = model.predict(X)
        r_squared = model.score(X, y)
        
        # Compare to Taylor's original parameters
        taylor_original = TAYLOR_RULE_PARAMS
        
        return {
            'estimated_coefficients': {
                'inflation': round(float(inflation_coef), 2),
                'unemployment': round(float(unemployment_coef), 2),
                'intercept': round(float(intercept), 2)
            },
            'taylor_original': {
                'inflation': taylor_original['inflation_coefficient'],
                'output': taylor_original['output_coefficient']
            },
            'r_squared': round(float(r_squared), 3),
            'interpretation': self._interpret_taylor_rule(
                inflation_coef,
                unemployment_coef,
                r_squared
            )
        }
    
    def _interpret_taylor_rule(
        self,
        inflation_coef: float,
        unemployment_coef: float,
        r_squared: float
    ) -> str:
        """Interpret Taylor Rule estimation."""
        
        if r_squared < 0.3:
            return f"Poor fit (R²={r_squared:.2f}) - Fed not following simple Taylor Rule"
        
        # Compare to original Taylor coefficients
        if inflation_coef > 2.0:
            inflation_stance = "very aggressive on inflation"
        elif inflation_coef > 1.5:
            inflation_stance = "Taylor-like on inflation"
        else:
            inflation_stance = "less aggressive on inflation"
        
        if abs(unemployment_coef) > 0.7:
            unemployment_stance = "strongly responsive to employment"
        elif abs(unemployment_coef) > 0.3:
            unemployment_stance = "moderately responsive to employment"
        else:
            unemployment_stance = "weakly responsive to employment"
        
        return (
            f"Fed {inflation_stance} (coef={inflation_coef:.1f}) and "
            f"{unemployment_stance} (coef={abs(unemployment_coef):.1f}), "
            f"R²={r_squared:.2f}"
        )
    
    def detect_asymmetry(
        self,
        meeting_data: List[Dict]
    ) -> Dict:
        """
        Detect asymmetry in Fed response (cuts faster than hikes).
        
        Args:
            meeting_data: Meeting data with actions
        
        Returns:
            Asymmetry analysis
        """
        logger.info("Detecting reaction asymmetry")
        
        df = pd.DataFrame(meeting_data)
        
        if 'action' not in df.columns:
            return {'error': 'Need action data'}
        
        # Separate increases and decreases
        increases = df[df['action'] == 'increase']
        decreases = df[df['action'] == 'decrease']
        
        if increases.empty or decreases.empty:
            return {'asymmetry': 'unknown', 'interpretation': 'Need both hikes and cuts'}
        
        # Calculate average change per move (if magnitude available)
        if 'change_amount' in df.columns:
            avg_increase = increases['change_amount'].mean()
            avg_decrease = decreases['change_amount'].mean()
            
            if avg_decrease > avg_increase * 1.5:
                asymmetry = "cuts_faster"
            elif avg_increase > avg_decrease * 1.5:
                asymmetry = "hikes_faster"
            else:
                asymmetry = "symmetric"
        else:
            # Just count frequency
            increase_freq = len(increases)
            decrease_freq = len(decreases)
            
            if decrease_freq > increase_freq:
                asymmetry = "cuts_more_frequent"
            elif increase_freq > decrease_freq:
                asymmetry = "hikes_more_frequent"
            else:
                asymmetry = "symmetric"
        
        return {
            'asymmetry': asymmetry,
            'num_increases': len(increases),
            'num_decreases': len(decreases),
            'interpretation': self._interpret_asymmetry(asymmetry)
        }
    
    def _interpret_asymmetry(self, asymmetry: str) -> str:
        """Interpret asymmetry pattern."""
        
        patterns = {
            'cuts_faster': "Fed cuts rates faster/larger than it hikes (typical pattern)",
            'hikes_faster': "Fed hiking faster than usual (unusual - suggests urgency)",
            'symmetric': "Fed adjusts rates symmetrically in both directions",
            'cuts_more_frequent': "Fed cuts more often than it hikes",
            'hikes_more_frequent': "Fed hiking frequently (extended tightening cycle)"
        }
        
        return patterns.get(asymmetry, "Unknown pattern")


class ForecastBiasTracker:
    """
    Track systematic errors in Fed forecasts.
    """
    
    def __init__(self):
        """Initialize forecast bias tracker."""
        logger.info("Initialized Forecast Bias Tracker")
    
    def analyze_forecast_bias(
        self,
        forecasts: List[Dict],
        actuals: List[Dict],
        variable: str = 'pce_inflation'
    ) -> Dict:
        """
        Analyze systematic bias in Fed forecasts.
        
        Args:
            forecasts: List of forecast values
            actuals: List of actual outcomes
            variable: Variable to analyze
        
        Returns:
            Bias analysis
        """
        logger.info(f"Analyzing forecast bias for {variable}")
        
        if len(forecasts) < BIAS_DETECTION_CONFIG['min_observations']:
            return {
                'error': f"Need {BIAS_DETECTION_CONFIG['min_observations']} observations"
            }
        
        # Match forecasts to actuals
        errors = []
        for f, a in zip(forecasts, actuals):
            if 'value' in f and 'value' in a:
                error = a['value'] - f['value']  # Actual - Forecast
                errors.append(error)
        
        if not errors:
            return {'error': 'No matching forecast-actual pairs'}
        
        errors = np.array(errors)
        
        # Calculate statistics
        mean_error = np.mean(errors)
        std_error = np.std(errors)
        
        # Test for systematic bias
        t_stat, p_value = stats.ttest_1samp(errors, 0)
        has_bias = p_value < BIAS_DETECTION_CONFIG['significance_level']
        
        # Classify bias type
        if abs(mean_error) < BIAS_DETECTION_CONFIG['bias_threshold']:
            bias_type = "no_systematic_bias"
        elif mean_error < 0:
            bias_type = "overestimation_bias"  # Forecasts too high
        else:
            bias_type = "underestimation_bias"  # Forecasts too low
        
        # Calculate accuracy metrics
        mae = np.mean(np.abs(errors))  # Mean absolute error
        rmse = np.sqrt(np.mean(errors ** 2))  # Root mean squared error
        
        return {
            'variable': variable,
            'num_observations': len(errors),
            'mean_error': round(float(mean_error), 2),
            'std_error': round(float(std_error), 2),
            'mae': round(float(mae), 2),
            'rmse': round(float(rmse), 2),
            'has_systematic_bias': has_bias,
            'bias_type': bias_type,
            'p_value': round(float(p_value), 4),
            'interpretation': self._interpret_bias(bias_type, mean_error, has_bias)
        }
    
    def _interpret_bias(
        self,
        bias_type: str,
        mean_error: float,
        has_bias: bool
    ) -> str:
        """Interpret forecast bias."""
        
        if not has_bias:
            return "No statistically significant systematic bias detected"
        
        if bias_type == "underestimation_bias":
            return (
                f"Fed systematically underestimates (forecasts too low by "
                f"{abs(mean_error):.2f}pp on average) - statistically significant"
            )
        elif bias_type == "overestimation_bias":
            return (
                f"Fed systematically overestimates (forecasts too high by "
                f"{abs(mean_error):.2f}pp on average) - statistically significant"
            )
        else:
            return "Forecasts appear unbiased"
    
    def identify_bias_patterns(
        self,
        forecast_errors: List[float],
        timestamps: List
    ) -> Dict:
        """
        Identify patterns in forecast errors over time.
        
        Args:
            forecast_errors: List of forecast errors
            timestamps: List of corresponding dates/times
        
        Returns:
            Pattern analysis
        """
        logger.info("Identifying bias patterns")
        
        if len(forecast_errors) < 8:
            return {'error': 'Need at least 8 observations'}
        
        errors = np.array(forecast_errors)
        
        # Check for time trend in errors
        X = np.arange(len(errors)).reshape(-1, 1)
        y = errors
        
        model = LinearRegression()
        model.fit(X, y)
        
        slope = model.coef_[0]
        r_squared = model.score(X, y)
        
        # Classify pattern
        if abs(slope) > 0.1 and r_squared > 0.3:
            if slope > 0:
                pattern = "deteriorating"  # Errors getting larger (worse)
            else:
                pattern = "improving"  # Errors getting smaller (better)
        else:
            pattern = "stable"
        
        # Check for recent vs historical bias
        mid_point = len(errors) // 2
        recent_mean = np.mean(errors[mid_point:])
        historical_mean = np.mean(errors[:mid_point])
        
        if abs(recent_mean - historical_mean) > 0.5:
            recent_vs_historical = "shift_detected"
        else:
            recent_vs_historical = "consistent"
        
        return {
            'pattern': pattern,
            'trend_slope': round(float(slope), 3),
            'r_squared': round(float(r_squared), 3),
            'recent_vs_historical': recent_vs_historical,
            'recent_mean_error': round(float(recent_mean), 2),
            'historical_mean_error': round(float(historical_mean), 2),
            'interpretation': self._interpret_pattern(pattern, slope)
        }
    
    def _interpret_pattern(self, pattern: str, slope: float) -> str:
        """Interpret bias pattern."""
        
        if pattern == "deteriorating":
            return f"Forecast accuracy deteriorating over time (slope={slope:.3f})"
        elif pattern == "improving":
            return f"Forecast accuracy improving over time (slope={slope:.3f})"
        else:
            return "Forecast bias stable over time"


def analyze_reaction_and_bias(
    meeting_data: List[Dict],
    economic_data: Optional[List[Dict]] = None,
    forecast_data: Optional[Dict] = None
) -> Dict:
    """
    Convenience function for reaction function and bias analysis.
    
    Args:
        meeting_data: Meeting data
        economic_data: Economic conditions
        forecast_data: Forecast vs actual data
    
    Returns:
        Complete analysis
    """
    reaction_analyzer = ReactionFunctionAnalyzer()
    bias_tracker = ForecastBiasTracker()
    
    results = {}
    
    # Taylor Rule estimation
    if economic_data:
        results['taylor_rule'] = reaction_analyzer.estimate_taylor_rule(
            meeting_data,
            economic_data
        )
    
    # Asymmetry detection
    results['asymmetry'] = reaction_analyzer.detect_asymmetry(meeting_data)
    
    # Forecast bias
    if forecast_data:
        if 'forecasts' in forecast_data and 'actuals' in forecast_data:
            results['forecast_bias'] = bias_tracker.analyze_forecast_bias(
                forecast_data['forecasts'],
                forecast_data['actuals'],
                forecast_data.get('variable', 'pce_inflation')
            )
    
    return results
