from typing import List, Dict, Tuple, Set
import re
import math
from collections import Counter
import logging
from models.article import Article
from services.text_preprocessor import BengaliTextPreprocessor, EnglishTextPreprocessor

logger = logging.getLogger(__name__)


class ContentSimilarityMatcher:
    """Calculate content similarity between articles using multiple algorithms"""
    
    def __init__(self):
        self.bengali_preprocessor = BengaliTextPreprocessor()
        self.english_preprocessor = EnglishTextPreprocessor()
        
        # Common words that should be weighted less in similarity calculations
        self.common_words = {
            'bengali': {
                'বাংলাদেশ', 'ঢাকা', 'সরকার', 'প্রধানমন্ত্রী', 'মন্ত্রী', 'দেশ', 'জনগণ',
                'আজ', 'গতকাল', 'আগামীকাল', 'এখন', 'তখন', 'সময়', 'বছর', 'মাস', 'দিন'
            },
            'english': {
                'bangladesh', 'dhaka', 'government', 'minister', 'prime', 'country', 'people',
                'today', 'yesterday', 'tomorrow', 'now', 'then', 'time', 'year', 'month', 'day'
            }
        }
    
    def calculate_similarity(self, article1: Article, article2: Article) -> float:
        """
        Calculate overall similarity between two articles
        
        Returns:
            Similarity score between 0.0 and 1.0
        """
        try:
            # Combine title and content for both articles
            text1 = f"{article1.title} {article1.content}"
            text2 = f"{article2.title} {article2.content}"
            
            # Calculate different similarity metrics
            title_similarity = self._calculate_title_similarity(article1.title, article2.title)
            content_similarity = self._calculate_content_similarity(article1.content, article2.content)
            tfidf_similarity = self._calculate_tfidf_similarity(text1, text2)
            
            # Weighted combination of similarities
            weights = {
                'title': 0.4,      # Title similarity is very important
                'content': 0.4,    # Content similarity
                'tfidf': 0.2       # TF-IDF similarity for semantic matching
            }
            
            overall_similarity = (
                title_similarity * weights['title'] +
                content_similarity * weights['content'] +
                tfidf_similarity * weights['tfidf']
            )
            
            return min(1.0, max(0.0, overall_similarity))
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between article titles"""
        if not title1 or not title2:
            return 0.0
        
        # Preprocess titles
        title1_clean = self._preprocess_text(title1)
        title2_clean = self._preprocess_text(title2)
        
        # Tokenize
        tokens1 = set(title1_clean.split())
        tokens2 = set(title2_clean.split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between article contents"""
        if not content1 or not content2:
            return 0.0
        
        # Preprocess content
        content1_clean = self._preprocess_text(content1)
        content2_clean = self._preprocess_text(content2)
        
        # Calculate cosine similarity using word frequencies
        return self._cosine_similarity(content1_clean, content2_clean)
    
    def _calculate_tfidf_similarity(self, text1: str, text2: str) -> float:
        """Calculate TF-IDF based similarity"""
        if not text1 or not text2:
            return 0.0
        
        # Preprocess texts
        text1_clean = self._preprocess_text(text1)
        text2_clean = self._preprocess_text(text2)
        
        # Tokenize
        tokens1 = text1_clean.split()
        tokens2 = text2_clean.split()
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Calculate TF-IDF vectors
        tfidf1 = self._calculate_tfidf_vector(tokens1, [tokens1, tokens2])
        tfidf2 = self._calculate_tfidf_vector(tokens2, [tokens1, tokens2])
        
        # Calculate cosine similarity between TF-IDF vectors
        return self._vector_cosine_similarity(tfidf1, tfidf2)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for similarity calculation"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation and special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove very short words (less than 3 characters)
        words = [word for word in text.split() if len(word) >= 3]
        
        return ' '.join(words)
    
    def _cosine_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        # Get word frequencies
        words1 = text1.split()
        words2 = text2.split()
        
        freq1 = Counter(words1)
        freq2 = Counter(words2)
        
        # Get all unique words
        all_words = set(freq1.keys()).union(set(freq2.keys()))
        
        if not all_words:
            return 0.0
        
        # Create vectors
        vector1 = [freq1.get(word, 0) for word in all_words]
        vector2 = [freq2.get(word, 0) for word in all_words]
        
        # Calculate cosine similarity
        return self._vector_cosine_similarity(vector1, vector2)
    
    def _vector_cosine_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vector1) != len(vector2):
            return 0.0
        
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        
        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in vector1))
        magnitude2 = math.sqrt(sum(a * a for a in vector2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _calculate_tfidf_vector(self, tokens: List[str], all_documents: List[List[str]]) -> List[float]:
        """Calculate TF-IDF vector for a document"""
        # Calculate term frequencies
        tf = Counter(tokens)
        total_terms = len(tokens)
        
        # Calculate document frequencies
        df = {}
        for doc in all_documents:
            unique_terms = set(doc)
            for term in unique_terms:
                df[term] = df.get(term, 0) + 1
        
        # Calculate TF-IDF
        tfidf_vector = []
        all_terms = sorted(set(term for doc in all_documents for term in doc))
        
        for term in all_terms:
            # Term frequency
            tf_score = tf.get(term, 0) / total_terms if total_terms > 0 else 0
            
            # Inverse document frequency
            idf_score = math.log(len(all_documents) / df.get(term, 1))
            
            # TF-IDF score
            tfidf_score = tf_score * idf_score
            tfidf_vector.append(tfidf_score)
        
        return tfidf_vector
    
    def find_similar_articles(self, target_article: Article, candidate_articles: List[Article], 
                            threshold: float = 0.3) -> List[Tuple[Article, float]]:
        """
        Find articles similar to the target article
        
        Args:
            target_article: Article to find similarities for
            candidate_articles: List of articles to compare against
            threshold: Minimum similarity threshold
            
        Returns:
            List of (article, similarity_score) tuples sorted by similarity
        """
        similar_articles = []
        
        for candidate in candidate_articles:
            # Skip if same article
            if candidate.url == target_article.url:
                continue
            
            # Calculate similarity
            similarity = self.calculate_similarity(target_article, candidate)
            
            # Add to results if above threshold
            if similarity >= threshold:
                similar_articles.append((candidate, similarity))
        
        # Sort by similarity score (descending)
        similar_articles.sort(key=lambda x: x[1], reverse=True)
        
        return similar_articles
    
    def group_similar_articles(self, articles: List[Article], threshold: float = 0.4) -> List[List[Article]]:
        """
        Group articles by similarity
        
        Args:
            articles: List of articles to group
            threshold: Similarity threshold for grouping
            
        Returns:
            List of article groups (each group is a list of similar articles)
        """
        if not articles:
            return []
        
        groups = []
        processed = set()
        
        for i, article in enumerate(articles):
            if article.url in processed:
                continue
            
            # Start new group with current article
            current_group = [article]
            processed.add(article.url)
            
            # Find similar articles
            for j, other_article in enumerate(articles[i+1:], i+1):
                if other_article.url in processed:
                    continue
                
                similarity = self.calculate_similarity(article, other_article)
                if similarity >= threshold:
                    current_group.append(other_article)
                    processed.add(other_article.url)
            
            groups.append(current_group)
        
        # Sort groups by size (largest first)
        groups.sort(key=len, reverse=True)
        
        return groups
    
    def calculate_topic_similarity(self, article1: Article, article2: Article) -> float:
        """
        Calculate topic-based similarity focusing on key entities and topics
        
        Returns:
            Topic similarity score between 0.0 and 1.0
        """
        try:
            # Extract key entities and topics from both articles
            entities1 = self._extract_key_entities(f"{article1.title} {article1.content}")
            entities2 = self._extract_key_entities(f"{article2.title} {article2.content}")
            
            if not entities1 or not entities2:
                return 0.0
            
            # Calculate entity overlap
            common_entities = entities1.intersection(entities2)
            total_entities = entities1.union(entities2)
            
            if not total_entities:
                return 0.0
            
            return len(common_entities) / len(total_entities)
            
        except Exception as e:
            logger.error(f"Failed to calculate topic similarity: {e}")
            return 0.0
    
    def _extract_key_entities(self, text: str) -> Set[str]:
        """Extract key entities and important terms from text"""
        # Preprocess text
        text_clean = self._preprocess_text(text)
        tokens = text_clean.split()
        
        # Filter out common words and short words
        entities = set()
        for token in tokens:
            if (len(token) >= 4 and 
                token not in self.common_words.get('bengali', set()) and 
                token not in self.common_words.get('english', set())):
                entities.add(token)
        
        return entities