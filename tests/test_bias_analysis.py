"""
Unit tests for bias analysis components
"""

import pytest
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.bias_analyzer import BiasAnalyzer
from services.sentiment_analyzer import SentimentAnalyzer
from services.political_bias_detector import PoliticalBiasDetector
from services.factual_opinion_classifier import FactualOpinionClassifier
from services.language_detector import LanguageDetector
from models.article import Article, BiasScore


class TestLanguageDetector:
    """Tests for language detection"""
    
    def test_english_detection(self):
        """Test English language detection"""
        detector = LanguageDetector()
        
        english_texts = [
            "This is an English article about politics and government.",
            "The prime minister announced new policies yesterday.",
            "According to sources, the meeting was successful."
        ]
        
        for text in english_texts:
            language = detector.detect_language(text)
            assert language == "english"
    
    def test_bengali_detection(self):
        """Test Bengali language detection"""
        detector = LanguageDetector()
        
        bengali_texts = [
            "এটি একটি বাংলা নিবন্ধ যা রাজনীতি সম্পর্কে।",
            "প্রধানমন্ত্রী গতকাল নতুন নীতি ঘোষণা করেছেন।",
            "সূত্র অনুযায়ী, সভাটি সফল হয়েছে।"
        ]
        
        for text in bengali_texts:
            language = detector.detect_language(text)
            assert language == "bengali"
    
    def test_language_confidence(self):
        """Test language detection confidence"""
        detector = LanguageDetector()
        
        # Clear English text
        english_text = "This is definitely an English sentence with no ambiguity."
        language, confidence = detector.get_language_confidence(english_text)
        
        assert language == "english"
        assert confidence > 0.5
        
        # Clear Bengali text
        bengali_text = "এটি নিশ্চিতভাবে একটি বাংলা বাক্য যাতে কোনো দ্বিধা নেই।"
        language, confidence = detector.get_language_confidence(bengali_text)
        
        assert language == "bengali"
        assert confidence > 0.5


class TestSentimentAnalyzer:
    """Tests for sentiment analysis"""
    
    def test_positive_sentiment_english(self):
        """Test positive sentiment detection in English"""
        analyzer = SentimentAnalyzer()
        
        positive_texts = [
            "This is an excellent and wonderful achievement.",
            "Great success and amazing progress for everyone.",
            "Beautiful and outstanding work by the team."
        ]
        
        for text in positive_texts:
            score = analyzer.analyze_sentiment(text, "english")
            assert score > 0.1, f"Expected positive sentiment for: {text}"
    
    def test_negative_sentiment_english(self):
        """Test negative sentiment detection in English"""
        analyzer = SentimentAnalyzer()
        
        negative_texts = [
            "This is terrible and awful news for everyone.",
            "Bad and disappointing results from the government.",
            "Horrible and painful situation for the people."
        ]
        
        for text in negative_texts:
            score = analyzer.analyze_sentiment(text, "english")
            assert score < -0.1, f"Expected negative sentiment for: {text}"
    
    def test_neutral_sentiment(self):
        """Test neutral sentiment detection"""
        analyzer = SentimentAnalyzer()
        
        neutral_texts = [
            "The meeting was held yesterday at 3 PM.",
            "According to the report, there were 100 participants.",
            "The document contains information about the policy."
        ]
        
        for text in neutral_texts:
            score = analyzer.analyze_sentiment(text, "english")
            assert -0.1 <= score <= 0.1, f"Expected neutral sentiment for: {text}"
    
    def test_bengali_sentiment(self):
        """Test sentiment analysis in Bengali"""
        analyzer = SentimentAnalyzer()
        
        # Positive Bengali text
        positive_text = "এটি একটি চমৎকার এবং অসাধারণ অর্জন।"
        score = analyzer.analyze_sentiment(positive_text, "bengali")
        assert score > 0, "Expected positive sentiment for Bengali text"
        
        # Negative Bengali text
        negative_text = "এটি একটি খারাপ এবং ভয়ানক পরিস্থিতি।"
        score = analyzer.analyze_sentiment(negative_text, "bengali")
        assert score < 0, "Expected negative sentiment for Bengali text"
    
    def test_emotional_intensity(self):
        """Test emotional intensity detection"""
        analyzer = SentimentAnalyzer()
        
        # High emotional intensity
        emotional_text = "This is absolutely terrible and completely devastating!"
        intensity = analyzer.detect_emotional_intensity(emotional_text, "english")
        assert intensity > 0.3, "Expected high emotional intensity"
        
        # Low emotional intensity
        neutral_text = "The report was published yesterday."
        intensity = analyzer.detect_emotional_intensity(neutral_text, "english")
        assert intensity < 0.3, "Expected low emotional intensity"


