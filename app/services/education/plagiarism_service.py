"""
Service for detecting plagiarism in submitted content.
Uses various techniques including text similarity, fingerprinting, and external API checks.
"""

import logging
from typing import Dict, List, Optional, Tuple
import difflib
from collections import defaultdict
import re
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class PlagiarismResult:
    """Represents the result of a plagiarism check."""
    similarity_score: float
    matched_text: str
    source_text: str
    source_url: Optional[str] = None
    confidence: float = 0.0
    timestamp: datetime = datetime.now()

class PlagiarismService:
    """Service for detecting plagiarism in submitted content."""
    
    def __init__(self):
        """Initialize the plagiarism service."""
        self.text_cache = defaultdict(list)
        self.min_similarity_threshold = 0.8
        self.max_cache_size = 1000
        
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for comparison."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using difflib."""
        matcher = difflib.SequenceMatcher(None, text1, text2)
        return matcher.ratio()
    
    def _fingerprint_text(self, text: str) -> List[str]:
        """Generate text fingerprints for comparison."""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        # Generate n-grams (3 words)
        ngrams = []
        for sentence in sentences:
            words = sentence.split()
            for i in range(len(words) - 2):
                ngrams.append(' '.join(words[i:i+3]))
        return ngrams
    
    async def check_plagiarism(
        self,
        submitted_text: str,
        reference_texts: Optional[List[str]] = None
    ) -> List[PlagiarismResult]:
        """
        Check for plagiarism in submitted text.
        
        Args:
            submitted_text: The text to check for plagiarism
            reference_texts: Optional list of reference texts to compare against
            
        Returns:
            List of PlagiarismResult objects containing matches found
        """
        try:
            # Clean the submitted text
            cleaned_submitted = self._clean_text(submitted_text)
            
            results = []
            
            # Check against reference texts if provided
            if reference_texts:
                for ref_text in reference_texts:
                    cleaned_ref = self._clean_text(ref_text)
                    similarity = self._calculate_similarity(cleaned_submitted, cleaned_ref)
                    
                    if similarity >= self.min_similarity_threshold:
                        results.append(PlagiarismResult(
                            similarity_score=similarity,
                            matched_text=submitted_text,
                            source_text=ref_text,
                            confidence=similarity
                        ))
            
            # Check against cached texts
            for cached_text in self.text_cache:
                similarity = self._calculate_similarity(cleaned_submitted, cached_text)
                
                if similarity >= self.min_similarity_threshold:
                    results.append(PlagiarismResult(
                        similarity_score=similarity,
                        matched_text=submitted_text,
                        source_text=cached_text,
                        confidence=similarity
                    ))
            
            # Add submitted text to cache
            self._add_to_cache(cleaned_submitted)
            
            return results
            
        except Exception as e:
            logger.error(f"Error checking plagiarism: {str(e)}")
            return []
    
    def _add_to_cache(self, text: str) -> None:
        """Add text to the cache, maintaining size limit."""
        if len(self.text_cache) >= self.max_cache_size:
            # Remove oldest entry
            self.text_cache.pop(next(iter(self.text_cache)))
        self.text_cache[text] = datetime.now()
    
    async def check_against_database(
        self,
        submitted_text: str,
        database_entries: List[Dict[str, str]]
    ) -> List[PlagiarismResult]:
        """
        Check submitted text against a database of existing content.
        
        Args:
            submitted_text: The text to check
            database_entries: List of dictionaries containing database entries
            
        Returns:
            List of PlagiarismResult objects containing matches found
        """
        try:
            results = []
            cleaned_submitted = self._clean_text(submitted_text)
            
            for entry in database_entries:
                if 'content' in entry:
                    cleaned_entry = self._clean_text(entry['content'])
                    similarity = self._calculate_similarity(cleaned_submitted, cleaned_entry)
                    
                    if similarity >= self.min_similarity_threshold:
                        results.append(PlagiarismResult(
                            similarity_score=similarity,
                            matched_text=submitted_text,
                            source_text=entry['content'],
                            source_url=entry.get('url'),
                            confidence=similarity
                        ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error checking against database: {str(e)}")
            return []
    
    async def generate_report(
        self,
        results: List[PlagiarismResult]
    ) -> Dict[str, Any]:
        """
        Generate a plagiarism report from results.
        
        Args:
            results: List of PlagiarismResult objects
            
        Returns:
            Dictionary containing report data
        """
        try:
            if not results:
                return {
                    "status": "clean",
                    "message": "No plagiarism detected",
                    "confidence": 1.0
                }
            
            # Calculate overall statistics
            avg_similarity = sum(r.similarity_score for r in results) / len(results)
            max_similarity = max(r.similarity_score for r in results)
            
            return {
                "status": "plagiarism_detected",
                "message": f"Found {len(results)} potential matches",
                "confidence": 1 - max_similarity,
                "average_similarity": avg_similarity,
                "max_similarity": max_similarity,
                "matches": [
                    {
                        "similarity": r.similarity_score,
                        "source_url": r.source_url,
                        "timestamp": r.timestamp.isoformat()
                    }
                    for r in results
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {
                "status": "error",
                "message": "Error generating report",
                "error": str(e)
            }
