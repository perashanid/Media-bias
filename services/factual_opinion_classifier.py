from typing import Dict, List, Set
import re
import logging
from services.text_preprocessor import BengaliTextPreprocessor, EnglishTextPreprocessor

logger = logging.getLogger(__name__)


class FactualOpinionClassifier:
    """Classify text content as factual vs opinion-based"""
    
    def __init__(self):
        self.bengali_preprocessor = BengaliTextPreprocessor()
        self.english_preprocessor = EnglishTextPreprocessor()
        
        # Factual indicators
        self.factual_indicators = {
            'bengali': {
                'reporting_verbs': {
                    'জানানো হয়েছে', 'বলা হয়েছে', 'উল্লেখ করা হয়েছে', 'প্রকাশ করা হয়েছে',
                    'ঘোষণা করা হয়েছে', 'নিশ্চিত করা হয়েছে', 'তথ্য দেওয়া হয়েছে'
                },
                'source_attribution': {
                    'সূত্র জানিয়েছে', 'কর্মকর্তারা জানিয়েছেন', 'মন্ত্রী বলেছেন',
                    'প্রধানমন্ত্রী বলেছেন', 'পুলিশ জানিয়েছে', 'সরকারি সূত্র'
                },
                'factual_phrases': {
                    'তথ্য অনুযায়ী', 'পরিসংখ্যান অনুযায়ী', 'রিপোর্ট অনুযায়ী',
                    'গবেষণায় দেখা গেছে', 'জরিপে দেখা গেছে', 'তদন্তে প্রমাণিত'
                },
                'time_date_indicators': {
                    'গতকাল', 'আজ', 'গত সপ্তাহে', 'গত মাসে', 'এ বছর', 'গত বছর',
                    'সকালে', 'দুপুরে', 'বিকেলে', 'সন্ধ্যায়', 'রাতে'
                }
            },
            'english': {
                'reporting_verbs': {
                    'reported', 'stated', 'announced', 'confirmed', 'revealed', 'disclosed',
                    'said', 'told', 'informed', 'declared', 'mentioned'
                },
                'source_attribution': {
                    'according to', 'sources said', 'officials said', 'minister said',
                    'prime minister said', 'police said', 'government sources'
                },
                'factual_phrases': {
                    'according to data', 'statistics show', 'report shows', 'study found',
                    'research indicates', 'survey reveals', 'investigation proved'
                },
                'time_date_indicators': {
                    'yesterday', 'today', 'last week', 'last month', 'this year', 'last year',
                    'morning', 'afternoon', 'evening', 'night', 'on monday', 'on tuesday'
                }
            }
        }
        
        # Opinion indicators
        self.opinion_indicators = {
            'bengali': {
                'opinion_verbs': {
                    'মনে করি', 'বিশ্বাস করি', 'ভাবি', 'মতামত', 'অভিমত', 'দৃষ্টিভঙ্গি',
                    'আমার মতে', 'আমি মনে করি', 'আমার বিশ্বাস', 'আমার ধারণা'
                },
                'subjective_adjectives': {
                    'সুন্দর', 'খারাপ', 'ভালো', 'চমৎকার', 'জঘন্য', 'অসাধারণ',
                    'বিরক্তিকর', 'আকর্ষণীয়', 'অপ্রয়োজনীয়', 'গুরুত্বপূর্ণ'
                },
                'speculation_words': {
                    'সম্ভবত', 'হয়তো', 'বোধহয়', 'মনে হচ্ছে', 'দেখে মনে হচ্ছে',
                    'অনুমান করা যায়', 'ধারণা করা হচ্ছে'
                },
                'evaluation_phrases': {
                    'উচিত', 'উচিত নয়', 'করা দরকার', 'করা উচিত নয়', 'ভুল সিদ্ধান্ত',
                    'সঠিক সিদ্ধান্ত', 'প্রয়োজনীয়', 'অপ্রয়োজনীয়'
                }
            },
            'english': {
                'opinion_verbs': {
                    'think', 'believe', 'feel', 'opinion', 'view', 'perspective',
                    'i think', 'i believe', 'i feel', 'in my opinion', 'my view'
                },
                'subjective_adjectives': {
                    'beautiful', 'ugly', 'good', 'bad', 'excellent', 'terrible',
                    'amazing', 'boring', 'interesting', 'unnecessary', 'important'
                },
                'speculation_words': {
                    'probably', 'possibly', 'maybe', 'perhaps', 'seems', 'appears',
                    'likely', 'unlikely', 'presumably', 'supposedly'
                },
                'evaluation_phrases': {
                    'should', 'should not', 'ought to', 'must', 'need to', 'wrong decision',
                    'right decision', 'necessary', 'unnecessary', 'appropriate'
                }
            }
        }
        
        # Numerical and statistical patterns
        self.numerical_patterns = [
            r'\d+%',  # Percentages
            r'\d+\.\d+',  # Decimal numbers
            r'\d+,\d+',  # Numbers with commas
            r'\d+\s*(million|billion|thousand|crore|lakh)',  # Large numbers
            r'\d+\s*(টাকা|dollar|taka|rupee)',  # Currency
        ]
    
    def classify_factual_vs_opinion(self, text: str, language: str) -> float:
        """
        Classify text as factual vs opinion
        
        Returns:
            Score between 0 (opinion) and 1 (factual)
        """
        if not text or not text.strip():
            return 0.5  # Neutral if no text
        
        if language == 'bengali':
            return self._analyze_bengali_factual_opinion(text)
        elif language == 'english':
            return self._analyze_english_factual_opinion(text)
        else:
            # Try both languages and average
            bengali_score = self._analyze_bengali_factual_opinion(text)
            english_score = self._analyze_english_factual_opinion(text)
            return (bengali_score + english_score) / 2
    
    def _analyze_bengali_factual_opinion(self, text: str) -> float:
        """Analyze factual vs opinion content in Bengali text"""
        tokens = self.bengali_preprocessor.tokenize_bengali(text)
        text_lower = text.lower()
        
        factual_score = 0.0
        opinion_score = 0.0
        
        # Count factual indicators
        factual_indicators = self.factual_indicators['bengali']
        for category, indicators in factual_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    if category == 'reporting_verbs':
                        factual_score += 2.0  # Strong factual indicator
                    elif category == 'source_attribution':
                        factual_score += 3.0  # Very strong factual indicator
                    else:
                        factual_score += 1.0
        
        # Count opinion indicators
        opinion_indicators = self.opinion_indicators['bengali']
        for category, indicators in opinion_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    if category == 'opinion_verbs':
                        opinion_score += 3.0  # Strong opinion indicator
                    elif category == 'evaluation_phrases':
                        opinion_score += 2.0  # Strong evaluative content
                    else:
                        opinion_score += 1.0
        
        # Check for numerical/statistical content (factual indicator)
        numerical_matches = 0
        for pattern in self.numerical_patterns:
            numerical_matches += len(re.findall(pattern, text_lower))
        factual_score += numerical_matches * 1.5
        
        # Check for first-person pronouns (opinion indicator)
        first_person_pronouns = ['আমি', 'আমার', 'আমাদের', 'আমরা']
        for pronoun in first_person_pronouns:
            if pronoun in text_lower:
                opinion_score += 1.0
        
        # Calculate final score
        total_score = factual_score + opinion_score
        if total_score == 0:
            return 0.5  # Neutral if no indicators found
        
        factual_ratio = factual_score / total_score
        return min(1.0, max(0.0, factual_ratio))
    
    def _analyze_english_factual_opinion(self, text: str) -> float:
        """Analyze factual vs opinion content in English text"""
        tokens = self.english_preprocessor.tokenize_english(text)
        text_lower = text.lower()
        
        factual_score = 0.0
        opinion_score = 0.0
        
        # Count factual indicators
        factual_indicators = self.factual_indicators['english']
        for category, indicators in factual_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    if category == 'reporting_verbs':
                        factual_score += 2.0
                    elif category == 'source_attribution':
                        factual_score += 3.0
                    else:
                        factual_score += 1.0
        
        # Count opinion indicators
        opinion_indicators = self.opinion_indicators['english']
        for category, indicators in opinion_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    if category == 'opinion_verbs':
                        opinion_score += 3.0
                    elif category == 'evaluation_phrases':
                        opinion_score += 2.0
                    else:
                        opinion_score += 1.0
        
        # Check for numerical/statistical content
        numerical_matches = 0
        for pattern in self.numerical_patterns:
            numerical_matches += len(re.findall(pattern, text_lower))
        factual_score += numerical_matches * 1.5
        
        # Check for first-person pronouns
        first_person_pronouns = ['i ', 'my ', 'we ', 'our ', 'me ']
        for pronoun in first_person_pronouns:
            if pronoun in text_lower:
                opinion_score += 1.0
        
        # Calculate final score
        total_score = factual_score + opinion_score
        if total_score == 0:
            return 0.5
        
        factual_ratio = factual_score / total_score
        return min(1.0, max(0.0, factual_ratio))
    
    def get_content_analysis(self, text: str, language: str) -> Dict[str, any]:
        """Get detailed factual vs opinion analysis"""
        factual_score = self.classify_factual_vs_opinion(text, language)
        
        # Classify content type
        if factual_score > 0.7:
            content_type = 'factual'
        elif factual_score < 0.3:
            content_type = 'opinion'
        else:
            content_type = 'mixed'
        
        # Calculate confidence
        confidence = abs(factual_score - 0.5) * 2  # Distance from neutral (0.5)
        
        return {
            'factual_score': factual_score,
            'content_type': content_type,
            'confidence': confidence,
            'language': language
        }
    
    def detect_speculation(self, text: str, language: str) -> float:
        """
        Detect speculative language in text
        
        Returns:
            Score between 0 (no speculation) and 1 (highly speculative)
        """
        if language == 'bengali':
            speculation_words = self.opinion_indicators['bengali']['speculation_words']
            tokens = self.bengali_preprocessor.tokenize_bengali(text)
        else:
            speculation_words = self.opinion_indicators['english']['speculation_words']
            tokens = self.english_preprocessor.tokenize_english(text)
        
        speculation_count = 0
        total_words = len(tokens)
        
        text_lower = text.lower()
        for word in speculation_words:
            if word in text_lower:
                speculation_count += 1
        
        if total_words == 0:
            return 0.0
        
        # Calculate speculation ratio
        speculation_ratio = speculation_count / total_words
        
        # Normalize to 0-1 scale
        return min(1.0, speculation_ratio * 20)  # Multiply by 20 to amplify the signal