class TestPoliticalBiasDetector:
    """Tests for political bias detection"""
    
    def test_neutral_political_content(self):
        """Test neutral political content"""
        detector = PoliticalBiasDetector()
        
        neutral_texts = [
            "The parliament session was held yesterday.",
            "According to official sources, the meeting ended at 5 PM.",
            "The report contains statistical information."
        ]
        
        for text in neutral_texts:
            score = detector.detect_political_bias(text, "english")
            assert -0.2 <= score <= 0.2, f"Expected neutral political bias for: {text}"
    
    def test_loaded_language_detection(self):
        """Test loaded language detection"""
        detector = PoliticalBiasDetector()
        
        # High loaded language
        loaded_text = "This devastating and outrageous decision is completely unacceptable!"
        score = detector.detect_loaded_language(loaded_text, "english")
        assert score > 0.3, "Expected high loaded language score"
        
        # Low loaded language
        neutral_text = "The committee reviewed the proposal."
        score = detector.detect_loaded_language(neutral_text, "english")
        assert score < 0.3, "Expected low loaded language score"
    
    def test_bengali_political_bias(self):
        """Test political bias detection in Bengali"""
        detector = PoliticalBiasDetector()
        
        # Test with Bengali political content
        bengali_text = "সরকারের এই সিদ্ধান্ত দেশের উন্নয়নে সহায়ক।"
        score = detector.detect_political_bias(bengali_text, "bengali")
        assert isinstance(score, float)
        assert -1.0 <= score <= 1.0


class TestFactualOpinionClassifier:
    """Tests for factual vs opinion classification"""
    
    def test_factual_content(self):
        """Test factual content detection"""
        classifier = FactualOpinionClassifier()
        
        factual_texts = [
            "According to the report, GDP grew by 3.2% last year.",
            "The meeting was held on Monday at 10 AM.",
            "Statistics show that 75% of participants agreed.",
            "The minister announced the policy yesterday."
        ]
        
        for text in factual_texts:
            score = classifier.classify_factual_vs_opinion(text, "english")
            assert score > 0.5, f"Expected factual classification for: {text}"
    
    def test_opinion_content(self):
        """Test opinion content detection"""
        classifier = FactualOpinionClassifier()
        
        opinion_texts = [
            "I think this policy is wrong and should be changed.",
            "In my opinion, the government made a bad decision.",
            "This is probably the worst idea they've had.",
            "I believe we should take a different approach."
        ]
        
        for text in opinion_texts:
            score = classifier.classify_factual_vs_opinion(text, "english")
            assert score < 0.5, f"Expected opinion classification for: {text}"
    
    def test_speculation_detection(self):
        """Test speculation detection"""
        classifier = FactualOpinionClassifier()
        
        # High speculation
        speculative_text = "This probably means that maybe the government might consider changing the policy."
        score = classifier.detect_speculation(speculative_text, "english")
        assert score > 0.3, "Expected high speculation score"
        
        # Low speculation
        factual_text = "The minister confirmed the policy change."
        score = classifier.detect_speculation(factual_text, "english")
        assert score < 0.3, "Expected low speculation score"
    
    def test_bengali_factual_opinion(self):
        """Test factual vs opinion classification in Bengali"""
        classifier = FactualOpinionClassifier()
        
        # Factual Bengali text
        factual_text = "সূত্র জানিয়েছে যে সভাটি গতকাল অনুষ্ঠিত হয়েছে।"
        score = classifier.classify_factual_vs_opinion(factual_text, "bengali")
        assert score > 0.5, "Expected factual classification for Bengali text"
        
        # Opinion Bengali text
        opinion_text = "আমি মনে করি এই নীতিটি ভুল এবং পরিবর্তন করা উচিত।"
        score = classifier.classify_factual_vs_opinion(opinion_text, "bengali")
        assert score < 0.5, "Expected opinion classification for Bengali text"


