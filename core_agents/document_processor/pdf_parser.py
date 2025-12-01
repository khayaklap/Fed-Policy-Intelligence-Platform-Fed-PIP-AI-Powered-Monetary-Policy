"""
PDF Parser

Handles PDF reading, text extraction, and basic structure parsing
for FOMC documents.
"""

import logging
import pdfplumber
import pymupdf as fitz  # PyMuPDF for fast text extraction
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime

try:
    # Try relative imports first (when used as module)
    from .document_processor_config import (
        TABLE_SETTINGS,
        VALIDATION_THRESHOLDS,
        DATE_PATTERNS
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from document_processor_config import (
        TABLE_SETTINGS,
        VALIDATION_THRESHOLDS,
        DATE_PATTERNS
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFParser:
    """
    PDF parsing utility for FOMC documents.
    
    Uses pdfplumber for table extraction (best for structured tables)
    and PyMuPDF for fast text extraction.
    """
    
    def __init__(self, file_path: str):
        """
        Initialize PDF parser.
        
        Args:
            file_path: Path to PDF file
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")
        
        logger.info(f"Initializing PDF parser for: {self.file_path.name}")
    
    def extract_text(self) -> str:
        """
        Extract all text from PDF using PyMuPDF (fast).
    
        Returns:
            Full text content of PDF
        """
        logger.info("Extracting text from PDF")
    
        try:
            # Open document and keep reference
            doc = fitz.open(str(self.file_path))  # Ensure string path
            text = ""
            page_count = len(doc)  # Get count before iteration
        
            # Extract text from all pages
            for page_num in range(page_count):
                page = doc[page_num]  # Access by index
                page_text = page.get_text()
                text += page_text + "\n\n"
        
            # Close document explicitly
            doc.close()
        
            # Validate
            if len(text) < VALIDATION_THRESHOLDS['min_text_length']:
                logger.warning(f"Extracted text is unusually short: {len(text)} characters")
        
            logger.info(f"Extracted {len(text)} characters from {page_count} pages")
            return text
        
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            raise
    
    def extract_text_by_page(self) -> List[str]:
        """
        Extract text page by page.
    
        Returns:
            List of strings, one per page
        """
        logger.info("Extracting text by page")
    
        doc = None
        try:
            doc = fitz.open(str(self.file_path))
            pages = []
            page_count = len(doc)
        
            for page_num in range(page_count):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                pages.append(page_text)
        
            logger.info(f"Extracted {len(pages)} pages")
            return pages
        
        except Exception as e:
            logger.error(f"Error extracting pages: {e}")
            raise
    
        finally:
            if doc is not None:
                try:
                    doc.close()
                except:
                    pass
    
    def extract_tables(self, page_numbers: Optional[List[int]] = None) -> List[Dict]:
        """
        Extract tables from PDF using pdfplumber.
        
        Args:
            page_numbers: Specific pages to extract from (0-indexed), or None for all
        
        Returns:
            List of dictionaries with table data and metadata
        """
        logger.info("Extracting tables from PDF")
        
        tables = []
        
        try:
            with pdfplumber.open(self.file_path) as pdf:
                pages_to_process = page_numbers if page_numbers else range(len(pdf.pages))
                
                for page_num in pages_to_process:
                    if page_num >= len(pdf.pages):
                        logger.warning(f"Page {page_num} out of range")
                        continue
                    
                    page = pdf.pages[page_num]
                    
                    # Extract tables with custom settings
                    page_tables = page.extract_tables(table_settings=TABLE_SETTINGS)
                    
                    for table_idx, table in enumerate(page_tables):
                        if table and len(table) > 0:
                            tables.append({
                                'page': page_num,
                                'table_index': table_idx,
                                'data': table,
                                'rows': len(table),
                                'cols': len(table[0]) if table else 0
                            })
            
            logger.info(f"Extracted {len(tables)} tables")
            return tables
            
        except Exception as e:
            logger.error(f"Error extracting tables: {e}")
            return []
    
    def find_table_by_header(self, header_text: str) -> Optional[Dict]:
        """
        Find a table by searching for header text.
        
        Args:
            header_text: Text to search for in table headers
        
        Returns:
            First matching table or None
        """
        logger.info(f"Searching for table with header: {header_text}")
        
        tables = self.extract_tables()
        
        for table in tables:
            if table['data']:
                # Check first row for header
                first_row = table['data'][0]
                if any(header_text.lower() in str(cell).lower() for cell in first_row if cell):
                    logger.info(f"Found table on page {table['page']}")
                    return table
        
        logger.warning(f"No table found with header: {header_text}")
        return None
    
    def extract_metadata_from_text(self, text: str) -> Dict:
        """
        Extract metadata from document text.
        
        Args:
            text: Full document text
        
        Returns:
            Dictionary with metadata
        """
        logger.info("Extracting metadata from text")
        
        metadata = {
            'meeting_date': None,
            'release_date': None,
            'title': None,
            'page_count': None
        }
        
        # Extract meeting date
        metadata['meeting_date'] = self._extract_meeting_date(text)
        
        # Extract title (typically in first 500 characters)
        title_section = text[:500]
        title_lines = [line.strip() for line in title_section.split('\n') if line.strip()]
        if title_lines:
            metadata['title'] = title_lines[0]
        
        # Get page count
        try:
            doc = fitz.open(self.file_path)
            metadata['page_count'] = len(doc)
            doc.close()
        except:
            pass
        
        return metadata
    
    def _extract_meeting_date(self, text: str) -> Optional[datetime]:
        """
        Extract meeting date from document text.
        
        Args:
            text: Document text
        
        Returns:
            Meeting date as datetime or None
        """
        # Try each date pattern
        for pattern in DATE_PATTERNS:
            matches = re.findall(pattern, text[:2000])  # Search first 2000 chars
            if matches:
                date_str = matches[0]
                
                # Parse date
                try:
                    # Handle date ranges (e.g., "June 14-15, 2023")
                    # Extract the first date
                    if '–' in date_str or '-' in date_str:
                        # Take the start date
                        parts = re.split(r'[–-]', date_str)
                        if len(parts) >= 2:
                            # Reconstruct: "June 14, 2023"
                            import dateparser
                            parsed = dateparser.parse(parts[0] + ', ' + date_str.split(',')[-1].strip())
                            if parsed:
                                return parsed
                    else:
                        import dateparser
                        parsed = dateparser.parse(date_str)
                        if parsed:
                            return parsed
                except Exception as e:
                    logger.warning(f"Could not parse date '{date_str}': {e}")
                    continue
        
        # Fallback: try to extract from filename
        filename = self.file_path.stem
        date_match = re.search(r'(\d{8})', filename)
        if date_match:
            date_str = date_match.group(1)
            try:
                return datetime.strptime(date_str, '%Y%m%d')
            except:
                pass
        
        return None
    
    def search_text(self, pattern: str, text: Optional[str] = None) -> List[str]:
        """
        Search for text pattern in document.
        
        Args:
            pattern: Regex pattern to search for
            text: Text to search (if None, extracts from PDF)
        
        Returns:
            List of matches
        """
        if text is None:
            text = self.extract_text()
        
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches
    
    def extract_section(self, start_marker: str, end_marker: Optional[str] = None, text: Optional[str] = None) -> str:
        """
        Extract a section of text between markers.
        
        Args:
            start_marker: Regex pattern for section start
            end_marker: Regex pattern for section end (if None, goes to document end)
            text: Text to search (if None, extracts from PDF)
        
        Returns:
            Extracted section text
        """
        if text is None:
            text = self.extract_text()
        
        # Find start
        start_match = re.search(start_marker, text, re.IGNORECASE)
        if not start_match:
            logger.warning(f"Start marker not found: {start_marker}")
            return ""
        
        start_pos = start_match.end()
        
        # Find end
        if end_marker:
            end_match = re.search(end_marker, text[start_pos:], re.IGNORECASE)
            if end_match:
                end_pos = start_pos + end_match.start()
                return text[start_pos:end_pos].strip()
        
        # No end marker or not found - return to end of document
        return text[start_pos:].strip()
    
    def get_document_info(self) -> Dict:
        """
        Get comprehensive document information.
    
        Returns:
            Dictionary with document info
        """
        logger.info("Getting document information")
    
        text = self.extract_text()
        metadata = self.extract_metadata_from_text(text)
    
        # Get page count safely
        page_count = None
        doc = None
        try:
            doc = fitz.open(str(self.file_path))
            page_count = len(doc)
        except:
            pass
        finally:
            if doc is not None:
                try:
                    doc.close()
                except:
                    pass
    
        info = {
            'file_name': self.file_path.name,
            'file_path': str(self.file_path),
            'file_size': self.file_path.stat().st_size,
            'text_length': len(text),
            'page_count': page_count,  # Add this
            'metadata': metadata
        }
        
        return info

def parse_pdf_document(file_path: str) -> Tuple[str, List[Dict], Dict]:
    """
    Convenience function to parse a PDF and extract text, tables, and metadata.
    
    Args:
        file_path: Path to PDF file
    
    Returns:
        Tuple of (text, tables, metadata)
    """
    parser = PDFParser(file_path)
    
    text = parser.extract_text()
    tables = parser.extract_tables()
    metadata = parser.extract_metadata_from_text(text)
    
    return text, tables, metadata
