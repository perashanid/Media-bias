import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BengaliTextPreprocessor:
    """Text preprocessing utilities for Bengali language"""
    
    def __init__(self):
        # Bengali punctuation and special characters
        self.bengali_punctuation = '।,;:!?()[]{}""''—–-'
        
        # Common Bengali stopwords
        self.bengali_stopwords = {
            'এবং', 'বা', 'কিন্তু', 'তবে', 'যদি', 'তাহলে', 'কারণ', 'যেহেতু',
            'এই', 'সেই', 'ওই', 'যে', 'যা', 'যার', 'যাকে', 'যাদের',
            'আমি', 'তুমি', 'সে', 'তার', 'তাদের', 'আমার', 'তোমার',
            'হয়', 'হবে', 'হয়েছে', 'হচ্ছে', 'ছিল', 'থাকে', 'আছে',
            'না', 'নয়', 'নেই', 'নাই', 'কোন', 'কোনো', 'সব', 'সকল',
            'দিয়ে', 'থেকে', 'পর্যন্ত', 'মধ্যে', 'ভিতরে', 'বাইরে',
            'উপর', 'নিচে', 'সামনে', 'পিছনে', 'পাশে', 'কাছে'
        }
        
        # Bengali numbers to digits mapping
        self.bengali_digits = {
            '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
            '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
        }
    
    def preprocess_bengali_text(self, text: str) -> str:
        """Comprehensive preprocessing for Bengali text"""
        if not text:
            return ""
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Convert Bengali digits to English digits
        text = self._convert_bengali_digits(text)
        
        # Normalize Bengali punctuation
        text = self._normalize_bengali_punctuation(text)
        
        # Remove extra punctuation
        text = re.sub(r'[।]{2,}', '।', text)  # Multiple Bengali periods
        text = re.sub(r'[!]{2,}', '!', text)  # Multiple exclamations
        text = re.sub(r'[?]{2,}', '?', text)  # Multiple questions
        
        return text.strip()
    
    def _convert_bengali_digits(self, text: str) -> str:
        """Convert Bengali digits to English digits"""
        for bengali_digit, english_digit in self.bengali_digits.items():
            text = text.replace(bengali_digit, english_digit)
        return text
    
    def _normalize_bengali_punctuation(self, text: str) -> str:
        """Normalize Bengali punctuation marks"""
        # Replace various dash types with standard dash
        text = re.sub(r'[—–−]', '-', text)
        
        # Normalize quotation marks
        text = re.sub(r'[""''`´]', '"', text)
        
        # Ensure proper spacing around punctuation
        text = re.sub(r'([।!?])', r'\1 ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def tokenize_bengali(self, text: str) -> List[str]:
        """Tokenize Bengali text into words"""
        # Preprocess first
        text = self.preprocess_bengali_text(text)
        
        # Split on whitespace and punctuation
        tokens = re.findall(r'[^\s।,;:!?()\[\]{}""''—–\\-]+', text)
        
        # Filter out empty tokens and very short tokens
        tokens = [token.strip() for token in tokens if len(token.strip()) > 1]
        
        return tokens
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove Bengali stopwords from token list"""
        return [token for token in tokens if token not in self.bengali_stopwords]
    
    def extract_bengali_features(self, text: str) -> Dict[str, Any]:
        """Extract linguistic features from Bengali text"""
        tokens = self.tokenize_bengali(text)
        tokens_no_stopwords = self.remove_stopwords(tokens)
        
        # Count different types of characters
        bengali_chars = sum(1 for char in text if '\u0980' <= char <= '\u09FF')
        total_chars = len([char for char in text if char.isalpha()])
        
        # Count sentences (using Bengali period)
        sentences = len(re.split(r'[।!?]+', text))
        
        # Average word length
        avg_word_length = sum(len(token) for token in tokens) / len(tokens) if tokens else 0
        
        return {
            'total_tokens': len(tokens),
            'unique_tokens': len(set(tokens)),
            'tokens_without_stopwords': len(tokens_no_stopwords),
            'bengali_char_ratio': bengali_chars / total_chars if total_chars > 0 else 0,
            'sentence_count': sentences,
            'avg_word_length': avg_word_length,
            'stopword_ratio': (len(tokens) - len(tokens_no_stopwords)) / len(tokens) if tokens else 0
        }


class EnglishTextPreprocessor:
    """Text preprocessing utilities for English language"""
    
    def __init__(self):
        # Common English stopwords
        self.english_stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'would', 'you', 'your', 'this', 'they',
            'we', 'been', 'have', 'their', 'said', 'each', 'which', 'she', 'do',
            'how', 'if', 'not', 'what', 'all', 'any', 'can', 'had', 'her', 'his',
            'but', 'or', 'so', 'up', 'out', 'who', 'get', 'use', 'man', 'new',
            'now', 'old', 'see', 'him', 'two', 'way', 'may', 'say', 'come', 'could',
            'time', 'very', 'when', 'much', 'go', 'well', 'were', 'been', 'than'
        }
    
    def preprocess_english_text(self, text: str) -> str:
        """Comprehensive preprocessing for English text"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove or normalize special characters
        text = re.sub(r'[""''`´]', '"', text)  # Normalize quotes
        text = re.sub(r'[—–−]', '-', text)    # Normalize dashes
        
        # Remove extra punctuation
        text = re.sub(r'[.]{2,}', '.', text)   # Multiple periods
        text = re.sub(r'[!]{2,}', '!', text)   # Multiple exclamations
        text = re.sub(r'[?]{2,}', '?', text)   # Multiple questions
        
        return text.strip()
    
    def tokenize_english(self, text: str) -> List[str]:
        """Tokenize English text into words"""
        # Preprocess first
        text = self.preprocess_english_text(text)
        
        # Split on whitespace and punctuation, keep only alphabetic tokens
        tokens = re.findall(r'\b[a-zA-Z]+\b', text)
        
        # Filter out very short tokens
        tokens = [token for token in tokens if len(token) > 1]
        
        return tokens
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove English stopwords from token list"""
        return [token for token in tokens if token.lower() not in self.english_stopwords]
    
    def extract_english_features(self, text: str) -> Dict[str, Any]:
        """Extract linguistic features from English text"""
        tokens = self.tokenize_english(text)
        tokens_no_stopwords = self.remove_stopwords(tokens)
        
        # Count sentences
        sentences = len(re.split(r'[.!?]+', text))
        
        # Average word length
        avg_word_length = sum(len(token) for token in tokens) / len(tokens) if tokens else 0
        
        # Count syllables (rough approximation)
        syllable_count = sum(self._count_syllables(token) for token in tokens)
        
        return {
            'total_tokens': len(tokens),
            'unique_tokens': len(set(tokens)),
            'tokens_without_stopwords': len(tokens_no_stopwords),
            'sentence_count': sentences,
            'avg_word_length': avg_word_length,
            'syllable_count': syllable_count,
            'stopword_ratio': (len(tokens) - len(tokens_no_stopwords)) / len(tokens) if tokens else 0
        }
    
    def _count_syllables(self, word: str) -> int:
        """Rough syllable counting for English words"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)  # Every word has at least 1 syllable