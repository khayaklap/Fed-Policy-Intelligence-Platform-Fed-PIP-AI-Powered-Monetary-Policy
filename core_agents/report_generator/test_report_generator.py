"""
Report Generator Tests

Test suite for report generation, export, and formatting.
"""

import pytest
try:
    # Try relative imports first (when used as module)
    from .report_builder import ReportBuilder
    from .format_exporters import ReportExporter
    from .visualization_generator import VisualizationGenerator
    from .report_generator_tools import (
        generate_comprehensive_report_tool,
        generate_episode_comparison_report_tool,
        generate_quick_summary_tool,
        generate_custom_report_tool,
        export_report_tool
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from report_builder import ReportBuilder
    from format_exporters import ReportExporter
    from visualization_generator import VisualizationGenerator
    from report_generator_tools import (
        generate_comprehensive_report_tool,
        generate_episode_comparison_report_tool,
        generate_quick_summary_tool,
        generate_custom_report_tool,
        export_report_tool
    )

# Sample test data
SAMPLE_AGENT_DATA = {
    'document_processor': {
        'most_recent_meeting': {
            'date': '2024-11-07',
            'action': 'decrease',
            'sentiment': 'dovish',
            'score': -5,
            'fed_funds': 4.75
        }
    },
    'policy_analyzer': {
        'current_stance': {
            'classification': 'restrictive',
            'appropriateness': 'appropriate'
        },
        'sentiment_trend': {
            'direction': 'dovish',
            'strength': 'moderate',
            'duration': 4
        }
    },
    'trend_tracker': {
        'policy_cycles': {
            'current_phase': 'slowdown',
            'duration': 15
        },
        'prediction': {
            'predicted_action': 'decrease',
            'confidence': 0.75
        }
    }
}

class TestReportBuilder:
    """Test report building functionality."""
    
    def test_build_comprehensive_report(self):
        """Test comprehensive report generation."""
        builder = ReportBuilder()
        report = builder.build_comprehensive_report(SAMPLE_AGENT_DATA)
        
        assert 'metadata' in report
        assert 'sections' in report
        assert len(report['sections']) >= 2
        
        # Check executive summary exists
        summary = next((s for s in report['sections'] if s['title'] == 'Executive Summary'), None)
        assert summary is not None
        
        print(f"\nComprehensive report: {len(report['sections'])} sections")
    
    def test_build_quick_summary(self):
        """Test quick summary generation."""
        builder = ReportBuilder()
        meetings = [SAMPLE_AGENT_DATA['document_processor']['most_recent_meeting']]
        
        report = builder.build_quick_summary(meetings, {})
        
        assert 'metadata' in report
        assert 'sections' in report
        assert report['metadata']['report_type'] == 'quick_summary'
        
        print(f"\nQuick summary: {len(report['sections'])} sections")

class TestReportExporter:
    """Test report export functionality."""
    
    def test_export_to_json(self):
        """Test JSON export."""
        builder = ReportBuilder()
        report = builder.build_comprehensive_report(SAMPLE_AGENT_DATA)
        
        exporter = ReportExporter()
        path = exporter.export_to_json(report, "test_report")
        
        assert path.endswith('.json')
        print(f"\nJSON exported: {path}")
    
    def test_export_to_markdown(self):
        """Test Markdown export."""
        builder = ReportBuilder()
        report = builder.build_comprehensive_report(SAMPLE_AGENT_DATA)
        
        exporter = ReportExporter()
        path = exporter.export_to_markdown(report, "test_report")
        
        assert path.endswith('.md')
        print(f"\nMarkdown exported: {path}")

class TestTools:
    """Test ADK tools."""
    
    def test_generate_comprehensive_report_tool(self):
        """Test comprehensive report tool."""
        result = generate_comprehensive_report_tool(
            SAMPLE_AGENT_DATA,
            export_format='json'
        )
        
        assert 'error' not in result
        assert 'report' in result
        assert 'metadata' in result
        
        print(f"\nComprehensive tool: {result['num_sections']} sections")
    
    def test_generate_quick_summary_tool(self):
        """Test quick summary tool."""
        meetings = [SAMPLE_AGENT_DATA['document_processor']['most_recent_meeting']]
        
        result = generate_quick_summary_tool(
            meetings,
            export_format='markdown'
        )
        
        assert 'error' not in result
        assert 'report' in result
        
        print(f"\nQuick summary tool: {result['num_meetings_analyzed']} meetings")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("REPORT GENERATOR TEST SUITE")
    print("="*80)
    
    pytest.main([__file__, '-v', '--tb=short'])
    
    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80)
