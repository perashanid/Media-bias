from typing import Dict, List, Set, Tuple
import re
import logging
from services.text_preprocessor import BengaliTextPreprocessor, EnglishTextPreprocessor

logger = logging.getLogger(__name__)


class PoliticalBiasDetector:
    """Detect political bias in Bengali and English news text"""
    
    def __init__(self):
        self.bengali_preprocessor = BengaliTextPreprocessor()
        self.english_preprocessor = EnglishTextPreprocessor()
        
        # Bengali political keywords and phrases
        self.bengali_political_keywords = {
            'left_leaning': {
                # Pro-government/ruling party terms
                'সরকার', 'প্রধানমন্ত্রী', 'মাননীয়', 'উন্নয়ন', 'অগ্রগতি', 'সাফল্য',
                'জনগণের সেবা', 'গণতন্ত্র', 'মুক্তিযুদ্ধ', 'স্বাধীনতা', 'বঙ্গবন্ধু',
                'আওয়ামী লীগ', 'নৌকা', 'শেখ হাসিনা', 'জয় বাংলা', 'সোনার বাংলা'
            },
            'right_leaning': {
                # Opposition/critical terms
                'বিরোধী দল', 'প্রতিবাদ', 'আন্দোলন', 'দুর্নীতি', 'স্বৈরাচার', 'অন্যায়',
                'জামায়াত', 'বিএনপি', 'ধানের শীষ', 'খালেদা জিয়া', 'তারেক রহমান',
                'হরতাল', 'অবরোধ', 'গণতন্ত্র পুনরুদ্ধার', 'নির্বাচন', 'ভোট'
            },
            'neutral': {
                'সংবাদ', 'প্রতিবেদন', 'তথ্য', 'ঘটনা', 'বিষয়', 'পরিস্থিতি',
                'জানানো হয়েছে', 'বলা হয়েছে', 'উল্লেখ করা হয়েছে'
            }
        }
        
        # English political keywords
        self.english_political_keywords = {
            'left_leaning': {
                # Pro-government terms
                'government', 'prime minister', 'development', 'progress', 'success',
                'democracy', 'liberation war', 'independence', 'bangabandhu',
                'awami league', 'sheikh hasina', 'ruling party', 'achievement'
            },
            'right_leaning': {
                # Opposition/critical terms
                'opposition', 'protest', 'movement', 'corruption', 'autocracy', 'injustice',
                'bnp', 'jamaat', 'khaleda zia', 'tarique rahman', 'hartal', 'blockade',
                'election', 'vote', 'democracy restoration', 'human rights'
            },
            'neutral': {
                'news', 'report', 'information', 'event', 'situation', 'according to',
                'it was reported', 'sources said', 'officials said'
            }
        }
        
        # Loaded/biased language patterns
        self.biased_language_patterns = {
            'bengali': {
                'positive_bias': [
                    r'অসাধারণ\s+সাফল্য', r'চমৎকার\s+উদ্যোগ', r'প্রশংসনীয়\s+কাজ',
                    r'যুগান্তকারী\s+সিদ্ধান্ত', r'ঐতিহাসিক\s+অর্জন'
                ],
                'negative_bias': [
                    r'চরম\s+ব্যর্থতা', r'জঘন্য\s+কাজ', r'নিন্দনীয়\s+আচরণ',
                    r'ভয়াবহ\s+পরিস্থিতি', r'অগ্রহণযোগ্য\s+সিদ্ধান্ত'
                ]
            },
            'english': {
                'positive_bias': [
                    r'remarkable\s+success', r'outstanding\s+achievement', r'excellent\s+initiative',
                    r'groundbreaking\s+decision', r'historic\s+accomplishment'
                ],
                'negative_bias': [
                    r'complete\s+failure', r'terrible\s+decision', r'outrageous\s+behavior',
                    r'devastating\s+situation', r'unacceptable\s+action'
                ]
            }
        }
        
        # Emotional/loaded terms
        self.loaded_terms = {
            'bengali': {
                'high_emotion': {
                    'ভয়াবহ', 'জঘন্য', 'চরম', 'অসহনীয়', 'অগ্রহণযোগ্য', 'নিন্দনীয়',
                    'অসাধারণ', 'চমৎকার', 'যুগান্তকারী', 'ঐতিহাসিক', 'অভূতপূর্ব'
                },
                'medium_emotion': {
                    'গুরুতর', 'উদ্বেগজনক', 'আশাব্যঞ্জক', 'প্রশংসনীয়', 'সন্তোষজনক'
                }
            },
            'english': {
                'high_emotion': {
                    'devastating', 'outrageous', 'terrible', 'shocking', 'unacceptable',
                    'remarkable', 'outstanding', 'groundbreaking', 'historic', 'unprecedented'
                },
                'medium_emotion': {
                    'serious', 'concerning', 'promising', 'commendable', 'satisfactory'
                }
            }
        }
    
    def detect_political_bias(self, text: str, language: str) -> float:
        """
        Detect political bias in text
        
        Returns:
            Score between -1 (left-leaning) and 1 (right-leaning), 0 is neutral
        """
        if not text or not text.strip():
            return 0.0
        
        if language in ['bengali', 'bn']:
            return self._analyze_bengali_political_bias(text)
        elif language in ['english', 'en']:
            return self._analyze_english_political_bias(text)
        else:
            # Try both languages and average
            bengali_score = self._analyze_bengali_political_bias(text)
            english_score = self._analyze_english_political_bias(text)
            return (bengali_score + english_score) / 2
    
    def _analyze_bengali_political_bias(self, text: str) -> float:
        """Analyze political bias in Bengali text"""
        tokens = self.bengali_preprocessor.tokenize_bengali(text)
        text_lower = text.lower()
        
        left_score = 0.0
        right_score = 0.0
        neutral_score = 0.0
        
        # Count keyword occurrences
        for token in tokens:
            if token in self.bengali_political_keywords['left_leaning']:
                left_score += 1.0
            elif token in self.bengali_political_keywords['right_leaning']:
                right_score += 1.0
            elif token in self.bengali_political_keywords['neutral']:
                neutral_score += 0.5
        
        # Check for biased language patterns
        for pattern in self.biased_language_patterns['bengali']['positive_bias']:
            matches = len(re.findall(pattern, text_lower))
            left_score += matches * 2.0  # Weight pattern matches higher
        
        for pattern in self.biased_language_patterns['bengali']['negative_bias']:
            matches = len(re.findall(pattern, text_lower))
            right_score += matches * 2.0
        
        # Calculate bias score
        total_political_content = left_score + right_score + neutral_score
        if total_political_content == 0:
            return 0.0
        
        # Normalize scores
        left_ratio = left_score / total_political_content
        right_ratio = right_score / total_political_content
        
        # Calculate final bias score (-1 to 1)
        bias_score = right_ratio - left_ratio
        return max(-1.0, min(1.0, bias_score))
    
    def _analyze_english_political_bias(self, text: str) -> float:
        """Analyze political bias in English text"""
        tokens = self.english_preprocessor.tokenize_english(text)
        text_lower = text.lower()
        
        left_score = 0.0
        right_score = 0.0
        neutral_score = 0.0
        
        # Count keyword occurrences
        for token in tokens:
            token_lower = token.lower()
            if token_lower in self.english_political_keywords['left_leaning']:
                left_score += 1.0
            elif token_lower in self.english_political_keywords['right_leaning']:
                right_score += 1.0
            elif token_lower in self.english_political_keywords['neutral']:
                neutral_score += 0.5
        
        # Check for biased language patterns
        for pattern in self.biased_language_patterns['english']['positive_bias']:
            matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
            left_score += matches * 2.0
        
        for pattern in self.biased_language_patterns['english']['negative_bias']:
            matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
            right_score += matches * 2.0
        
        # Calculate bias score
        total_political_content = left_score + right_score + neutral_score
        if total_political_content == 0:
            return 0.0
        
        # Normalize scores
        left_ratio = left_score / total_political_content
        right_ratio = right_score / total_political_content
        
        # Calculate final bias score (-1 to 1)
        bias_score = right_ratio - left_ratio
        return max(-1.0, min(1.0, bias_score))
    
    def detect_loaded_language(self, text: str, language: str) -> float:
        """
        Detect emotionally loaded language
        
        Returns:
            Score between 0 (neutral) and 1 (highly loaded)
        """
        if language in ['bengali', 'bn']:
            tokens = self.bengali_preprocessor.tokenize_bengali(text)
            loaded_terms = self.loaded_terms['bengali']
        else:
            tokens = self.english_preprocessor.tokenize_english(text)
            loaded_terms = self.loaded_terms['english']
        
        high_emotion_count = 0
        medium_emotion_count = 0
        total_words = len(tokens)
        
        for token in tokens:
            token_lower = token.lower()
            if token_lower in loaded_terms['high_emotion']:
                high_emotion_count += 1
            elif token_lower in loaded_terms['medium_emotion']:
                medium_emotion_count += 1
        
        if total_words == 0:
            return 0.0
        
        # Calculate loaded language score
        loaded_score = (high_emotion_count * 2.0 + medium_emotion_count * 1.0) / total_words
        
        # Normalize to 0-1 scale
        return min(1.0, loaded_score * 10)  # Multiply by 10 to amplify the signal
    
    def get_political_bias_breakdown(self, text: str, language: str) -> Dict[str, any]:
        """Get detailed political bias analysis"""
        bias_score = self.detect_political_bias(text, language)
        loaded_language_score = self.detect_loaded_language(text, language)
        
        # Classify bias direction
        if bias_score > 0.2:
            bias_direction = 'right_leaning'
        elif bias_score < -0.2:
            bias_direction = 'left_leaning'
        else:
            bias_direction = 'neutral'
        
        # Calculate confidence
        confidence = abs(bias_score)
        
        return {
            'political_bias_score': bias_score,
            'bias_direction': bias_direction,
            'loaded_language_score': loaded_language_score,
            'confidence': confidence,
            'language': language
        }