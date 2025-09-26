from typing import Dict, List, Tuple
import re
import logging
from services.text_preprocessor import BengaliTextPreprocessor, EnglishTextPreprocessor

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Sentiment analysis for Bengali and English text"""
    
    def __init__(self):
        self.bengali_preprocessor = BengaliTextPreprocessor()
        self.english_preprocessor = EnglishTextPreprocessor()
        
        # Bengali sentiment words
        self.bengali_positive_words = {
            'ভালো', 'সুন্দর', 'চমৎকার', 'দুর্দান্ত', 'অসাধারণ', 'চমৎকার', 'উৎকৃষ্ট',
            'সফল', 'জয়', 'বিজয়', 'সাফল্য', 'উন্নতি', 'প্রগতি', 'সমৃদ্ধি',
            'খুশি', 'আনন্দ', 'হাসি', 'প্রশংসা', 'স্বাগত', 'ধন্যবাদ', 'কৃতজ্ঞতা',
            'শান্তি', 'স্বস্তি', 'আশা', 'আশাবাদী', 'ইতিবাচক', 'গর্ব', 'গর্বিত',
            'সম্মান', 'সম্মানিত', 'প্রিয়', 'ভালোবাসা', 'স্নেহ', 'মমতা'
        }
        
        self.bengali_negative_words = {
            'খারাপ', 'বাজে', 'ভয়ানক', 'জঘন্য', 'নিকৃষ্ট', 'অসহ্য', 'বিরক্তিকর',
            'ব্যর্থ', 'পরাজয়', 'হার', 'ক্ষতি', 'ধ্বংস', 'বিপর্যয়', 'সমস্যা',
            'দুঃখ', 'কষ্ট', 'ব্যথা', 'যন্ত্রণা', 'কান্না', 'রাগ', 'ক্রোধ',
            'ভয়', 'আতঙ্ক', 'চিন্তা', 'দুশ্চিন্তা', 'নিরাশ', 'হতাশা', 'বিষাদ',
            'অপমান', 'লজ্জা', 'ঘৃণা', 'বিদ্বেষ', 'শত্রুতা', 'অবিচার', 'অন্যায়'
        }
        
        # English sentiment words
        self.english_positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'outstanding',
            'success', 'successful', 'win', 'victory', 'achievement', 'progress', 'improvement',
            'happy', 'joy', 'smile', 'laugh', 'praise', 'welcome', 'thank', 'grateful',
            'peace', 'calm', 'hope', 'optimistic', 'positive', 'proud', 'pride',
            'honor', 'respect', 'love', 'care', 'support', 'help', 'benefit'
        }
        
        self.english_negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'poor', 'disappointing',
            'fail', 'failure', 'lose', 'loss', 'defeat', 'damage', 'destroy', 'problem',
            'sad', 'pain', 'hurt', 'suffer', 'cry', 'angry', 'rage', 'mad',
            'fear', 'scared', 'worry', 'concern', 'disappointed', 'frustrated', 'upset',
            'shame', 'hate', 'dislike', 'enemy', 'unfair', 'wrong', 'injustice'
        }
        
        # Intensity modifiers
        self.intensity_modifiers = {
            'bengali': {
                'খুব': 1.5, 'অত্যন্ত': 2.0, 'অনেক': 1.3, 'বেশ': 1.2, 'যথেষ্ট': 1.1,
                'সামান্য': 0.5, 'কিছুটা': 0.7, 'একটু': 0.6, 'সম্পূর্ণ': 1.8, 'পুরোপুরি': 1.9
            },
            'english': {
                'very': 1.5, 'extremely': 2.0, 'quite': 1.3, 'rather': 1.2, 'fairly': 1.1,
                'slightly': 0.5, 'somewhat': 0.7, 'a bit': 0.6, 'completely': 1.8, 'totally': 1.9
            }
        }
        
        # Negation words
        self.negation_words = {
            'bengali': {'না', 'নয়', 'নেই', 'নাই', 'ছাড়া', 'বিনা', 'অভাবে'},
            'english': {'not', 'no', 'never', 'nothing', 'nobody', 'nowhere', 'neither', 'nor', 'without'}
        }
    
    def analyze_sentiment(self, text: str, language: str) -> float:
        """
        Analyze sentiment of text and return score between -1 (negative) and 1 (positive)
        
        Args:
            text: Input text to analyze
            language: 'bengali' or 'english'
            
        Returns:
            Sentiment score between -1.0 and 1.0
        """
        if not text or not text.strip():
            return 0.0
        
        if language in ['bengali', 'bn']:
            return self._analyze_bengali_sentiment(text)
        elif language in ['english', 'en']:
            return self._analyze_english_sentiment(text)
        else:
            # Try both and take average
            bengali_score = self._analyze_bengali_sentiment(text)
            english_score = self._analyze_english_sentiment(text)
            return (bengali_score + english_score) / 2
    
    def _analyze_bengali_sentiment(self, text: str) -> float:
        """Analyze sentiment for Bengali text"""
        tokens = self.bengali_preprocessor.tokenize_bengali(text)
        
        positive_score = 0.0
        negative_score = 0.0
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Check for intensity modifiers
            intensity = 1.0
            if token in self.intensity_modifiers['bengali']:
                intensity = self.intensity_modifiers['bengali'][token]
                i += 1
                if i >= len(tokens):
                    break
                token = tokens[i]
            
            # Check for negation
            is_negated = False
            if i > 0 and tokens[i-1] in self.negation_words['bengali']:
                is_negated = True
            
            # Calculate sentiment score for current token
            if token in self.bengali_positive_words:
                score = 1.0 * intensity
                if is_negated:
                    negative_score += score
                else:
                    positive_score += score
            elif token in self.bengali_negative_words:
                score = 1.0 * intensity
                if is_negated:
                    positive_score += score
                else:
                    negative_score += score
            
            i += 1
        
        # Calculate final sentiment score
        total_sentiment_words = positive_score + negative_score
        if total_sentiment_words == 0:
            return 0.0
        
        net_score = (positive_score - negative_score) / total_sentiment_words
        return max(-1.0, min(1.0, net_score))
    
    def _analyze_english_sentiment(self, text: str) -> float:
        """Analyze sentiment for English text"""
        tokens = self.english_preprocessor.tokenize_english(text)
        
        positive_score = 0.0
        negative_score = 0.0
        
        i = 0
        while i < len(tokens):
            token = tokens[i].lower()
            
            # Check for intensity modifiers
            intensity = 1.0
            if token in self.intensity_modifiers['english']:
                intensity = self.intensity_modifiers['english'][token]
                i += 1
                if i >= len(tokens):
                    break
                token = tokens[i].lower()
            
            # Check for negation
            is_negated = False
            if i > 0 and tokens[i-1].lower() in self.negation_words['english']:
                is_negated = True
            
            # Calculate sentiment score for current token
            if token in self.english_positive_words:
                score = 1.0 * intensity
                if is_negated:
                    negative_score += score
                else:
                    positive_score += score
            elif token in self.english_negative_words:
                score = 1.0 * intensity
                if is_negated:
                    positive_score += score
                else:
                    negative_score += score
            
            i += 1
        
        # Calculate final sentiment score
        total_sentiment_words = positive_score + negative_score
        if total_sentiment_words == 0:
            return 0.0
        
        net_score = (positive_score - negative_score) / total_sentiment_words
        return max(-1.0, min(1.0, net_score))
    
    def get_sentiment_breakdown(self, text: str, language: str) -> Dict[str, any]:
        """Get detailed sentiment analysis breakdown"""
        sentiment_score = self.analyze_sentiment(text, language)
        
        # Classify sentiment
        if sentiment_score > 0.1:
            sentiment_label = 'positive'
        elif sentiment_score < -0.1:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        # Calculate confidence based on absolute score
        confidence = abs(sentiment_score)
        
        return {
            'sentiment_score': sentiment_score,
            'sentiment_label': sentiment_label,
            'confidence': confidence,
            'language': language
        }
    
    def detect_emotional_intensity(self, text: str, language: str) -> float:
        """Detect emotional intensity regardless of polarity (0-1 scale)"""
        if language in ['bengali', 'bn']:
            tokens = self.bengali_preprocessor.tokenize_bengali(text)
            emotional_words = self.bengali_positive_words.union(self.bengali_negative_words)
        else:
            tokens = self.english_preprocessor.tokenize_english(text)
            emotional_words = self.english_positive_words.union(self.english_negative_words)
        
        emotional_word_count = 0
        total_words = len(tokens)
        
        for token in tokens:
            if token.lower() in emotional_words:
                emotional_word_count += 1
        
        if total_words == 0:
            return 0.0
        
        # Calculate emotional intensity ratio
        intensity_ratio = emotional_word_count / total_words
        
        # Normalize to 0-1 scale (cap at reasonable maximum)
        return min(1.0, intensity_ratio * 5)  # Multiply by 5 to amplify the signal