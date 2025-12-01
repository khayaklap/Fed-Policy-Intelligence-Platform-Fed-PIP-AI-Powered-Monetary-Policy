"""
Comparative Analyzer Tools

Five ADK tools for comparing Fed policy episodes, identifying patterns,
and extracting lessons learned.
"""

import logging
from typing import Dict, List, Optional

try:
    # Try relative imports first (when used as module)
    from .episode_comparator import EpisodeComparator
    from .pattern_matcher import PatternMatcher
    from .cross_episode_analyzer import CrossEpisodeAnalyzer
    
    from .comparative_analyzer_config import POLICY_EPISODES, FED_CHAIRS
except ImportError:
    # Fall back to absolute imports (when run directly)
    from episode_comparator import EpisodeComparator
    from pattern_matcher import PatternMatcher
    from cross_episode_analyzer import CrossEpisodeAnalyzer
    
    from comparative_analyzer_config import POLICY_EPISODES, FED_CHAIRS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# TOOL 1: COMPARE TWO EPISODES
# ============================================================================

def compare_episodes_tool(
    episode1: str,
    episode2: str,
    method: str = 'weighted'
) -> Dict:
    """
    Compare two Fed policy episodes across multiple dimensions.
    
    This tool identifies similarities and differences between two historical
    Fed policy episodes, helping understand what strategies worked in different
    contexts and what lessons can be applied to current situations.
    
    Args:
        episode1: Key for first episode. Available episodes:
            - volcker_disinflation_1979_1982
            - greenspan_1987_crisis
            - dotcom_tightening_1999_2000
            - dotcom_bust_easing_2001
            - housing_boom_tightening_2004_2006
            - gfc_response_2007_2008
            - gfc_recovery_2009_2015
            - normalization_2015_2018
            - 2019_pivot
            - covid_response_2020
            - covid_recovery_2020_2021
            - inflation_fight_2022_2023
            - higher_for_longer_2023_2024
        episode2: Key for second episode (same options as episode1)
        method: Comparison method ('weighted', 'euclidean', 'cosine')
    
    Returns:
        Dictionary containing:
        - overall_similarity: Float 0-1 (1 = identical)
        - similarity_classification: very_similar, similar, somewhat_similar, dissimilar
        - dimension_scores: Scores for speed, magnitude, duration, economic_context, policy_tools, outcome
        - key_similarities: List of main similarities
        - key_differences: List of main differences
        - lessons: Lessons learned from comparison
        - interpretation: Human-readable summary
    
    Example:
        >>> result = compare_episodes_tool(
        ...     episode1='gfc_response_2007_2008',
        ...     episode2='covid_response_2020'
        ... )
        >>> print(result['overall_similarity'])
        0.73
        >>> print(result['key_similarities'])
        ['Both episodes: emergency_cuts', 'Similar speed: How quickly Fed acted']
    """
    logger.info(f"Tool called: compare_episodes({episode1}, {episode2})")
    
    try:
        comparator = EpisodeComparator()
        result = comparator.compare_episodes(episode1, episode2, method)
        
        logger.info(f"Comparison complete: {result['overall_similarity']} similarity")
        return result
        
    except Exception as e:
        logger.error(f"Error in compare_episodes_tool: {e}")
        return {
            'error': str(e),
            'message': 'Failed to compare episodes'
        }


# ============================================================================
# TOOL 2: IDENTIFY CURRENT PATTERN
# ============================================================================

