"""
Document Processor

FOMC document parsing and analysis agent.
"""

__version__ = "1.0.0"

# Handle relative imports for package usage and absolute for direct execution
try:
    # Import main components
    from .document_processor_agent import DocumentProcessorAgent
    from .document_processor_config import (
        DOCUMENT_TYPES,
        PARSING_PATTERNS,
        METADATA_EXTRACTION_RULES,
        DOCS_BASE_DIR,
        validate_config,
        get_config_info,
        is_fully_configured
    )
    from .document_processor_tools import (
        parse_fomc_document,
        extract_document_metadata,
        analyze_document_sentiment,
        compare_documents,
        get_document_summary
    )
    from .pdf_parser import PDFParser
    from .text_analyzer import TextAnalyzer
    from .sep_extractor import SEPExtractor
except ImportError:
    # Fallback for direct execution
    from document_processor_agent import DocumentProcessorAgent
    from document_processor_config import (
        DOCUMENT_TYPES,
        PARSING_PATTERNS,
        METADATA_EXTRACTION_RULES,
        DOCS_BASE_DIR,
        validate_config,
        get_config_info,
        is_fully_configured
    )
    from document_processor_tools import (
        parse_fomc_document,
        extract_document_metadata,
        analyze_document_sentiment,
        compare_documents,
        get_document_summary
    )
    from pdf_parser import PDFParser
    from text_analyzer import TextAnalyzer
    from sep_extractor import SEPExtractor

__all__ = [
    # Main agent
    "DocumentProcessorAgent",
    
    # Configuration
    "DOCUMENT_TYPES",
    "PARSING_PATTERNS",
    "METADATA_EXTRACTION_RULES",
    "DOCS_BASE_DIR",
    "validate_config",
    "get_config_info",
    "is_fully_configured",
    
    # Tool functions
    "parse_fomc_document",
    "extract_document_metadata",
    "analyze_document_sentiment",
    "compare_documents",
    "get_document_summary",
    
    # Utility classes
    "PDFParser",
    "TextAnalyzer",
    "SEPExtractor"
]