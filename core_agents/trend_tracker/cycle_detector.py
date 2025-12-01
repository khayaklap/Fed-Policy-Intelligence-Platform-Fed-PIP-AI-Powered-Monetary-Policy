"""
Cycle Detector

Identifies Fed policy cycles, phases, and compares current cycle to historical cycles.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from scipy import signal
from collections import Counter

try:
    # Try relative imports first (when used as module)
    from .trend_tracker_config import (
        POLICY_CYCLE_PHASES,
        HISTORICAL_CYCLES,
        AVERAGE_CYCLE_METRICS,
        PEAK_TROUGH_CONFIG,
        CYCLE_SIMILARITY_WEIGHTS
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from trend_tracker_config import (
        POLICY_CYCLE_PHASES,
        HISTORICAL_CYCLES,
        AVERAGE_CYCLE_METRICS,
        PEAK_TROUGH_CONFIG,
        CYCLE_SIMILARITY_WEIGHTS
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CycleDetector:
    """
    Detect and analyze Fed policy cycles.
    """
    
    def __init__(self):
        """Initialize cycle detector."""
        logger.info("Initialized Cycle Detector")
    
    def identify_cycle_phase(
        self,
        recent_data: List[Dict],
        lookback: int = 12
    ) -> Dict:
        """
        Identify current phase of policy cycle.
        
        Args:
            recent_data: Recent meeting data
            lookback: Meetings to consider
        
        Returns:
            Dictionary with cycle phase classification
        """
        logger.info("Identifying cycle phase")
        
        if len(recent_data) < 6:
            return {'error': 'Need at least 6 meetings'}
        
        recent = recent_data[-lookback:]
        
        # Extract key indicators
        actions = [m.get('action') for m in recent if m.get('action')]
        sentiments = [m.get('sentiment') for m in recent if m.get('sentiment')]
        
        # Counters
        action_counts = Counter(actions)
        sentiment_counts = Counter(sentiments)
        
        # Determine phase
        phase = self._classify_phase(action_counts, sentiment_counts, recent)
        
        # Find duration of current phase
        duration = self._calculate_phase_duration(recent_data, phase)
        
        # Expected next phase
        next_phase = self._predict_next_phase(phase, duration)
        
        return {
            'current_phase': phase,
            'duration': duration,
            'description': POLICY_CYCLE_PHASES.get(phase, {}).get('description', 'Unknown phase'),
            'expected_next_phase': next_phase,
            'confidence': self._assess_phase_confidence(action_counts, sentiment_counts)
        }
    
    def _classify_phase(
        self,
        action_counts: Counter,
        sentiment_counts: Counter,
        recent_data: List[Dict]
    ) -> str:
        """
        Classify which phase of the cycle we're in.
        
        Uses actions, sentiment, and economic context.
        """
        total_actions = sum(action_counts.values())
        
        # Check for recession phase (emergency actions)
        if action_counts.get('decrease', 0) >= total_actions * 0.5:
            # Many rate cuts
            if sentiment_counts.get('highly_dovish', 0) > 0 or sentiment_counts.get('dovish', 0) >= len(recent_data) * 0.6:
                return "recession"
            else:
                return "slowdown"
        
        # Check for tightening phases
        elif action_counts.get('increase', 0) >= total_actions * 0.5:
            # Many rate hikes
            if sentiment_counts.get('highly_hawkish', 0) >= 2:
                return "expansion_late"
            else:
                return "expansion_mid"
        
        # Check for stable/early expansion
        else:
            # Mostly unchanged
            if sentiment_counts.get('dovish', 0) >= len(recent_data) * 0.4:
                return "expansion_early"
            elif sentiment_counts.get('hawkish', 0) >= len(recent_data) * 0.4:
                return "expansion_late"
            else:
                return "expansion_mid"
    
    def _calculate_phase_duration(
        self,
        all_data: List[Dict],
        current_phase: str
    ) -> int:
        """Calculate how long we've been in current phase."""
        
        # Look backwards to find when phase started
        duration = 0
        lookback_window = 6
        
        for i in range(len(all_data) - 1, max(0, len(all_data) - 24), -1):
            window_start = max(0, i - lookback_window)
            window = all_data[window_start:i+1]
            
            actions = [m.get('action') for m in window if m.get('action')]
            sentiments = [m.get('sentiment') for m in window if m.get('sentiment')]
            
            phase = self._classify_phase(Counter(actions), Counter(sentiments), window)
            
            if phase == current_phase:
                duration += 1
            else:
                break
        
        return duration
    
    def _predict_next_phase(self, current_phase: str, duration: int) -> str:
        """Predict next likely phase based on current phase and duration."""
        
        # Typical phase transitions
        transitions = {
            "recession": "expansion_early",
            "expansion_early": "expansion_mid",
            "expansion_mid": "expansion_late",
            "expansion_late": "slowdown",
            "slowdown": "recession"  # or back to expansion_early
        }
        
        # If phase has lasted long time, transition more likely
        typical_duration = 8  # ~2 years
        
        if duration >= typical_duration * 1.5:
            return transitions.get(current_phase, "unknown")
        else:
            return current_phase  # Likely to continue
    
    def _assess_phase_confidence(
        self,
        action_counts: Counter,
        sentiment_counts: Counter
    ) -> str:
        """Assess confidence in phase classification."""
        
        total_actions = sum(action_counts.values())
        
        # Check if one action dominates
        if total_actions > 0:
            max_action = max(action_counts.values())
            action_dominance = max_action / total_actions
        else:
            action_dominance = 0
        
        # Check if one sentiment dominates
        total_sentiment = sum(sentiment_counts.values())
        if total_sentiment > 0:
            max_sentiment = max(sentiment_counts.values())
            sentiment_dominance = max_sentiment / total_sentiment
        else:
            sentiment_dominance = 0
        
        avg_dominance = (action_dominance + sentiment_dominance) / 2
        
        if avg_dominance >= 0.75:
            return "high"
        elif avg_dominance >= 0.5:
            return "moderate"
        else:
            return "low"
    
    def detect_peaks_and_troughs(
        self,
        meeting_data: List[Dict],
        variable: str = 'fed_funds'
    ) -> Dict:
        """
        Detect peaks (rate tops) and troughs (rate bottoms).
        
        Args:
            meeting_data: List of meeting data
            variable: Variable to analyze (fed_funds, score, etc.)
        
        Returns:
            Dictionary with peaks and troughs
        """
        logger.info(f"Detecting peaks and troughs in {variable}")
        
        df = pd.DataFrame(meeting_data)
        
        if variable not in df.columns:
            return {'error': f'Variable {variable} not found'}
        
        values = df[variable].values
        
        # Find peaks
        peaks, peak_props = signal.find_peaks(
            values,
            prominence=PEAK_TROUGH_CONFIG['prominence'],
            distance=PEAK_TROUGH_CONFIG['distance'],
            width=PEAK_TROUGH_CONFIG['width']
        )
        
        # Find troughs (peaks in inverted signal)
        troughs, trough_props = signal.find_peaks(
            -values,
            prominence=PEAK_TROUGH_CONFIG['prominence'],
            distance=PEAK_TROUGH_CONFIG['distance'],
            width=PEAK_TROUGH_CONFIG['width']
        )
        
        # Build results
        peak_list = []
        for idx in peaks:
            if idx < len(df):
                peak_list.append({
                    'index': int(idx),
                    'date': df.iloc[idx]['date'] if 'date' in df.columns else idx,
                    'value': round(float(values[idx]), 2),
                    'type': 'peak'
                })
        
        trough_list = []
        for idx in troughs:
            if idx < len(df):
                trough_list.append({
                    'index': int(idx),
                    'date': df.iloc[idx]['date'] if 'date' in df.columns else idx,
                    'value': round(float(values[idx]), 2),
                    'type': 'trough'
                })
        
        return {
            'peaks': peak_list,
            'troughs': trough_list,
            'num_peaks': len(peak_list),
            'num_troughs': len(trough_list),
            'interpretation': self._interpret_peaks_troughs(peak_list, trough_list)
        }
    
    def _interpret_peaks_troughs(self, peaks: List, troughs: List) -> str:
        """Interpret peaks and troughs."""
        
        if not peaks and not troughs:
            return "No clear peaks or troughs detected - may be in transition"
        
        # Get most recent peak/trough
        all_points = sorted(
            peaks + troughs,
            key=lambda x: x['index']
        )
        
        if not all_points:
            return "No turning points detected"
        
        latest = all_points[-1]
        
        if latest['type'] == 'peak':
            return f"Most recent peak at {latest['value']} - rates may be declining from here"
        else:
            return f"Most recent trough at {latest['value']} - rates may be rising from here"
    
    def calculate_cycle_metrics(
        self,
        meeting_data: List[Dict],
        peaks: List[Dict],
        troughs: List[Dict]
    ) -> Dict:
        """
        Calculate cycle metrics (duration, amplitude, etc.).
        
        Args:
            meeting_data: Full meeting data
            peaks: Detected peaks
            troughs: Detected troughs
        
        Returns:
            Dictionary with cycle metrics
        """
        logger.info("Calculating cycle metrics")
        
        if not peaks or not troughs:
            return {'error': 'Need both peaks and troughs'}
        
        # Sort by index
        peaks_sorted = sorted(peaks, key=lambda x: x['index'])
        troughs_sorted = sorted(troughs, key=lambda x: x['index'])
        
        # Calculate peak-to-peak duration
        if len(peaks_sorted) >= 2:
            peak_to_peak = peaks_sorted[-1]['index'] - peaks_sorted[-2]['index']
        else:
            peak_to_peak = None
        
        # Calculate amplitude (peak to trough)
        if peaks_sorted and troughs_sorted:
            latest_peak = peaks_sorted[-1]['value']
            latest_trough = troughs_sorted[-1]['value']
            amplitude = abs(latest_peak - latest_trough)
        else:
            amplitude = None
        
        # Compare to average cycle
        comparison = self._compare_to_average_cycle(peak_to_peak, amplitude)
        
        return {
            'peak_to_peak_duration': peak_to_peak,
            'amplitude': round(amplitude, 2) if amplitude else None,
            'comparison_to_average': comparison,
            'interpretation': self._interpret_cycle_metrics(peak_to_peak, amplitude)
        }
    
    def _compare_to_average_cycle(
        self,
        duration: Optional[int],
        amplitude: Optional[float]
    ) -> Dict:
        """Compare current cycle to historical averages."""
        
        avg_duration = AVERAGE_CYCLE_METRICS['total_duration']
        avg_amplitude = AVERAGE_CYCLE_METRICS['rate_change_per_cycle'] / 100  # Convert bp to %
        
        comparison = {}
        
        if duration is not None:
            if duration > avg_duration * 1.2:
                comparison['duration'] = "longer_than_average"
            elif duration < avg_duration * 0.8:
                comparison['duration'] = "shorter_than_average"
            else:
                comparison['duration'] = "typical"
        
        if amplitude is not None:
            if amplitude > avg_amplitude * 1.2:
                comparison['amplitude'] = "larger_than_average"
            elif amplitude < avg_amplitude * 0.8:
                comparison['amplitude'] = "smaller_than_average"
            else:
                comparison['amplitude'] = "typical"
        
        return comparison
    
    def _interpret_cycle_metrics(
        self,
        duration: Optional[int],
        amplitude: Optional[float]
    ) -> str:
        """Interpret cycle metrics."""
        
        if duration is None and amplitude is None:
            return "Insufficient cycle data"
        
        parts = []
        
        if duration is not None:
            parts.append(f"Cycle duration: {duration} meetings")
        
        if amplitude is not None:
            parts.append(f"Rate change amplitude: {amplitude:.1%}")
        
        return ", ".join(parts)
    
    def compare_to_historical_cycle(
        self,
        current_data: List[Dict],
        historical_cycle: str
    ) -> Dict:
        """
        Compare current cycle to a historical cycle.
        
        Args:
            current_data: Current meeting data
            historical_cycle: Key from HISTORICAL_CYCLES
        
        Returns:
            Dictionary with comparison
        """
        logger.info(f"Comparing to {historical_cycle}")
        
        if historical_cycle not in HISTORICAL_CYCLES:
            return {'error': f'Unknown historical cycle: {historical_cycle}'}
        
        hist_cycle = HISTORICAL_CYCLES[historical_cycle]
        
        # Extract current cycle characteristics
        current_actions = [m.get('action') for m in current_data if m.get('action')]
        current_sentiments = [m.get('sentiment') for m in current_data if m.get('sentiment')]
        
        # Calculate similarity
        similarity_scores = {}
        
        # Duration similarity
        current_duration = len(current_data)
        # Note: Would need to parse hist_cycle['period'] to get exact duration
        # For now, use rough estimate
        similarity_scores['duration'] = 0.7  # Placeholder
        
        # Characteristics similarity
        hist_chars = set(hist_cycle.get('characteristics', []))
        current_chars = set(current_actions + current_sentiments)
        
        if hist_chars:
            overlap = len(hist_chars & current_chars) / len(hist_chars)
            similarity_scores['characteristics'] = overlap
        else:
            similarity_scores['characteristics'] = 0
        
        # Overall similarity
        overall_similarity = np.mean(list(similarity_scores.values()))
        
        return {
            'historical_cycle': historical_cycle,
            'description': hist_cycle['description'],
            'similarity_score': round(float(overall_similarity), 2),
            'similarity_breakdown': similarity_scores,
            'interpretation': self._interpret_cycle_comparison(
                historical_cycle,
                overall_similarity
            )
        }
    
    def _interpret_cycle_comparison(
        self,
        cycle_name: str,
        similarity: float
    ) -> str:
        """Interpret comparison to historical cycle."""
        
        if similarity >= 0.7:
            return f"Very similar to {cycle_name} (similarity: {similarity:.0%})"
        elif similarity >= 0.5:
            return f"Somewhat similar to {cycle_name} (similarity: {similarity:.0%})"
        else:
            return f"Quite different from {cycle_name} (similarity: {similarity:.0%})"


