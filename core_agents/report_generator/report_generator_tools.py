"""
Report Generator Tools

Five ADK tools for generating comprehensive Fed policy reports.
"""

import logging
from typing import Any, Dict, List, Optional

try:
    # Try relative imports first (when used as module)
    from .report_builder import ReportBuilder
    from .format_exporters import ReportExporter
    from .visualization_generator import VisualizationGenerator
    
    from .report_generator_config import REPORT_TYPES, OUTPUT_FORMATS
except ImportError:
    # Fall back to absolute imports (when run directly)
    from report_builder import ReportBuilder
    from format_exporters import ReportExporter
    from visualization_generator import VisualizationGenerator
    
    from report_generator_config import REPORT_TYPES, OUTPUT_FORMATS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# TOOL 1: GENERATE COMPREHENSIVE REPORT
# ============================================================================

def generate_comprehensive_report_tool(
    agent_data: Dict,
    time_period: Optional[tuple] = None,
    export_format: str = 'pdf'
) -> Dict:
    """
    Generate comprehensive Fed policy analysis report using all agents.
    
    This tool aggregates data from all available agents (Document Processor,
    Policy Analyzer, Trend Tracker, Comparative Analyzer, FRED, BLS, Treasury)
    to create a complete analysis report.
    
    Args:
        agent_data: Dictionary with data from agents:
            {
                'document_processor': {...},  # Recent meeting analyses
                'policy_analyzer': {...},      # Sentiment trends, regime changes
                'trend_tracker': {...},        # Long-term patterns, cycles
                'comparative_analyzer': {...}, # Historical comparisons
                'fred': {...},                 # Economic data
                'bls': {...},                  # Inflation/employment data
                'treasury': {...}              # Market expectations
            }
        time_period: Optional (start_date, end_date) tuple
        export_format: Output format ('pdf', 'docx', 'html', 'markdown', 'json')
    
    Returns:
        Dictionary containing:
        - report: Full report structure
        - metadata: Report metadata
        - sections: List of report sections
        - export_path: Path to exported file (if applicable)
        - summary: Executive summary
    
    Report Sections (8 total):
        1. Executive Summary - Key findings and recommendations
        2. Current Policy Stance - Fed funds rate, recent actions, sentiment
        3. Recent Trends (1.5-6 years) - Sentiment evolution, regime changes
        4. Long-Term Patterns (6-20 years) - Structural breaks, cycles
        5. Historical Comparisons - Similar episodes, pattern identification
        6. Economic Context - Inflation, unemployment, GDP, market expectations
        7. Predictive Indicators - Leading signals, next move prediction
        8. Recommendations - Key takeaways and implications
    
    Example:
        >>> # Gather data from all agents
        >>> data = {
        ...     'document_processor': analyze_fomc_minutes_tool(recent_file),
        ...     'policy_analyzer': analyze_sentiment_trend_tool(all_meetings),
        ...     'trend_tracker': analyze_long_term_trends_tool(all_meetings),
        ...     'comparative_analyzer': find_similar_episodes_tool('current'),
        ...     'fred': fred_get_inflation_data(),
        ...     'bls': bls_get_cpi(),
        ...     'treasury': treasury_get_yield_curve()
        ... }
        >>> 
        >>> report = generate_comprehensive_report_tool(data, export_format='pdf')
        >>> print(report['export_path'])
        'fed_policy_comprehensive_report_2024-11-29.pdf'
    """
    logger.info("Tool called: generate_comprehensive_report")
    
    try:
        builder = ReportBuilder()
        report = builder.build_comprehensive_report(agent_data, time_period)
        
        # Export if format specified
        export_path = None
        if export_format and export_format != 'json':
            exporter = ReportExporter()
            filename = f"fed_policy_comprehensive_report_{report['metadata']['generated_at'][:10]}"
            
            if export_format == 'pdf':
                export_path = exporter.export_to_pdf(report, filename)
            elif export_format == 'docx':
                export_path = exporter.export_to_docx(report, filename)
            elif export_format == 'html':
                export_path = exporter.export_to_html(report, filename)
            elif export_format == 'markdown':
                export_path = exporter.export_to_markdown(report, filename)
        
        # Extract summary
        summary_section = next(
            (s for s in report['sections'] if s['title'] == 'Executive Summary'),
            None
        )
        summary = summary_section['content'] if summary_section else {}
        
        logger.info(f"Comprehensive report generated with {len(report['sections'])} sections")
        
        return {
            'report': report,
            'metadata': report['metadata'],
            'sections': [s['title'] for s in report['sections']],
            'export_path': export_path,
            'summary': summary,
            'num_sections': len(report['sections'])
        }
        
    except Exception as e:
        logger.error(f"Error generating comprehensive report: {e}")
        return {
            'error': str(e),
            'message': 'Failed to generate comprehensive report'
        }