class TestBiasAnalyzer:
    """Tests for the main bias analyzer"""
    
    def test_complete_bias_analysis(self):
        """Test complete bias analysis workflow"""
        analyzer = BiasAnalyzer()
        
        # Create test article
        test_article = Article(
            url="http://test.com/article1",
            title="Test Article About Politics",
            content="This is a test article about government policies and political decisions. The minister announced new reforms yesterday.",
            author="Test Author",
            source="Test Source",
            publication_date=datetime.now(),
            scraped_at=datetime.now(),
            language="english"
        )
        
        # Analyze bias
        bias_scores = analyzer.analyze_article_bias(test_article)
        
        # Check that all scores are present and valid
        assert isinstance(bias_scores, BiasScore)
        assert isinstance(bias_scores.sentiment_score, float)
        assert isinstance(bias_scores.political_bias_score, float)
        assert isinstance(bias_scores.emotional_language_score, float)
        assert isinstance(bias_scores.factual_vs_opinion_score, float)
        assert isinstance(bias_scores.overall_bias_score, float)
        
        # Check score ranges
        assert -1.0 <= bias_scores.sentiment_score <= 1.0
        assert -1.0 <= bias_scores.political_bias_score <= 1.0
        assert 0.0 <= bias_scores.emotional_language_score <= 1.0
        assert 0.0 <= bias_scores.factual_vs_opinion_score <= 1.0
        assert 0.0 <= bias_scores.overall_bias_score <= 1.0
    
    def test_text_sample_analysis(self):
        """Test text sample analysis"""
        analyzer = BiasAnalyzer()
        
        test_text = "This is an excellent government policy that will benefit everyone greatly."
        result = analyzer.analyze_text_sample(test_text, "english")
        
        # Check required fields
        required_fields = [
            'sentiment_score', 'political_bias_score', 'emotional_language_score',
            'factual_vs_opinion_score', 'overall_bias_score', 'bias_classification'
        ]
        
        for field in required_fields:
            assert field in result
        
        # Check bias classification
        assert result['bias_classification'] in ['low_bias', 'moderate_bias', 'high_bias', 'very_high_bias']
    
    def test_detailed_analysis(self):
        """Test detailed analysis output"""
        analyzer = BiasAnalyzer()
        
        test_article = Article(
            url="http://test.com/article2",
            title="Detailed Analysis Test",
            content="The government announced new economic policies. According to experts, this will impact the market.",
            author="Test Author",
            source="Test Source",
            publication_date=datetime.now(),
            scraped_at=datetime.now(),
            language="english"
        )
        
        detailed_analysis = analyzer.get_detailed_analysis(test_article)
        
        # Check structure
        assert 'article_title' in detailed_analysis
        assert 'language_detection' in detailed_analysis
        assert 'sentiment_analysis' in detailed_analysis
        assert 'political_bias_analysis' in detailed_analysis
        assert 'content_analysis' in detailed_analysis
        assert 'overall_bias_score' in detailed_analysis
        assert 'bias_classification' in detailed_analysis
    
    def test_bias_score_calculation(self):
        """Test overall bias score calculation"""
        analyzer = BiasAnalyzer()
        
        # Test with known values
        sentiment_score = 0.5  # Positive
        political_bias_score = 0.3  # Slightly right-leaning
        emotional_language_score = 0.7  # High emotional language
        factual_vs_opinion_score = 0.4  # More opinion than factual
        
        overall_bias = analyzer._calculate_overall_bias(
            sentiment_score, political_bias_score, emotional_language_score, factual_vs_opinion_score
        )
        
        assert 0.0 <= overall_bias <= 1.0
        assert overall_bias > 0.3  # Should indicate some bias given the inputs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])