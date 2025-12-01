"""
Stance Classifier

Classifies overall Fed policy stance by combining multiple signals:
- Policy actions (rate changes)
- Sentiment (hawkish/dovish)
- Forward guidance
- Real rates (from Treasury data)
"""

import logging
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

try:
    # Try relative imports first (when used as module)
    from .policy_analyzer_config import STANCE_THRESHOLDS, HISTORICAL_EPISODES
except ImportError:
    # Fall back to absolute imports (when run directly)
    from policy_analyzer_config import STANCE_THRESHOLDS, HISTORICAL_EPISODES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StanceClassifier:
    """
    Classify Fed's overall policy stance.
    """
    
    def __init__(self):
        """Initialize stance classifier."""
        logger.info("Initialized Stance Classifier")
    
    def classify_overall_stance(
        self,
        policy_actions: List[str],
        sentiment_scores: List[int],
        fed_funds_rate: Optional[float] = None,
        real_rate: Optional[float] = None,
        inflation_rate: Optional[float] = None
    ) -> Dict:
        """
        Classify overall policy stance using multiple signals.
        
        Args:
            policy_actions: Recent policy actions
            sentiment_scores: Recent sentiment scores
            fed_funds_rate: Current Fed Funds rate
            real_rate: Current real interest rate (nominal - inflation)
            inflation_rate: Current inflation rate
        
        Returns:
            Dictionary with stance classification
        """
        logger.info("Classifying overall policy stance")
        
        scores = {
            'action_score': self._score_actions(policy_actions),
            'sentiment_score': sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0,
            'rate_score': self._score_rate_level(fed_funds_rate, real_rate, inflation_rate)
        }
        
        # Weighted combination
        weights = {
            'action_score': 0.4,  # Actions are most important
            'sentiment_score': 0.3,  # Sentiment shows direction
            'rate_score': 0.3  # Rate level shows absolute stance
        }
        
        overall_score = sum(scores[k] * weights[k] for k in scores.keys())
        
        # Classify
        if overall_score > 10:
            stance = "highly_restrictive"
            description = "Very tight policy - fighting inflation aggressively"
        elif overall_score > 5:
            stance = "restrictive"
            description = "Tight policy - slowing economy to control inflation"
        elif overall_score > -5:
            stance = "neutral"
            description = "Balanced policy - data-dependent approach"
        elif overall_score > -10:
            stance = "accommodative"
            description = "Supportive policy - encouraging growth"
        else:
            stance = "highly_accommodative"
            description = "Very loose policy - maximum support for economy"
        
        return {
            'stance': stance,
            'overall_score': round(overall_score, 2),
            'description': description,
            'component_scores': scores,
            'confidence': self._assess_confidence(scores)
        }
    
    def _score_actions(self, actions: List[str]) -> float:
        """
        Score policy actions.
        
        Rate increases = positive (restrictive)
        Rate decreases = negative (accommodative)
        """
        if not actions:
            return 0
        
        action_scores = {
            'increase': 10,
            'decrease': -10,
            'unchanged': 0
        }
        
        scores = [action_scores.get(a, 0) for a in actions]
        return sum(scores) / len(scores)
    
    def _score_rate_level(
        self,
        fed_funds: Optional[float],
        real_rate: Optional[float],
        inflation: Optional[float]
    ) -> float:
        """
        Score rate levels.
        
        High real rates = restrictive
        Negative real rates = accommodative
        """
        if real_rate is not None:
            # Use real rate if available (best measure)
            if real_rate > 2.0:
                return 15  # Very restrictive
            elif real_rate > 1.0:
                return 10  # Restrictive
            elif real_rate > 0:
                return 5   # Moderately restrictive
            elif real_rate > -1.0:
                return -5  # Moderately accommodative
            else:
                return -10 # Very accommodative
        
        elif fed_funds is not None and inflation is not None:
            # Calculate implied real rate
            implied_real = fed_funds - inflation
            return self._score_rate_level(None, implied_real, None)
        
        elif fed_funds is not None:
            # Use nominal rate as proxy
            if fed_funds > 5.0:
                return 10
            elif fed_funds > 3.0:
                return 5
            elif fed_funds > 1.0:
                return 0
            else:
                return -5
        
        return 0
    
    def _assess_confidence(self, scores: Dict) -> str:
        """
        Assess confidence in stance classification.
        
        High confidence when all signals agree.
        """
        score_values = list(scores.values())
        
        # Check if all scores have same sign
        all_positive = all(s > 0 for s in score_values if s != 0)
        all_negative = all(s < 0 for s in score_values if s != 0)
        
        if all_positive or all_negative:
            return "high"
        
        # Check alignment
        positive_count = sum(1 for s in score_values if s > 0)
        negative_count = sum(1 for s in score_values if s < 0)
        
        if abs(positive_count - negative_count) >= 2:
            return "moderate"
        
        return "low"
    
    def compare_stance_to_conditions(
        self,
        stance: str,
        inflation: float,
        unemployment: float,
        gdp_growth: float
    ) -> Dict:
        """
        Compare policy stance to economic conditions.
        
        Assess if stance is appropriate given conditions.
        
        Args:
            stance: Policy stance classification
            inflation: Current inflation rate
            unemployment: Current unemployment rate
            gdp_growth: Current GDP growth rate
        
        Returns:
            Dictionary with appropriateness assessment
        """
        logger.info("Comparing stance to economic conditions")
        
        # Economic conditions assessment
        high_inflation = inflation > 3.0
        low_inflation = inflation < 1.5
        high_unemployment = unemployment > 5.0
        low_unemployment = unemployment < 4.0
        strong_growth = gdp_growth > 2.5
        weak_growth = gdp_growth < 1.0
        
        # Determine appropriate stance
        if high_inflation and low_unemployment:
            appropriate_stance = "restrictive"
            rationale = "High inflation + low unemployment = economy overheating, needs tightening"
        elif low_inflation and high_unemployment:
            appropriate_stance = "accommodative"
            rationale = "Low inflation + high unemployment = economy weak, needs support"
        elif high_inflation:
            appropriate_stance = "restrictive"
            rationale = "High inflation requires tightening even if unemployment rising"
        elif high_unemployment and weak_growth:
            appropriate_stance = "accommodative"
            rationale = "Weak economy needs support"
        else:
            appropriate_stance = "neutral"
            rationale = "Balanced conditions support neutral stance"
        
        # Compare to actual stance
        stance_alignment = self._assess_stance_alignment(stance, appropriate_stance)
        
        return {
            'conditions': {
                'inflation': inflation,
                'unemployment': unemployment,
                'gdp_growth': gdp_growth
            },
            'conditions_assessment': {
                'high_inflation': high_inflation,
                'high_unemployment': high_unemployment,
                'strong_growth': strong_growth
            },
            'appropriate_stance': appropriate_stance,
            'rationale': rationale,
            'actual_stance': stance,
            'alignment': stance_alignment,
            'interpretation': self._interpret_alignment(stance, appropriate_stance, stance_alignment)
        }
    
    def _assess_stance_alignment(self, actual: str, appropriate: str) -> str:
        """Assess how well actual stance aligns with appropriate stance."""
        
        restrictiveness_order = [
            "highly_accommodative",
            "accommodative",
            "neutral",
            "restrictive",
            "highly_restrictive"
        ]
        
        try:
            actual_idx = restrictiveness_order.index(actual)
            appropriate_idx = restrictiveness_order.index(appropriate)
            
            diff = abs(actual_idx - appropriate_idx)
            
            if diff == 0:
                return "well_aligned"
            elif diff == 1:
                return "mostly_aligned"
            elif diff == 2:
                return "somewhat_misaligned"
            else:
                return "misaligned"
        except ValueError:
            return "unknown"
    
    def _interpret_alignment(self, actual: str, appropriate: str, alignment: str) -> str:
        """Generate interpretation of stance alignment."""
        
        if alignment == "well_aligned":
            return f"Policy stance ({actual}) is appropriate for current economic conditions"
        
        elif alignment == "mostly_aligned":
            return f"Policy stance ({actual}) is close to appropriate ({appropriate})"
        
        elif alignment == "somewhat_misaligned":
            if "restrictive" in actual and "accommodative" in appropriate:
                return f"Policy may be too tight ({actual}) given conditions suggest {appropriate}"
            elif "accommodative" in actual and "restrictive" in appropriate:
                return f"Policy may be too loose ({actual}) given conditions suggest {appropriate}"
            else:
                return f"Policy stance ({actual}) somewhat misaligned with conditions ({appropriate})"
        
        else:
            if "restrictive" in actual and "accommodative" in appropriate:
                return f"Policy significantly too tight ({actual}) - conditions call for {appropriate}"
            elif "accommodative" in actual and "restrictive" in appropriate:
                return f"Policy significantly too loose ({actual}) - conditions call for {appropriate}"
            else:
                return f"Policy stance ({actual}) not well-matched to conditions ({appropriate})"
    
    def get_stance_trajectory(
        self,
        meeting_data: List[Dict]
    ) -> Dict:
        """
        Analyze trajectory of policy stance over time.
        
        Args:
            meeting_data: List of meetings with stance data
        
        Returns:
            Dictionary with trajectory analysis
        """
        logger.info("Analyzing stance trajectory")
        
        if len(meeting_data) < 3:
            return {'error': 'Insufficient data for trajectory analysis'}
        
        df = pd.DataFrame(meeting_data)
        
        # Create stance scores
        # Simplified scoring
        stance_to_score = {
            'highly_accommodative': -2,
            'accommodative': -1,
            'neutral': 0,
            'restrictive': 1,
            'highly_restrictive': 2
        }
        
        if 'stance' in df.columns:
            df['stance_score'] = df['stance'].map(stance_to_score)
            
            # Calculate trajectory
            start_score = df.iloc[0]['stance_score']
            end_score = df.iloc[-1]['stance_score']
            change = end_score - start_score
            
            if change > 1:
                trajectory = "tightening"
                description = f"Policy has shifted toward restriction (score: {start_score} → {end_score})"
            elif change < -1:
                trajectory = "easing"
                description = f"Policy has shifted toward accommodation (score: {start_score} → {end_score})"
            else:
                trajectory = "stable"
                description = f"Policy stance relatively stable (score: {start_score} → {end_score})"
            
            return {
                'trajectory': trajectory,
                'start_stance': df.iloc[0]['stance'],
                'end_stance': df.iloc[-1]['stance'],
                'change': change,
                'description': description,
                'num_meetings': len(df)
            }
        
        return {'error': 'No stance data in meetings'}


