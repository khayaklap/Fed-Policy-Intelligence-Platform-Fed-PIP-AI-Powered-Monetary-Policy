"""
Document Processor Tools

ADK tools for parsing FOMC documents and extracting structured data.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from google.adk.tools.tool_context import ToolContext

try:
    # Try relative imports first (when used as module)
    from .sep_extractor import SEPExtractor, extract_sep_projections
    from .text_analyzer import TextAnalyzer, analyze_fomc_minutes
    from .pdf_parser import PDFParser, parse_pdf_document
except ImportError:
    # Fall back to absolute imports (when run directly)
    from sep_extractor import SEPExtractor, extract_sep_projections
    from text_analyzer import TextAnalyzer, analyze_fomc_minutes
    from pdf_parser import PDFParser, parse_pdf_document

logger = logging.getLogger(__name__)


def extract_sep_forecasts(
    file_path: str,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Extract Fed economic projections from SEP (Summary of Economic Projections).
    
    SEP contains FOMC participants' median projections for:
    - GDP growth
    - Unemployment rate  
    - PCE inflation & Core PCE inflation
    - Federal funds rate
    
    Published 4 times per year (March, June, September, December).
    
    Args:
        file_path: Path to SEP PDF file
        tool_context: ADK tool context
    
    Returns:
        Dictionary with extracted projections by variable and year
    
    Example:
        >>> extract_sep_forecasts("/path/to/sep_20230614.pdf")
        {
            'gdp': {
                'variable_name': 'Change in real GDP',
                'unit': 'percent',
                'projections': {
                    '2023': 1.0,
                    '2024': 1.1,
                    '2025': 1.8,
                    'longer_run': 1.8
                }
            },
            'pce_inflation': {
                'variable_name': 'PCE inflation',
                'unit': 'percent',
                'projections': {
                    '2023': 3.2,
                    '2024': 2.5,
                    '2025': 2.1,
                    'longer_run': 2.0
                }
            },
            ...
        }
    """
    logger.info(f"Extracting SEP forecasts from: {file_path}")
    
    try:
        extractor = SEPExtractor(file_path)
        projections = extractor.extract_projections()
        
        # Add metadata
        meeting_date = extractor.get_meeting_date()
        
        result = {
            'meeting_date': meeting_date.strftime('%Y-%m-%d') if meeting_date else None,
            'file_path': file_path,
            'projections': projections,
            'num_variables': len(projections)
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error extracting SEP forecasts: {e}")
        return {'error': str(e), 'file_path': file_path}


def analyze_fomc_minutes_tool(
    file_path: str,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Analyze FOMC Minutes for policy decisions, sentiment, and key content.
    
    Extracts:
    - Policy decision (rate increase/decrease/unchanged)
    - Hawkish/dovish sentiment
    - Forward guidance statements
    - Economic assessment (optimistic/pessimistic)
    - Voting record (unanimous or split)
    - Key phrases and themes
    
    Args:
        file_path: Path to FOMC Minutes PDF
        tool_context: ADK tool context
    
    Returns:
        Dictionary with comprehensive analysis
    
    Example:
        >>> analyze_fomc_minutes_tool("/path/to/minutes_20220504.pdf")
        {
            'policy_decision': {
                'action': 'increase',
                'change_amount': 50,  # basis points
                'target_range': (0.75, 1.0)
            },
            'sentiment': {
                'sentiment': 'hawkish',
                'confidence': 'high',
                'score': 12  # Positive = hawkish
            },
            'forward_guidance': [
                'Committee anticipates that ongoing increases in the target range will be appropriate...'
            ],
            'voting': {
                'unanimous': True,
                'dissenters': []
            }
        }
    """
    logger.info(f"Analyzing FOMC Minutes: {file_path}")
    
    try:
        analyzer = TextAnalyzer(file_path)
        analysis = analyzer.get_full_analysis()
        
        # Add metadata
        parser = PDFParser(file_path)
        metadata = parser.extract_metadata_from_text(parser.extract_text())
        
        analysis['metadata'] = {
            'meeting_date': metadata['meeting_date'].strftime('%Y-%m-%d') if metadata.get('meeting_date') else None,
            'file_path': file_path
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing Minutes: {e}")
        return {'error': str(e), 'file_path': file_path}


def extract_policy_decision(
    file_path: str,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Extract just the policy decision from FOMC Minutes.
    
    Faster than full analysis when you only need the rate decision.
    
    Args:
        file_path: Path to FOMC Minutes PDF
        tool_context: ADK tool context
    
    Returns:
        Dictionary with policy decision details
    
    Example:
        >>> extract_policy_decision("/path/to/minutes_20230503.pdf")
        {
            'action': 'increase',
            'change_amount': 25,
            'target_range': (5.0, 5.25),
            'meeting_date': '2023-05-03',
            'interpretation': 'Fed raised rates by 25bp to 5.00-5.25%'
        }
    """
    logger.info(f"Extracting policy decision from: {file_path}")
    
    try:
        analyzer = TextAnalyzer(file_path)
        decision = analyzer.extract_policy_decision()
        
        # Add interpretation
        if decision['action'] == 'increase':
            interp = f"Fed raised rates by {decision['change_amount']}bp"
            if decision['target_range']:
                interp += f" to {decision['target_range'][0]:.2f}-{decision['target_range'][1]:.2f}%"
        elif decision['action'] == 'decrease':
            interp = f"Fed cut rates by {decision['change_amount']}bp"
            if decision['target_range']:
                interp += f" to {decision['target_range'][0]:.2f}-{decision['target_range'][1]:.2f}%"
        else:
            interp = "Fed held rates unchanged"
            if decision['target_range']:
                interp += f" at {decision['target_range'][0]:.2f}-{decision['target_range'][1]:.2f}%"
        
        decision['interpretation'] = interp
        
        # Get meeting date
        parser = PDFParser(file_path)
        metadata = parser.extract_metadata_from_text(parser.extract_text())
        decision['meeting_date'] = metadata['meeting_date'].strftime('%Y-%m-%d') if metadata.get('meeting_date') else None
        
        return decision
        
    except Exception as e:
        logger.error(f"Error extracting policy decision: {e}")
        return {'error': str(e), 'file_path': file_path}


def compare_sep_with_actual(
    sep_file_path: str,
    variable: str,
    year: str,
    actual_value: float,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Compare SEP forecast with actual outcome.
    
    Critical for assessing Fed forecast accuracy and identifying
    systematic forecast errors.
    
    Args:
        sep_file_path: Path to SEP PDF
        variable: Variable to compare ('gdp', 'unemployment', 'pce_inflation', etc.)
        year: Year of forecast
        actual_value: Actual outcome (from FRED/BLS)
        tool_context: ADK tool context
    
    Returns:
        Dictionary with forecast vs actual comparison
    
    Example:
        >>> compare_sep_with_actual(
        ...     "/path/to/sep_20210616.pdf",
        ...     "pce_inflation",
        ...     "2022",
        ...     6.5  # Actual from FRED
        ... )
        {
            'variable': 'pce_inflation',
            'year': '2022',
            'forecast': 2.1,
            'actual': 6.5,
            'error': -4.4,  # Underestimate
            'error_percent': -209.5,
            'interpretation': 'Fed significantly underestimated inflation by 4.4pp'
        }
    """
    logger.info(f"Comparing SEP forecast with actual: {variable} for {year}")
    
    try:
        extractor = SEPExtractor(sep_file_path)
        projections = extractor.extract_projections()
        
        if variable not in projections:
            return {
                'error': f'Variable {variable} not found in SEP',
                'available_variables': list(projections.keys())
            }
        
        forecast = projections[variable]['projections'].get(year)
        
        if forecast is None:
            return {
                'error': f'No forecast for {year}',
                'available_years': list(projections[variable]['projections'].keys())
            }
        
        # Calculate error
        error = actual_value - forecast
        error_percent = (error / forecast * 100) if forecast != 0 else None
        
        # Interpretation
        var_name = projections[variable]['variable_name']
        if abs(error) < 0.5:
            interp = f"Fed forecast for {var_name} was accurate (error: {error:+.1f}pp)"
        elif error > 0:
            magnitude = "significantly" if abs(error) > 2.0 else "moderately"
            interp = f"Fed {magnitude} underestimated {var_name} by {abs(error):.1f}pp"
        else:
            magnitude = "significantly" if abs(error) > 2.0 else "moderately"
            interp = f"Fed {magnitude} overestimated {var_name} by {abs(error):.1f}pp"
        
        return {
            'variable': variable,
            'variable_name': var_name,
            'year': year,
            'forecast': forecast,
            'actual': actual_value,
            'error': round(error, 2),
            'error_percent': round(error_percent, 1) if error_percent else None,
            'interpretation': interp,
            'meeting_date': extractor.get_meeting_date().strftime('%Y-%m-%d') if extractor.get_meeting_date() else None
        }
        
    except Exception as e:
        logger.error(f"Error comparing forecast: {e}")
        return {'error': str(e)}


def get_document_metadata(
    file_path: str,
    tool_context: Optional[ToolContext] = None
) -> Dict:
    """
    Extract metadata from any FOMC document.
    
    Quick way to get document info without full parsing.
    
    Args:
        file_path: Path to PDF file
        tool_context: ADK tool context
    
    Returns:
        Dictionary with document metadata
    
    Example:
        >>> get_document_metadata("/path/to/minutes_20230726.pdf")
        {
            'file_name': 'minutes_20230726.pdf',
            'document_type': 'minutes',
            'meeting_date': '2023-07-26',
            'page_count': 12,
            'file_size': 245678,
            'text_length': 15432
        }
    """
    logger.info(f"Extracting metadata from: {file_path}")
    
    try:
        parser = PDFParser(file_path)
        info = parser.get_document_info()
        
        # Determine document type from filename
        filename = info['file_name'].lower()
        if 'minute' in filename:
            doc_type = 'minutes'
        elif 'mpr' in filename or 'monetary policy report' in filename:
            doc_type = 'mpr'
        elif 'sep' in filename or 'proj' in filename:
            doc_type = 'sep'
        else:
            doc_type = 'unknown'
        
        info['document_type'] = doc_type
        
        # Format meeting date
        if info['metadata'].get('meeting_date'):
            info['meeting_date'] = info['metadata']['meeting_date'].strftime('%Y-%m-%d')
        
        return info
        
    except Exception as e:
        logger.error(f"Error extracting metadata: {e}")
        return {'error': str(e), 'file_path': file_path}


# Export all tools
__all__ = [
    'extract_sep_forecasts',
    'analyze_fomc_minutes_tool',
    'extract_policy_decision',
    'compare_sep_with_actual',
    'get_document_metadata'
]