def identify_pattern_tool(
    meeting_data: List[Dict],
    min_meetings: int = 6
) -> Dict:
    """
    Identify which known Fed policy pattern the current episode matches.
    
    This tool analyzes recent meeting data to identify recurring patterns like
    "gradual tightening", "emergency easing", "pivot", etc. Helps predict
    likely future Fed actions based on historical precedent.
    
    Args:
        meeting_data: List of recent meetings, each containing:
            - date: Meeting date
            - action: 'increase', 'decrease', or 'unchanged'
            - score: Sentiment score (-20 to +20)
            - sentiment: 'dovish', 'neutral', 'hawkish'
        min_meetings: Minimum meetings needed (default 6)
    
    Returns:
        Dictionary containing:
        - best_match: Best matching pattern with score and confidence
        - all_matches: All patterns scoring above 0.5 threshold
        - features: Extracted features (num_increases, volatility, trend, etc.)
        - interpretation: What this pattern implies for future policy
    
    Pattern Types Detected:
        - v_shaped_response: Rapid cuts followed by rapid hikes (e.g., 2020 COVID)
        - gradual_tightening: Slow, steady rate increases (e.g., 2004-2006)
        - emergency_easing: Fast, large cuts during crisis (e.g., 2008, 2020)
        - extended_pause: Long period at same rate (e.g., 2009-2015)
        - pivot: Sharp reversal in policy direction (e.g., 2019)
        - overshooting: Fed goes too far, then reverses (e.g., 2018)
    
    Example:
        >>> meetings = [
        ...     {'date': '2022-03-16', 'action': 'increase', 'score': 8},
        ...     {'date': '2022-05-04', 'action': 'increase', 'score': 12},
        ...     {'date': '2022-06-15', 'action': 'increase', 'score': 15},
        ...     # ... more meetings
        ... ]
        >>> result = identify_pattern_tool(meetings)
        >>> print(result['best_match']['pattern'])
        'gradual_tightening'
    """
    logger.info(f"Tool called: identify_pattern with {len(meeting_data)} meetings")
    
    try:
        matcher = PatternMatcher()
        result = matcher.identify_pattern(meeting_data, min_meetings)
        
        if 'best_match' in result:
            logger.info(f"Pattern identified: {result['best_match']['pattern']}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in identify_pattern_tool: {e}")
        return {
            'error': str(e),
            'message': 'Failed to identify pattern'
        }


# ============================================================================
# TOOL 3: FIND SIMILAR HISTORICAL EPISODES
# ============================================================================

def find_similar_episodes_tool(
    target_episode: str,
    top_n: int = 5
) -> List[Dict]:
    """
    Find historical episodes most similar to a target episode.
    
    This tool ranks all available historical episodes by their similarity
    to a target episode, helping identify the best historical comparisons
    for understanding likely outcomes.
    
    Args:
        target_episode: Episode to compare against (e.g., 'inflation_fight_2022_2023')
        top_n: Number of similar episodes to return (default 5)
    
    Returns:
        List of similar episodes, each containing:
        - episode: Episode key
        - name: Episode name
        - similarity: Similarity score 0-1
        - classification: very_similar, similar, somewhat_similar, dissimilar
        - key_similarities: Top 3 similarities
    
    Example:
        >>> result = find_similar_episodes_tool('inflation_fight_2022_2023', top_n=3)
        >>> for ep in result:
        ...     print(f"{ep['name']}: {ep['similarity']}")
        Volcker Disinflation: 0.68
        Housing Boom Normalization: 0.52
        Post-GFC Normalization: 0.48
    """
    logger.info(f"Tool called: find_similar_episodes for {target_episode}")
    
    try:
        comparator = EpisodeComparator()
        result = comparator.rank_similar_episodes(target_episode)
        
        # Return top N
        top_results = result[:top_n]
        
        logger.info(f"Found {len(top_results)} similar episodes")
        return top_results
        
    except Exception as e:
        logger.error(f"Error in find_similar_episodes_tool: {e}")
        return [{
            'error': str(e),
            'message': 'Failed to find similar episodes'
        }]


# ============================================================================
# TOOL 4: COMPARE FED CHAIRS
# ============================================================================

def compare_fed_chairs_tool(
    chair1: str,
    chair2: str
) -> Dict:
    """
    Compare two Fed chairs' approaches, styles, and effectiveness.
    
    This tool analyzes differences in policy philosophy, crisis management,
    and outcomes between different Fed chairs, helping understand how
    leadership affects monetary policy.
    
    Args:
        chair1: Key for first chair. Available chairs:
            - paul_volcker (1979-1987)
            - alan_greenspan (1987-2006)
            - ben_bernanke (2006-2014)
            - janet_yellen (2014-2018)
            - jerome_powell (2018-present)
        chair2: Key for second chair (same options)
    
    Returns:
        Dictionary containing:
        - chair1/chair2: Name, tenure, tenure_years, style
        - style_differences: List of key style differences
        - episode_comparison: Number and types of episodes handled
        - notable_achievements: What each chair is known for
        - interpretation: Summary of comparison
    
    Example:
        >>> result = compare_fed_chairs_tool('ben_bernanke', 'jerome_powell')
        >>> print(result['style_differences'])
        ['Ben Bernanke: innovative', 'Jerome Powell: pragmatic']
        >>> print(result['chair1']['notable_for'])
        ['GFC response', 'QE pioneer', 'Unconventional tools']
    """
    logger.info(f"Tool called: compare_fed_chairs({chair1}, {chair2})")
    
    try:
        analyzer = CrossEpisodeAnalyzer()
        result = analyzer.compare_fed_chairs(chair1, chair2)
        
        logger.info(f"Chair comparison complete")
        return result
        
    except Exception as e:
        logger.error(f"Error in compare_fed_chairs_tool: {e}")
        return {
            'error': str(e),
            'message': 'Failed to compare Fed chairs'
        }


