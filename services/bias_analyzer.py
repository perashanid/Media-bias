from typing import Dict, Any
from datetime import datetime
import logging
from models.article import Article, BiasScore
from services.language_detector import LanguageDetector
from services.sentiment_analyzer import SentimentAnalyzer
from services.political_bias_detector import PoliticalBiasDetector
from services.factual_opinion_classifier import FactualOpinionClassifier

logger = logging.getLogger(__name__)


class BiasAnalyzer:
    """Main bias analysis engine that orchestrates all analysis modules"""
    
    def __init__(self):
        self.language_detector = LanguageDetector()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.political_bias_detector = PoliticalBiasDetector()
        self.factual_opinion_classifier = FactualOpinionClassifier()
    
    def analyze_article_bias(self, article: Article) -> BiasScore:
        """
        Perform comprehensive bias analysis on an article
        
        Args:
            article: Article object to analyze
            
        Returns:
            BiasScore object with all bias metrics
        """
        try:
            # Combine title and content for analysis
            full_text = f"{article.title} {article.content}"
            
            # Detect language if not already set or verify existing language
            detected_language, confidence = self.language_detector.get_language_confidence(full_text)
            
            # Use detected language or fall back to article's language
            analysis_language = detected_language if confidence > 0.6 else article.language
            
            logger.info(f"Analyzing article bias for: {article.title[:50]}... (Language: {analysis_language})")
            
            # Perform all bias analyses
            sentiment_score = self.sentiment_analyzer.analyze_sentiment(full_text, analysis_language)
            political_bias_score = self.political_bias_detector.detect_political_bias(full_text, analysis_language)
            emotional_language_score = self.sentiment_analyzer.detect_emotional_intensity(full_text, analysis_language)
            factual_vs_opinion_score = self.factual_opinion_classifier.classify_factual_vs_opinion(full_text, analysis_language)
            
            # Calculate overall bias score
            overall_bias_score = self._calculate_overall_bias(
                sentiment_score, political_bias_score, emotional_language_score, factual_vs_opinion_score
            )
            
            # Create BiasScore object
            bias_score = BiasScore(
                sentiment_score=sentiment_score,
                political_bias_score=political_bias_score,
                emotional_language_score=emotional_language_score,
                factual_vs_opinion_score=factual_vs_opinion_score,
                overall_bias_score=overall_bias_score,
                analyzed_at=datetime.now()
            )
            
            logger.info(f"Bias analysis complete. Overall bias: {overall_bias_score:.3f}")
            return bias_score
            
        except Exception as e:
            logger.error(f"Failed to analyze article bias: {e}")
            # Return neutral scores in case of error
            return BiasScore(
                sentiment_score=0.0,
                political_bias_score=0.0,
                emotional_language_score=0.0,
                factual_vs_opinion_score=0.5,
                overall_bias_score=0.0,
                analyzed_at=datetime.now()
            )
    
    def _calculate_overall_bias(self, sentiment_score: float, political_bias_score: float, 
                              emotional_language_score: float, factual_vs_opinion_score: float) -> float:
        """
        Calculate overall bias score from individual components
        
        Args:
            sentiment_score: -1 to 1 (negative to positive sentiment)
            political_bias_score: -1 to 1 (left to right leaning)
            emotional_language_score: 0 to 1 (neutral to highly emotional)
            factual_vs_opinion_score: 0 to 1 (opinion to factual)
            
        Returns:
            Overall bias score from 0 (unbiased) to 1 (highly biased)
        """
        # Convert sentiment and political bias to absolute values (bias magnitude)
        sentiment_bias = abs(sentiment_score)
        political_bias = abs(political_bias_score)
        
        # Emotional language is already 0-1 scale
        emotional_bias = emotional_language_score
        
        # Convert factual score to bias (1 - factual_score, since factual = less biased)
        opinion_bias = 1.0 - factual_vs_opinion_score
        
        # Weighted combination of bias components
        weights = {
            'sentiment': 0.2,      # 20% - sentiment bias
            'political': 0.3,      # 30% - political bias (most important)
            'emotional': 0.25,     # 25% - emotional language
            'opinion': 0.25        # 25% - opinion vs factual content
        }
        
        overall_bias = (
            sentiment_bias * weights['sentiment'] +
            political_bias * weights['political'] +
            emotional_bias * weights['emotional'] +
            opinion_bias * weights['opinion']
        )
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, overall_bias))
    
    def get_detailed_analysis(self, article: Article) -> Dict[str, Any]:
        """
        Get detailed bias analysis breakdown
        
        Returns:
            Dictionary with detailed analysis results
        """
        try:
            full_text = f"{article.title} {article.content}"
            
            # Detect language
            detected_language, language_confidence = self.language_detector.get_language_confidence(full_text)
            analysis_language = detected_language if language_confidence > 0.6 else article.language
            
            # Get detailed breakdowns from each analyzer
            sentiment_breakdown = self.sentiment_analyzer.get_sentiment_breakdown(full_text, analysis_language)
            political_breakdown = self.political_bias_detector.get_political_bias_breakdown(full_text, analysis_language)
            content_analysis = self.factual_opinion_classifier.get_content_analysis(full_text, analysis_language)
            
            # Additional metrics
            loaded_language_score = self.political_bias_detector.detect_loaded_language(full_text, analysis_language)
            speculation_score = self.factual_opinion_classifier.detect_speculation(full_text, analysis_language)
            
            # Calculate overall bias
            overall_bias = self._calculate_overall_bias(
                sentiment_breakdown['sentiment_score'],
                political_breakdown['political_bias_score'],
                political_breakdown['loaded_language_score'],
                content_analysis['factual_score']
            )
            
            return {
                'article_id': article.id,
                'article_title': article.title,
                'article_source': article.source,
                'language_detection': {
                    'detected_language': detected_language,
                    'confidence': language_confidence,
                    'analysis_language': analysis_language
                },
                'sentiment_analysis': sentiment_breakdown,
                'political_bias_analysis': political_breakdown,
                'content_analysis': content_analysis,
                'additional_metrics': {
                    'loaded_language_score': loaded_language_score,
                    'speculation_score': speculation_score
                },
                'overall_bias_score': overall_bias,
                'bias_classification': self._classify_bias_level(overall_bias),
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get detailed analysis: {e}")
            return {
                'error': str(e),
                'article_id': article.id if article.id else 'unknown'
            }
    
    def _classify_bias_level(self, bias_score: float) -> str:
        """Classify bias level based on overall bias score"""
        if bias_score < 0.2:
            return 'low_bias'
        elif bias_score < 0.4:
            return 'moderate_bias'
        elif bias_score < 0.6:
            return 'high_bias'
        else:
            return 'very_high_bias'
    
    def analyze_text_sample(self, text: str, language: str = None) -> Dict[str, Any]:
        """
        Analyze a text sample for bias (useful for testing)
        
        Args:
            text: Text to analyze
            language: Language of the text ('bengali' or 'english')
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Detect language if not provided
            if not language:
                language, confidence = self.language_detector.get_language_confidence(text)
            
            # Perform analyses
            sentiment_score = self.sentiment_analyzer.analyze_sentiment(text, language)
            political_bias_score = self.political_bias_detector.detect_political_bias(text, language)
            emotional_language_score = self.sentiment_analyzer.detect_emotional_intensity(text, language)
            factual_vs_opinion_score = self.factual_opinion_classifier.classify_factual_vs_opinion(text, language)
            
            # Calculate overall bias
            overall_bias = self._calculate_overall_bias(
                sentiment_score, political_bias_score, emotional_language_score, factual_vs_opinion_score
            )
            
            return {
                'text_sample': text[:100] + '...' if len(text) > 100 else text,
                'language': language,
                'sentiment_score': sentiment_score,
                'political_bias_score': political_bias_score,
                'emotional_language_score': emotional_language_score,
                'factual_vs_opinion_score': factual_vs_opinion_score,
                'overall_bias_score': overall_bias,
                'bias_classification': self._classify_bias_level(overall_bias)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze text sample: {e}")
            return {'error': str(e)}