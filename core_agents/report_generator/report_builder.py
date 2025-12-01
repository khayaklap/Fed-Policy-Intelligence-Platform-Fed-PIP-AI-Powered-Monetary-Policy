"""
Report Builder

Core report construction logic for aggregating data from multiple agents
and building structured reports.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

try:
    # Try relative imports first (when used as module)
    from .report_generator_config import (
        REPORT_TYPES,
        SECTION_TEMPLATES,
        REPORT_METADATA,
        VALIDATION_RULES
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from report_generator_config import (
        REPORT_TYPES,
        SECTION_TEMPLATES,
        REPORT_METADATA,
        VALIDATION_RULES
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportBuilder:
    """
    Build Fed policy reports by aggregating data from multiple agents.
    """
    
    def __init__(self):
        """Initialize report builder."""
        logger.info("Initialized Report Builder")
        self.metadata = REPORT_METADATA.copy()
    
    def build_comprehensive_report(
        self,
        agent_data: Dict,
        time_period: Optional[tuple] = None
    ) -> Dict:
        """
        Build comprehensive Fed policy analysis report.
        
        Args:
            agent_data: Dictionary with data from all agents:
                {
                    'document_processor': {...},
                    'policy_analyzer': {...},
                    'trend_tracker': {...},
                    'comparative_analyzer': {...},
                    'fred': {...},
                    'bls': {...},
                    'treasury': {...}
                }
            time_period: Optional (start_date, end_date) tuple
        
        Returns:
            Dictionary with complete report structure
        """
        logger.info("Building comprehensive report")
        
        report = self._initialize_report("comprehensive_analysis", time_period)
        
        # Build each section
        report['sections'] = []
        
        # 1. Executive Summary
        report['sections'].append(
            self._build_executive_summary(agent_data)
        )
        
        # 2. Current Policy Stance
        if 'document_processor' in agent_data and 'policy_analyzer' in agent_data:
            report['sections'].append(
                self._build_current_stance_section(
                    agent_data['document_processor'],
                    agent_data['policy_analyzer']
                )
            )
        
        # 3. Recent Trends
        if 'policy_analyzer' in agent_data:
            report['sections'].append(
                self._build_recent_trends_section(agent_data['policy_analyzer'])
            )
        
        # 4. Long-Term Patterns
        if 'trend_tracker' in agent_data:
            report['sections'].append(
                self._build_long_term_section(agent_data['trend_tracker'])
            )
        
        # 5. Historical Comparisons
        if 'comparative_analyzer' in agent_data:
            report['sections'].append(
                self._build_historical_comparisons_section(
                    agent_data['comparative_analyzer']
                )
            )
        
        # 6. Economic Context
        if any(k in agent_data for k in ['fred', 'bls', 'treasury']):
            report['sections'].append(
                self._build_economic_context_section(agent_data)
            )
        
        # 7. Predictive Indicators
        if 'trend_tracker' in agent_data:
            report['sections'].append(
                self._build_predictive_indicators_section(
                    agent_data['trend_tracker']
                )
            )
        
        # 8. Recommendations
        report['sections'].append(
            self._build_recommendations_section(agent_data)
        )
        
        # Validate and finalize
        report = self._validate_report(report)
        
        logger.info(f"Comprehensive report built with {len(report['sections'])} sections")
        return report
    
    def build_episode_comparison_report(
        self,
        comparison_data: Dict,
        episode1: str,
        episode2: str
    ) -> Dict:
        """
        Build episode comparison report.
        
        Args:
            comparison_data: Data from comparative_analyzer
            episode1: First episode key
            episode2: Second episode key
        
        Returns:
            Report dictionary
        """
        logger.info(f"Building episode comparison report: {episode1} vs {episode2}")
        
        report = self._initialize_report("episode_comparison")
        
        report['sections'] = [
            self._build_executive_summary(
                {'comparative_analyzer': comparison_data},
                focus="comparison"
            ),
            self._build_episode_overview_section(comparison_data, episode1, episode2),
            self._build_detailed_comparison_section(comparison_data),
            self._build_similarity_analysis_section(comparison_data),
            self._build_lessons_learned_section(comparison_data),
            self._build_implications_section(comparison_data)
        ]
        
        report = self._validate_report(report)
        
        logger.info("Episode comparison report built")
        return report
    
    def build_quick_summary(
        self,
        recent_meetings: List[Dict],
        policy_data: Dict
    ) -> Dict:
        """
        Build quick summary report (2-3 pages).
        
        Args:
            recent_meetings: List of recent meeting analyses
            policy_data: Current policy stance data
        
        Returns:
            Report dictionary
        """
        logger.info("Building quick summary")
        
        report = self._initialize_report("quick_summary")
        
        report['sections'] = [
            self._build_current_stance_summary(recent_meetings, policy_data),
            self._build_recent_actions_summary(recent_meetings),
            self._build_key_metrics_summary(policy_data),
            self._build_outlook_summary(policy_data)
        ]
        
        report = self._validate_report(report)
        
        logger.info("Quick summary built")
        return report
    
    def build_custom_report(
        self,
        sections: List[str],
        agent_data: Dict,
        title: Optional[str] = None
    ) -> Dict:
        """
        Build custom report with specified sections.
        
        Args:
            sections: List of section names to include
            agent_data: Data from agents
            title: Optional custom title
        
        Returns:
            Report dictionary
        """
        logger.info(f"Building custom report with {len(sections)} sections")
        
        report = self._initialize_report("custom", title=title)
        
        report['sections'] = []
        for section_name in sections:
            section = self._build_section(section_name, agent_data)
            if section:
                report['sections'].append(section)
        
        report = self._validate_report(report)
        
        logger.info("Custom report built")
        return report
    
    # ========================================================================
    # SECTION BUILDERS
    # ========================================================================
    
    def _build_executive_summary(
        self,
        agent_data: Dict,
        focus: str = "comprehensive"
    ) -> Dict:
        """Build executive summary section."""
        
        logger.info("Building executive summary")
        
        summary_points = []
        
        # Current stance
        if 'policy_analyzer' in agent_data:
            stance = agent_data['policy_analyzer'].get('current_stance', {})
            if stance:
                summary_points.append(
                    f"Current Fed stance: {stance.get('classification', 'Unknown')}"
                )
        
        # Recent trend
        if 'policy_analyzer' in agent_data:
            trend = agent_data['policy_analyzer'].get('sentiment_trend', {})
            if trend:
                summary_points.append(
                    f"Recent trend: {trend.get('direction', 'stable')} "
                    f"({trend.get('interpretation', '')})"
                )
        
        # Cycle position
        if 'trend_tracker' in agent_data:
            cycles = agent_data['trend_tracker'].get('policy_cycles', {})
            if cycles:
                summary_points.append(
                    f"Cycle phase: {cycles.get('current_phase', 'Unknown')}"
                )
        
        # Historical comparison
        if 'comparative_analyzer' in agent_data:
            comp = agent_data['comparative_analyzer'].get('most_similar', {})
            if comp:
                summary_points.append(
                    f"Most similar to: {comp.get('name', 'N/A')} "
                    f"({comp.get('similarity', 0):.2f} similarity)"
                )
        
        # Prediction
        if 'trend_tracker' in agent_data:
            prediction = agent_data['trend_tracker'].get('prediction', {})
            if prediction:
                summary_points.append(
                    f"Next likely action: {prediction.get('predicted_action', 'Unchanged')} "
                    f"(confidence: {prediction.get('confidence', 0):.2f})"
                )
        
        return {
            'title': 'Executive Summary',
            'type': 'summary',
            'content': {
                'key_points': summary_points[:5],  # Top 5
                'word_count': sum(len(p.split()) for p in summary_points)
            }
        }
    
    def _build_current_stance_section(
        self,
        doc_data: Dict,
        policy_data: Dict
    ) -> Dict:
        """Build current policy stance section."""
        
        logger.info("Building current stance section")
        
        # Get most recent meeting
        recent_meeting = doc_data.get('most_recent_meeting', {})
        
        # Get current stance
        current_stance = policy_data.get('current_stance', {})
        
        content = {
            'fed_funds_rate': recent_meeting.get('fed_funds', 'N/A'),
            'recent_action': recent_meeting.get('action', 'N/A'),
            'sentiment': recent_meeting.get('sentiment', 'N/A'),
            'score': recent_meeting.get('score', 0),
            'forward_guidance': recent_meeting.get('forward_guidance', 'N/A'),
            'stance_classification': current_stance.get('classification', 'N/A'),
            'appropriateness': current_stance.get('appropriateness', 'N/A')
        }
        
        return {
            'title': 'Current Policy Stance',
            'type': 'analysis',
            'content': content,
            'visualization': {
                'type': 'gauge_chart',
                'data': {
                    'score': content['score'],
                    'sentiment': content['sentiment']
                }
            }
        }
    
    def _build_recent_trends_section(self, policy_data: Dict) -> Dict:
        """Build recent trends section."""
        
        logger.info("Building recent trends section")
        
        sentiment_trend = policy_data.get('sentiment_trend', {})
        regime_changes = policy_data.get('regime_changes', {})
        
        content = {
            'trend_direction': sentiment_trend.get('direction', 'Unknown'),
            'strength': sentiment_trend.get('strength', 'N/A'),
            'duration': sentiment_trend.get('duration', 0),
            'regime_changes': regime_changes.get('num_changes', 0),
            'current_regime': regime_changes.get('current_regime', 'Unknown'),
            'interpretation': sentiment_trend.get('interpretation', '')
        }
        
        return {
            'title': 'Recent Policy Trends (1.5-6 years)',
            'type': 'analysis',
            'content': content,
            'visualization': {
                'type': 'time_series',
                'data': sentiment_trend.get('historical_data', [])
            }
        }
    
    def _build_long_term_section(self, trend_data: Dict) -> Dict:
        """Build long-term patterns section."""
        
        logger.info("Building long-term patterns section")
        
        long_term = trend_data.get('long_term_trends', {})
        cycles = trend_data.get('policy_cycles', {})
        reaction = trend_data.get('reaction_function', {})
        
        content = {
            'structural_breaks': long_term.get('changepoints', []),
            'cycle_phase': cycles.get('current_phase', 'Unknown'),
            'cycle_duration': cycles.get('duration', 0),
            'taylor_rule_fit': reaction.get('r_squared', 0),
            'inflation_coefficient': reaction.get('inflation_coef', 0),
            'interpretation': long_term.get('interpretation', '')
        }
        
        return {
            'title': 'Long-Term Patterns (6-20 years)',
            'type': 'analysis',
            'content': content,
            'visualization': {
                'type': 'cycle_chart',
                'data': cycles.get('peaks_and_troughs', {})
            }
        }
    
    def _build_historical_comparisons_section(self, comp_data: Dict) -> Dict:
        """Build historical comparisons section."""
        
        logger.info("Building historical comparisons section")
        
        similar_episodes = comp_data.get('similar_episodes', [])
        pattern = comp_data.get('pattern', {})
        lessons = comp_data.get('lessons', [])
        
        content = {
            'most_similar_episodes': similar_episodes[:3],  # Top 3
            'identified_pattern': pattern.get('pattern', 'Unknown'),
            'pattern_confidence': pattern.get('confidence', 'Low'),
            'key_lessons': lessons[:5]  # Top 5
        }
        
        return {
            'title': 'Historical Comparisons',
            'type': 'analysis',
            'content': content,
            'visualization': {
                'type': 'comparison_table',
                'data': similar_episodes
            }
        }
    
    def _build_economic_context_section(self, agent_data: Dict) -> Dict:
        """Build economic context section."""
        
        logger.info("Building economic context section")
        
        fred_data = agent_data.get('fred', {})
        bls_data = agent_data.get('bls', {})
        treasury_data = agent_data.get('treasury', {})
        
        content = {
            'inflation': fred_data.get('inflation', {}),
            'unemployment': fred_data.get('unemployment', {}),
            'gdp_growth': fred_data.get('gdp', {}),
            'cpi': bls_data.get('cpi', {}),
            'pce': bls_data.get('pce', {}),
            'yield_curve': treasury_data.get('yield_curve', {}),
            'market_expectations': treasury_data.get('expectations', {})
        }
        
        return {
            'title': 'Economic Context',
            'type': 'data',
            'content': content,
            'visualization': {
                'type': 'dashboard',
                'data': content
            }
        }
    
    def _build_predictive_indicators_section(self, trend_data: Dict) -> Dict:
        """Build predictive indicators section."""
        
        logger.info("Building predictive indicators section")
        
        indicators = trend_data.get('predictive_indicators', {})
        prediction = trend_data.get('prediction', {})
        
        content = {
            'active_indicators': indicators.get('active_indicators', []),
            'predicted_action': prediction.get('predicted_action', 'Unchanged'),
            'confidence': prediction.get('confidence', 0),
            'time_horizon': prediction.get('time_horizon', 'Unknown'),
            'supporting_signals': indicators.get('signals', [])
        }
        
        return {
            'title': 'Predictive Indicators',
            'type': 'forecast',
            'content': content,
            'visualization': {
                'type': 'indicator_panel',
                'data': indicators
            }
        }
    
    def _build_recommendations_section(self, agent_data: Dict) -> Dict:
        """Build recommendations section."""
        
        logger.info("Building recommendations section")
        
        recommendations = []
        
        # From policy stance
        if 'policy_analyzer' in agent_data:
            stance = agent_data['policy_analyzer'].get('current_stance', {})
            if stance.get('appropriateness') == 'too_tight':
                recommendations.append(
                    "Consider cuts - Policy appears too restrictive for current conditions"
                )
            elif stance.get('appropriateness') == 'too_loose':
                recommendations.append(
                    "Consider hikes - Policy appears too accommodative"
                )
        
        # From predictive indicators
        if 'trend_tracker' in agent_data:
            prediction = agent_data['trend_tracker'].get('prediction', {})
            if prediction.get('confidence', 0) >= 0.75:
                action = prediction.get('predicted_action', 'unchanged')
                recommendations.append(
                    f"High confidence next move: {action} "
                    f"(within {prediction.get('time_horizon', 'N/A')} meetings)"
                )
        
        # From historical lessons
        if 'comparative_analyzer' in agent_data:
            lessons = agent_data['comparative_analyzer'].get('lessons', [])
            for lesson in lessons[:2]:
                if 'implication' in lesson:
                    recommendations.append(lesson['implication'])
        
        return {
            'title': 'Key Takeaways & Recommendations',
            'type': 'recommendations',
            'content': {
                'recommendations': recommendations[:5]  # Top 5
            }
        }
    
    # Additional section builders would go here...
    def _build_episode_overview_section(self, data: Dict, ep1: str, ep2: str) -> Dict:
        """Build episode overview section."""
        return {
            'title': 'Episode Overview',
            'type': 'overview',
            'content': {
                'episode1': data.get('episode1', {}),
                'episode2': data.get('episode2', {})
            }
        }
    
    def _build_detailed_comparison_section(self, data: Dict) -> Dict:
        """Build detailed comparison section."""
        return {
            'title': 'Detailed Comparison',
            'type': 'comparison',
            'content': {
                'dimension_scores': data.get('dimension_scores', {}),
                'overall_similarity': data.get('overall_similarity', 0)
            }
        }
    
    def _build_similarity_analysis_section(self, data: Dict) -> Dict:
        """Build similarity analysis section."""
        return {
            'title': 'Similarity Analysis',
            'type': 'analysis',
            'content': {
                'classification': data.get('similarity_classification', ''),
                'similarities': data.get('key_similarities', []),
                'differences': data.get('key_differences', [])
            }
        }
    
    def _build_lessons_learned_section(self, data: Dict) -> Dict:
        """Build lessons learned section."""
        return {
            'title': 'Lessons Learned',
            'type': 'lessons',
            'content': {
                'lessons': data.get('lessons', [])
            }
        }
    
    def _build_implications_section(self, data: Dict) -> Dict:
        """Build implications section."""
        return {
            'title': 'Implications for Current Policy',
            'type': 'implications',
            'content': {
                'interpretation': data.get('interpretation', '')
            }
        }
    
    def _build_section(self, section_name: str, agent_data: Dict) -> Optional[Dict]:
        """Build a generic section."""
        # Implement generic section builder
        return None
    
    # Quick summary builders
    def _build_current_stance_summary(self, meetings: List, policy: Dict) -> Dict:
        return {'title': 'Current Stance', 'type': 'summary', 'content': {}}
    
    def _build_recent_actions_summary(self, meetings: List) -> Dict:
        return {'title': 'Recent Actions', 'type': 'summary', 'content': {}}
    
    def _build_key_metrics_summary(self, policy: Dict) -> Dict:
        return {'title': 'Key Metrics', 'type': 'summary', 'content': {}}
    
    def _build_outlook_summary(self, policy: Dict) -> Dict:
        return {'title': 'Outlook', 'type': 'summary', 'content': {}}
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _initialize_report(
        self,
        report_type: str,
        time_period: Optional[tuple] = None,
        title: Optional[str] = None
    ) -> Dict:
        """Initialize report structure."""
        
        report_config = REPORT_TYPES.get(report_type, {})
        
        return {
            'metadata': {
                **self.metadata,
                'report_type': report_type,
                'title': title or report_config.get('name', 'Fed Policy Report'),
                'generated_at': datetime.now().isoformat(),
                'time_period': time_period
            },
            'sections': []
        }
    
    def _validate_report(self, report: Dict) -> Dict:
        """Validate report against rules."""
        
        # Check minimum sections
        if len(report['sections']) < VALIDATION_RULES['min_sections']:
            logger.warning(f"Report has fewer than {VALIDATION_RULES['min_sections']} sections")
        
        # Add validation timestamp
        report['metadata']['validated_at'] = datetime.now().isoformat()
        
        return report
    
    def export_to_json(self, report: Dict) -> str:
        """Export report to JSON string."""
        return json.dumps(report, indent=2)
