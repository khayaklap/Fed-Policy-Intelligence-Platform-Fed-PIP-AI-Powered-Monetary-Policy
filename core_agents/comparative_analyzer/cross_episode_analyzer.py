"""
Cross-Episode Analyzer

Analyzes patterns across multiple Fed policy episodes, compares Fed chairs,
and extracts lessons learned.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import Counter

try:
    # Try relative imports first (when used as module)
    from .comparative_analyzer_config import (
        POLICY_EPISODES,
        FED_CHAIRS,
        LESSON_CATEGORIES
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from comparative_analyzer_config import (
        POLICY_EPISODES,
        FED_CHAIRS,
        LESSON_CATEGORIES
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrossEpisodeAnalyzer:
    """
    Analyze patterns across multiple Fed policy episodes.
    """
    
    def __init__(self):
        """Initialize cross-episode analyzer."""
        logger.info("Initialized Cross-Episode Analyzer")
    
    def compare_fed_chairs(
        self,
        chair1_key: str,
        chair2_key: str
    ) -> Dict:
        """
        Compare two Fed chairs' approaches and effectiveness.
        
        Args:
            chair1_key: Key for first chair from FED_CHAIRS
            chair2_key: Key for second chair
        
        Returns:
            Dictionary with chair comparison
        """
        logger.info(f"Comparing {chair1_key} vs {chair2_key}")
        
        chair1 = FED_CHAIRS.get(chair1_key)
        chair2 = FED_CHAIRS.get(chair2_key)
        
        if not chair1 or not chair2:
            return {'error': 'Chair not found'}
        
        # Extract key differences
        style_differences = self._compare_styles(chair1, chair2)
        
        # Compare episodes
        episode_comparison = self._compare_chair_episodes(chair1, chair2)
        
        # Notable achievements
        achievements = {
            'chair1': chair1['notable_for'],
            'chair2': chair2['notable_for']
        }
        
        return {
            'chair1': {
                'name': chair1['name'],
                'tenure': chair1['tenure'],
                'tenure_years': self._calculate_tenure_years(chair1['tenure']),
                'style': chair1['style']
            },
            'chair2': {
                'name': chair2['name'],
                'tenure': chair2['tenure'],
                'tenure_years': self._calculate_tenure_years(chair2['tenure']),
                'style': chair2['style']
            },
            'style_differences': style_differences,
            'episode_comparison': episode_comparison,
            'notable_achievements': achievements,
            'interpretation': self._interpret_chair_comparison(chair1, chair2, style_differences)
        }
    
    def _compare_styles(self, chair1: Dict, chair2: Dict) -> List[str]:
        """Identify style differences between chairs."""
        
        differences = []
        
        style1 = chair1['style'].lower()
        style2 = chair2['style'].lower()
        
        # Check for key style markers
        markers = ['aggressive', 'gradual', 'innovative', 'cautious', 'data-dependent']
        
        for marker in markers:
            in1 = marker in style1
            in2 = marker in style2
            
            if in1 and not in2:
                differences.append(f"{chair1['name']}: {marker}")
            elif in2 and not in1:
                differences.append(f"{chair2['name']}: {marker}")
        
        return differences
    
    def _compare_chair_episodes(self, chair1: Dict, chair2: Dict) -> Dict:
        """Compare episodes handled by each chair."""
        
        ep1_keys = chair1.get('key_episodes', [])
        ep2_keys = chair2.get('key_episodes', [])
        
        # Get episode details
        ep1_details = [POLICY_EPISODES[k] for k in ep1_keys if k in POLICY_EPISODES]
        ep2_details = [POLICY_EPISODES[k] for k in ep2_keys if k in POLICY_EPISODES]
        
        # Count episode types
        ep1_types = Counter([
            'crisis' if any(word in ep['context'].lower() for word in ['crisis', 'crash', 'pandemic']) else 'normal'
            for ep in ep1_details
        ])
        
        ep2_types = Counter([
            'crisis' if any(word in ep['context'].lower() for word in ['crisis', 'crash', 'pandemic']) else 'normal'
            for ep in ep2_details
        ])
        
        return {
            'chair1_episodes': len(ep1_keys),
            'chair2_episodes': len(ep2_keys),
            'chair1_crises': ep1_types.get('crisis', 0),
            'chair2_crises': ep2_types.get('crisis', 0),
            'chair1_major': [ep['name'] for ep in ep1_details[:3]],  # Top 3
            'chair2_major': [ep['name'] for ep in ep2_details[:3]]
        }
    
    def _calculate_tenure_years(self, tenure: Tuple[str, str]) -> float:
        """Calculate tenure length in years."""
        from datetime import datetime
        
        if tenure[1] == 'present':
            end = datetime.now()
        else:
            end = datetime.strptime(tenure[1], '%Y-%m-%d')
        
        start = datetime.strptime(tenure[0], '%Y-%m-%d')
        
        years = (end - start).days / 365.25
        return round(years, 1)
    
    def _interpret_chair_comparison(
        self,
        chair1: Dict,
        chair2: Dict,
        differences: List[str]
    ) -> str:
        """Generate interpretation of chair comparison."""
        
        name1 = chair1['name']
        name2 = chair2['name']
        
        interp = f"{name1} vs {name2}: "
        
        if len(differences) >= 3:
            interp += "Distinct styles - "
        else:
            interp += "Similar approaches - "
        
        # Notable distinction
        notable1 = chair1['notable_for'][0] if chair1['notable_for'] else "Fed leadership"
        notable2 = chair2['notable_for'][0] if chair2['notable_for'] else "Fed leadership"
        
        interp += f"{name1} known for {notable1.lower()}, "
        interp += f"{name2} known for {notable2.lower()}."
        
        return interp
    
    def extract_lessons_learned(
        self,
        episode_keys: List[str]
    ) -> Dict:
        """
        Extract lessons learned from multiple episodes.
        
        Args:
            episode_keys: List of episode keys to analyze
        
        Returns:
            Lessons organized by category
        """
        logger.info(f"Extracting lessons from {len(episode_keys)} episodes")
        
        episodes = [POLICY_EPISODES[k] for k in episode_keys if k in POLICY_EPISODES]
        
        lessons_by_category = {cat: [] for cat in LESSON_CATEGORIES.keys()}
        
        # Analyze each episode for lessons
        for episode in episodes:
            # Timing lessons
            if 'late' in episode.get('context', '').lower() or 'behind' in episode.get('outcome', '').lower():
                lessons_by_category['timing'].append({
                    'episode': episode['name'],
                    'lesson': f"Fed was late to act - inflation/crisis already building",
                    'implication': "Act early when warning signs appear"
                })
            
            # Magnitude lessons
            if 'aggressive' in episode.get('characteristics', []) or episode.get('key_features', {}).get('rate_change', 0) > 400:
                lessons_by_category['magnitude'].append({
                    'episode': episode['name'],
                    'lesson': f"Large, decisive action taken",
                    'implication': "Front-load when behind curve or in crisis"
                })
            
            # Communication lessons
            if 'transitory' in episode.get('key_features', {}).get('forward_guidance', '').lower():
                lessons_by_category['communication'].append({
                    'episode': episode['name'],
                    'lesson': "'Transitory' messaging proved incorrect",
                    'implication': "Avoid premature commitments about inflation"
                })
            
            # Tools lessons
            if episode.get('key_features', {}).get('qe'):
                lessons_by_category['tools'].append({
                    'episode': episode['name'],
                    'lesson': "QE effective at zero bound",
                    'implication': "Unconventional tools available when needed"
                })
            
            # Mistakes
            if 'recession' in episode.get('outcome', '').lower() and 'tolerated' not in episode.get('outcome', ''):
                lessons_by_category['mistakes'].append({
                    'episode': episode['name'],
                    'lesson': "Policy resulted in unintended recession",
                    'implication': "Balance inflation control with growth support"
                })
        
        # Add general lessons from configuration
        for category, config in LESSON_CATEGORIES.items():
            if not lessons_by_category[category]:  # If no specific lessons found
                for general_lesson in config['key_lessons'][:2]:  # Add first 2 general lessons
                    lessons_by_category[category].append({
                        'episode': 'General',
                        'lesson': general_lesson,
                        'implication': f"Based on historical patterns ({category})"
                    })
        
        return {
            'lessons_by_category': lessons_by_category,
            'num_episodes_analyzed': len(episodes),
            'key_takeaways': self._generate_key_takeaways(lessons_by_category)
        }
    
    def _generate_key_takeaways(self, lessons_by_category: Dict) -> List[str]:
        """Generate top takeaways from lessons."""
        
        takeaways = []
        
        # Most common lesson per category
        for category, lessons in lessons_by_category.items():
            if lessons:
                # First lesson in each category
                lesson = lessons[0]
                takeaway = f"{category.title()}: {lesson['implication']}"
                takeaways.append(takeaway)
        
        return takeaways[:5]  # Top 5
    
    def analyze_policy_evolution(
        self,
        episode_keys: List[str]
    ) -> Dict:
        """
        Analyze how Fed policy evolved across episodes.
        
        Args:
            episode_keys: Chronologically ordered episode keys
        
        Returns:
            Evolution analysis
        """
        logger.info("Analyzing policy evolution")
        
        episodes = [POLICY_EPISODES[k] for k in episode_keys if k in POLICY_EPISODES]
        
        # Track evolution of key metrics
        rate_changes = []
        durations = []
        chairs = []
        
        for ep in episodes:
            rate_change = ep.get('key_features', {}).get('rate_change', 0)
            duration = ep.get('key_features', {}).get('duration_months', 0)
            
            rate_changes.append(abs(rate_change))
            durations.append(duration)
            chairs.append(ep.get('chair', 'Unknown'))
        
        # Calculate trends
        if len(rate_changes) > 1:
            rate_trend = "increasing" if rate_changes[-1] > rate_changes[0] else "decreasing"
            duration_trend = "longer" if durations[-1] > durations[0] else "shorter"
        else:
            rate_trend = "stable"
            duration_trend = "stable"
        
        # Identify shifts in approach
        shifts = []
        for i in range(1, len(episodes)):
            prev_ep = episodes[i-1]
            curr_ep = episodes[i]
            
            # Chair change
            if prev_ep.get('chair') != curr_ep.get('chair'):
                shifts.append({
                    'date': curr_ep['period'][0],
                    'type': 'chair_change',
                    'description': f"Chair changed: {prev_ep.get('chair')} → {curr_ep.get('chair')}"
                })
            
            # Tool innovation
            prev_qe = prev_ep.get('key_features', {}).get('qe', False)
            curr_qe = curr_ep.get('key_features', {}).get('qe', False)
            
            if curr_qe and not prev_qe:
                shifts.append({
                    'date': curr_ep['period'][0],
                    'type': 'tool_innovation',
                    'description': f"QE introduced in {curr_ep['name']}"
                })
        
        return {
            'rate_change_trend': rate_trend,
            'duration_trend': duration_trend,
            'policy_shifts': shifts,
            'interpretation': self._interpret_evolution(rate_trend, duration_trend, shifts)
        }
    
    def _interpret_evolution(
        self,
        rate_trend: str,
        duration_trend: str,
        shifts: List[Dict]
    ) -> str:
        """Interpret policy evolution."""
        
        interp = f"Policy responses show {rate_trend} magnitude and {duration_trend} duration. "
        
        if shifts:
            interp += f"{len(shifts)} major shifts in approach detected. "
        
        if rate_trend == "increasing":
            interp += "Fed becoming more aggressive over time."
        elif rate_trend == "decreasing":
            interp += "Fed becoming more gradual over time."
        
        return interp


def compare_chairs(chair1: str, chair2: str) -> Dict:
    """
    Convenience function for comparing two Fed chairs.
    
    Args:
        chair1: First chair key
        chair2: Second chair key
    
    Returns:
        Chair comparison
    """
    analyzer = CrossEpisodeAnalyzer()
    return analyzer.compare_fed_chairs(chair1, chair2)


def extract_lessons(episode_keys: List[str]) -> Dict:
    """
    Convenience function for extracting lessons.
    
    Args:
        episode_keys: List of episode keys
    
    Returns:
        Lessons learned
    """
    analyzer = CrossEpisodeAnalyzer()
    return analyzer.extract_lessons_learned(episode_keys)
