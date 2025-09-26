import axios from 'axios';
import { Article, ComparisonReport, SourceStatistics, BiasAnalysisResult } from '../types/Article';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Articles API
export const articlesApi = {
  getArticles: async (params?: {
    source?: string;
    limit?: number;
    skip?: number;
    start_date?: string;
    end_date?: string;
  }) => {
    const response = await api.get('/articles', { params });
    return response.data;
  },

  getArticle: async (id: string): Promise<Article> => {
    const response = await api.get(`/articles/${id}`);
    return response.data;
  },

  searchArticles: async (query: string, limit?: number) => {
    const response = await api.get('/articles/search', {
      params: { q: query, limit },
    });
    return response.data;
  },

  getArticleBias: async (id: string) => {
    const response = await api.get(`/articles/${id}/bias`);
    return response.data;
  },

  analyzeArticleBias: async (id: string) => {
    const response = await api.post(`/articles/${id}/bias`);
    return response.data;
  },
};

// Bias Analysis API
export const biasApi = {
  analyzeText: async (text: string, language?: string): Promise<BiasAnalysisResult> => {
    const response = await api.post('/bias/analyze-text', { text, language });
    return response.data;
  },

  batchAnalyze: async (articleIds: string[]) => {
    const response = await api.post('/bias/batch-analyze', { article_ids: articleIds });
    return response.data;
  },

  analyzePending: async (limit?: number) => {
    const response = await api.post('/bias/analyze-pending', { limit });
    return response.data;
  },

  getBiasDistribution: async (params?: { days?: number; source?: string }) => {
    const response = await api.get('/bias/distribution', { params });
    return response.data;
  },
};

// Comparison API
export const comparisonApi = {
  getSimilarArticles: async (articleId: string, threshold?: number) => {
    const response = await api.get(`/comparison/articles/${articleId}/similar`, {
      params: { threshold },
    });
    return response.data;
  },

  getComparisonReport: async (articleId: string): Promise<ComparisonReport> => {
    const response = await api.get(`/comparison/articles/${articleId}/report`);
    return response.data;
  },

  compareSources: async (days?: number) => {
    const response = await api.get('/comparison/sources', {
      params: { days },
    });
    return response.data;
  },

  getStoryClusters: async (params?: { days?: number; threshold?: number }) => {
    const response = await api.get('/comparison/clusters', { params });
    return response.data;
  },

  calculateBiasDifferences: async (articleIds: string[]) => {
    const response = await api.post('/comparison/bias-differences', { article_ids: articleIds });
    return response.data;
  },

  customComparison: async (inputs: Array<{
    type: 'url' | 'text' | 'article_id';
    value: string;
    title?: string;
    source?: string;
    language?: string;
  }>) => {
    const response = await api.post('/comparison/custom', { inputs });
    return response.data;
  },
};

// Statistics API
export const statisticsApi = {
  getOverview: async () => {
    const response = await api.get('/statistics/overview');
    return response.data;
  },

  getSourceStatistics: async (days?: number): Promise<{ source_statistics: Record<string, SourceStatistics> }> => {
    const response = await api.get('/statistics/sources', {
      params: { days },
    });
    return response.data;
  },

  getBiasTrends: async (params?: { days?: number; source?: string }) => {
    const response = await api.get('/statistics/bias-trends', { params });
    return response.data;
  },

  getComparisonSummary: async (days?: number) => {
    const response = await api.get('/statistics/comparison-summary', {
      params: { days },
    });
    return response.data;
  },
};

// Scraping API
export const scrapingApi = {
  getAvailableSources: async () => {
    const response = await api.get('/scrape/sources');
    return response.data;
  },

  manualScrape: async (params: { url?: string; source?: string }) => {
    const response = await api.post('/scrape/manual', params);
    return response.data;
  },

  testUrl: async (url: string) => {
    const response = await api.post('/scrape/test-url', { url });
    return response.data;
  },
};

// Health check
export const healthApi = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;