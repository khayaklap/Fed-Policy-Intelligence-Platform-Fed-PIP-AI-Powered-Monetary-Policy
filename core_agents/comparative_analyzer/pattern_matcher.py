"""
Pattern Matcher

Identifies recurring patterns in Fed policy episodes and matches current
policy to historical patterns.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    from fastdtw import fastdtw
    DTW_AVAILABLE = True
except ImportError:
    DTW_AVAILABLE = False
    logging.warning("fastdtw not installed - DTW pattern matching limited")

try:
    # Try relative imports first (when used as module)
    from .comparative_analyzer_config import (
        POLICY_EPISODES,
        PATTERN_TYPES,
        FED_CHAIRS
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from comparative_analyzer_config import (
        POLICY_EPISODES,
        PATTERN_TYPES,
        FED_CHAIRS
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PatternMatcher:
    """
    Identify and match Fed policy patterns.
    """
    
    def __init__(self):
        """Initialize pattern matcher."""
        logger.info("Initialized Pattern Matcher")
    
    def identify_pattern(
        self,
        meeting_data: List[Dict],
        min_meetings: int = 6
    ) -> Dict:
        """
        Identify which known pattern current episode matches.
        
        Args:
            meeting_data: Recent meeting data
            min_meetings: Minimum meetings to analyze
        
        Returns:
            Dictionary with pattern identification
        """
        logger.info(f"Identifying pattern in {len(meeting_data)} meetings")
        
        if len(meeting_data) < min_meetings:
            return {'error': f'Need at least {min_meetings} meetings'}
        
        # Extract key features
        features = self._extract_features(meeting_data)
        
        # Match against known patterns
        pattern_scores = {}
        for pattern_name, pattern_config in PATTERN_TYPES.items():
            score = self._match_pattern(features, pattern_name, pattern_config)
            pattern_scores[pattern_name] = score
        
        # Best match
        best_pattern = max(pattern_scores.items(), key=lambda x: x[1])
        
        # All matches above threshold
        matches = [
            {
                'pattern': name,
                'score': score,
                'description': PATTERN_TYPES[name]['description'],
                'examples': PATTERN_TYPES[name]['examples']
            }
            for name, score in pattern_scores.items()
            if score >= 0.5
        ]
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'best_match': {
                'pattern': best_pattern[0],
                'score': round(best_pattern[1], 3),
                'description': PATTERN_TYPES[best_pattern[0]]['description'],
                'confidence': 'high' if best_pattern[1] >= 0.75 else 'moderate' if best_pattern[1] >= 0.5 else 'low'
            },
            'all_matches': matches,
            'features': features,
            'interpretation': self._interpret_pattern(best_pattern[0], best_pattern[1], features)
        }
    
    def _extract_features(self, meeting_data: List[Dict]) -> Dict:
        """Extract pattern features from meeting data."""
        
        actions = [m.get('action') for m in meeting_data if m.get('action')]
        scores = [m.get('score', 0) for m in meeting_data]
        
        # Calculate features
        features = {
            'num_increases': actions.count('increase'),
            'num_decreases': actions.count('decrease'),
            'num_unchanged': actions.count('unchanged'),
            'net_action': actions.count('increase') - actions.count('decrease'),
            'volatility': np.std(scores) if scores else 0,
            'trend': np.polyfit(range(len(scores)), scores, 1)[0] if len(scores) > 1 else 0,
            'duration': len(meeting_data)
        }
        
        # Detect reversals
        if len(actions) >= 3:
            # Check for pivot (direction change)
            first_half = actions[:len(actions)//2]
            second_half = actions[len(actions)//2:]
            
            first_bias = first_half.count('increase') - first_half.count('decrease')
            second_bias = second_half.count('increase') - second_half.count('decrease')
            
            features['has_pivot'] = (first_bias > 0 and second_bias < 0) or (first_bias < 0 and second_bias > 0)
        else:
            features['has_pivot'] = False
        
        return features
    
    def _match_pattern(
        self,
        features: Dict,
        pattern_name: str,
        pattern_config: Dict
    ) -> float:
        """
        Match features against a pattern.
        
        Returns score 0-1 (1 = perfect match).
        """
        score = 0.0
        checks = 0
        
        # V-shaped response
        if pattern_name == 'v_shaped_response':
            if features['has_pivot']:
                score += 0.5
            if features['volatility'] > 8:
                score += 0.3
            if abs(features['net_action']) < 2:  # Balanced
                score += 0.2
            checks = 1
        
        # Gradual tightening
        elif pattern_name == 'gradual_tightening':
            if features['num_increases'] > features['num_decreases']:
                score += 0.4
            if features['volatility'] < 5:  # Stable
                score += 0.3
            if features['trend'] > 0.5:  # Hawkish trend
                score += 0.3
            checks = 1
        
        # Emergency easing
        elif pattern_name == 'emergency_easing':
            if features['num_decreases'] > features['num_increases']:
                score += 0.4
            if features['num_decreases'] >= 3:
                score += 0.3
            if features['trend'] < -1:  # Strong dovish
                score += 0.3
            checks = 1
        
        # Extended pause
        elif pattern_name == 'extended_pause':
            if features['num_unchanged'] >= features['duration'] * 0.75:
                score += 0.5
            if features['volatility'] < 3:
                score += 0.3
            if features['duration'] >= 12:
                score += 0.2
            checks = 1
        
        # Pivot
        elif pattern_name == 'pivot':
            if features['has_pivot']:
                score += 0.6
            if features['volatility'] > 5:
                score += 0.2
            if features['duration'] <= 8:  # Quick
                score += 0.2
            checks = 1
        
        # Overshooting
        elif pattern_name == 'overshooting':
            if features['has_pivot']:
                score += 0.4
            if features['num_increases'] >= 5:  # Extended tightening
                score += 0.3
            if features['num_decreases'] >= 2:  # Then reversal
                score += 0.3
            checks = 1
        
        return score if checks > 0 else 0.5
    
    def _interpret_pattern(self, pattern_name: str, score: float, features: Dict) -> str:
        """Generate interpretation of pattern match."""
        
        pattern = PATTERN_TYPES[pattern_name]
        
        confidence = 'high' if score >= 0.75 else 'moderate' if score >= 0.5 else 'low'
        
        interp = f"Current episode shows {pattern_name.replace('_', ' ')} pattern with {confidence} confidence. "
        interp += f"{pattern['description']}. "
        
        if pattern['examples']:
            interp += f"Similar to: {', '.join(pattern['examples'])}."
        
        return interp
    
    def compare_episode_patterns(
        self,
        episode1_data: List[Dict],
        episode2_data: List[Dict]
    ) -> Dict:
        """
        Compare patterns between two episodes using time series similarity.
        
        Args:
            episode1_data: Meeting data for first episode
            episode2_data: Meeting data for second episode
        
        Returns:
            Pattern similarity analysis
        """
        logger.info("Comparing episode patterns")
        
        # Extract time series
        ts1 = [m.get('score', 0) for m in episode1_data]
        ts2 = [m.get('score', 0) for m in episode2_data]
        
        if not ts1 or not ts2:
            return {'error': 'Insufficient data'}
        
        # Calculate similarities using different methods
        similarities = {}
        
        # Correlation (if same length)
        if len(ts1) == len(ts2):
            correlation = np.corrcoef(ts1, ts2)[0, 1]
            similarities['correlation'] = round(float(correlation), 3)
        
        # Euclidean distance (normalized)
        if len(ts1) == len(ts2):
            euclidean = np.linalg.norm(np.array(ts1) - np.array(ts2))
            # Normalize by length
            euclidean_norm = euclidean / np.sqrt(len(ts1))
            similarities['euclidean'] = round(float(euclidean_norm), 3)
        
        # DTW (works with different lengths)
        if DTW_AVAILABLE:
            try:
                dtw_dist, _ = fastdtw(ts1, ts2)
                # Normalize by average length
                dtw_norm = dtw_dist / ((len(ts1) + len(ts2)) / 2)
                similarities['dtw'] = round(float(dtw_norm), 3)
            except Exception as e:
                logger.warning(f"DTW failed: {e}")
        
        # Overall similarity (average of methods)
        if similarities:
            # Convert distances to similarities (1 - normalized distance)
            similarity_scores = []
            for method, value in similarities.items():
                if method == 'correlation':
                    # Correlation is already a similarity
                    similarity_scores.append(max(0, value))
                else:
                    # Distance metrics - convert to similarity
                    similarity_scores.append(max(0, 1 - value))
            
            overall_similarity = np.mean(similarity_scores)
        else:
            overall_similarity = 0.5
        
        return {
            'overall_similarity': round(overall_similarity, 3),
            'method_scores': similarities,
            'interpretation': self._interpret_episode_similarity(overall_similarity)
        }
    
    def _interpret_episode_similarity(self, similarity: float) -> str:
        """Interpret episode similarity score."""
        
        if similarity >= 0.85:
            return "Episodes follow very similar patterns"
        elif similarity >= 0.70:
            return "Episodes show significant pattern similarity"
        elif similarity >= 0.50:
            return "Episodes have some pattern similarities"
        else:
            return "Episodes follow different patterns"
    
    def find_similar_episodes(
        self,
        current_data: List[Dict],
        historical_episodes: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Find historical episodes with similar patterns to current.
        
        Args:
            current_data: Current meeting data
            historical_episodes: Dict of {name: meeting_data} or None for all
        
        Returns:
            Ranked list of similar episodes
        """
        logger.info("Finding similar historical episodes")
        
        if historical_episodes is None:
            # Use defined episodes (would need actual data)
            return [{
                'note': 'Historical episode data not provided',
                'suggestion': 'Pass historical_episodes dict with meeting data'
            }]
        
        similarities = []
        
        for name, hist_data in historical_episodes.items():
            comparison = self.compare_episode_patterns(current_data, hist_data)
            
            if 'error' not in comparison:
                similarities.append({
                    'episode': name,
                    'similarity': comparison['overall_similarity'],
                    'interpretation': comparison['interpretation']
                })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities
    
    def identify_recurring_patterns(
        self,
        all_episodes: Dict[str, List[Dict]]
    ) -> Dict:
        """
        Identify patterns that recur across multiple episodes.
        
        Args:
            all_episodes: Dict of {episode_name: meeting_data}
        
        Returns:
            Analysis of recurring patterns
        """
        logger.info(f"Analyzing {len(all_episodes)} episodes for recurring patterns")
        
        # Identify pattern for each episode
        episode_patterns = {}
        for name, data in all_episodes.items():
            pattern = self.identify_pattern(data)
            if 'best_match' in pattern:
                episode_patterns[name] = pattern['best_match']['pattern']
        
        # Count pattern frequencies
        pattern_counts = {}
        for pattern in episode_patterns.values():
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # Identify most common patterns
        sorted_patterns = sorted(
            pattern_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            'episode_patterns': episode_patterns,
            'pattern_frequencies': pattern_counts,
            'most_common': sorted_patterns[0] if sorted_patterns else None,
            'interpretation': self._interpret_recurring_patterns(sorted_patterns)
        }
    
    def _interpret_recurring_patterns(self, sorted_patterns: List[Tuple]) -> str:
        """Interpret recurring pattern analysis."""
        
        if not sorted_patterns:
            return "Insufficient data to identify recurring patterns"
        
        most_common = sorted_patterns[0]
        pattern_name = most_common[0]
        count = most_common[1]
        
        return (
            f"Most common pattern: {pattern_name.replace('_', ' ')} "
            f"(appears in {count} episodes). "
            f"Fed tends to repeat this policy approach."
        )


def identify_current_pattern(meeting_data: List[Dict]) -> Dict:
    """
    Convenience function to identify current pattern.
    
    Args:
        meeting_data: Recent meeting data
    
    Returns:
        Pattern identification
    """
    matcher = PatternMatcher()
    return matcher.identify_pattern(meeting_data)
