import re
from typing import List, Set
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class TopicExtractor:
    """Service for extracting topics from article content"""
    
    # Common Bengali and English stop words
    STOP_WORDS = {
        'english': {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'said', 'says', 'say', 'told', 'tells',
            'news', 'report', 'reports', 'today', 'yesterday', 'tomorrow', 'now', 'then', 'here', 'there'
        },
        'bengali': {
            'এই', 'সেই', 'যে', 'যা', 'কি', 'কে', 'কার', 'কাকে', 'কিন্তু', 'এবং', 'অথবা', 'বা', 'না',
            'হয়', 'হয়েছে', 'হবে', 'করে', 'করেছে', 'করবে', 'বলে', 'বলেছে', 'বলেন', 'জানায়', 'জানিয়েছে',
            'আজ', 'কাল', 'গতকাল', 'আগামীকাল', 'এখন', 'তখন', 'এখানে', 'সেখানে', 'খবর', 'সংবাদ', 'প্রতিবেদন'
        }
    }
    
    # Common topic categories in Bengali and English
    TOPIC_CATEGORIES = {
        'politics': ['রাজনীতি', 'সরকার', 'মন্ত্রী', 'প্রধানমন্ত্রী', 'রাষ্ট্রপতি', 'নির্বাচন', 'ভোট', 'দল', 'politics', 'government', 'minister', 'election', 'vote', 'party'],
        'economy': ['অর্থনীতি', 'ব্যাংক', 'টাকা', 'দাম', 'বাজার', 'ব্যবসা', 'শিল্প', 'economy', 'bank', 'money', 'price', 'market', 'business', 'industry'],
        'sports': ['খেলা', 'ক্রিকেট', 'ফুটবল', 'খেলোয়াড়', 'ম্যাচ', 'টুর্নামেন্ট', 'sports', 'cricket', 'football', 'player', 'match', 'tournament'],
        'education': ['শিক্ষা', 'স্কুল', 'কলেজ', 'বিশ্ববিদ্যালয়', 'ছাত্র', 'পরীক্ষা', 'education', 'school', 'college', 'university', 'student', 'exam'],
        'health': ['স্বাস্থ্য', 'হাসপাতাল', 'ডাক্তার', 'চিকিৎসা', 'রোগ', 'ওষুধ', 'health', 'hospital', 'doctor', 'treatment', 'disease', 'medicine'],
        'technology': ['প্রযুক্তি', 'কম্পিউটার', 'ইন্টারনেট', 'মোবাইল', 'সফটওয়্যার', 'technology', 'computer', 'internet', 'mobile', 'software'],
        'international': ['আন্তর্জাতিক', 'বিদেশ', 'দেশ', 'যুক্তরাষ্ট্র', 'ভারত', 'চীন', 'international', 'foreign', 'country', 'usa', 'india', 'china'],
        'crime': ['অপরাধ', 'পুলিশ', 'গ্রেফতার', 'চুরি', 'ডাকাতি', 'হত্যা', 'crime', 'police', 'arrest', 'theft', 'robbery', 'murder'],
        'entertainment': ['বিনোদন', 'সিনেমা', 'নাটক', 'গান', 'শিল্পী', 'অভিনেতা', 'entertainment', 'movie', 'drama', 'song', 'artist', 'actor'],
        'weather': ['আবহাওয়া', 'বৃষ্টি', 'ঝড়', 'গরম', 'ঠান্ডা', 'weather', 'rain', 'storm', 'hot', 'cold']
    }
    
    def extract_topics(self, title: str, content: str, language: str = 'bengali') -> List[str]:
        """Extract topics from article title and content"""
        try:
            # Combine title and content for analysis
            text = f"{title} {content}"
            
            # Extract keywords
            keywords = self._extract_keywords(text, language)
            
            # Categorize topics
            topics = self._categorize_topics(keywords, language)
            
            # Add direct keyword matches
            direct_topics = self._extract_direct_topics(text, language)
            topics.extend(direct_topics)
            
            # Remove duplicates and limit to top 5 topics
            unique_topics = list(dict.fromkeys(topics))[:5]
            
            logger.debug(f"Extracted topics: {unique_topics}")
            return unique_topics
            
        except Exception as e:
            logger.error(f"Failed to extract topics: {e}")
            return []
    
    def _extract_keywords(self, text: str, language: str) -> List[str]:
        """Extract meaningful keywords from text"""
        # Clean and normalize text
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Remove stop words
        stop_words = self.STOP_WORDS.get(language, set())
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Count word frequency
        word_counts = Counter(filtered_words)
        
        # Return top keywords
        return [word for word, count in word_counts.most_common(20) if count > 1]
    
    def _categorize_topics(self, keywords: List[str], language: str) -> List[str]:
        """Categorize keywords into topic categories"""
        topics = []
        
        for category, category_words in self.TOPIC_CATEGORIES.items():
            # Check if any keywords match this category
            matches = sum(1 for keyword in keywords if any(cat_word in keyword for cat_word in category_words))
            if matches > 0:
                topics.append(category)
        
        return topics
    
    def _extract_direct_topics(self, text: str, language: str) -> List[str]:
        """Extract direct topic mentions from text"""
        topics = []
        text_lower = text.lower()
        
        # Look for direct mentions of topic categories
        for category, category_words in self.TOPIC_CATEGORIES.items():
            for word in category_words:
                if word.lower() in text_lower:
                    topics.append(category)
                    break
        
        return topics
    
    def get_available_topics(self) -> List[str]:
        """Get list of all available topic categories"""
        return list(self.TOPIC_CATEGORIES.keys())