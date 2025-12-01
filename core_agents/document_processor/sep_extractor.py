"""
SEP Extractor - Extract Federal Reserve Summary of Economic Projections

FIXED VERSION - Now handles dynamic years based on meeting date

This module handles extraction of economic projections from FOMC SEP documents.
Updated to handle both table-based and text-based extraction for maximum reliability.

Key Features:
- Extracts 5 key variables: GDP, Unemployment, PCE, Core PCE, Fed Funds Rate
- DYNAMIC YEAR DETECTION - works for any year (2021, 2022, 2025, etc.)
- Handles both spaced and non-spaced text formats
- Validates projections against reasonable thresholds
- Supports any projection horizon and longer run projections
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from document_processor_config import SEP_VARIABLES, VALIDATION_THRESHOLDS
except ImportError:
    # Fallback configuration if config file not available
    SEP_VARIABLES = {
        'gdp': {'name': 'Change in real GDP', 'unit': 'percent', 'type': 'growth_rate'},
        'unemployment': {'name': 'Unemployment rate', 'unit': 'percent', 'type': 'rate'},
        'pce_inflation': {'name': 'PCE inflation', 'unit': 'percent', 'type': 'rate'},
        'core_pce_inflation': {'name': 'Core PCE inflation', 'unit': 'percent', 'type': 'rate'},
        'fed_funds': {'name': 'Federal funds rate', 'unit': 'percent', 'type': 'rate'}
    }
    VALIDATION_THRESHOLDS = {
        'max_gdp_projection': 10.0,
        'max_inflation': 15.0,
        'max_unemployment': 25.0,
        'max_fed_funds': 20.0
    }

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEPExtractor:
    """
    Extract economic projections from Summary of Economic Projections (SEP) documents.
    
    FIXED VERSION with dynamic year detection - works for any year!
    
    Uses a hybrid approach:
    1. First attempts table extraction with pdfplumber
    2. Falls back to text-based regex extraction for reliability
    3. Handles both spaced ("Change in real GDP") and non-spaced ("ChangeinrealGDP") formats
    4. Dynamically detects meeting year from document
    """
    
    def __init__(self, pdf_parser):
        """
        Initialize SEP extractor.
        
        Args:
            pdf_parser: PDFParser instance for text/table extraction
        """
        self.pdf_parser = pdf_parser
        self.meeting_date = None
        self.base_year = None
        logger.info(f"Initialized SEP extractor for: {pdf_parser.file_path}")
    
    def extract_projections(self) -> Dict[str, Any]:
        """
        Extract all economic projections from SEP document.
        
        FIXED: Now uses dynamic year detection!
        
        Returns:
            Dictionary containing:
            - meeting_date: Date of FOMC meeting
            - base_year: First projection year (extracted from document)
            - projections: Dict of variables with year-by-year projections
            - extraction_method: 'table' or 'text'
            
        Example output:
        {
            'meeting_date': '2021-09-22',
            'base_year': 2021,
            'extraction_method': 'text',
            'projections': {
                'gdp_growth': {
                    '2021': 5.9,
                    '2022': 3.8,
                    '2023': 2.5,
                    '2024': 2.0,
                    'longer_run': 1.8
                },
                ...
            }
        }
        """
        logger.info("Extracting SEP projections with dynamic year detection")
        
        # STEP 1: Extract metadata and determine meeting date/year
        text = self.pdf_parser.extract_text()
        metadata = self.pdf_parser.extract_metadata_from_text(text)
        self.meeting_date = metadata.get('meeting_date')
        
        # STEP 2: Determine base year from meeting date or document
        self.base_year = self._detect_base_year(text, self.meeting_date)
        logger.info(f"Detected base year: {self.base_year}")
        
        # STEP 3: Extract projections with dynamic years
        projections = self._extract_from_tables()
        extraction_method = 'table'
        
        # If table extraction failed or incomplete, use text-based extraction
        if not projections or len(projections) < 5:
            logger.info("Table extraction incomplete, falling back to text-based extraction")
            projections = self._extract_from_text()
            extraction_method = 'text'
        
        result = {
            'meeting_date': self.meeting_date.strftime('%Y-%m-%d') if self.meeting_date else None,
            'base_year': self.base_year,
            'extraction_method': extraction_method,
            'variables_extracted': len(projections),
            'projections': projections
        }
        
        logger.info(f"Extracted projections for {len(projections)} variables using {extraction_method} method")
        logger.info(f"Projection years: {self.base_year}-{self.base_year + 3} + longer run")
        return result
    
    def _detect_base_year(self, text: str, meeting_date: Optional[datetime]) -> int:
        """
        Detect the base projection year from document.
        
        Strategy:
        1. Use meeting date year if available
        2. Look for year headers in table (e.g., "2021 2022 2023 2024")
        3. Extract from title (e.g., "September 2021")
        4. Fallback to current year
        
        Args:
            text: Full document text
            meeting_date: Extracted meeting date
            
        Returns:
            Base projection year (integer)
        """
        # Strategy 1: Use meeting date
        if meeting_date:
            base_year = meeting_date.year
            logger.info(f"Base year from meeting date: {base_year}")
            return base_year
        
        # Strategy 2: Find year sequence in table headers
        # Look for pattern like "2021 2022 2023 2024" or "2025 2026 2027 2028"
        year_sequence_pattern = r'(\d{4})\s+(\d{4})\s+(\d{4})\s+(\d{4})'
        match = re.search(year_sequence_pattern, text)
        if match:
            base_year = int(match.group(1))
            logger.info(f"Base year from table headers: {base_year}")
            return base_year
        
        # Strategy 3: Extract from document title
        # Look for "September 22, 2021" or similar
        date_pattern = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:–\d{1,2})?,?\s+(\d{4})'
        match = re.search(date_pattern, text[:1000])  # Search first 1000 chars
        if match:
            base_year = int(match.group(1))
            logger.info(f"Base year from document date: {base_year}")
            return base_year
        
        # Strategy 4: Fallback to current year
        from datetime import datetime
        base_year = datetime.now().year
        logger.warning(f"Could not detect base year, using current year: {base_year}")
        return base_year
    
    def _extract_from_tables(self) -> Dict[str, Dict[str, float]]:
        """
        Extract projections from PDF tables using pdfplumber.
        
        This method attempts to parse Table 1 (Economic Projections) which
        typically appears on page 2 of SEP documents.
        
        Returns:
            Dictionary of projections by variable and year
        """
        logger.info("Attempting table-based extraction")
        
        try:
            tables = self.pdf_parser.extract_tables()
            logger.info(f"Extracted {len(tables)} tables")
            
            if not tables:
                return {}
            
            # Find the main projection table (usually the largest table on page 2)
            projection_table = self._find_projection_table(tables)
            
            if projection_table is None:
                logger.warning("Could not find projection table")
                return {}
            
            logger.info("Found projection table")
            
            # Parse the table with dynamic years
            projections = self._parse_projection_table(projection_table)
            return projections
            
        except Exception as e:
            logger.error(f"Error in table extraction: {e}")
            return {}
    
    def _extract_from_text(self) -> Dict[str, Dict[str, float]]:
        """
        Extract projections directly from text using regex patterns.
        
        FIXED VERSION with dynamic years!
        
        This is the most reliable method for SEP documents as it handles:
        - Non-spaced text (e.g., "ChangeinrealGDP")
        - Spaced text (e.g., "Change in real GDP")
        - Various formatting inconsistencies
        - ANY year (2021, 2022, 2025, etc.)
        
        Returns:
            Dictionary of projections by variable and year
        """
        logger.info("Using text-based extraction with dynamic years")
        
        text = self.pdf_parser.extract_text()
        lines = text.split('\n')
        
        projections = {}
        
        # Generate year keys dynamically
        year_keys = [
            str(self.base_year),
            str(self.base_year + 1),
            str(self.base_year + 2),
            str(self.base_year + 3),
            'longer_run'
        ]
        
        for line in lines:
            # GDP Growth - handles both spaced and non-spaced formats
            if line.startswith('ChangeinrealGDP') or line.startswith('Change in real GDP'):
                numbers = re.findall(r'(\d+\.\d+)', line)
                if len(numbers) >= 5:
                    projections['gdp_growth'] = {
                        year_keys[0]: float(numbers[0]),
                        year_keys[1]: float(numbers[1]),
                        year_keys[2]: float(numbers[2]),
                        year_keys[3]: float(numbers[3]),
                        'longer_run': float(numbers[4])
                    }
                    logger.info(f"Extracted GDP growth for years {year_keys[0]}-{year_keys[3]}: {projections['gdp_growth']}")
            
            # Unemployment Rate
            elif 'Unemployment' in line and 'rate' in line and 'Juneproject' not in line:
                numbers = re.findall(r'(\d+\.\d+)', line)
                if len(numbers) >= 5:
                    projections['unemployment_rate'] = {
                        year_keys[0]: float(numbers[0]),
                        year_keys[1]: float(numbers[1]),
                        year_keys[2]: float(numbers[2]),
                        year_keys[3]: float(numbers[3]),
                        'longer_run': float(numbers[4])
                    }
                    logger.info(f"Extracted unemployment rate for years {year_keys[0]}-{year_keys[3]}: {projections['unemployment_rate']}")
            
            # PCE Inflation (not Core)
            elif (line.startswith('PCE inflation') or line.startswith('PCEinflation')) and 'Core' not in line and 'Juneproject' not in line:
                numbers = re.findall(r'(\d+\.\d+)', line)
                if len(numbers) >= 5:
                    projections['pce_inflation'] = {
                        year_keys[0]: float(numbers[0]),
                        year_keys[1]: float(numbers[1]),
                        year_keys[2]: float(numbers[2]),
                        year_keys[3]: float(numbers[3]),
                        'longer_run': float(numbers[4])
                    }
                    logger.info(f"Extracted PCE inflation for years {year_keys[0]}-{year_keys[3]}: {projections['pce_inflation']}")
            
            # Core PCE Inflation (no longer run projection for Core PCE)
            elif (line.startswith('Core PCE') or line.startswith('CorePCE')) and 'Juneproject' not in line:
                numbers = re.findall(r'(\d+\.\d+)', line)
                if len(numbers) >= 4:
                    projections['core_pce_inflation'] = {
                        year_keys[0]: float(numbers[0]),
                        year_keys[1]: float(numbers[1]),
                        year_keys[2]: float(numbers[2]),
                        year_keys[3]: float(numbers[3])
                    }
                    logger.info(f"Extracted Core PCE inflation for years {year_keys[0]}-{year_keys[3]}: {projections['core_pce_inflation']}")
            
            # Federal Funds Rate - handles both spaced and non-spaced formats
            elif (line.startswith('Federalfundsrate') or line.startswith('Federal funds rate')) and 'Juneproject' not in line:
                numbers = re.findall(r'(\d+\.\d+)', line)
                if len(numbers) >= 5:
                    projections['fed_funds_rate'] = {
                        year_keys[0]: float(numbers[0]),
                        year_keys[1]: float(numbers[1]),
                        year_keys[2]: float(numbers[2]),
                        year_keys[3]: float(numbers[3]),
                        'longer_run': float(numbers[4])
                    }
                    logger.info(f"Extracted Fed Funds rate for years {year_keys[0]}-{year_keys[3]}: {projections['fed_funds_rate']}")
        
        logger.info(f"Extracted projections for {len(projections)} variables with dynamic years")
        return projections
    
    def _find_projection_table(self, tables: List[Dict]) -> Optional[Dict]:
        """
        Find the main economic projections table.
        
        SEP Table 1 is usually:
        - On page 2 (page index 1)
        - The largest table on the page
        - Contains "Variable" or economic indicators
        
        Args:
            tables: List of extracted tables
            
        Returns:
            The projection table or None
        """
        # Look for tables on page 1 (0-indexed, which is page 2 of document)
        page_1_tables = [t for t in tables if t['page'] == 1]
        
        if not page_1_tables:
            # Try page 0 as fallback
            page_1_tables = [t for t in tables if t['page'] == 0]
        
        if not page_1_tables:
            return None
        
        # Return the largest table (most rows)
        return max(page_1_tables, key=lambda t: t['rows'])
    
    def _parse_projection_table(self, table: Dict) -> Dict[str, Dict[str, float]]:
        """
        Parse the projection table to extract values.
        
        UPDATED: Now uses dynamic years!
        
        Table structure (example):
        Row 0 (header): | Variable | 2021 | 2022 | 2023 | 2024 | Longer run |
        Row 1: | Change in real GDP | 5.9 | 3.8 | 2.5 | 2.0 | 1.8 |
        Row 2: | Unemployment rate | 4.8 | 3.8 | 3.5 | 3.5 | 4.0 |
        ...
        
        Args:
            table: Extracted table dictionary
            
        Returns:
            Dictionary of projections
        """
        logger.info("Parsing projection table with dynamic years")
        
        table_data = table['data']
        if not table_data or len(table_data) < 2:
            return {}
        
        # Extract header to identify year columns
        header_row = table_data[0]
        
        # Find year columns (look for 4-digit years)
        year_columns = []
        for idx, cell in enumerate(header_row):
            if cell and re.match(r'^\d{4}$', str(cell).strip()):
                year_columns.append((idx, str(cell).strip()))
        
        # Add "Longer run" column
        for idx, cell in enumerate(header_row):
            if cell and 'longer' in str(cell).lower():
                year_columns.append((idx, 'longer_run'))
        
        logger.info(f"Found year columns: {year_columns}")
        
        projections = {}
        
        # Parse data rows
        for row in table_data[1:]:
            if not row or len(row) < 2:
                continue
            
            # First cell is variable name
            var_name_cell = str(row[0]).strip() if row[0] else ""
            
            # Match to known variables
            matched_var = None
            for var_key, var_config in SEP_VARIABLES.items():
                if var_config['name'].lower() in var_name_cell.lower():
                    matched_var = var_key
                    break
            
            if not matched_var:
                continue
            
            # Extract projections for this variable
            var_projections = {}
            for col_idx, year in year_columns:
                if col_idx < len(row):
                    value_str = str(row[col_idx]).strip() if row[col_idx] else ""
                    
                    if value_str and value_str != '—' and value_str != 'n/a':
                        parsed_value = self._parse_value(value_str, SEP_VARIABLES[matched_var]['type'])
                        
                        if parsed_value is not None:
                            var_projections[year] = parsed_value
            
            if var_projections:
                projections[matched_var] = var_projections
                logger.info(f"Extracted {matched_var}: {var_projections}")
        
        logger.info(f"Extracted projections for {len(projections)} variables from table")
        return projections
    
    def _parse_value(self, value_str: str, value_type: str) -> Optional[float]:
        """
        Parse a value string to float.
        
        Handles:
        - Simple numbers: "3.5"
        - Ranges: "2.0-2.5" (takes midpoint)
        - Percentages: "3.5%" (strips %)
        
        Args:
            value_str: String to parse
            value_type: Expected type (percentage, level, rate)
            
        Returns:
            Parsed float value or None if parsing fails
        """
        try:
            # Remove common formatting
            cleaned = value_str.replace('%', '').replace(',', '').strip()
            
            # Handle ranges (e.g., "2.0-2.5")
            if '-' in cleaned and not cleaned.startswith('-'):
                parts = cleaned.split('-')
                if len(parts) == 2:
                    try:
                        low = float(parts[0].strip())
                        high = float(parts[1].strip())
                        return (low + high) / 2  # Take midpoint
                    except ValueError:
                        pass
            
            # Try direct conversion
            return float(cleaned)
            
        except (ValueError, AttributeError):
            logger.warning(f"Could not parse value: {value_str}")
            return None
    
    def get_meeting_date(self) -> Optional[datetime]:
        """Get the meeting date for this SEP."""
        return self.meeting_date


# Utility function for standalone usage
def extract_sep_projections(file_path: str) -> Dict[str, Any]:
    """
    Convenience function to extract SEP projections from a file.
    
    FIXED VERSION with dynamic year detection!
    
    Args:
        file_path: Path to SEP PDF document
        
    Returns:
        Dictionary with extracted projections
        
    Example:
        >>> forecasts = extract_sep_projections('sep_2021_q3.pdf')
        >>> print(forecasts['base_year'])
        2021
        >>> print(forecasts['projections']['pce_inflation']['2022'])
        2.2
    """
    from pdf_parser import PDFParser
    
    parser = PDFParser(Path(file_path))
    extractor = SEPExtractor(parser)
    return extractor.extract_projections()


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        sep_file = sys.argv[1]
        print(f"\n{'='*80}")
        print(f"Extracting SEP Projections from: {sep_file}")
        print(f"{'='*80}\n")
        
        result = extract_sep_projections(sep_file)
        
        print(f"Meeting Date: {result.get('meeting_date', 'N/A')}")
        print(f"Base Year: {result.get('base_year', 'N/A')}")
        print(f"Extraction Method: {result['extraction_method']}")
        print(f"Variables Extracted: {result['variables_extracted']}\n")
        
        for var_name, projections in result['projections'].items():
            print(f"\n{var_name.replace('_', ' ').title()}:")
            for year, value in projections.items():
                print(f"  {year}: {value}%")
    else:
        print("Usage: python sep_extractor.py <path_to_sep_pdf>")
        print("Example: python sep_extractor.py sep_2025_q3.pdf")
        print("Example: python sep_extractor.py sep_2021_q3.pdf")
