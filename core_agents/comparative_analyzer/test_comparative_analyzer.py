"""
Comparative Analyzer Tests

Comprehensive test suite for episode comparisons, pattern matching,
and cross-episode analysis.
"""

import pytest
import sys

# Add parent directory to path for imports
sys.path.insert(0, '.')

try:
    # Try relative imports first (when used as module)
    from .episode_comparator import EpisodeComparator
    from .pattern_matcher import PatternMatcher
    from .cross_episode_analyzer import CrossEpisodeAnalyzer
    
    from .comparative_analyzer_tools import (
        compare_episodes_tool,
        identify_pattern_tool,
        find_similar_episodes_tool,
        compare_fed_chairs_tool,
        extract_lessons_tool,
        list_available_episodes,
        list_available_chairs
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from episode_comparator import EpisodeComparator
    from pattern_matcher import PatternMatcher
    from cross_episode_analyzer import CrossEpisodeAnalyzer
    
    from comparative_analyzer_tools import (
        compare_episodes_tool,
        identify_pattern_tool,
        find_similar_episodes_tool,
        compare_fed_chairs_tool,
        extract_lessons_tool,
        list_available_episodes,
        list_available_chairs
    )


# ============================================================================
# TEST DATA
# ============================================================================

# Sample meeting data for pattern testing
GRADUAL_TIGHTENING_DATA = [
    {'date': '2022-03-16', 'action': 'increase', 'score': 5},
    {'date': '2022-05-04', 'action': 'increase', 'score': 8},
    {'date': '2022-06-15', 'action': 'increase', 'score': 12},
    {'date': '2022-07-27', 'action': 'increase', 'score': 14},
    {'date': '2022-09-21', 'action': 'increase', 'score': 16},
    {'date': '2022-11-02', 'action': 'increase', 'score': 18},
    {'date': '2022-12-14', 'action': 'increase', 'score': 17},
    {'date': '2023-02-01', 'action': 'increase', 'score': 15}
]

EMERGENCY_EASING_DATA = [
    {'date': '2020-03-03', 'action': 'decrease', 'score': -5},
    {'date': '2020-03-15', 'action': 'decrease', 'score': -15},
    {'date': '2020-04-29', 'action': 'unchanged', 'score': -18},
    {'date': '2020-06-10', 'action': 'unchanged', 'score': -16},
    {'date': '2020-07-29', 'action': 'unchanged', 'score': -14},
    {'date': '2020-09-16', 'action': 'unchanged', 'score': -12}
]

PIVOT_DATA = [
    {'date': '2018-09-26', 'action': 'increase', 'score': 12},
    {'date': '2018-11-08', 'action': 'unchanged', 'score': 10},
    {'date': '2018-12-19', 'action': 'increase', 'score': 8},
    {'date': '2019-01-30', 'action': 'unchanged', 'score': 2},
    {'date': '2019-03-20', 'action': 'unchanged', 'score': -2},
    {'date': '2019-06-19', 'action': 'unchanged', 'score': -5},
    {'date': '2019-07-31', 'action': 'decrease', 'score': -8},
    {'date': '2019-09-18', 'action': 'decrease', 'score': -10}
]


# ============================================================================
# EPISODE COMPARATOR TESTS
# ============================================================================

class TestEpisodeComparator:
    """Test episode comparison functionality."""
    
    def test_compare_two_episodes(self):
        """Test comparing two policy episodes."""
        comparator = EpisodeComparator()
        
        result = comparator.compare_episodes(
            'gfc_response_2007_2008',
            'covid_response_2020'
        )
        
        # Check structure
        assert 'overall_similarity' in result
        assert 'similarity_classification' in result
        assert 'dimension_scores' in result
        assert 'key_similarities' in result
        assert 'key_differences' in result
        assert 'lessons' in result
        assert 'interpretation' in result
        
        # Check similarity score is valid
        assert 0 <= result['overall_similarity'] <= 1
        
        # Check dimensions
        assert 'speed' in result['dimension_scores']
        assert 'magnitude' in result['dimension_scores']
        assert 'duration' in result['dimension_scores']
        
        # Should have some similarities (both crises)
        assert len(result['key_similarities']) > 0
        
        print(f"\nGFC vs COVID similarity: {result['overall_similarity']:.3f}")
        print(f"Classification: {result['similarity_classification']}")
    
    def test_rank_similar_episodes(self):
        """Test ranking episodes by similarity."""
        comparator = EpisodeComparator()
        
        result = comparator.rank_similar_episodes(
            target_episode='inflation_fight_2022_2023'
        )
        
        # Should return ranked list
        assert len(result) > 0
        assert isinstance(result, list)
        
        # First result should have highest similarity
        if len(result) >= 2:
            assert result[0]['similarity'] >= result[1]['similarity']
        
        print(f"\nTop 3 episodes similar to 2022 inflation fight:")
        for i, ep in enumerate(result[:3]):
            print(f"{i+1}. {ep['name']}: {ep['similarity']:.3f}")


# ============================================================================
# PATTERN MATCHER TESTS
# ============================================================================

class TestPatternMatcher:
    """Test pattern identification functionality."""
    
    def test_identify_gradual_tightening(self):
        """Test gradual tightening pattern identification."""
        matcher = PatternMatcher()
        
        result = matcher.identify_pattern(GRADUAL_TIGHTENING_DATA)
        
        # Check structure
        assert 'best_match' in result
        assert 'all_matches' in result
        assert 'features' in result
        assert 'interpretation' in result
        
        # Should identify gradual tightening
        assert result['best_match']['pattern'] == 'gradual_tightening'
        
        # Check features
        features = result['features']
        assert features['num_increases'] > features['num_decreases']
        assert features['trend'] > 0  # Hawkish trend
        
        print(f"\nGradual tightening pattern score: {result['best_match']['score']:.3f}")
    
    def test_insufficient_data(self):
        """Test handling of insufficient data."""
        matcher = PatternMatcher()
        
        result = matcher.identify_pattern(
            GRADUAL_TIGHTENING_DATA[:3],  # Only 3 meetings
            min_meetings=6
        )
        
        # Should return error
        assert 'error' in result


# ============================================================================
# CROSS-EPISODE ANALYZER TESTS
# ============================================================================

class TestCrossEpisodeAnalyzer:
    """Test cross-episode analysis functionality."""
    
    def test_compare_fed_chairs(self):
        """Test Fed chair comparison."""
        analyzer = CrossEpisodeAnalyzer()
        
        result = analyzer.compare_fed_chairs(
            'ben_bernanke',
            'jerome_powell'
        )
        
        # Check structure
        assert 'chair1' in result
        assert 'chair2' in result
        assert 'style_differences' in result
        assert 'episode_comparison' in result
        assert 'notable_achievements' in result
        assert 'interpretation' in result
        
        # Check chair details
        assert result['chair1']['name'] == 'Ben Bernanke'
        assert result['chair2']['name'] == 'Jerome Powell'
        assert result['chair1']['tenure_years'] > 0
        
        print(f"\nBernanke vs Powell:")
        print(f"Tenure: {result['chair1']['tenure_years']} vs {result['chair2']['tenure_years']} years")
    
    def test_extract_lessons(self):
        """Test lesson extraction from episodes."""
        analyzer = CrossEpisodeAnalyzer()
        
        result = analyzer.extract_lessons_learned([
            'gfc_response_2007_2008',
            'covid_response_2020',
            'inflation_fight_2022_2023'
        ])
        
        # Check structure
        assert 'lessons_by_category' in result
        assert 'num_episodes_analyzed' in result
        assert 'key_takeaways' in result
        
        # Should have 5 categories
        assert 'timing' in result['lessons_by_category']
        assert 'magnitude' in result['lessons_by_category']
        
        print(f"\nLessons from 3 episodes:")
        print(f"Episodes analyzed: {result['num_episodes_analyzed']}")


# ============================================================================
# TOOL TESTS
# ============================================================================

class TestTools:
    """Test all ADK tools."""
    
    def test_compare_episodes_tool(self):
        """Test compare episodes tool."""
        result = compare_episodes_tool(
            'gfc_response_2007_2008',
            'covid_response_2020'
        )
        
        assert 'error' not in result
        assert 'overall_similarity' in result
        
        print(f"\ncompare_episodes_tool: {result['overall_similarity']:.3f} similarity")
    
    def test_identify_pattern_tool(self):
        """Test identify pattern tool."""
        result = identify_pattern_tool(GRADUAL_TIGHTENING_DATA)
        
        assert 'error' not in result
        assert 'best_match' in result
        
        print(f"\nidentify_pattern_tool: {result['best_match']['pattern']}")
    
    def test_find_similar_episodes_tool(self):
        """Test find similar episodes tool."""
        result = find_similar_episodes_tool(
            'inflation_fight_2022_2023',
            top_n=3
        )
        
        assert len(result) <= 3
        
        print(f"\nfind_similar_episodes_tool: Found {len(result)} episodes")
    
    def test_compare_fed_chairs_tool(self):
        """Test compare Fed chairs tool."""
        result = compare_fed_chairs_tool(
            'ben_bernanke',
            'jerome_powell'
        )
        
        assert 'error' not in result
        assert 'chair1' in result
        
        print(f"\ncompare_fed_chairs_tool: {result['chair1']['name']} vs {result['chair2']['name']}")
    
    def test_extract_lessons_tool(self):
        """Test extract lessons tool."""
        result = extract_lessons_tool([
            'gfc_response_2007_2008',
            'covid_response_2020'
        ])
        
        assert 'error' not in result
        assert 'lessons_by_category' in result
        
        print(f"\nextract_lessons_tool: {len(result['key_takeaways'])} takeaways")


# ============================================================================
# EXAMPLE USAGE DEMONSTRATIONS
# ============================================================================

def example_compare_crisis_responses():
    """Example: Compare GFC and COVID crisis responses."""
    print("\n" + "="*80)
    print("EXAMPLE: Compare GFC vs COVID crisis responses")
    print("="*80)
    
    result = compare_episodes_tool(
        'gfc_response_2007_2008',
        'covid_response_2020'
    )
    
    print(f"\nOverall Similarity: {result['overall_similarity']:.3f}")
    print(f"Classification: {result['similarity_classification']}")
    
    print(f"\nDimension Scores:")
    for dim, score in result['dimension_scores'].items():
        print(f"  {dim}: {score:.3f}")


def example_identify_current_pattern():
    """Example: Identify pattern in recent Fed policy."""
    print("\n" + "="*80)
    print("EXAMPLE: Identify pattern in 2022-2023 tightening cycle")
    print("="*80)
    
    result = identify_pattern_tool(GRADUAL_TIGHTENING_DATA)
    
    print(f"\nBest Match: {result['best_match']['pattern']}")
    print(f"Confidence: {result['best_match']['confidence']}")
    print(f"Score: {result['best_match']['score']:.3f}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("COMPARATIVE ANALYZER TEST SUITE")
    print("="*80)
    
    # Run pytest
    pytest.main([__file__, '-v', '--tb=short'])
    
    # Run examples
    print("\n\n" + "="*80)
    print("EXAMPLE DEMONSTRATIONS")
    print("="*80)
    
    example_compare_crisis_responses()
    example_identify_current_pattern()
    
    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80)
