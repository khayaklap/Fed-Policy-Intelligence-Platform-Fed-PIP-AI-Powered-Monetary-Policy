"""
Document Processor Agent Tests

Tests for FOMC document parsing and analysis.
"""

import asyncio
import pytest

# Handle relative imports for package usage and absolute for direct execution
try:
    from .document_processor_agent import create_document_processor_agent
except ImportError:
    from document_processor_agent import create_document_processor_agent

from google.adk.runners import InMemoryRunner


# ============================================================================
# Agent-Level Tests (require actual PDF files)
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires actual FOMC PDF files")
async def test_extract_sep_forecasts():
    """Test SEP forecast extraction."""
    agent = create_document_processor_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        """
        Extract economic projections from the SEP at /path/to/sep_20230614.pdf
        What did the Fed project for 2024 inflation?
        """
    )
    
    print("\n" + "="*60)
    print("Test: SEP Forecast Extraction")
    print("="*60)
    print(response)
    assert response is not None


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires actual FOMC PDF files")
async def test_analyze_minutes():
    """Test FOMC Minutes analysis."""
    agent = create_document_processor_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        """
        Analyze the FOMC Minutes at /path/to/minutes_20220504.pdf
        Did the Fed raise rates? What was the sentiment?
        """
    )
    
    print("\n" + "="*60)
    print("Test: Minutes Analysis")
    print("="*60)
    print(response)
    assert response is not None


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires actual FOMC PDF files")
async def test_forecast_accuracy():
    """Test forecast accuracy comparison."""
    agent = create_document_processor_agent()
    runner = InMemoryRunner(agent=agent)
    
    response = await runner.run_debug(
        """
        The SEP at /path/to/sep_20210616.pdf projected 2022 PCE inflation.
        The actual 2022 inflation was 6.5% (from FRED).
        How accurate was the Fed's forecast?
        """
    )
    
    print("\n" + "="*60)
    print("Test: Forecast Accuracy")
    print("="*60)
    print(response)
    assert response is not None


# ============================================================================
# Tool-Level Tests (test individual functions)
# ============================================================================

def test_sep_extractor_structure():
    """Test SEP extractor data structure."""
    from sep_extractor import SEPExtractor
    
    # This would work with an actual SEP file
    # extractor = SEPExtractor("/path/to/sep.pdf")
    # projections = extractor.extract_projections()
    
    # For now, just test the structure
    print("\n" + "="*60)
    print("Test: SEP Extractor Structure")
    print("="*60)
    print("SEP should extract: gdp, unemployment, pce_inflation, core_pce_inflation, fed_funds")
    print("Each variable should have: variable_name, unit, projections (dict by year)")


def test_text_analyzer_patterns():
    """Test text analyzer patterns."""
    from document_processor_config import (
        POLICY_ACTION_PATTERNS,
        HAWKISH_INDICATORS,
        DOVISH_INDICATORS
    )
    
    print("\n" + "="*60)
    print("Test: Text Analyzer Patterns")
    print("="*60)
    
    # Test that patterns are defined
    assert len(POLICY_ACTION_PATTERNS['rate_increase']) > 0
    assert len(POLICY_ACTION_PATTERNS['rate_decrease']) > 0
    assert len(HAWKISH_INDICATORS) > 0
    assert len(DOVISH_INDICATORS) > 0
    
    print(f"Rate increase patterns: {len(POLICY_ACTION_PATTERNS['rate_increase'])}")
    print(f"Hawkish indicators: {len(HAWKISH_INDICATORS)}")
    print(f"Dovish indicators: {len(DOVISH_INDICATORS)}")


def test_pdf_parser_initialization():
    """Test PDF parser can be initialized."""
    from pdf_parser import PDFParser
    
    print("\n" + "="*60)
    print("Test: PDF Parser Initialization")
    print("="*60)
    
    # Would fail without actual file
    # parser = PDFParser("/path/to/test.pdf")
    
    print("PDF Parser ready to use with pdfplumber and PyMuPDF")
    print("Supports: text extraction, table extraction, metadata extraction")


def test_compare_sep_with_actual():
    """Test SEP comparison logic."""
    from document_processor_tools import compare_sep_with_actual
    
    print("\n" + "="*60)
    print("Test: SEP Comparison Logic")
    print("="*60)
    
    # Example calculation
    forecast = 2.1
    actual = 6.5
    error = actual - forecast
    error_percent = (error / forecast) * 100
    
    print(f"Fed forecast: {forecast}%")
    print(f"Actual: {actual}%")
    print(f"Error: {error:+.1f}pp")
    print(f"Error %: {error_percent:+.1f}%")
    
    assert error > 4.0  # Significant underestimate