def classify_policy_stance(meeting_data: List[Dict], economic_data: Optional[Dict] = None) -> Dict:
    """
    Convenience function for complete stance classification.
    
    Args:
        meeting_data: List of meeting data
        economic_data: Optional economic conditions data
    
    Returns:
        Complete stance analysis
    """
    classifier = StanceClassifier()
    
    # Extract recent actions and sentiments
    actions = [m.get('action') for m in meeting_data[-6:] if m.get('action')]
    sentiments = [m.get('sentiment_score', 0) for m in meeting_data[-6:]]
    
    # Get rate data if available
    fed_funds = economic_data.get('fed_funds') if economic_data else None
    real_rate = economic_data.get('real_rate') if economic_data else None
    inflation = economic_data.get('inflation') if economic_data else None
    
    overall_stance = classifier.classify_overall_stance(
        actions, sentiments, fed_funds, real_rate, inflation
    )
    
    # Compare to conditions if available
    if economic_data and all(k in economic_data for k in ['inflation', 'unemployment', 'gdp_growth']):
        conditions_comparison = classifier.compare_stance_to_conditions(
            overall_stance['stance'],
            economic_data['inflation'],
            economic_data['unemployment'],
            economic_data['gdp_growth']
        )
    else:
        conditions_comparison = None
    
    # Trajectory
    trajectory = classifier.get_stance_trajectory(meeting_data)
    
    return {
        'overall_stance': overall_stance,
        'conditions_comparison': conditions_comparison,
        'trajectory': trajectory
    }