# ============================================================================
# TOOL 2: GENERATE EPISODE COMPARISON REPORT
# ============================================================================

def generate_episode_comparison_report_tool(
    episode1: str,
    episode2: str,
    comparison_data: Optional[Dict] = None,
    export_format: str = 'pdf'
) -> Dict:
    """
    Generate report comparing two Fed policy episodes.
    
    This tool creates a detailed comparison report analyzing similarities
    and differences between two historical Fed policy episodes.
    
    Args:
        episode1: First episode key (e.g., 'gfc_response_2007_2008')
        episode2: Second episode key (e.g., 'covid_response_2020')
        comparison_data: Optional pre-computed comparison data from comparative_analyzer
        export_format: Output format ('pdf', 'docx', 'html', 'markdown')
    
    Returns:
        Dictionary containing:
        - report: Full report structure
        - metadata: Report metadata
        - export_path: Path to exported file
        - similarity_score: Overall similarity (0-1)
        - key_findings: Main similarities and differences
    
    Report Sections (6 total):
        1. Executive Summary
        2. Episode Overview - Context and key features
        3. Detailed Comparison - Dimension-by-dimension analysis
        4. Similarity Analysis - What's similar, what's different
        5. Lessons Learned - What history teaches
        6. Implications - Relevance for current policy
    
    Example:
        >>> report = generate_episode_comparison_report_tool(
        ...     episode1='gfc_response_2007_2008',
        ...     episode2='covid_response_2020',
        ...     export_format='pdf'
        ... )
        >>> print(f"Similarity: {report['similarity_score']:.3f}")
        Similarity: 0.730
        >>> print(report['export_path'])
        'episode_comparison_gfc_vs_covid_2024-11-29.pdf'
    """
    logger.info(f"Tool called: generate_episode_comparison_report({episode1}, {episode2})")
    
    try:
        # Get comparison data if not provided
        if comparison_data is None:
            try:
                # Try to import from sibling comparative_analyzer agent
                from ..comparative_analyzer.comparative_analyzer_tools import compare_episodes_tool  # type: ignore
                comparison_data = compare_episodes_tool(episode1, episode2)
            except ImportError:
                # Fallback when comparative_analyzer_tools is not available
                logger.warning("comparative_analyzer_tools not available, using mock comparison data")
                comparison_data = {
                    'episode1_key': episode1,
                    'episode2_key': episode2,
                    'overall_similarity': 0.5,
                    'key_similarities': ['Both involved monetary policy changes'],
                    'key_differences': ['Different economic contexts'],
                    'similarity_breakdown': {
                        'policy_actions': 0.5,
                        'economic_context': 0.4,
                        'market_response': 0.6,
                        'communication': 0.5
                    },
                    'lessons': ['Historical episodes provide valuable context for policy analysis']
                }
        
        builder = ReportBuilder()
        report = builder.build_episode_comparison_report(
            comparison_data,
            episode1,
            episode2
        )
        
        # Export
        export_path = None
        if export_format:
            exporter = ReportExporter()
            filename = f"episode_comparison_{episode1[:10]}_vs_{episode2[:10]}_{report['metadata']['generated_at'][:10]}"
            
            if export_format == 'pdf':
                export_path = exporter.export_to_pdf(report, filename)
            elif export_format == 'docx':
                export_path = exporter.export_to_docx(report, filename)
            elif export_format == 'html':
                export_path = exporter.export_to_html(report, filename)
            elif export_format == 'markdown':
                export_path = exporter.export_to_markdown(report, filename)
        
        logger.info("Episode comparison report generated")
        
        return {
            'report': report,
            'metadata': report['metadata'],
            'export_path': export_path,
            'similarity_score': comparison_data.get('overall_similarity', 0),
            'key_findings': {
                'similarities': comparison_data.get('key_similarities', []),
                'differences': comparison_data.get('key_differences', [])
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating episode comparison report: {e}")
        return {
            'error': str(e),
            'message': 'Failed to generate episode comparison report'
        }


# ============================================================================
# TOOL 3: GENERATE QUICK SUMMARY
# ============================================================================

def generate_quick_summary_tool(
    recent_meetings: List[Dict],
    policy_data: Optional[Dict] = None,
    export_format: str = 'markdown'
) -> Dict:
    """
    Generate quick 2-3 page executive summary of current Fed policy.
    
    This tool creates a concise summary report focused on current stance,
    recent actions, and outlook. Ideal for quick briefings.
    
    Args:
        recent_meetings: List of recent meeting analyses (last 3-6 meetings)
        policy_data: Optional current policy stance data
        export_format: Output format ('pdf', 'docx', 'html', 'markdown')
    
    Returns:
        Dictionary containing:
        - report: Full report structure
        - export_path: Path to exported file
        - current_stance: Current Fed stance classification
        - next_action: Predicted next action
    
    Report Sections (4 total):
        1. Current Stance - Fed funds rate, sentiment, classification
        2. Recent Actions - Last 3-6 meeting decisions
        3. Key Metrics - Critical economic indicators
        4. Outlook - Near-term expectations
    
    Example:
        >>> # Get recent meetings
        >>> meetings = [
        ...     analyze_fomc_minutes_tool(file1),
        ...     analyze_fomc_minutes_tool(file2),
        ...     analyze_fomc_minutes_tool(file3)
        ... ]
        >>> 
        >>> summary = generate_quick_summary_tool(meetings, export_format='markdown')
        >>> print(summary['current_stance'])
        'restrictive'
        >>> print(summary['export_path'])
        'fed_policy_quick_summary_2024-11-29.md'
    """
    logger.info("Tool called: generate_quick_summary")
    
    try:
        builder = ReportBuilder()
        report = builder.build_quick_summary(recent_meetings, policy_data or {})
        
        # Export
        export_path = None
        if export_format:
            exporter = ReportExporter()
            filename = f"fed_policy_quick_summary_{report['metadata']['generated_at'][:10]}"
            
            if export_format == 'pdf':
                export_path = exporter.export_to_pdf(report, filename)
            elif export_format == 'docx':
                export_path = exporter.export_to_docx(report, filename)
            elif export_format == 'html':
                export_path = exporter.export_to_html(report, filename)
            elif export_format == 'markdown':
                export_path = exporter.export_to_markdown(report, filename)
        
        # Extract key info
        current_stance = 'Unknown'
        if policy_data and 'current_stance' in policy_data:
            current_stance = policy_data['current_stance'].get('classification', 'Unknown')
        
        logger.info("Quick summary generated")
        
        return {
            'report': report,
            'export_path': export_path,
            'current_stance': current_stance,
            'num_meetings_analyzed': len(recent_meetings)
        }
        
    except Exception as e:
        logger.error(f"Error generating quick summary: {e}")
        return {
            'error': str(e),
            'message': 'Failed to generate quick summary'
        }


# ============================================================================
# TOOL 4: GENERATE CUSTOM REPORT
# ============================================================================

def generate_custom_report_tool(
    sections: List[str],
    agent_data: Dict,
    title: Optional[str] = None,
    export_format: str = 'pdf'
) -> Dict:
    """
    Generate custom report with specified sections.
    
    This tool allows you to build a report with only the sections you need,
    providing flexibility for specific use cases.
    
    Args:
        sections: List of section names to include:
            - 'executive_summary'
            - 'current_policy_stance'
            - 'recent_trends'
            - 'long_term_patterns'
            - 'historical_comparisons'
            - 'economic_context'
            - 'predictive_indicators'
            - 'recommendations'
        agent_data: Data from required agents for chosen sections
        title: Optional custom title for report
        export_format: Output format ('pdf', 'docx', 'html', 'markdown')
    
    Returns:
        Dictionary containing:
        - report: Full report structure
        - export_path: Path to exported file
        - sections_included: List of sections in report
    
    Example:
        >>> # Custom report with just trends and predictions
        >>> custom_report = generate_custom_report_tool(
        ...     sections=['recent_trends', 'predictive_indicators', 'recommendations'],
        ...     agent_data={
        ...         'policy_analyzer': trend_data,
        ...         'trend_tracker': prediction_data
        ...     },
        ...     title='Fed Policy Outlook Q1 2025',
        ...     export_format='docx'
        ... )
        >>> print(custom_report['sections_included'])
        ['Recent Trends', 'Predictive Indicators', 'Recommendations']
    """
    logger.info(f"Tool called: generate_custom_report with {len(sections)} sections")
    
    try:
        builder = ReportBuilder()
        report = builder.build_custom_report(sections, agent_data, title)
        
        # Export
        export_path = None
        if export_format:
            exporter = ReportExporter()
            filename = f"fed_policy_custom_report_{report['metadata']['generated_at'][:10]}"
            
            if export_format == 'pdf':
                export_path = exporter.export_to_pdf(report, filename)
            elif export_format == 'docx':
                export_path = exporter.export_to_docx(report, filename)
            elif export_format == 'html':
                export_path = exporter.export_to_html(report, filename)
            elif export_format == 'markdown':
                export_path = exporter.export_to_markdown(report, filename)
        
        logger.info("Custom report generated")
        
        return {
            'report': report,
            'export_path': export_path,
            'sections_included': [s['title'] for s in report['sections']],
            'num_sections': len(report['sections'])
        }
        
    except Exception as e:
        logger.error(f"Error generating custom report: {e}")
        return {
            'error': str(e),
            'message': 'Failed to generate custom report'
        }


# ============================================================================
# TOOL 5: EXPORT REPORT
# ============================================================================

def export_report_tool(
    report: Dict,
    filename: str,
    formats: List[str] = ['pdf']
) -> Dict:
    """
    Export an existing report to multiple formats.
    
    This tool takes a report dictionary and exports it to one or more formats.
    Useful for generating the same report in multiple output types.
    
    Args:
        report: Report dictionary (from any generate_* tool)
        filename: Base filename (without extension)
        formats: List of formats to export ('pdf', 'docx', 'html', 'markdown', 'json')
    
    Returns:
        Dictionary containing:
        - export_paths: Dict of {format: filepath}
        - formats_exported: List of successfully exported formats
        - errors: Any errors encountered
    
    Example:
        >>> # Generate report once, export to multiple formats
        >>> report_data = generate_comprehensive_report_tool(data, export_format=None)
        >>> report = report_data['report']
        >>> 
        >>> exports = export_report_tool(
        ...     report,
        ...     filename='fed_policy_report_2024_q4',
        ...     formats=['pdf', 'docx', 'html', 'markdown']
        ... )
        >>> print(exports['export_paths'])
        {
            'pdf': 'fed_policy_report_2024_q4.pdf',
            'docx': 'fed_policy_report_2024_q4.docx',
            'html': 'fed_policy_report_2024_q4.html',
            'markdown': 'fed_policy_report_2024_q4.md'
        }
    """
    logger.info(f"Tool called: export_report to {len(formats)} formats")
    
    try:
        exporter = ReportExporter()
        export_paths = {}
        errors = {}
        
        for format in formats:
            try:
                if format == 'pdf':
                    path = exporter.export_to_pdf(report, filename)
                elif format == 'docx':
                    path = exporter.export_to_docx(report, filename)
                elif format == 'html':
                    path = exporter.export_to_html(report, filename)
                elif format == 'markdown' or format == 'md':
                    path = exporter.export_to_markdown(report, filename)
                elif format == 'json':
                    path = exporter.export_to_json(report, filename)
                else:
                    errors[format] = f"Unsupported format: {format}"
                    continue
                
                export_paths[format] = path
                
            except Exception as e:
                errors[format] = str(e)
                logger.error(f"Error exporting to {format}: {e}")
        
        logger.info(f"Exported to {len(export_paths)} formats")
        
        return {
            'export_paths': export_paths,
            'formats_exported': list(export_paths.keys()),
            'errors': errors if errors else None,
            'num_exports': len(export_paths)
        }
        
    except Exception as e:
        logger.error(f"Error exporting report: {e}")
        return {
            'error': str(e),
            'message': 'Failed to export report'
        }


# ============================================================================
# HELPER: LIST AVAILABLE REPORT TYPES
# ============================================================================

def list_report_types() -> Dict:
    """
    List all available report types.
    
    Returns:
        Dictionary with report type information
    """
    return {
        'num_types': len(REPORT_TYPES),
        'types': {
            key: {
                'name': config['name'],
                'description': config['description'],
                'typical_length': config['typical_length'],
                'sections': config['sections']
            }
            for key, config in REPORT_TYPES.items()
        }
    }


# ============================================================================
# HELPER: LIST AVAILABLE FORMATS
# ============================================================================

def list_export_formats() -> Dict:
    """
    List all available export formats.
    
    Returns:
        Dictionary with format information
    """
    return {
        'num_formats': len(OUTPUT_FORMATS),
        'formats': {
            key: {
                'extension': config['extension'],
                'mime_type': config['mime_type'],
                'features': config['features']
            }
            for key, config in OUTPUT_FORMATS.items()
        }
    }