# ============================================================================
# TOOL 5: EXTRACT LESSONS LEARNED
# ============================================================================

def extract_lessons_tool(
    episode_keys: List[str],
    categories: Optional[List[str]] = None
) -> Dict:
    """
    Extract lessons learned from multiple Fed policy episodes.
    
    This tool analyzes historical episodes to identify what worked, what
    didn't, and what lessons should guide future policy. Organizes lessons
    by category: timing, magnitude, communication, tools, and mistakes.
    
    Args:
        episode_keys: List of episode keys to analyze
        categories: Optional list of categories to focus on:
            - timing: When to act
            - magnitude: How much to move
            - communication: How to signal
            - tools: Which tools to use
            - mistakes: What went wrong
            If None, returns all categories.
    
    Returns:
        Dictionary containing:
        - lessons_by_category: Lessons organized by category
        - num_episodes_analyzed: Number of episodes examined
        - key_takeaways: Top 5 actionable insights
    
    Lesson Categories:
        - timing: "Act early for inflation", "Act big and fast in crisis"
        - magnitude: "Front-load when behind curve", "Gradual when uncertain"
        - communication: "Forward guidance critical", "Avoid premature commitments"
        - tools: "QE works at zero bound", "Conventional tools preferred"
        - mistakes: "Too slow to recognize inflation", "Tightened too much"
    
    Example:
        >>> episodes = [
        ...     'gfc_response_2007_2008',
        ...     'covid_response_2020',
        ...     'inflation_fight_2022_2023'
        ... ]
        >>> result = extract_lessons_tool(episodes)
        >>> for takeaway in result['key_takeaways']:
        ...     print(takeaway)
        Timing: Act early when warning signs appear
        Magnitude: Front-load when behind curve or in crisis
        Tools: Unconventional tools available when needed
    """
    logger.info(f"Tool called: extract_lessons from {len(episode_keys)} episodes")
    
    try:
        analyzer = CrossEpisodeAnalyzer()
        result = analyzer.extract_lessons_learned(episode_keys)
        
        # Filter by categories if specified
        if categories:
            filtered_lessons = {
                cat: result['lessons_by_category'][cat]
                for cat in categories
                if cat in result['lessons_by_category']
            }
            result['lessons_by_category'] = filtered_lessons
        
        logger.info(f"Extracted {len(result['lessons_by_category'])} lesson categories")
        return result
        
    except Exception as e:
        logger.error(f"Error in extract_lessons_tool: {e}")
        return {
            'error': str(e),
            'message': 'Failed to extract lessons'
        }


# ============================================================================
# HELPER: LIST AVAILABLE EPISODES
# ============================================================================

def list_available_episodes() -> Dict:
    """
    List all available policy episodes for comparison.
    
    Returns:
        Dictionary with episode keys, names, periods, and chairs
    """
    episodes = []
    
    for key, data in POLICY_EPISODES.items():
        episodes.append({
            'key': key,
            'name': data['name'],
            'period': data['period'],
            'chair': data['chair'],
            'context': data['context']
        })
    
    return {
        'num_episodes': len(episodes),
        'episodes': episodes
    }


# ============================================================================
# HELPER: LIST AVAILABLE CHAIRS
# ============================================================================

def list_available_chairs() -> Dict:
    """
    List all available Fed chairs for comparison.
    
    Returns:
        Dictionary with chair keys, names, and tenures
    """
    chairs = []
    
    for key, data in FED_CHAIRS.items():
        chairs.append({
            'key': key,
            'name': data['name'],
            'tenure': data['tenure'],
            'notable_for': data['notable_for']
        })
    
    return {
        'num_chairs': len(chairs),
        'chairs': chairs
    }
