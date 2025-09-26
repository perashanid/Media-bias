import re
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Utility class for detecting Bengali vs English text"""
    
    def __init__(self):
        # Bengali Unicode ranges
        self.bengali_ranges = [
            (0x0980, 0x09FF),  # Bengali block
            (0x200C, 0x200D),  # Zero-width non-joiner and joiner (used in Bengali)
        ]
        
        # Common Bengali words for additional detection
        self.bengali_words = {
            'এবং', 'যে', 'এই', 'তার', 'সে', 'হয়', 'না', 'আছে', 'করে', 'দিয়ে',
            'থেকে', 'হবে', 'বলে', 'যা', 'কিন্তু', 'আর', 'তাই', 'এর', 'সব', 'কোন',
            'বাংলাদেশ', 'ঢাকা', 'সরকার', 'প্রধানমন্ত্রী', 'মন্ত্রী', 'দেশ', 'জনগণ'
        }
        
        # Common English words
        self.english_words = {
            'the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with',
            'for', 'as', 'was', 'on', 'are', 'you', 'all', 'be', 'at', 'have',
            'bangladesh', 'dhaka', 'government', 'minister', 'prime', 'country'
        }
    
    def detect_language(self, text: str) -> str:
        """
        Detect if text is primarily Bengali or English
        
        Args:
            text: Input text to analyze
            
        Returns:
            'bengali', 'english', or 'mixed'
        """
        if not text or len(text.strip()) == 0:
            return 'unknown'
        
        # Calculate character-based detection
        char_scores = self._analyze_characters(text)
        
        # Calculate word-based detection
        word_scores = self._analyze_words(text)
        
        # Combine scores with weights
        bengali_score = (char_scores['bengali'] * 0.7) + (word_scores['bengali'] * 0.3)
        english_score = (char_scores['english'] * 0.7) + (word_scores['english'] * 0.3)
        
        # Determine language based on scores
        if bengali_score > 0.6:
            return 'bengali'
        elif english_score > 0.6:
            return 'english'
        elif bengali_score > english_score:
            return 'bengali'
        elif english_score > bengali_score:
            return 'english'
        else:
            return 'mixed'
    
    def _analyze_characters(self, text: str) -> Dict[str, float]:
        """Analyze character distribution to detect language"""
        total_chars = 0
        bengali_chars = 0
        english_chars = 0
        
        for char in text:
            if char.isalpha():
                total_chars += 1
                
                # Check if character is in Bengali Unicode ranges
                char_code = ord(char)
                is_bengali = any(start <= char_code <= end for start, end in self.bengali_ranges)
                
                if is_bengali:
                    bengali_chars += 1
                elif char.isascii() and char.isalpha():
                    english_chars += 1
        
        if total_chars == 0:
            return {'bengali': 0.0, 'english': 0.0}
        
        bengali_ratio = bengali_chars / total_chars
        english_ratio = english_chars / total_chars
        
        return {
            'bengali': bengali_ratio,
            'english': english_ratio
        }
    
    def _analyze_words(self, text: str) -> Dict[str, float]:
        """Analyze word patterns to detect language"""
        # Clean and tokenize text
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not words:
            return {'bengali': 0.0, 'english': 0.0}
        
        bengali_word_count = 0
        english_word_count = 0
        
        for word in words:
            if word in self.bengali_words:
                bengali_word_count += 1
            elif word in self.english_words:
                english_word_count += 1
        
        total_recognized_words = bengali_word_count + english_word_count
        
        if total_recognized_words == 0:
            return {'bengali': 0.0, 'english': 0.0}
        
        return {
            'bengali': bengali_word_count / total_recognized_words,
            'english': english_word_count / total_recognized_words
        }
    
    def get_language_confidence(self, text: str) -> Tuple[str, float]:
        """
        Get language detection with confidence score
        
        Returns:
            Tuple of (language, confidence_score)
        """
        char_scores = self._analyze_characters(text)
        word_scores = self._analyze_words(text)
        
        # Combine scores
        bengali_score = (char_scores['bengali'] * 0.7) + (word_scores['bengali'] * 0.3)
        english_score = (char_scores['english'] * 0.7) + (word_scores['english'] * 0.3)
        
        if bengali_score > english_score:
            language = 'bengali'
            confidence = bengali_score
        else:
            language = 'english'
            confidence = english_score
        
        return language, confidence
    
    def is_mixed_language(self, text: str, threshold: float = 0.3) -> bool:
        """Check if text contains significant amounts of both languages"""
        char_scores = self._analyze_characters(text)
        
        bengali_ratio = char_scores['bengali']
        english_ratio = char_scores['english']
        
        # Consider mixed if both languages have significant presence
        return bengali_ratio > threshold and english_ratio > threshold