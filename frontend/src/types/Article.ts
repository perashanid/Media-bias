export interface BiasScore {
  sentiment_score: number;
  political_bias_score: number;
  emotional_language_score: number;
  factual_vs_opinion_score: number;
  overall_bias_score: number;
  analyzed_at: string;
}

export interface Article {
  id: string;
  url: string;
  title: string;
  content: string;
  author?: string;
  publication_date: string;
  source: string;
  scraped_at: string;
  language: string;
  content_hash?: string;
  bias_scores?: BiasScore;
}

export interface ComparisonReport {
  story_id: string;
  articles: Article[];
  bias_differences: Record<string, number>;
  key_differences: string[];
  similarity_scores: Record<string, number>;
  created_at: string;
}

export interface SourceStatistics {
  total_articles: number;
  analyzed_articles: number;
  analysis_percentage: number;
  average_bias_scores: {
    sentiment: number;
    political_bias: number;
    emotional_language: number;
    factual_content: number;
    overall_bias: number;
  };
  language_distribution: Record<string, number>;
}

export interface BiasAnalysisResult {
  sentiment_score: number;
  political_bias_score: number;
  emotional_language_score: number;
  factual_vs_opinion_score: number;
  overall_bias_score: number;
  bias_classification: string;
  language: string;
}