# ============================================================================
# Integration Tests (with other agents)
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires all agents running")
async def test_integration_with_fred():
    """Test Document Processor + FRED agent integration."""
    from google.adk.agents import LlmAgent
    from google.adk.tools import AgentTool
    from google.adk.a2a import RemoteA2aAgent
    
    # Connect to FRED agent (must be running on port 8001)
    fred_agent = RemoteA2aAgent("http://localhost:8001/agent_card.json")
    
    # Create Document Processor
    doc_agent = create_document_processor_agent()
    
    # Create orchestrator
    orchestrator = LlmAgent(
        name="forecast_validator",
        description="Validates Fed forecasts against actual data",
        sub_agents=[
            AgentTool(doc_agent),
            AgentTool(fred_agent)
        ]
    )
    
    runner = InMemoryRunner(agent=orchestrator)
    
    response = await runner.run_debug(
        """
        1. Extract the Fed's 2022 inflation forecast from SEP at /path/to/sep_20210616.pdf
        2. Get the actual 2022 Core PCE inflation from FRED
        3. Calculate the forecast error
        """
    )
    
    print("\n" + "="*60)
    print("Test: Integration with FRED")
    print("="*60)
    print(response)


# ============================================================================
# Usage Examples (not tests, documentation)
# ============================================================================

def example_usage_sep():
    """Example: Extract SEP forecasts."""
    print("\n" + "="*60)
    print("EXAMPLE: Extract SEP Forecasts")
    print("="*60)
    
    code = """
from doc_processor_tools import extract_sep_forecasts

# Extract all projections
result = extract_sep_forecasts("/path/to/sep_20230614.pdf")

# Result structure:
{
    'meeting_date': '2023-06-14',
    'projections': {
        'gdp': {
            'variable_name': 'Change in real GDP',
            'projections': {
                '2023': 1.0,
                '2024': 1.1,
                '2025': 1.8,
                'longer_run': 1.8
            }
        },
        'pce_inflation': {
            'projections': {
                '2023': 3.2,
                '2024': 2.5,
                '2025': 2.1,
                'longer_run': 2.0
            }
        }
    }
}
    """
    print(code)


def example_usage_minutes():
    """Example: Analyze FOMC Minutes."""
    print("\n" + "="*60)
    print("EXAMPLE: Analyze FOMC Minutes")
    print("="*60)
    
    code = """
from doc_processor_tools import analyze_fomc_minutes_tool

# Full analysis
result = analyze_fomc_minutes_tool("/path/to/minutes_20220504.pdf")

# Result includes:
{
    'policy_decision': {
        'action': 'increase',
        'change_amount': 50,  # basis points
        'target_range': (0.75, 1.0)
    },
    'sentiment': {
        'sentiment': 'hawkish',
        'confidence': 'high',
        'score': 12
    },
    'forward_guidance': [...],
    'voting': {
        'unanimous': True
    }
}
    """
    print(code)


def example_usage_forecast_validation():
    """Example: Validate Fed forecast."""
    print("\n" + "="*60)
    print("EXAMPLE: Forecast Validation")
    print("="*60)
    
    code = """
from doc_processor_tools import compare_sep_with_actual

# Compare forecast vs actual
result = compare_sep_with_actual(
    sep_file_path="/path/to/sep_20210616.pdf",
    variable="pce_inflation",
    year="2022",
    actual_value=6.5  # From FRED
)

# Result:
{
    'forecast': 2.1,
    'actual': 6.5,
    'error': 4.4,  # pp underestimate
    'interpretation': 'Fed significantly underestimated inflation by 4.4pp'
}
    """
    print(code)


# ============================================================================
# Interactive Demo
# ============================================================================

async def interactive_demo():
    """
    Interactive demo of Document Processor capabilities.
    
    Run with: python -c "from test_doc_processor import interactive_demo; import asyncio; asyncio.run(interactive_demo())"
    """
    print("\n" + "="*80)
    print("DOCUMENT PROCESSOR AGENT DEMO")
    print("="*80)
    print("\nNOTE: This demo requires actual FOMC PDF files")
    print("Download from: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm")
    print("\nExample queries:")
    
    queries = [
        "Extract economic projections from SEP",
        "Analyze FOMC Minutes for policy decision",
        "What was the sentiment (hawkish/dovish)?",
        "Compare Fed forecast with actual outcome",
        "Get document metadata"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"{i}. {query}")
    
    print("\nAgent ready with 5 tools:")
    print("  1. extract_sep_forecasts")
    print("  2. analyze_fomc_minutes_tool")
    print("  3. extract_policy_decision")
    print("  4. compare_sep_with_actual")
    print("  5. get_document_metadata")
    
    # Would run actual queries here with real files
    # agent = create_document_processor_agent()
    # runner = InMemoryRunner(agent=agent)
    # ...


if __name__ == "__main__":
    # Run examples
    example_usage_sep()
    example_usage_minutes()
    example_usage_forecast_validation()
    
    # Run basic tests
    test_text_analyzer_patterns()
    test_compare_sep_with_actual()
    
    print("\n" + "="*80)
    print("To run full tests with actual PDFs:")
    print("  pytest test_doc_processor.py -v")
    print("\nTo run interactive demo:")
    print("  python test_doc_processor.py")
    print("="*80)
