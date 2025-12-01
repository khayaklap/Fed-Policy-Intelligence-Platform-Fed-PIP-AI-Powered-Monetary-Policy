"""
Query Router

Analyzes user queries and determines which agents to invoke.
"""

import logging
from typing import Dict, List, Optional, Tuple
import re

try:
    # Try relative imports first (when used as module)
    from .orchestrator_config import (
        AGENT_REGISTRY,
        ROUTING_KEYWORDS,
        QUERY_TYPES,
        ROUTING_THRESHOLDS
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from orchestrator_config import (
        AGENT_REGISTRY,
        ROUTING_KEYWORDS,
        QUERY_TYPES,
        ROUTING_THRESHOLDS
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryRouter:
    """
    Route queries to appropriate agents based on content analysis.
    """
    
    def __init__(self):
        """Initialize query router."""
        logger.info("Initialized Query Router")
    
    def route_query(self, query: str, context: Optional[Dict] = None) -> Dict:
        """
        Analyze query and determine which agents to use.
        
        Args:
            query: User query string
            context: Optional conversation context
        
        Returns:
            Dictionary with:
            - query_type: Classified query type
            - required_agents: List of required agents
            - optional_agents: List of optional agents
            - confidence: Routing confidence (0-1)
            - reasoning: Why these agents were selected
        """
        logger.info(f"Routing query: {query[:100]}...")
        
        # Normalize query
        query_lower = query.lower()
        
        # Detect query type
        query_type, type_confidence = self._classify_query_type(query_lower)
        
        # Score all agents
        agent_scores = self._score_agents(query_lower)
        
        # Select agents based on scores and query type
        required_agents, optional_agents = self._select_agents(
            query_type,
            agent_scores
        )
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(type_confidence, agent_scores)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(query_type, required_agents, agent_scores)
        
        return {
            'query_type': query_type,
            'required_agents': required_agents,
            'optional_agents': optional_agents,
            'confidence': round(confidence, 3),
            'reasoning': reasoning,
            'agent_scores': {k: round(v, 3) for k, v in agent_scores.items()}
        }
    
    def _classify_query_type(self, query: str) -> Tuple[str, float]:
        """
        Classify query into predefined types.
        
        Returns:
            (query_type, confidence)
        """
        type_scores = {}
        
        for qtype, config in QUERY_TYPES.items():
            score = 0.0
            
            # Check example similarity
            if 'example' in config:
                example_words = set(config['example'].lower().split())
                query_words = set(query.split())
                overlap = len(example_words & query_words)
                if overlap > 0:
                    score += overlap * 0.1
            
            # Check for type-specific keywords
            if qtype == "meeting_analysis" and any(w in query for w in ["meeting", "fomc", "minutes", "analyze"]):
                score += 0.5
            elif qtype == "current_stance" and any(w in query for w in ["current", "now", "stance", "policy"]):
                score += 0.5
            elif qtype == "trend_analysis" and any(w in query for w in ["trend", "evolution", "over time", "years"]):
                score += 0.5
            elif qtype == "historical_comparison" and any(w in query for w in ["compare", "similar", "like", "versus"]):
                score += 0.5
            elif qtype == "comprehensive_analysis" and any(w in query for w in ["comprehensive", "complete", "full analysis"]):
                score += 0.7
            elif qtype == "economic_context" and any(w in query for w in ["inflation", "unemployment", "gdp", "economy"]):
                score += 0.4
            elif qtype == "prediction" and any(w in query for w in ["predict", "next", "will", "likely", "forecast"]):
                score += 0.5
            elif qtype == "report_generation" and any(w in query for w in ["report", "generate", "create", "pdf", "summary"]):
                score += 0.6
            
            type_scores[qtype] = score
        
        # Get best match
        if type_scores:
            best_type = max(type_scores.items(), key=lambda x: x[1])
            return best_type[0], min(best_type[1], 1.0)
        
        # Default to comprehensive
        return "comprehensive_analysis", 0.5
    
    def _score_agents(self, query: str) -> Dict[str, float]:
        """
        Score each agent's relevance to query.
        
        Returns:
            Dictionary of {agent_name: score}
        """
        agent_scores = {}
        
        for agent_name, keywords in ROUTING_KEYWORDS.items():
            score = 0.0
            
            # Primary keywords (high weight)
            for keyword in keywords['primary']:
                if keyword in query:
                    score += 0.3
            
            # Secondary keywords (low weight)
            for keyword in keywords['secondary']:
                if keyword in query:
                    score += 0.1
            
            # Cap at 1.0
            agent_scores[agent_name] = min(score, 1.0)
        
        return agent_scores
    
    def _select_agents(
        self,
        query_type: str,
        agent_scores: Dict[str, float]
    ) -> Tuple[List[str], List[str]]:
        """
        Select required and optional agents.
        
        Returns:
            (required_agents, optional_agents)
        """
        query_config = QUERY_TYPES.get(query_type, {})
        
        # Get agents from query type config
        required = query_config.get('required_agents', [])
        optional = query_config.get('optional_agents', [])
        
        # Add high-scoring agents not already in lists
        for agent, score in agent_scores.items():
            if score >= 0.5 and agent not in required and agent not in optional:
                optional.append(agent)
        
        return required, optional
    
    def _calculate_confidence(
        self,
        type_confidence: float,
        agent_scores: Dict[str, float]
    ) -> float:
        """Calculate overall routing confidence."""
        
        # Average agent scores
        if agent_scores:
            avg_agent_score = sum(agent_scores.values()) / len(agent_scores)
        else:
            avg_agent_score = 0.0
        
        # Weighted combination
        confidence = (type_confidence * 0.6) + (avg_agent_score * 0.4)
        
        return confidence
    
    def _generate_reasoning(
        self,
        query_type: str,
        agents: List[str],
        scores: Dict[str, float]
    ) -> str:
        """Generate explanation for routing decision."""
        
        reasoning = f"Query classified as '{query_type}'. "
        
        if agents:
            reasoning += f"Using {len(agents)} agent(s): {', '.join(agents)}. "
        
        # Mention high-scoring agents
        high_scorers = [name for name, score in scores.items() if score >= 0.5]
        if high_scorers:
            reasoning += f"High relevance: {', '.join(high_scorers)}."
        
        return reasoning
    
    def suggest_clarification(self, query: str, routing_result: Dict) -> Optional[str]:
        """
        Suggest clarification if routing confidence is low.
        
        Returns:
            Clarification question or None
        """
        confidence = routing_result['confidence']
        
        if confidence < ROUTING_THRESHOLDS['clarification_needed']:
            return (
                "I'm not entirely sure how to help with that. "
                "Could you clarify if you want:\n"
                "1. Analysis of a specific FOMC meeting?\n"
                "2. Current Fed policy stance?\n"
                "3. Historical comparison to past episodes?\n"
                "4. Long-term trend analysis?\n"
                "5. A comprehensive report?"
            )
        
        return None
    
    def extract_parameters(self, query: str) -> Dict:
        """
        Extract parameters from query (dates, episodes, formats, etc.).
        
        Returns:
            Dictionary of extracted parameters
        """
        params = {}
        
        # Extract dates (YYYY-MM-DD or Month YYYY)
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # 2024-11-07
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',  # November 2024
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, query)
            if matches:
                params['dates'] = matches
                break
        
        # Extract episode names
        episode_keywords = [
            'gfc', 'covid', 'volcker', 'inflation fight',
            '2008', '2020', '2022', 'great financial crisis',
            'pandemic'
        ]
        
        episodes = []
        query_lower = query.lower()
        for keyword in episode_keywords:
            if keyword in query_lower:
                episodes.append(keyword)
        
        if episodes:
            params['episodes'] = episodes
        
        # Extract output format
        format_keywords = {
            'pdf': 'pdf',
            'word': 'docx',
            'docx': 'docx',
            'html': 'html',
            'markdown': 'markdown',
            'json': 'json'
        }
        
        for keyword, format_type in format_keywords.items():
            if keyword in query_lower:
                params['output_format'] = format_type
                break
        
        # Extract time periods
        if 'last' in query_lower:
            # "last 5 years", "last quarter", etc.
            time_match = re.search(r'last\s+(\d+)\s+(year|month|quarter)', query_lower)
            if time_match:
                params['time_period'] = {
                    'value': int(time_match.group(1)),
                    'unit': time_match.group(2)
                }
        
        return params


def route_user_query(query: str, context: Optional[Dict] = None) -> Dict:
    """
    Convenience function to route a query.
    
    Args:
        query: User query
        context: Optional context
    
    Returns:
        Routing result
    """
    router = QueryRouter()
    return router.route_query(query, context)
