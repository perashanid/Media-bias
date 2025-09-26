from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import logging
from models.article import Article, ComparisonReport
from services.content_similarity_matcher import ContentSimilarityMatcher
from services.bias_analyzer import BiasAnalyzer

logger = logging.getLogger(__name__)


class ArticleComparator:
    """Compare articles and generate bias comparison reports"""
    
    def __init__(self):
        self.similarity_matcher = ContentSimilarityMatcher()
        self.bias_analyzer = BiasAnalyzer()
        
    def find_related_articles(self, target_article: Article, candidate_articles: List[Article],
                            similarity_threshold: float = 0.3, time_window_hours: int = 72) -> List[Article]:
        """
        Find articles related to the target article
        
        Args:
            target_article: Article to find related articles for
            candidate_articles: Pool of articles to search in
            similarity_threshold: Minimum similarity score to consider articles related
            time_window_hours: Time window in hours to look for related articles
            
        Returns:
            List of related articles sorted by similarity
        """
        try:
            # Filter candidates by time window
            time_filtered_candidates = self._filter_by_time_window(
                target_article, candidate_articles, time_window_hours
            )
            
            # Find similar articles
            similar_articles = self.similarity_matcher.find_similar_articles(
                target_article, time_filtered_candidates, similarity_threshold
            )
            
            # Extract just the articles (without similarity scores)
            related_articles = [article for article, _ in similar_articles]
            
            logger.info(f"Found {len(related_articles)} related articles for: {target_article.title[:50]}...")
            return related_articles
            
        except Exception as e:
            logger.error(f"Failed to find related articles: {e}")
            return []
    
    def _filter_by_time_window(self, target_article: Article, candidates: List[Article], 
                              time_window_hours: int) -> List[Article]:
        """Filter candidate articles by time window"""
        target_time = target_article.publication_date
        time_delta = timedelta(hours=time_window_hours)
        
        filtered_candidates = []
        for candidate in candidates:
            # Skip same article
            if candidate.url == target_article.url:
                continue
            
            # Check if within time window
            time_diff = abs(candidate.publication_date - target_time)
            if time_diff <= time_delta:
                filtered_candidates.append(candidate)
        
        return filtered_candidates
    
    def calculate_bias_differences(self, articles: List[Article]) -> Dict[str, float]:
        """
        Calculate percentage differences in bias scores between sources
        
        Args:
            articles: List of related articles from different sources
            
        Returns:
            Dictionary mapping source pairs to percentage differences
        """
        try:
            if len(articles) < 2:
                return {}
            
            # Ensure all articles have bias scores
            for article in articles:
                if not article.bias_scores:
                    article.bias_scores = self.bias_analyzer.analyze_article_bias(article)
            
            bias_differences = {}
            
            # Compare each pair of articles
            for i, article1 in enumerate(articles):
                for j, article2 in enumerate(articles[i+1:], i+1):
                    source_pair = f"{article1.source} vs {article2.source}"
                    
                    # Calculate percentage difference in overall bias
                    bias1 = article1.bias_scores.overall_bias_score
                    bias2 = article2.bias_scores.overall_bias_score
                    
                    # Calculate percentage difference
                    avg_bias = (bias1 + bias2) / 2
                    if avg_bias > 0:
                        percentage_diff = abs(bias1 - bias2) / avg_bias * 100
                    else:
                        percentage_diff = 0.0
                    
                    bias_differences[source_pair] = percentage_diff
            
            return bias_differences
            
        except Exception as e:
            logger.error(f"Failed to calculate bias differences: {e}")
            return {}
    
    def generate_comparison_report(self, articles: List[Article]) -> Optional[ComparisonReport]:
        """
        Generate comprehensive comparison report for related articles
        
        Args:
            articles: List of related articles to compare
            
        Returns:
            ComparisonReport object or None if generation fails
        """
        try:
            if len(articles) < 2:
                logger.warning("Need at least 2 articles to generate comparison report")
                return None
            
            # Generate unique story ID based on articles
            story_id = self._generate_story_id(articles)
            
            # Calculate bias differences
            bias_differences = self.calculate_bias_differences(articles)
            
            # Calculate similarity scores between all pairs
            similarity_scores = self._calculate_pairwise_similarities(articles)
            
            # Identify key differences in coverage
            key_differences = self._identify_key_differences(articles)
            
            # Create comparison report
            report = ComparisonReport(
                story_id=story_id,
                articles=articles,
                bias_differences=bias_differences,
                key_differences=key_differences,
                similarity_scores=similarity_scores,
                created_at=datetime.now()
            )
            
            logger.info(f"Generated comparison report for story: {story_id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate comparison report: {e}")
            return None
    
    def _generate_story_id(self, articles: List[Article]) -> str:
        """Generate unique story ID for a group of related articles"""
        # Use the earliest publication date and a hash of combined titles
        earliest_date = min(article.publication_date for article in articles)
        combined_titles = " ".join(article.title for article in articles)
        
        # Create a simple hash
        title_hash = abs(hash(combined_titles)) % 10000
        
        # Format: YYYYMMDD_HASH
        story_id = f"{earliest_date.strftime('%Y%m%d')}_{title_hash:04d}"
        return story_id
    
    def _calculate_pairwise_similarities(self, articles: List[Article]) -> Dict[str, float]:
        """Calculate similarity scores between all pairs of articles"""
        similarity_scores = {}
        
        for i, article1 in enumerate(articles):
            for j, article2 in enumerate(articles[i+1:], i+1):
                source_pair = f"{article1.source}_{article2.source}"
                similarity = self.similarity_matcher.calculate_similarity(article1, article2)
                similarity_scores[source_pair] = similarity
        
        return similarity_scores
    
    def _identify_key_differences(self, articles: List[Article]) -> List[str]:
        """Identify key differences in how sources cover the story"""
        key_differences = []
        
        try:
            # Analyze bias score differences
            bias_scores = []
            for article in articles:
                if article.bias_scores:
                    bias_scores.append({
                        'source': article.source,
                        'sentiment': article.bias_scores.sentiment_score,
                        'political': article.bias_scores.political_bias_score,
                        'emotional': article.bias_scores.emotional_language_score,
                        'factual': article.bias_scores.factual_vs_opinion_score
                    })
            
            if len(bias_scores) >= 2:
                # Find sources with most positive/negative sentiment
                sentiment_scores = [(score['source'], score['sentiment']) for score in bias_scores]
                sentiment_scores.sort(key=lambda x: x[1])
                
                if sentiment_scores[-1][1] - sentiment_scores[0][1] > 0.3:
                    key_differences.append(
                        f"{sentiment_scores[-1][0]} shows more positive sentiment than {sentiment_scores[0][0]}"
                    )
                
                # Find sources with different political leanings
                political_scores = [(score['source'], score['political']) for score in bias_scores]
                political_scores.sort(key=lambda x: x[1])
                
                if political_scores[-1][1] - political_scores[0][1] > 0.3:
                    key_differences.append(
                        f"{political_scores[-1][0]} shows more right-leaning bias than {political_scores[0][0]}"
                    )
                
                # Find sources with different factual vs opinion content
                factual_scores = [(score['source'], score['factual']) for score in bias_scores]
                factual_scores.sort(key=lambda x: x[1])
                
                if factual_scores[-1][1] - factual_scores[0][1] > 0.3:
                    key_differences.append(
                        f"{factual_scores[-1][0]} provides more factual content than {factual_scores[0][0]}"
                    )
            
            # Analyze content length differences
            content_lengths = [(article.source, len(article.content)) for article in articles]
            content_lengths.sort(key=lambda x: x[1])
            
            if len(content_lengths) >= 2:
                longest = content_lengths[-1]
                shortest = content_lengths[0]
                
                if longest[1] > shortest[1] * 2:  # More than double the length
                    key_differences.append(
                        f"{longest[0]} provides significantly more detailed coverage than {shortest[0]}"
                    )
            
        except Exception as e:
            logger.error(f"Failed to identify key differences: {e}")
            key_differences.append("Unable to analyze key differences due to processing error")
        
        return key_differences
    
    def compare_source_bias_patterns(self, articles_by_source: Dict[str, List[Article]]) -> Dict[str, Any]:
        """
        Compare bias patterns across different news sources
        
        Args:
            articles_by_source: Dictionary mapping source names to lists of articles
            
        Returns:
            Dictionary with bias pattern analysis by source
        """
        try:
            source_analysis = {}
            
            for source, articles in articles_by_source.items():
                if not articles:
                    continue
                
                # Ensure articles have bias scores
                analyzed_articles = []
                for article in articles:
                    if not article.bias_scores:
                        article.bias_scores = self.bias_analyzer.analyze_article_bias(article)
                    analyzed_articles.append(article)
                
                # Calculate average bias scores for this source
                sentiment_scores = [a.bias_scores.sentiment_score for a in analyzed_articles]
                political_scores = [a.bias_scores.political_bias_score for a in analyzed_articles]
                emotional_scores = [a.bias_scores.emotional_language_score for a in analyzed_articles]
                factual_scores = [a.bias_scores.factual_vs_opinion_score for a in analyzed_articles]
                overall_scores = [a.bias_scores.overall_bias_score for a in analyzed_articles]
                
                source_analysis[source] = {
                    'article_count': len(analyzed_articles),
                    'average_sentiment': sum(sentiment_scores) / len(sentiment_scores),
                    'average_political_bias': sum(political_scores) / len(political_scores),
                    'average_emotional_language': sum(emotional_scores) / len(emotional_scores),
                    'average_factual_content': sum(factual_scores) / len(factual_scores),
                    'average_overall_bias': sum(overall_scores) / len(overall_scores),
                    'sentiment_range': max(sentiment_scores) - min(sentiment_scores),
                    'political_bias_range': max(political_scores) - min(political_scores)
                }
            
            return source_analysis
            
        except Exception as e:
            logger.error(f"Failed to compare source bias patterns: {e}")
            return {}
    
    def find_story_clusters(self, articles: List[Article], similarity_threshold: float = 0.4) -> List[List[Article]]:
        """
        Group articles into story clusters based on content similarity
        
        Args:
            articles: List of articles to cluster
            similarity_threshold: Minimum similarity to group articles together
            
        Returns:
            List of article clusters (each cluster is a list of similar articles)
        """
        try:
            clusters = self.similarity_matcher.group_similar_articles(articles, similarity_threshold)
            
            # Filter out single-article clusters for comparison purposes
            multi_article_clusters = [cluster for cluster in clusters if len(cluster) > 1]
            
            logger.info(f"Found {len(multi_article_clusters)} story clusters with multiple articles")
            return multi_article_clusters
            
        except Exception as e:
            logger.error(f"Failed to find story clusters: {e}")
            return []