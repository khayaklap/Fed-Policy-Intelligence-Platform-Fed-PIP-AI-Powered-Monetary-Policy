"""
Episode Comparator

Compares two Fed policy episodes across multiple dimensions to identify
similarities, differences, and lessons learned.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from scipy.spatial import distance
from scipy import stats

try:
    # Try relative imports first (when used as module)
    from .comparative_analyzer_config import (
        POLICY_EPISODES,
        COMPARISON_DIMENSIONS,
        SIMILARITY_METHODS,
        SIMILARITY_THRESHOLDS,
        LESSON_CATEGORIES
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from comparative_analyzer_config import (
        POLICY_EPISODES,
        COMPARISON_DIMENSIONS,
        SIMILARITY_METHODS,
        SIMILARITY_THRESHOLDS,
        LESSON_CATEGORIES
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EpisodeComparator:
    """
    Compare Fed policy episodes to identify similarities and differences.
    """
    
    def __init__(self):
        """Initialize episode comparator."""
        logger.info("Initialized Episode Comparator")
    
    def compare_episodes(
        self,
        episode1_key: str,
        episode2_key: str,
        method: str = 'weighted'
    ) -> Dict:
        """
        Compare two policy episodes.
        
        Args:
            episode1_key: Key for first episode from POLICY_EPISODES
            episode2_key: Key for second episode
            method: Comparison method ('weighted', 'euclidean', 'cosine')
        
        Returns:
            Dictionary with comparison results
        """
        logger.info(f"Comparing {episode1_key} vs {episode2_key}")
        
        # Get episode data
        ep1 = POLICY_EPISODES.get(episode1_key)
        ep2 = POLICY_EPISODES.get(episode2_key)
        
        if not ep1 or not ep2:
            return {'error': 'Episode not found'}
        
        # Compare across dimensions
        dimension_scores = {}
        for dim_name, dim_config in COMPARISON_DIMENSIONS.items():
            score = self._compare_dimension(ep1, ep2, dim_name, dim_config)
            dimension_scores[dim_name] = score
        
        # Calculate overall similarity
        if method == 'weighted':
            overall_similarity = sum(
                dimension_scores[dim] * COMPARISON_DIMENSIONS[dim]['weight']
                for dim in dimension_scores
            )
        else:
            overall_similarity = np.mean(list(dimension_scores.values()))
        
        # Identify key similarities and differences
        similarities = self._identify_similarities(ep1, ep2, dimension_scores)
        differences = self._identify_differences(ep1, ep2, dimension_scores)
        
        # Extract lessons
        lessons = self._extract_lessons(ep1, ep2, similarities, differences)
        
        return {
            'episode1': {
                'key': episode1_key,
                'name': ep1['name'],
                'period': ep1['period'],
                'chair': ep1['chair']
            },
            'episode2': {
                'key': episode2_key,
                'name': ep2['name'],
                'period': ep2['period'],
                'chair': ep2['chair']
            },
            'overall_similarity': round(overall_similarity, 3),
            'similarity_classification': self._classify_similarity(overall_similarity),
            'dimension_scores': {k: round(v, 3) for k, v in dimension_scores.items()},
            'key_similarities': similarities,
            'key_differences': differences,
            'lessons': lessons,
            'interpretation': self._interpret_comparison(
                ep1, ep2, overall_similarity, similarities, differences
            )
        }
    
    def _compare_dimension(
        self,
        ep1: Dict,
        ep2: Dict,
        dim_name: str,
        dim_config: Dict
    ) -> float:
        """
        Compare two episodes on a specific dimension.
        
        Returns similarity score 0-1 (1 = identical).
        """
        metrics = dim_config['metrics']
        scores = []
        
        for metric in metrics:
            score = self._compare_metric(ep1, ep2, metric)
            if score is not None:
                scores.append(score)
        
        return np.mean(scores) if scores else 0.5
    
    def _compare_metric(self, ep1: Dict, ep2: Dict, metric: str) -> Optional[float]:
        """Compare a specific metric between episodes."""
        
        # Get values from key_features
        val1 = ep1.get('key_features', {}).get(metric)
        val2 = ep2.get('key_features', {}).get(metric)
        
        if val1 is None or val2 is None:
            # Check characteristics for boolean metrics
            if metric in ['recession', 'qe']:
                val1 = metric in ep1.get('characteristics', [])
                val2 = metric in ep2.get('characteristics', [])
            else:
                return None
        
        # Boolean comparison
        if isinstance(val1, bool) and isinstance(val2, bool):
            return 1.0 if val1 == val2 else 0.0
        
        # Numeric comparison
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            # Normalize by max value
            max_val = max(abs(val1), abs(val2))
            if max_val == 0:
                return 1.0
            diff = abs(val1 - val2) / max_val
            return 1.0 - min(diff, 1.0)
        
        # String comparison
        if isinstance(val1, str) and isinstance(val2, str):
            return 1.0 if val1 == val2 else 0.0
        
        return None
    
    def _classify_similarity(self, score: float) -> str:
        """Classify similarity score into categories."""
        
        if score >= SIMILARITY_THRESHOLDS['very_similar']:
            return "very_similar"
        elif score >= SIMILARITY_THRESHOLDS['similar']:
            return "similar"
        elif score >= SIMILARITY_THRESHOLDS['somewhat_similar']:
            return "somewhat_similar"
        else:
            return "dissimilar"
    
    def _identify_similarities(
        self,
        ep1: Dict,
        ep2: Dict,
        dimension_scores: Dict
    ) -> List[str]:
        """Identify key similarities between episodes."""
        
        similarities = []
        
        # High-scoring dimensions
        for dim, score in dimension_scores.items():
            if score >= 0.7:
                dim_config = COMPARISON_DIMENSIONS[dim]
                similarities.append(f"Similar {dim}: {dim_config['description']}")
        
        # Shared characteristics
        chars1 = set(ep1.get('characteristics', []))
        chars2 = set(ep2.get('characteristics', []))
        shared = chars1 & chars2
        
        for char in shared:
            similarities.append(f"Both episodes: {char.replace('_', ' ')}")
        
        # Same outcome type
        if ep1.get('outcome') and ep2.get('outcome'):
            if any(word in ep1['outcome'] and word in ep2['outcome'] 
                   for word in ['recession', 'soft landing', 'successful']):
                similarities.append(f"Similar outcomes: Both episodes had similar results")
        
        return similarities[:5]  # Top 5
    
    def _identify_differences(
        self,
        ep1: Dict,
        ep2: Dict,
        dimension_scores: Dict
    ) -> List[str]:
        """Identify key differences between episodes."""
        
        differences = []
        
        # Low-scoring dimensions
        for dim, score in dimension_scores.items():
            if score < 0.3:
                dim_config = COMPARISON_DIMENSIONS[dim]
                differences.append(f"Different {dim}: {dim_config['description']}")
        
        # Different chairs
        if ep1.get('chair') != ep2.get('chair'):
            differences.append(f"Different chairs: {ep1['chair']} vs {ep2['chair']}")
        
        # Rate change magnitude
        rate1 = ep1.get('key_features', {}).get('rate_change', 0)
        rate2 = ep2.get('key_features', {}).get('rate_change', 0)
        
        if abs(rate1 - rate2) > 200:  # >200bp difference
            differences.append(
                f"Rate change magnitude: {abs(rate1)}bp vs {abs(rate2)}bp"
            )
        
        # Speed difference
        dur1 = ep1.get('key_features', {}).get('duration_months', 12)
        dur2 = ep2.get('key_features', {}).get('duration_months', 12)
        
        if abs(rate1/dur1 - rate2/dur2) > 10:  # >10bp/month difference
            speed1 = abs(rate1/dur1)
            speed2 = abs(rate2/dur2)
            differences.append(
                f"Speed: {speed1:.0f}bp/month vs {speed2:.0f}bp/month"
            )
        
        return differences[:5]  # Top 5
    
    def _extract_lessons(
        self,
        ep1: Dict,
        ep2: Dict,
        similarities: List[str],
        differences: List[str]
    ) -> List[Dict]:
        """Extract lessons from episode comparison."""
        
        lessons = []
        
        # Lesson from similarities
        if len(similarities) >= 3:
            lessons.append({
                'category': 'pattern',
                'lesson': f"Episodes share key features - pattern may repeat",
                'relevance': 'high'
            })
        
        # Lesson from speed differences
        if any('Speed' in d for d in differences):
            lessons.append({
                'category': 'timing',
                'lesson': "Fed response speed varies by context - act faster in crisis",
                'relevance': 'high'
            })
        
        # Lesson from outcomes
        outcome1 = ep1.get('outcome', '')
        outcome2 = ep2.get('outcome', '')
        
        if 'successful' in outcome1.lower() and 'recession' in outcome2.lower():
            lessons.append({
                'category': 'effectiveness',
                'lesson': f"Similar policy can have different outcomes - context matters",
                'relevance': 'high'
            })
        
        return lessons
    
    def _interpret_comparison(
        self,
        ep1: Dict,
        ep2: Dict,
        similarity: float,
        similarities: List[str],
        differences: List[str]
    ) -> str:
        """Generate human-readable interpretation."""
        
        ep1_name = ep1['name']
        ep2_name = ep2['name']
        
        if similarity >= 0.85:
            interp = f"{ep1_name} and {ep2_name} are very similar episodes"
        elif similarity >= 0.70:
            interp = f"{ep1_name} and {ep2_name} share significant similarities"
        elif similarity >= 0.50:
            interp = f"{ep1_name} and {ep2_name} have some similarities but notable differences"
        else:
            interp = f"{ep1_name} and {ep2_name} are quite different episodes"
        
        # Add context
        if ep1.get('chair') == ep2.get('chair'):
            interp += f" (both under {ep1['chair']})"
        
        return interp
    
    def compare_multiple_episodes(
        self,
        episode_keys: List[str]
    ) -> Dict:
        """
        Compare multiple episodes and create similarity matrix.
        
        Args:
            episode_keys: List of episode keys to compare
        
        Returns:
            Dictionary with pairwise comparisons and similarity matrix
        """
        logger.info(f"Comparing {len(episode_keys)} episodes")
        
        n = len(episode_keys)
        similarity_matrix = np.zeros((n, n))
        
        pairwise_comparisons = {}
        
        for i in range(n):
            for j in range(i, n):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                else:
                    comparison = self.compare_episodes(
                        episode_keys[i],
                        episode_keys[j]
                    )
                    similarity = comparison['overall_similarity']
                    similarity_matrix[i][j] = similarity
                    similarity_matrix[j][i] = similarity
                    
                    pair_key = f"{episode_keys[i]}_vs_{episode_keys[j]}"
                    pairwise_comparisons[pair_key] = comparison
        
        # Find most and least similar pairs
        max_sim = 0
        min_sim = 1
        most_similar_pair = None
        least_similar_pair = None
        
        for i in range(n):
            for j in range(i+1, n):
                sim = similarity_matrix[i][j]
                if sim > max_sim:
                    max_sim = sim
                    most_similar_pair = (episode_keys[i], episode_keys[j])
                if sim < min_sim:
                    min_sim = sim
                    least_similar_pair = (episode_keys[i], episode_keys[j])
        
        return {
            'num_episodes': n,
            'episodes': episode_keys,
            'similarity_matrix': similarity_matrix.tolist(),
            'most_similar_pair': {
                'episodes': most_similar_pair,
                'similarity': round(max_sim, 3)
            },
            'least_similar_pair': {
                'episodes': least_similar_pair,
                'similarity': round(min_sim, 3)
            },
            'pairwise_comparisons': pairwise_comparisons
        }
    
    def rank_similar_episodes(
        self,
        target_episode: str,
        candidate_episodes: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Rank episodes by similarity to target episode.
        
        Args:
            target_episode: Episode to compare against
            candidate_episodes: Episodes to consider (or all if None)
        
        Returns:
            Ranked list of similar episodes
        """
        logger.info(f"Ranking episodes similar to {target_episode}")
        
        if candidate_episodes is None:
            candidate_episodes = [k for k in POLICY_EPISODES.keys() if k != target_episode]
        
        similarities = []
        
        for candidate in candidate_episodes:
            comparison = self.compare_episodes(target_episode, candidate)
            similarities.append({
                'episode': candidate,
                'name': POLICY_EPISODES[candidate]['name'],
                'similarity': comparison['overall_similarity'],
                'classification': comparison['similarity_classification'],
                'key_similarities': comparison['key_similarities'][:3]
            })
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities


def compare_two_episodes(episode1: str, episode2: str) -> Dict:
    """
    Convenience function for comparing two episodes.
    
    Args:
        episode1: First episode key
        episode2: Second episode key
    
    Returns:
        Comparison results
    """
    comparator = EpisodeComparator()
    return comparator.compare_episodes(episode1, episode2)