def detect_policy_cycles(meeting_data: List[Dict]) -> Dict:
    """
    Convenience function for complete cycle analysis.
    
    Args:
        meeting_data: List of meeting data
    
    Returns:
        Complete cycle analysis
    """
    detector = CycleDetector()
    
    # Identify current phase
    current_phase = detector.identify_cycle_phase(meeting_data)
    
    # Detect peaks and troughs
    if any('fed_funds' in m for m in meeting_data):
        peaks_troughs = detector.detect_peaks_and_troughs(meeting_data, 'fed_funds')
        
        # Calculate cycle metrics
        if peaks_troughs.get('peaks') and peaks_troughs.get('troughs'):
            cycle_metrics = detector.calculate_cycle_metrics(
                meeting_data,
                peaks_troughs['peaks'],
                peaks_troughs['troughs']
            )
        else:
            cycle_metrics = None
    else:
        peaks_troughs = None
        cycle_metrics = None
    
    # Compare to most relevant historical cycle
    # Pick based on current phase
    if current_phase.get('current_phase') in ['recession', 'expansion_early']:
        historical_comparison = detector.compare_to_historical_cycle(
            meeting_data[-24:] if len(meeting_data) >= 24 else meeting_data,
            'covid_inflation'  # Most recent similar episode
        )
    else:
        historical_comparison = detector.compare_to_historical_cycle(
            meeting_data[-24:] if len(meeting_data) >= 24 else meeting_data,
            'post_gfc_normalization'
        )
    
    return {
        'current_phase': current_phase,
        'peaks_and_troughs': peaks_troughs,
        'cycle_metrics': cycle_metrics,
        'historical_comparison': historical_comparison
    }
