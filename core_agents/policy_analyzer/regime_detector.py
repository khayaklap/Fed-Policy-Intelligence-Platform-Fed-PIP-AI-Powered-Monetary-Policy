"""
Regime Detector

Identifies Fed policy regimes (accommodative, tightening, neutral) and
detects regime changes over time.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import Counter

try:
    # Try relative imports first (when used as module)
    from .policy_analyzer_config import (
        POLICY_REGIMES,
        MIN_REGIME_LENGTH,
        REGIME_CHANGE_INDICATORS,
        HISTORICAL_EPISODES
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from policy_analyzer_config import (
        POLICY_REGIMES,
        MIN_REGIME_LENGTH,
        REGIME_CHANGE_INDICATORS,
        HISTORICAL_EPISODES
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RegimeDetector:
    """
    Detect and classify Fed policy regimes.
    """
    
    def __init__(self):
        """Initialize regime detector."""
        logger.info("Initialized Regime Detector")
    
    def classify_regime(
        self,
        actions: List[str],
        sentiments: List[str],
        forward_guidance: Optional[List[str]] = None
    ) -> str:
        """
        Classify current policy regime based on actions and sentiment.
        
        Args:
            actions: List of recent policy actions ('increase', 'decrease', 'unchanged')
            sentiments: List of recent sentiment classifications
            forward_guidance: Optional forward guidance text
        
        Returns:
            Regime classification
        """
        logger.info("Classifying policy regime")
        
        if not actions or not sentiments:
            return "unknown"
        
        # Count action types
        action_counts = Counter(actions)
        sentiment_counts = Counter(sentiments)
        
        # Recent actions
        recent_action = actions[-1] if actions else None
        dominant_sentiment = sentiment_counts.most_common(1)[0][0] if sentiment_counts else None
        
        # Determine regime
        if action_counts.get('increase', 0) >= len(actions) * 0.5:
            # Mostly rate increases
            if dominant_sentiment in ['hawkish', 'highly_hawkish']:
                return "tightening"
            else:
                return "pivot_to_tightening"
        
        elif action_counts.get('decrease', 0) >= len(actions) * 0.5:
            # Mostly rate decreases
            if dominant_sentiment in ['dovish', 'highly_dovish']:
                return "accommodative"
            else:
                return "pivot_to_easing"
        
        else:
            # Mostly unchanged
            if dominant_sentiment in ['hawkish', 'highly_hawkish']:
                return "pivot_to_tightening"
            elif dominant_sentiment in ['dovish', 'highly_dovish']:
                return "pivot_to_easing"
            else:
                return "neutral"
    
    def detect_regime_changes(
        self,
        meeting_data: List[Dict]
    ) -> List[Dict]:
        """
        Detect regime changes in meeting sequence.
        
        Args:
            meeting_data: List of dicts with 'date', 'action', 'sentiment'
        
        Returns:
            List of detected regime changes
        """
        logger.info(f"Detecting regime changes in {len(meeting_data)} meetings")
        
        if len(meeting_data) < MIN_REGIME_LENGTH * 2:
            return []
        
        # Convert to DataFrame
        df = pd.DataFrame(meeting_data)
        
        # Classify regime for each meeting
        regimes = []
        window_size = 3  # Look at 3 meetings at a time
        
        for i in range(len(df)):
            start_idx = max(0, i - window_size + 1)
            end_idx = i + 1
            
            window_df = df.iloc[start_idx:end_idx]
            
            actions = window_df['action'].tolist() if 'action' in window_df.columns else []
            sentiments = window_df['sentiment'].tolist() if 'sentiment' in window_df.columns else []
            
            regime = self.classify_regime(actions, sentiments)
            regimes.append(regime)
        
        df['regime'] = regimes
        
        # Find regime changes
        changes = []
        current_regime = regimes[0]
        regime_start = 0
        
        for i in range(1, len(regimes)):
            if regimes[i] != current_regime:
                # Regime changed
                if i - regime_start >= MIN_REGIME_LENGTH:
                    # Valid regime (lasted minimum length)
                    change = {
                        'date': df.iloc[i]['date'] if 'date' in df.columns else i,
                        'previous_regime': current_regime,
                        'new_regime': regimes[i],
                        'duration': i - regime_start,
                        'type': self._classify_regime_change_type(current_regime, regimes[i])
                    }
                    changes.append(change)
                
                current_regime = regimes[i]
                regime_start = i
        
        logger.info(f"Detected {len(changes)} regime changes")
        return changes
    
    def _classify_regime_change_type(self, old_regime: str, new_regime: str) -> str:
        """Classify the type of regime change."""
        
        if old_regime == new_regime:
            return "no_change"
        
        # Tightening transitions
        if new_regime == "tightening":
            return "shift_to_tightening"
        
        # Easing transitions
        if new_regime == "accommodative":
            return "shift_to_easing"
        
        # Pivot transitions
        if "pivot" in new_regime:
            return "policy_pivot"
        
        # Neutral
        if new_regime == "neutral":
            return "normalization"
        
        return "regime_shift"
    
    def get_current_regime(
        self,
        meeting_data: List[Dict],
        lookback_meetings: int = 6
    ) -> Dict:
        """
        Determine current policy regime.
        
        Args:
            meeting_data: List of meeting data
            lookback_meetings: Number of recent meetings to consider
        
        Returns:
            Dictionary with current regime analysis
        """
        logger.info("Determining current policy regime")
        
        if not meeting_data:
            return {'error': 'No data'}
        
        # Get recent meetings
        recent_data = meeting_data[-lookback_meetings:]
        
        # Extract actions and sentiments
        actions = [m.get('action') for m in recent_data if m.get('action')]
        sentiments = [m.get('sentiment') for m in recent_data if m.get('sentiment')]
        
        # Classify regime
        regime = self.classify_regime(actions, sentiments)
        
        # Determine duration (how long in current regime)
        regime_duration = 1
        for i in range(len(recent_data) - 2, -1, -1):
            window_actions = [m.get('action') for m in meeting_data[max(0, i-2):i+1] if m.get('action')]
            window_sentiments = [m.get('sentiment') for m in meeting_data[max(0, i-2):i+1] if m.get('sentiment')]
            
            if self.classify_regime(window_actions, window_sentiments) == regime:
                regime_duration += 1
            else:
                break
        
        # Assess stability
        if regime_duration >= 6:
            stability = "well_established"
        elif regime_duration >= 3:
            stability = "established"
        else:
            stability = "transitioning"
        
        return {
            'regime': regime,
            'description': POLICY_REGIMES.get(regime, {}).get('description', 'Unknown regime'),
            'duration': regime_duration,
            'stability': stability,
            'recent_actions': actions,
            'recent_sentiments': sentiments
        }
    
    def compare_to_historical(
        self,
        current_regime: str,
        current_duration: int,
        current_sentiment: str
    ) -> Dict:
        """
        Compare current regime to historical episodes.
        
        Args:
            current_regime: Current policy regime
            current_duration: How long in current regime
            current_sentiment: Current sentiment classification
        
        Returns:
            Dictionary with historical comparison
        """
        logger.info("Comparing to historical episodes")
        
        similar_episodes = []
        
        for episode_name, episode_data in HISTORICAL_EPISODES.items():
            # Check if regime matches
            if episode_data['regime'] == current_regime:
                similarity_score = 0.5  # Base similarity for matching regime
                
                # Check sentiment alignment
                if current_sentiment in episode_data.get('characteristics', []):
                    similarity_score += 0.3
                
                # Check duration similarity (normalized)
                # This is simplified - would need actual episode durations
                similarity_score += 0.2
                
                similar_episodes.append({
                    'episode': episode_name,
                    'description': episode_data['description'],
                    'period': episode_data['period'],
                    'similarity': round(similarity_score, 2),
                    'characteristics': episode_data.get('characteristics', [])
                })
        
        # Sort by similarity
        similar_episodes.sort(key=lambda x: x['similarity'], reverse=True)
        
        return {
            'most_similar': similar_episodes[0] if similar_episodes else None,
            'similar_episodes': similar_episodes[:3],  # Top 3
            'comparison': self._generate_historical_comparison(current_regime, similar_episodes)
        }
    
    def _generate_historical_comparison(
        self,
        current_regime: str,
        similar_episodes: List[Dict]
    ) -> str:
        """Generate textual comparison to historical episodes."""
        
        if not similar_episodes:
            return f"Current {current_regime} regime is unique in recent Fed history"
        
        most_similar = similar_episodes[0]
        
        return (
            f"Current {current_regime} regime most similar to {most_similar['episode']} "
            f"({most_similar['period'][0][:4]}-{most_similar['period'][1][:4]}). "
            f"Key characteristics: {', '.join(most_similar['characteristics'][:3])}"
        )
    
    def get_regime_timeline(
        self,
        meeting_data: List[Dict]
    ) -> pd.DataFrame:
        """
        Create timeline of regimes.
        
        Args:
            meeting_data: List of meeting data
        
        Returns:
            DataFrame with regime timeline
        """
        logger.info("Creating regime timeline")
        
        if not meeting_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(meeting_data)
        
        # Classify regime for each meeting
        regimes = []
        window_size = 3
        
        for i in range(len(df)):
            start_idx = max(0, i - window_size + 1)
            end_idx = i + 1
            
            window_df = df.iloc[start_idx:end_idx]
            actions = window_df['action'].tolist() if 'action' in window_df.columns else []
            sentiments = window_df['sentiment'].tolist() if 'sentiment' in window_df.columns else []
            
            regime = self.classify_regime(actions, sentiments)
            regimes.append(regime)
        
        df['regime'] = regimes
        
        return df[['date', 'regime', 'action', 'sentiment']]


def detect_policy_regimes(meeting_data: List[Dict]) -> Dict:
    """
    Convenience function for complete regime analysis.
    
    Args:
        meeting_data: List of meeting data
    
    Returns:
        Complete regime analysis
    """
    detector = RegimeDetector()
    
    current_regime = detector.get_current_regime(meeting_data)
    regime_changes = detector.detect_regime_changes(meeting_data)
    
    if 'error' not in current_regime:
        historical_comp = detector.compare_to_historical(
            current_regime['regime'],
            current_regime['duration'],
            meeting_data[-1].get('sentiment', 'neutral') if meeting_data else 'neutral'
        )
    else:
        historical_comp = None
    
    return {
        'current_regime': current_regime,
        'regime_changes': regime_changes,
        'historical_comparison': historical_comp,
        'num_meetings_analyzed': len(meeting_data)
    }
