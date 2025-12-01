"""
Text Analyzer for FOMC Documents - FIXED VERSION
Extracts policy decisions, sentiment, and key information from FOMC documents
"""

import re
from typing import Dict, Optional, List, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TextAnalyzer:
    """Analyzes FOMC document text to extract policy information"""
    
    def __init__(self, pdf_path: str, pdf_parser):
        """
        Initialize text analyzer
        
        Args:
            pdf_path: Path to the PDF file
            pdf_parser: PDFParser instance for text extraction
        """
        self.pdf_path = pdf_path
        self.pdf_parser = pdf_parser
        logger.info(f"Initialized text analyzer for: {pdf_path}")
    
    def analyze_full_document(self) -> Dict:
        """
        Perform comprehensive analysis of the document
        
        Returns:
            Dictionary containing all analysis results
        """
        logger.info("Performing full text analysis")
        
        # Extract text
        text = self.pdf_parser.extract_text()
        
        # Perform all analyses
        policy_decision = self.extract_policy_decision(text)
        sentiment = self.analyze_sentiment(text)
        forward_guidance = self.extract_forward_guidance(text)
        economic_assessment = self.extract_economic_assessment(text)
        voting_record = self.extract_voting_record(text)
        key_phrases = self.extract_key_phrases(text)
        
        return {
            'policy_decision': policy_decision,
            'sentiment': sentiment,
            'forward_guidance': forward_guidance,
            'economic_assessment': economic_assessment,
            'voting_record': voting_record,
            'key_phrases': key_phrases,
            'metadata': self.pdf_parser.get_metadata()
        }
    
    def extract_policy_decision(self, text: Optional[str] = None) -> Dict:
        """
        Extract the policy decision from FOMC Minutes
        
        UPDATED PATTERNS based on actual FOMC Minutes language:
        - "decided to lower the target range"
        - "decided to raise the target range"  
        - "voted to maintain the target range"
        - "to keep the target range"
        - "lowering of the target range by X basis points"
        
        Args:
            text: Document text (if None, will extract from PDF)
            
        Returns:
            Dictionary with policy decision details
        """
        logger.info("Extracting policy decision")
        
        if text is None:
            text = self.pdf_parser.extract_text()
        
        # Initialize result
        decision = {
            'action': 'unknown',
            'change_bps': None,
            'target_range_lower': None,
            'target_range_upper': None,
            'decision_text': None
        }
        
        # ========================================
        # PATTERN 1: "decided/voted to lower/raise/maintain the target range"
        # ========================================
        # Examples:
        # - "decided to lower the target range for the federal funds rate by ¼ percentage point to 3¾ to 4 percent"
        # - "voted to maintain the target range"
        # - "decided to raise the target range by 50 basis points"
        
        rate_action_pattern = re.compile(
            r'(?:decided|voted)\s+to\s+(lower|raise|maintain|keep)\s+the\s+target\s+range'
            r'(?:\s+for\s+the\s+federal\s+funds\s+rate)?'
            r'(?:\s+by\s+([¼½¾\d]+)\s+(?:percentage\s+point|basis\s+points?))?'
            r'(?:\s+to\s+([\d.¼½¾]+)\s+to\s+([\d.¼½¾]+)\s+percent)?',
            re.IGNORECASE
        )
        
        # ========================================
        # PATTERN 2: "lowering/raising of the target range"
        # ========================================
        # Example: "In support of the lowering of the target range by 25 basis points"
        
        action_of_pattern = re.compile(
            r'(?:lowering|raising)\s+of\s+the\s+target\s+range'
            r'(?:\s+by\s+(\d+)\s+basis\s+points?)?',
            re.IGNORECASE
        )
        
        # ========================================
        # PATTERN 3: Direct target range statement
        # ========================================
        # Example: "the target range for the federal funds rate at 0 to 1/4 percent"
        
        target_range_pattern = re.compile(
            r'target\s+range\s+(?:for\s+the\s+federal\s+funds\s+rate\s+)?'
            r'(?:at|to|of)\s+([\d.¼½¾]+)\s+to\s+([\d.¼½¾]+)\s+percent',
            re.IGNORECASE
        )
        
        # ========================================
        # Try all patterns
        # ========================================
        
        # Try Pattern 1: decided/voted to...
        match = rate_action_pattern.search(text)
        if match:
            action_word = match.group(1).lower()
            change_str = match.group(2)
            lower_str = match.group(3)
            upper_str = match.group(4)
            
            # Map action word to decision type
            if action_word in ['lower', 'lowering']:
                decision['action'] = 'rate_decrease'
            elif action_word in ['raise', 'raising']:
                decision['action'] = 'rate_increase'
            elif action_word in ['maintain', 'keep']:
                decision['action'] = 'rate_unchanged'
            
            # Extract change amount
            if change_str:
                decision['change_bps'] = self._parse_bps(change_str)
            
            # Extract target range
            if lower_str and upper_str:
                decision['target_range_lower'] = self._parse_rate(lower_str)
                decision['target_range_upper'] = self._parse_rate(upper_str)
            
            decision['decision_text'] = match.group(0)
            logger.info(f"Found policy decision (Pattern 1): {decision['action']}")
            
        # Try Pattern 2 if Pattern 1 failed
        if decision['action'] == 'unknown':
            match = action_of_pattern.search(text)
            if match:
                action_text = match.group(0)
                
                if 'lowering' in action_text.lower():
                    decision['action'] = 'rate_decrease'
                elif 'raising' in action_text.lower():
                    decision['action'] = 'rate_increase'
                
                if match.group(1):
                    decision['change_bps'] = int(match.group(1))
                
                decision['decision_text'] = action_text
                logger.info(f"Found policy decision (Pattern 2): {decision['action']}")
        
        # Try Pattern 3: Extract target range even if action unknown
        if decision['target_range_lower'] is None:
            match = target_range_pattern.search(text)
            if match:
                decision['target_range_lower'] = self._parse_rate(match.group(1))
                decision['target_range_upper'] = self._parse_rate(match.group(2))
                logger.info(f"Found target range: {decision['target_range_lower']}-{decision['target_range_upper']}")
        
        # ========================================
        # FALLBACK: Look in "Committee Policy Actions" section
        # ========================================
        if decision['action'] == 'unknown':
            # Find the "Committee Policy Actions" section
            section_match = re.search(
                r'Committee\s+Policy\s+Actions(.*?)(?=\n[A-Z][a-z]+\s+(?:Vote|Voting|Notation)|$)',
                text,
                re.IGNORECASE | re.DOTALL
            )
            
            if section_match:
                section_text = section_match.group(1)
                
                # Check for rate changes in this section
                if 'lower' in section_text.lower() or 'decrease' in section_text.lower() or 'cut' in section_text.lower():
                    if 'target range' in section_text.lower() or 'federal funds rate' in section_text.lower():
                        decision['action'] = 'rate_decrease'
                        logger.info("Detected rate decrease from Policy Actions section")
                        
                elif 'raise' in section_text.lower() or 'increase' in section_text.lower() or 'hike' in section_text.lower():
                    if 'target range' in section_text.lower() or 'federal funds rate' in section_text.lower():
                        decision['action'] = 'rate_increase'
                        logger.info("Detected rate increase from Policy Actions section")
                        
                elif 'maintain' in section_text.lower() or 'unchanged' in section_text.lower() or 'kept' in section_text.lower():
                    if 'target range' in section_text.lower() or 'federal funds rate' in section_text.lower():
                        decision['action'] = 'rate_unchanged'
                        logger.info("Detected rate unchanged from Policy Actions section")
        
        return decision
    
    def _parse_bps(self, bps_str: str) -> int:
        """
        Parse basis points from string
        
        Args:
            bps_str: String containing basis points (e.g., "25", "¼", "0.25")
            
        Returns:
            Integer basis points
        """
        # Handle fractions
        fraction_map = {
            '¼': 0.25,
            '½': 0.50,
            '¾': 0.75
        }
        
        if bps_str in fraction_map:
            return int(fraction_map[bps_str] * 100)
        
        # Handle decimal
        try:
            return int(float(bps_str) * 100)
        except:
            return 0
    
    def _parse_rate(self, rate_str: str) -> float:
        """
        Parse interest rate from string
        
        Args:
            rate_str: String containing rate (e.g., "3¾", "3.75", "0")
            
        Returns:
            Float rate percentage
        """
        # Handle fractions
        fraction_map = {
            '¼': 0.25,
            '½': 0.50,
            '¾': 0.75
        }
        
        # Check for whole number + fraction
        match = re.match(r'(\d+)([¼½¾])?', rate_str)
        if match:
            whole = int(match.group(1))
            frac_char = match.group(2)
            frac = fraction_map.get(frac_char, 0)
            return whole + frac
        
        # Try direct float conversion
        try:
            return float(rate_str)
        except:
            return 0.0
    
    def analyze_sentiment(self, text: Optional[str] = None) -> Dict:
        """
        Analyze the sentiment/tone of the document
        
        Args:
            text: Document text (if None, will extract from PDF)
            
        Returns:
            Dictionary with sentiment analysis
        """
        logger.info("Analyzing sentiment")
        
        if text is None:
            text = self.pdf_parser.extract_text()
        
        # Define sentiment keywords
        hawkish_keywords = [
            'inflation', 'inflationary', 'price pressures', 'elevated inflation',
            'tight', 'tighten', 'restrictive', 'vigilant', 'concerned', 'risks to upside'
        ]
        
        dovish_keywords = [
            'accommodative', 'supportive', 'gradual', 'patient', 'appropriate',
            'uncertainty', 'downside risks', 'monitor', 'flexible', 'lower'
        ]
        
        # Count occurrences (case-insensitive)
        text_lower = text.lower()
        hawkish_count = sum(text_lower.count(kw) for kw in hawkish_keywords)
        dovish_count = sum(text_lower.count(kw) for kw in dovish_keywords)
        
        # Determine overall sentiment
        if hawkish_count > dovish_count * 1.5:
            sentiment = 'hawkish'
        elif dovish_count > hawkish_count * 1.5:
            sentiment = 'dovish'
        else:
            sentiment = 'neutral'
        
        # Calculate confidence
        total = hawkish_count + dovish_count
        if total == 0:
            confidence = 'low'
        elif abs(hawkish_count - dovish_count) / total > 0.4:
            confidence = 'high'
        else:
            confidence = 'medium'
        
        # Calculate sentiment score (-10 to +10, negative = dovish, positive = hawkish)
        if total > 0:
            score = int(10 * (hawkish_count - dovish_count) / total)
        else:
            score = 0
        
        return {
            'overall': sentiment,
            'confidence': confidence,
            'score': score,
            'hawkish_signals': hawkish_count,
            'dovish_signals': dovish_count
        }
    
    def extract_forward_guidance(self, text: Optional[str] = None) -> Dict:
        """Extract forward guidance language"""
        logger.info("Extracting forward guidance")
        
        if text is None:
            text = self.pdf_parser.extract_text()
        
        # Look for forward guidance patterns
        guidance_patterns = [
            r'Committee\s+(?:will|expects to|intends to|anticipates)\s+(.{50,200})',
            r'(?:policy|stance)\s+will\s+(?:remain|be|continue)\s+(.{50,200})',
            r'appropriate\s+to\s+(?:maintain|keep|adjust)\s+(.{50,200})'
        ]
        
        guidance_text = []
        for pattern in guidance_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                guidance_text.append(match.group(0).strip())
        
        return {
            'guidance_statements': guidance_text[:3],  # Top 3
            'has_guidance': len(guidance_text) > 0
        }
    
    def extract_economic_assessment(self, text: Optional[str] = None) -> Dict:
        """Extract economic assessment"""
        logger.info("Extracting economic assessment")
        
        if text is None:
            text = self.pdf_parser.extract_text()
        
        # Look for economic indicators
        assessment = {
            'employment': self._find_assessment(text, ['employment', 'labor market', 'unemployment']),
            'inflation': self._find_assessment(text, ['inflation', 'price', 'PCE']),
            'growth': self._find_assessment(text, ['growth', 'GDP', 'economic activity']),
            'outlook': self._find_assessment(text, ['outlook', 'forecast', 'projection'])
        }
        
        return assessment
    
    def _find_assessment(self, text: str, keywords: List[str]) -> str:
        """Find assessment for given keywords"""
        for keyword in keywords:
            pattern = rf'{keyword}\s+(?:was|remained|has|had)\s+(.{{50,150}}?)[.;]'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        return "No assessment found"
    
    def extract_voting_record(self, text: Optional[str] = None) -> Dict:
        """
        Extract voting record from FOMC Minutes
        
        Args:
            text: Document text (if None, will extract from PDF)
            
        Returns:
            Dictionary with voting information
        """
        logger.info("Extracting voting record")
        
        if text is None:
            text = self.pdf_parser.extract_text()
        
        # Find voting section
        voting_pattern = re.compile(
            r'Voting\s+(?:for|against)\s+(?:this|the)\s+(?:action|decision):(.+?)(?=\n\n|\n[A-Z])',
            re.IGNORECASE | re.DOTALL
        )
        
        votes_for = []
        votes_against = []
        
        # Extract votes FOR
        for_match = re.search(r'Voting\s+for\s+(?:this|the)\s+(?:action|decision):(.+?)(?=Voting\s+against|Consistent\s+with|\n\n|$)', text, re.IGNORECASE | re.DOTALL)
        if for_match:
            votes_text = for_match.group(1)
            # Extract names (typically "FirstName LastName" or "FirstName I. LastName")
            names = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)', votes_text)
            votes_for = names
        
        # Extract votes AGAINST
        against_match = re.search(r'Voting\s+against\s+(?:this|the)\s+(?:action|decision):(.+?)(?=Consistent\s+with|\n\n|$)', text, re.IGNORECASE | re.DOTALL)
        if against_match:
            votes_text = against_match.group(1)
            names = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)', votes_text)
            votes_against = names
        
        # Check for unanimous vote
        unanimous = len(votes_against) == 0 and len(votes_for) > 0
        
        return {
            'votes_for': votes_for,
            'votes_against': votes_against,
            'unanimous': unanimous,
            'total_votes': len(votes_for) + len(votes_against)
        }
    
    def extract_key_phrases(self, text: Optional[str] = None, n: int = 10) -> List[str]:
        """
        Extract key phrases from the document
        
        Args:
            text: Document text (if None, will extract from PDF)
            n: Number of phrases to extract
            
        Returns:
            List of key phrases
        """
        logger.info(f"Extracting {n} key phrases")
        
        if text is None:
            text = self.pdf_parser.extract_text()
        
        # Find phrases in quotes (often key statements)
        quoted_phrases = re.findall(r'"([^"]{20,150})"', text)
        
        # Find important statements (sentences with key words)
        important_words = ['Committee', 'decided', 'voted', 'inflation', 'employment', 'expects', 'appropriate']
        important_sentences = []
        
        sentences = re.split(r'[.!?]\s+', text)
        for sentence in sentences:
            if any(word in sentence for word in important_words) and 50 < len(sentence) < 200:
                important_sentences.append(sentence.strip())
        
        # Combine and deduplicate
        all_phrases = quoted_phrases + important_sentences
        unique_phrases = list(dict.fromkeys(all_phrases))  # Preserve order, remove duplicates
        
        return unique_phrases[:n]


# Example usage
if __name__ == "__main__":
    from pdf_parser import PDFParser
    
    pdf_path = "example_minutes.pdf"
    parser = PDFParser(pdf_path)
    analyzer = TextAnalyzer(pdf_path, parser)
    
    # Full analysis
    results = analyzer.analyze_full_document()
    print("Policy Decision:", results['policy_decision'])
    print("Sentiment:", results['sentiment'])
